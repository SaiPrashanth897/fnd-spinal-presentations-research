from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"

SEARCH_QUERIES = [
    "Functional neurological disorder spine",
    "Functional neurological disorder back pain",
    "Functional neurological disorder lumbar",
    "conversion disorder back pain",
    "functional neurologic symptom disorder cervical spine",
    "functional neurological symptom disorder spinal pain",
]

DEFAULT_EXPORT_COLUMNS = [
    "title",
    "authors",
    "journal",
    "publication_year",
    "query",
    "doi",
    "url",
    "abstract",
]
