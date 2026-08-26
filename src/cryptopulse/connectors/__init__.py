"""Approved external data connectors."""

from .coinbase import CoinbaseCandleConnector
from .newsapi import NewsApiConnector

__all__ = ["CoinbaseCandleConnector", "NewsApiConnector"]
