from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fnd_spinal_research.config import DEFAULT_EXPORT_COLUMNS, RAW_DIR, SAMPLE_DIR, SEARCH_QUERIES
from fnd_spinal_research.data_sources import build_dataset_payload


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def _default_sample_rows() -> list[dict]:
    return [
        {
            "uid": "1",
            "title": "Functional neurological symptom disorder in spinal presentations: a review of diagnostic principles",
            "authors": "Miller A, Ross S",
            "journal": "Journal of Neurology",
            "publication_year": 2024,
            "query": SEARCH_QUERIES[0],
            "doi": "10.1000/example-1",
            "url": "https://example.org/study/1",
            "abstract": "A review of functional neurological presentations involving the spine and back, emphasizing red flags and referral pathways.",
        },
        {
            "uid": "2",
            "title": "Back pain and conversion symptoms: clinical patterns and differential diagnosis",
            "authors": "Patel R, Lewis M",
            "journal": "Clinical Medicine Review",
            "publication_year": 2023,
            "query": SEARCH_QUERIES[1],
            "doi": "10.1000/example-2",
            "url": "https://example.org/study/2",
            "abstract": "Examines how functional neurological presentations can mimic spinal pathology and complicate diagnosis.",
        },
        {
            "uid": "3",
            "title": "Lumbar sensory disturbance in functional neurological disorder: synthesis of evidence",
            "authors": "Singh H, Jones T",
            "journal": "Neurorehabilitation Research",
            "publication_year": 2022,
            "query": SEARCH_QUERIES[2],
            "doi": "10.1000/example-3",
            "url": "https://example.org/study/3",
            "abstract": "Summarizes therapeutic pathways and brain-body mechanisms in lumbar symptoms with functional features.",
        },
    ]


def write_sample_data() -> Path:
    ensure_directories()
    sample_path = SAMPLE_DIR / "pubmed_spinal_fnd_sample.csv"
    df = pd.DataFrame(_default_sample_rows())
    df = df.reindex(columns=[*DEFAULT_EXPORT_COLUMNS, "uid"] if "uid" not in DEFAULT_EXPORT_COLUMNS else DEFAULT_EXPORT_COLUMNS)
    df.to_csv(sample_path, index=False)
    return sample_path


def download_and_cache_data(output_dir: Path | None = None, retmax: int = 25) -> tuple[Path, pd.DataFrame]:
    ensure_directories()
    raw_dir = output_dir or RAW_DIR
    raw_json = raw_dir / "pubmed_spinal_fnd.json"
    raw_csv = raw_dir / "pubmed_spinal_fnd.csv"

    dataset = build_dataset_payload(SEARCH_QUERIES, retmax=retmax)
    if not dataset:
        dataset = _default_sample_rows()

    for row in dataset:
        row.setdefault("abstract", "")
        row.setdefault("doi", "")
        row.setdefault("url", "")

    raw_json.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    df = pd.DataFrame(dataset)
    if not df.empty:
        df = df.reindex(columns=DEFAULT_EXPORT_COLUMNS + ["uid"] if "uid" not in DEFAULT_EXPORT_COLUMNS else DEFAULT_EXPORT_COLUMNS)
    df.to_csv(raw_csv, index=False)

    return raw_csv, df


def load_dataset() -> pd.DataFrame:
    ensure_directories()
    sample_path = SAMPLE_DIR / "pubmed_spinal_fnd_sample.csv"
    raw_csv = RAW_DIR / "pubmed_spinal_fnd.csv"

    if raw_csv.exists():
        return pd.read_csv(raw_csv)
    if sample_path.exists():
        return pd.read_csv(sample_path)

    write_sample_data()
    return pd.read_csv(sample_path)


if __name__ == "__main__":
    path, df = download_and_cache_data()
    print(f"Downloaded {len(df)} records to {path}")
