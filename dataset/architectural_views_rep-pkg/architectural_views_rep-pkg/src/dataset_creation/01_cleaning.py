#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to remove duplicate views, check that images are referred to the repo where they're hosted and process image URLs for creating the downloadable image link.
"""

import pandas as pd
import csv
import time
from datetime import datetime, timedelta
import github
from github import Github
from src.config import ACCESS_TOKEN

g = Github(ACCESS_TOKEN)


def remove_duplicates(input_file='images1.csv', output_file='images_without_duplicates.csv'):
    try:
        df = pd.read_csv(input_file)
        df_unique = df.drop_duplicates(subset='Image URL', keep='first')
        df_unique.to_csv(output_file, index=False)
    except Exception as e:
        print(f'Error occurred: {str(e)}')

def create_downloadable_url(image_url):
    if image_url.startswith('http://'):
        updated_image_url = image_url.replace('http://', 'https://')
    parts = image_url.split('/')
    if parts[6] == 'raw':
        updated_image_url = image_url.replace('/raw/', '/blob/')
    if image_url.startswith('https://github.com'):
        downloadable_url = image_url + '?raw=true'
        updated_image_url = image_url
    elif image_url.startswith('https://raw.githubusercontent.com'):
        downloadable_url = image_url
        updated_image_url = image_url.replace('https://raw.githubusercontent.com', 'https://github.com')

        parts = updated_image_url.split('/')
        parts.insert(5, 'blob')
        updated_image_url = '/'.join(parts)
    elif image_url.startswith('https://raw.github.com'):
        downloadable_url = image_url
        updated_image_url = image_url.replace('https://raw.github.com', 'https://github.com')

        parts = updated_image_url.split('/')
        parts.insert(5, 'blob')
        updated_image_url = '/'.join(parts)
    elif image_url.startswith('https://rawgithub.com'):
        downloadable_url = image_url
        updated_image_url = image_url.replace('https://rawgithub.com', 'https://github.com')

        parts = updated_image_url.split('/')
        parts.insert(5, 'blob')
        updated_image_url = '/'.join(parts)
    elif image_url.startswith('https://rawgit.com'):
        downloadable_url = image_url
        updated_image_url = image_url.replace('https://rawgit.com', 'https://github.com')

        parts = updated_image_url.split('/')
        parts.insert(5, 'blob')
        updated_image_url = '/'.join(parts)
    else:
        downloadable_url = image_url
        updated_image_url = image_url

    return downloadable_url, updated_image_url


def wait_until_reset(g):
    rate_limit = g.get_rate_limit().core.remaining
    if rate_limit < 50:

        target_time = g.get_rate_limit().core.reset
        diff_hours = timedelta(hours=1)  # adjust with the difference between UTC and your local timezone
        target_time_correct = target_time + diff_hours
        current_time = datetime.now()
        time_difference = target_time_correct - current_time
        time_difference_seconds = time_difference.total_seconds() + 1

        if time_difference_seconds > 0:
            print(f"Waiting for {time_difference_seconds} seconds...until reset time {target_time_correct}")
            time.sleep(time_difference_seconds)
            print("Time reached!")
        else:
            print("Target time has already passed.")


def find_image_hosted_diff_repo(input_file):
    rows_to_process = pd.read_csv(input_file)
    rows_to_process['URL_parts'] = rows_to_process['Image URL'].apply(lambda x: '/'.join(x.split('/')[3:5]))

    different_values = rows_to_process[rows_to_process['URL_parts'] != rows_to_process['Repository Name']]
    df = different_values[different_values['Image URL'].str.startswith('https://github')]

    diff_repo_file = 'diff_repos.csv'
    df.to_csv(diff_repo_file, index=False)
    input = pd.read_csv(input_file)
    to_delete = pd.read_csv(diff_repo_file)
    urls_to_delete = to_delete['Image URL'].tolist()
    input = input[~input['Image URL'].isin(urls_to_delete)]
    input.to_csv(input_file, index=False)
    perform_search(diff_repo_file)


def perform_search(input_file):
    print(g.get_rate_limit().core)
    data = pd.read_csv(input_file)

    for index, row in data.iterrows():
        wait_until_reset(g)
        repo_name = row['URL_parts']
        img_url = row['Image URL']
        download_url = row['Downloadable URL']
        try:
            repository = g.get_repo(repo_name)
            repo_name = repository.full_name
            stars = repository.stargazers_count
            contributors = repository.get_contributors().totalCount
            forks = repository.forks_count
            repo_commits = repository.get_commits().totalCount
            language = repository.language
            sha = repository.get_commits()[0].sha
            description = repository.description
            first_commit = repository.get_commits()[repo_commits - 1].commit.author.date

            repository_data = [repo_name, img_url, stars, contributors, forks, repo_commits, language, sha,
                                   description, first_commit, download_url]
            with open('diff_repos_corrected.csv', 'a', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(repository_data)
            print([repo_name, img_url])
        except github.GithubException as ge:
            print(f'GithubError: {ge}')


def merge(file1_path, file2_path):
    merged_file_path = 'images2.csv'
    data1 = []
    with open(file1_path, 'r', newline='') as file1:
        reader = csv.reader(file1)
        data1.extend(list(reader))

    data2 = []
    with open(file2_path, 'r', newline='') as file2:
        reader = csv.reader(file2)
        next(reader)
        data2.extend(list(reader))

    merged_data = data1 + data2
    with open(merged_file_path, 'w', newline='') as merged_file:
        writer = csv.writer(merged_file)
        writer.writerows(merged_data)

if __name__ == "__main__":
    remove_duplicates()
    try:
        df = pd.read_csv('images_without_duplicates.csv')
        df[['Downloadable URL', 'Image URL']] = df['Image URL'].apply(create_downloadable_url).apply(pd.Series)
        df.to_csv('images_with_downloadable_url.csv', index=False)
    except pd.errors.EmptyDataError:
        print('No data found in the input file.')
    except Exception as e:
        print(f'Error occurred: {str(e)}')

    with open('diff_repos_corrected.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        header = ["Repository Name", "Image URL", "Stars", "Contributors", "Forks", "Repo Commits", "Language", "SHA",
              "Description", "First Repo Commit Date", "Downloadable URL"]
        writer.writerow(header)
    find_image_hosted_diff_repo('images_with_downloadable_url.csv')
    merge('images_with_downloadable_url.csv', 'diff_repo_corrected.csv') 
