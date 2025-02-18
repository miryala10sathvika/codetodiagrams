#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to extracts a data sample from a dataset.
"""

import pandas as pd
from src.config import SAMPLE_SIZE


def sample_dataset(input_file, output_file, sample_size = SAMPLE_SIZE):
    remove_repo_duplicates(input_file)
    try:
        data = pd.read_csv('images_dataset_unique_repo.csv')
        sampled_data = data.sample(n=sample_size, random_state=42)
        sampled_data.to_csv(output_file, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")


def remove_repo_duplicates(input_file):
    try:
        df = pd.read_csv(input_file)
        df_no_duplicates = df.drop_duplicates(subset=df.columns[0], keep='first')
        df_no_duplicates.to_csv('images_dataset_unique_repo.csv', index=False)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = 'images_dataset_all.csv'
    output_file = 'images_dataset_sampled.csv'

    sample_dataset(input_file, output_file, sample_size)
