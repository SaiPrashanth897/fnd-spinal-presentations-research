from __future__ import annotations

from typing import Any

import pandas as pd


def summarize_records(df: pd.DataFrame) -> dict[str, Any]:
    """Generate summary metrics for the literature dataset."""
    if df.empty:
        return {"records": 0, "by_year": {}, "by_journal": {}, "by_query": {}}

    frame = df.copy()
    frame["publication_year"] = pd.to_numeric(frame["publication_year"], errors="coerce")
    by_year = frame["publication_year"].dropna().astype(int).value_counts().sort_index().to_dict()
    by_journal = frame["journal"].fillna("Unknown").astype(str).value_counts().head(10).to_dict()
    by_query = frame["query"].fillna("Unknown").astype(str).value_counts().head(10).to_dict()

    return {
        "records": int(len(frame)),
        "by_year": {str(key): val for key, val in by_year.items()},
        "by_journal": by_journal,
        "by_query": by_query,
    }


def top_documents(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    frame = df.copy()
    if "publication_year" in frame.columns:
        frame["publication_year"] = pd.to_numeric(frame["publication_year"], errors="coerce")
    return frame.sort_values(["publication_year", "title"], ascending=[False, True], na_position="last").head(n)


def generate_report(df: pd.DataFrame) -> str:
    summary = summarize_records(df)
    top = top_documents(df, 5)
    lines = [
        "Functional Neurological Disorder in Spinal Presentations — Research Summary",
        "=" * 72,
        f"Total records reviewed: {summary['records']}",
        "",
        "Publication by year:",
    ]

    for year, count in summary["by_year"].items():
        lines.append(f"- {year}: {count} records")

    lines.extend(["", "Top research topics:"])
    for query, count in summary["by_query"].items():
        lines.append(f"- {query}: {count} records")

    lines.extend(["", "Top papers:"])
    for _, row in top.iterrows():
        title = row.get("title", "Unknown")
        year = row.get("publication_year", "n/a")
        journal = row.get("journal", "Unknown")
        lines.append(f"- {title} ({year}) — {journal}")

    return "\n".join(lines)
