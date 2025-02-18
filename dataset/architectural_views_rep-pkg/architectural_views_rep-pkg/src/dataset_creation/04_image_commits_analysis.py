#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to extract data for the commit history analysis.
"""

import pandas as pd


def add_columns(images_file, commits_file, output_file):
    try:
        images_df = pd.read_csv(images_file)
        commits_df = pd.read_csv(commits_file)

        commits_df['Date'] = pd.to_datetime(commits_df['Date'])
        images_df['First Repo Commit Date'] = pd.to_datetime(images_df['First Repo Commit Date'])
        commit_count = commits_df.groupby(['Repository Name', 'Image URL'])['Commit SHA'].count()
        unique_users = commits_df.groupby(['Repository Name', 'Image URL'])['Author Name'].nunique()
        unique_emails = commits_df.groupby(['Repository Name', 'Image URL'])['Author Email'].nunique()
        first_commit_date = commits_df.groupby(['Repository Name', 'Image URL'])['Date'].min()
        commits_introduction = commits_df.groupby(['Repository Name', 'Image URL'])['Repo Commits Until This Date'].min()

        merged_df = pd.merge(images_df, commit_count, on=['Repository Name', 'Image URL'], how='left')
        merged_df = pd.merge(merged_df, unique_users, on=['Repository Name', 'Image URL'], how='left')
        merged_df = pd.merge(merged_df, unique_emails, on=['Repository Name', 'Image URL'], how='left')
        merged_df = pd.merge(merged_df, first_commit_date, on=['Repository Name', 'Image URL'], how='left')
        merged_df = pd.merge(merged_df, commits_introduction, on=['Repository Name', 'Image URL'], how='left')
        merged_df.rename(columns={'Commit SHA': 'Image Commits',
                                  'Author Name': 'Image Contributors Name',
                                  'Author Email': 'Image Contributors Email',
                                  'Date': 'First Image Commit Date',
                                  'Repo Commits Until This Date': 'Repo Commits When The View Is Introduced'
                                  },
                         inplace=True)
        merged_df['Difference Between I Image Commit and I Repo Commit'] = (merged_df['First Image Commit Date'] -
                                                                        merged_df['First Repo Commit Date']).dt.days

        merged_df.to_csv(output_file, index=False)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    images_file = 'images_filtered.csv'
    commits_file = 'commit_history.csv'
    output_file = 'images_dataset_all.csv'
    add_columns(images_file, commits_file, output_file)
