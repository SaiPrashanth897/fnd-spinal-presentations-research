from __future__ import annotations

import json
from typing import Any

import requests

from fnd_spinal_research.config import SEARCH_QUERIES


PUBMED_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
OPENALEX_URL = "https://api.openalex.org/works"


def fetch_pubmed_results(search_queries: list[str] | None = None, retmax: int = 20) -> list[dict[str, Any]]:
    """Fetch a lightweight set of PubMed records using the NCBI E-Utilities.

    This returns a list of normalized records keyed for downstream analysis.
    """
    queries = search_queries or SEARCH_QUERIES
    results: list[dict[str, Any]] = []

    for query in queries:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "sort": "relevance",
            "retmode": "json",
        }
        try:
            search_response = requests.get(PUBMED_ESEARCH_URL, params=params, timeout=30)
            search_response.raise_for_status()
        except requests.RequestException:
            continue

        id_list = search_response.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            continue

        summary_response = requests.get(
            PUBMED_ESUMMARY_URL,
            params={"db": "pubmed", "id": ",".join(id_list), "retmode": "json"},
            timeout=30,
        )
        summary_response.raise_for_status()
        data = summary_response.json().get("result", {})

        for uid, item in data.items():
            if uid == "uids":
                continue
            if not isinstance(item, dict):
                continue

            authors = item.get("authors", [])
            author_names = [author.get("name", "") for author in authors if isinstance(author, dict)]
            doi = item.get("elocationid") or ""
            title = item.get("title", "")
            journal = item.get("fulljournalname", "") or item.get("source", "")
            pubdate = item.get("pubdate", "")
            publication_year = int(pubdate[:4]) if pubdate and pubdate[:4].isdigit() else None
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"

            normalized = {
                "uid": uid,
                "title": title,
                "authors": "; ".join(author_names),
                "journal": journal,
                "publication_year": publication_year,
                "query": query,
                "doi": doi,
                "url": url,
                "abstract": "",
            }
            results.append(normalized)

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in results:
        key = (row.get("uid") or row.get("title") or row.get("url") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return deduped


def fetch_openalex_results(search_terms: list[str] | None = None, per_page: int = 10) -> list[dict[str, Any]]:
    """Fallback dataset source using the OpenAlex API."""
    terms = search_terms or SEARCH_QUERIES
    combined: list[dict[str, Any]] = []

    for term in terms:
        params = {
            "search": term,
            "per-page": per_page,
            "select": "id,title,display_name,publication_year,source,doi,host_organization_name,primary_location",
        }
        try:
            response = requests.get(OPENALEX_URL, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            continue

        payload = response.json()
        for item in payload.get("results", []):
            source = item.get("source", {})
            primary_location = item.get("primary_location", {})
            location = primary_location.get("source", {}) if isinstance(primary_location, dict) else {}
            openalex_row = {
                "uid": item.get("id", "").split("/")[-1],
                "title": item.get("display_name", item.get("title", "")),
                "authors": "",
                "journal": source.get("display_name", location.get("display_name", "")),
                "publication_year": item.get("publication_year"),
                "query": term,
                "doi": item.get("doi", ""),
                "url": item.get("id", ""),
                "abstract": "",
            }
            combined.append(openalex_row)

    return combined


def build_dataset_payload(search_queries: list[str] | None = None, retmax: int = 20) -> list[dict[str, Any]]:
    """Build a combined dataset from PubMed and OpenAlex."""
    dataset = fetch_pubmed_results(search_queries=search_queries, retmax=retmax)
    if dataset:
        return dataset
    return fetch_openalex_results(search_queries, per_page=retmax)


if __name__ == "__main__":
    print(json.dumps(build_dataset_payload()[:3], indent=2))
