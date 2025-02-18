#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to query GitHub to extract architectural views from readme and contributing files in GitHub repositories.
"""

import csv
import github
from github import Github
import re
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta
from src.config import ACCESS_TOKEN

g = Github(ACCESS_TOKEN)


def extract_image_urls(code_file, repo):
    try:
        file_content = code_file.decoded_content.decode('utf-8')
        base_url = f'https://github.com/{repo.full_name}/blob/{repo.default_branch}/'
        path_to_file = code_file.path

        image_urls = re.findall(
            r'!\[[^\]]*\]\(([^)]*architect[^\/\)]*(.jpg|.jpeg|.png|.pdf|.gif|.svg))|<img[^>]*src=["\'](['
            r'^"\']*architect[^"\'\/>]*(.png|.jpg|.jpeg|.pdf|.gif|.svg))|^\s*\.\.\s+image::\s+(.*architect[^\/:]*('
            r'.png|.jpg|.jpeg|.svg|.gif|.pdf))',
            file_content, re.IGNORECASE)

        absolute_image_urls = []
        for url_tuple in image_urls:
            url = next(filter(None, url_tuple))
            if not url.startswith(('http://', 'https://')):
                url_without_spaces = url.replace(' ', '%20')
                path_to_image = urljoin(path_to_file, url_without_spaces)
                if path_to_image.startswith('/'):
                    path_to_image = path_to_image[1:]
                absolute_image_url = urljoin(base_url, path_to_image)
                absolute_image_urls.append(absolute_image_url)
            else:
                absolute_image_urls.append(url)
        return absolute_image_urls

    except AssertionError as ae:
        print(f'AssertionError occurred for {repo.full_name}: {ae}')
        return []
    except Exception as e:
        print(f"Exception for {repo.full_name}: {str(e)}")
        return []


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


def perform_search(filename):
    initial_size = 0
    step_size = 5
    final_size = 384000

    for i in range(initial_size, final_size, step_size):
        time.sleep(6)
        query = f"architect filename:{filename} size:{i}..{i + step_size}"
        code_results = g.search_code(query=query)
        print('-----------------')
        print(f'filesize:{i}..{i + step_size}')
        print(g.get_rate_limit().core)
        print(code_results.totalCount)

        for code_file in code_results:
            wait_until_reset(g)
            repository = code_file.repository
            urls = extract_image_urls(code_file, repository)
            for image in urls:
                try:
                    repo_name = repository.full_name
                    img_url = image
                    stars = repository.stargazers_count
                    contributors = repository.get_contributors().totalCount
                    forks = repository.forks_count
                    repo_commits = repository.get_commits().totalCount
                    language = repository.language
                    sha = repository.get_commits()[0].sha
                    description = repository.description
                    first_commit = repository.get_commits()[repo_commits - 1].commit.author.date

                    repository_data = [repo_name, img_url, stars, contributors, forks, repo_commits, language, sha,
                                       description, first_commit]
                    with open('images1.csv', 'a', newline='', encoding='utf-8') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(repository_data)
                    print([repo_name, img_url])
                except github.GithubException as ge:
                    print(f'GithubError: {ge}')

if __name__ == "__main__":

    with open('images1.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        header = ["Repository Name", "Image URL", "Stars", "Contributors", "Forks", "Repo Commits", "Language", "SHA",
                  "Description", "First Repo Commit Date"]
        writer.writerow(header)

    perform_search('readme')
    perform_search('contributing')
