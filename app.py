from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from fnd_spinal_research.analysis import generate_report, summarize_records, top_documents
from fnd_spinal_research.loader import download_and_cache_data, load_dataset


st.set_page_config(page_title="Spinal FND Research Atlas", page_icon="🧠", layout="wide")


def render_dashboard() -> None:
    st.title("Spinal FND Research Atlas")
    st.caption("Research synthesis for Functional Neurological Disorder in spinal presentations")

    with st.sidebar:
        st.header("Controls")
        action = st.button("Download fresh literature data")
        if action:
            _, df = download_and_cache_data(retmax=25)
            st.session_state["df"] = df
            st.success("Dataset refreshed from online sources.")

    if "df" not in st.session_state:
        st.session_state["df"] = load_dataset()

    df = st.session_state["df"].copy()
    if df.empty:
        st.warning("No records available. Run the download process.")
        return

    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    min_year = int(df["publication_year"].dropna().min()) if not df["publication_year"].dropna().empty else 2020
    max_year = int(df["publication_year"].dropna().max()) if not df["publication_year"].dropna().empty else 2026

    years = st.slider("Filter publication year", min_year, max_year, (min_year, max_year))
    subset = df[(df["publication_year"] >= years[0]) & (df["publication_year"] <= years[1])]

    summary = summarize_records(subset)
    c1, c2, c3 = st.columns(3)
    c1.metric("Records", summary["records"])
    c2.metric("Years represented", len(summary["by_year"]))
    c3.metric("Top journal", max(summary["by_journal"].items(), key=lambda item: item[1])[0] if summary["by_journal"] else "n/a")

    yearly_fig = px.bar(
        x=list(summary["by_year"].keys()),
        y=list(summary["by_year"].values()),
        title="Publications by Year",
        labels={"x": "Year", "y": "Count"},
    )
    query_fig = px.bar(
        x=list(summary["by_query"].keys()),
        y=list(summary["by_query"].values()),
        title="Publications by Search Topic",
        labels={"x": "Query", "y": "Count"},
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(yearly_fig, use_container_width=True)
    col2.plotly_chart(query_fig, use_container_width=True)

    st.subheader("Top studies")
    top_df = top_documents(subset, n=10)
    st.dataframe(top_df[["title", "authors", "journal", "publication_year", "doi", "url"]], use_container_width=True)

    st.subheader("Narrative report")
    st.text(generate_report(subset))


def main() -> None:
    render_dashboard()


if __name__ == "__main__":
    main()
