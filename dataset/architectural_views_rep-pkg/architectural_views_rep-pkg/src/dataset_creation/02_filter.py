#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to perfor all filtering steps listed in the paper and create the dataset of downloaded images.
"""

import pandas as pd
import os
import requests
from urllib.parse import urlparse
from src.config import OUTPUT_FOLDER, COMMITS_TRESHOLD, STARS_TRESHOLD


def filter_dataframe(input_file, output_file, min_commits_count=COMMITS_TRESHOLD, min_stars_count=STARS_TRESHOLD,
                     filter_words=['course', 'thesis', 'exam', 'demo', 'example', 'tutorial', 'sample']):
    
    df = pd.read_csv(input_file)

    df['Description'].fillna('', inplace=True)
    filter_condition = (
        (df['Repo Commits'] >= min_commits_count) &
        (df['Stars'] >= min_stars_count) &
        (~df['Description'].str.lower().str.contains('|'.join(filter_words))) &
        (~df['Repository Name'].str.lower().str.contains('|'.join(filter_words))) &
        (~df['Image URL'].str.lower().str.contains('|'.join(filter_words))) &
        (~df['Image URL'].str.startswith('https://img.shields.io'))
    )

    filtered_df = df[filter_condition]
    filtered_df.to_csv(output_file, index=False)

def download_image(url, destination_folder, counter):
    try:
        response = requests.get(url)
        response.raise_for_status()

        os.makedirs(destination_folder, exist_ok=True)

        filename = os.path.join(destination_folder, f"{counter:03d}_{os.path.basename(urlparse(url).path)}")

        with open(filename, 'wb') as file:
            file.write(response.content)

        return filename
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def download_images_from_csv(csv_file, output_folder):
    df = pd.read_csv(csv_file)
    os.makedirs(output_folder, exist_ok=True)
    rows_to_remove = []
    counter = 1

    for index, row in df.iterrows():
        downloaded_image = download_image(row['Downloadable URL'], output_folder, counter)

        if downloaded_image:
            print(f"Image downloaded successfully: {downloaded_image}")
            counter += 1 
        else:
            print(f"Failed to download image from {row['Downloadable URL']}")
            rows_to_remove.append(index)

    df = df.drop(index=rows_to_remove)
    df.to_csv(csv_file, index=False)

if __name__ == "__main__":
  input_file = 'images2.csv'
  output_file = 'images_filtered.csv'

  filter_dataframe(input_file, output_file)

  download_path = 'images_filtered.csv'

  download_images_from_csv(download_path, OUTPUT_FOLDER)
