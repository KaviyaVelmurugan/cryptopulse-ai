"""Pinned FinBERT inference and a fair comparison with the VADER baseline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Protocol, Sequence

from .contracts import AssetId, DatasetSplit, HumanAnnotation, SentimentLabel, SentimentPrediction
from .preprocessing import clean_article, deduplicate_articles
from .sentiment import VaderBaseline, deduplicated_annotations, evaluate
from .validation import load_csv, parse_annotation_row, parse_news_row


FINBERT_MODEL_ID = "ProsusAI/finbert"
FINBERT_REVISION = "4556d13015211d73dccd3fdd39d39232506f3e43"
FINBERT_MODEL_LICENSE = "not_declared_by_upstream"
LABEL_ORDER = tuple(SentimentLabel)


class InferenceRunner(Protocol):
    def __call__(self, texts: Sequence[str]) -> list[list[dict[str, object]]]: ...


class HuggingFaceRunner:
    """Lazy adapter so the large ML dependencies remain optional."""

    def __init__(self, *, device: str = "cpu") -> None:
        try:
            from transformers import pipeline
        except ImportError as error:
            raise RuntimeError(
                "FinBERT dependencies are not installed. Run: python -m pip install -e .[ml]"
            ) from error
        self._pipeline: Callable[..., object] = pipeline(
            "text-classification",
            model=FINBERT_MODEL_ID,
            tokenizer=FINBERT_MODEL_ID,
            revision=FINBERT_REVISION,
            device=device,
            trust_remote_code=False,
        )

    def __call__(self, texts: Sequence[str]) -> list[list[dict[str, object]]]:
        result = self._pipeline(list(texts), top_k=None, truncation=True, batch_size=1)
        if not isinstance(result, list):
            raise ValueError("FinBERT returned an unexpected response")
        return result  # type: ignore[return-value]


def _probabilities(raw_scores: Sequence[dict[str, object]]) -> dict[SentimentLabel, float]:
    aliases = {
        "positive": SentimentLabel.POSITIVE,
        "negative": SentimentLabel.NEGATIVE,
        "neutral": SentimentLabel.NEUTRAL,
        "label_0": SentimentLabel.POSITIVE,
        "label_1": SentimentLabel.NEGATIVE,
        "label_2": SentimentLabel.NEUTRAL,
    }
    probabilities: dict[SentimentLabel, float] = {}
    for item in raw_scores:
        label = str(item.get("label", "")).lower()
        if label not in aliases:
            raise ValueError(f"FinBERT returned unknown label: {label or '<empty>'}")
        score = float(item.get("score", -1))
        if not 0 <= score <= 1:
            raise ValueError("FinBERT probabilities must be between 0 and 1")
        probabilities[aliases[label]] = score
    if set(probabilities) != set(LABEL_ORDER):
        raise ValueError("FinBERT must return positive, negative, and neutral scores")
    if abs(sum(probabilities.values()) - 1.0) > 0.002:
        raise ValueError("FinBERT probabilities must sum to 1")
    return probabilities


class FinBertBaseline:
    def __init__(self, runner: InferenceRunner | None = None) -> None:
        self.runner = runner or HuggingFaceRunner()

    def score_many(
        self,
        requests: Sequence[tuple[object, AssetId]],
        *,
        predicted_at: datetime,
    ) -> list[SentimentPrediction]:
        if predicted_at.tzinfo is None or predicted_at.utcoffset() != UTC.utcoffset(predicted_at):
            raise ValueError("predicted_at must use UTC")
        articles = [request[0] for request in requests]
        texts = [getattr(article, "model_text") for article in articles]
        outputs = self.runner(texts)
        if len(outputs) != len(requests):
            raise ValueError("FinBERT returned a different number of predictions than inputs")
        predictions: list[SentimentPrediction] = []
        for (article, asset_id), raw_scores in zip(requests, outputs, strict=True):
            probabilities = _probabilities(raw_scores)
            label = max(LABEL_ORDER, key=probabilities.__getitem__)
            article_id = getattr(article, "article_id")
            preprocessing_version = getattr(article, "preprocessing_version")
            identity = f"{article_id}|{asset_id.value}|{FINBERT_MODEL_ID}|{FINBERT_REVISION}"
            predictions.append(
                SentimentPrediction(
                    prediction_id=f"finbert_{hashlib.sha256(identity.encode()).hexdigest()[:20]}",
                    article_id=article_id,
                    target_asset_id=asset_id,
                    negative_probability=probabilities[SentimentLabel.NEGATIVE],
                    neutral_probability=probabilities[SentimentLabel.NEUTRAL],
                    positive_probability=probabilities[SentimentLabel.POSITIVE],
                    predicted_label=label,
                    evidence_text=getattr(article, "model_text"),
                    model_name=FINBERT_MODEL_ID,
                    model_version=FINBERT_REVISION,
                    preprocessing_version=preprocessing_version,
                    predicted_at=predicted_at.astimezone(UTC),
                )
            )
        return predictions


@dataclass(frozen=True, slots=True)
class CalibrationMetrics:
    multiclass_brier_score: float
    expected_calibration_error: float
    bin_count: int


def calibration(
    annotations: Sequence[HumanAnnotation],
    predictions: dict[tuple[str, AssetId], SentimentPrediction],
    *,
    bin_count: int = 5,
) -> CalibrationMetrics:
    if bin_count < 1:
        raise ValueError("bin_count must be positive")
    if not annotations:
        return CalibrationMetrics(0.0, 0.0, bin_count)
    brier_total = 0.0
    bins: list[list[tuple[float, int]]] = [[] for _ in range(bin_count)]
    for annotation in annotations:
        prediction = predictions[(annotation.article_id, annotation.target_asset_id)]
        probs = {
            SentimentLabel.NEGATIVE: prediction.negative_probability,
            SentimentLabel.NEUTRAL: prediction.neutral_probability,
            SentimentLabel.POSITIVE: prediction.positive_probability,
        }
        brier_total += sum(
            (probability - float(label == annotation.sentiment_label)) ** 2
            for label, probability in probs.items()
        )
        confidence = max(probs.values())
        correct = int(prediction.predicted_label == annotation.sentiment_label)
        bins[min(int(confidence * bin_count), bin_count - 1)].append((confidence, correct))
    ece = sum(
        (len(bucket) / len(annotations))
        * abs(sum(x[0] for x in bucket) / len(bucket) - sum(x[1] for x in bucket) / len(bucket))
        for bucket in bins
        if bucket
    )
    return CalibrationMetrics(round(brier_total / len(annotations), 4), round(ece, 4), bin_count)


def generate_comparison_reports(
    news_path: Path,
    annotations_path: Path,
    output_dir: Path,
    *,
    predicted_at: datetime,
    runner: InferenceRunner | None = None,
) -> dict[str, object]:
    articles = load_csv(news_path, parse_news_row, "news_articles")
    annotations = load_csv(annotations_path, parse_annotation_row, "annotations")
    cleaned = {article.article_id: clean_article(article) for article in articles}
    dedup = deduplicate_articles(articles, cleaned)
    unique_keys = sorted(
        {(item.article_id, item.target_asset_id) for item in annotations},
        key=lambda item: (item[0], item[1].value),
    )
    requests = [(cleaned[article_id], asset_id) for article_id, asset_id in unique_keys]
    finbert_values = FinBertBaseline(runner).score_many(requests, predicted_at=predicted_at)
    finbert = {(item.article_id, item.target_asset_id): item for item in finbert_values}
    vader_model = VaderBaseline()
    vader = {
        key: vader_model.score(cleaned[key[0]], key[1], predicted_at=predicted_at) for key in unique_keys
    }
    deduplicated = deduplicated_annotations(annotations, dedup.group_by_article_id)
    test = [item for item in annotations if item.dataset_split == DatasetSplit.TEST]
    slices = {"all_records": annotations, "deduplicated_records": deduplicated, "locked_test_split": test}
    result: dict[str, object] = {
        "warning": "Synthetic sample metrics validate plumbing only; they are not model-performance claims.",
        "model": {
            "id": FINBERT_MODEL_ID,
            "revision": FINBERT_REVISION,
            "upstream_license": FINBERT_MODEL_LICENSE,
        },
        "evaluations": {},
    }
    evaluations: dict[str, object] = {}
    for name, rows in slices.items():
        evaluations[name] = {
            "vader": asdict(evaluate(rows, vader)),
            "finbert": asdict(evaluate(rows, finbert)),
            "finbert_calibration": asdict(calibration(rows, finbert)),
        }
    result["evaluations"] = evaluations
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "model_comparison.json").open("w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    with (output_dir / "finbert_predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "prediction_id", "article_id", "target_asset_id", "negative_probability",
            "neutral_probability", "positive_probability", "predicted_label", "model_name",
            "model_version", "preprocessing_version", "predicted_at",
        ))
        writer.writeheader()
        for item in finbert_values:
            writer.writerow({
                "prediction_id": item.prediction_id,
                "article_id": item.article_id,
                "target_asset_id": item.target_asset_id.value,
                "negative_probability": f"{item.negative_probability:.6f}",
                "neutral_probability": f"{item.neutral_probability:.6f}",
                "positive_probability": f"{item.positive_probability:.6f}",
                "predicted_label": item.predicted_label.value,
                "model_name": item.model_name,
                "model_version": item.model_version,
                "preprocessing_version": item.preprocessing_version,
                "predicted_at": item.predicted_at.isoformat().replace("+00:00", "Z"),
            })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pinned FinBERT comparison")
    parser.add_argument("--news", type=Path, default=Path("data/sample/news_articles.csv"))
    parser.add_argument("--annotations", type=Path, default=Path("data/sample/annotations.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/model_comparison"))
    args = parser.parse_args()
    annotation_rows = load_csv(args.annotations, parse_annotation_row, "annotations")
    result = generate_comparison_reports(
        args.news,
        args.annotations,
        args.output,
        predicted_at=max(item.created_at for item in annotation_rows),
    )
    sample = result["evaluations"]["deduplicated_records"]  # type: ignore[index]
    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    main()
