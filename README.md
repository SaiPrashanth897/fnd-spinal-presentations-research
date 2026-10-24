#!/usr/bin/env python3

from fnd_spinal_research.loader import download_and_cache_data


if __name__ == "__main__":
    csv_path, df = download_and_cache_data(retmax=25)
    print(f"Downloaded {len(df)} records to {csv_path}")
