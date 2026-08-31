import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CryptoPulse AI | Explainable Market Intelligence",
  description: "Evidence-first Bitcoin and Ethereum sentiment research dashboard.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
