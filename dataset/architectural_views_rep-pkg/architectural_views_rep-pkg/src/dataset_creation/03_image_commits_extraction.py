#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script allows to retrieve the commit history for images hosted on GitHub.
"""

from github import Github
import csv
import time
from src.config import ACCESS_TOKEN

g = Github(ACCESS_TOKEN)


def get_image_commit_history(repo_name, image_repo_name, url, image_path, last_commit_sha):
    try:
        creation_date = g.get_repo(repo_name).created_at
        repo = g.get_repo(repo_name)
        image_repo = g.get_repo(image_repo_name)
        last_commit = repo.get_commit(sha=last_commit_sha)
        last_commit_timestamp = last_commit.commit.author.date

        image_commits = image_repo.get_commits(path=image_path, until=last_commit_timestamp)

        for commit in image_commits:
            commit_date = commit.commit.author.date
            total_commits_repo = repo.get_commits(until=commit_date).totalCount

            row = [
                repo_name,
                url,
                creation_date,
                commit.sha,
                commit.commit.author.name,
                commit.commit.author.email,
                commit.commit.author.date,
                commit.commit.message,
                total_commits_repo
            ]
            print(row)
            csv_writer.writerow(row)
            print("-" * 40)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file = 'images_filtered.csv'
    output_file = 'commit_history.csv'
    data_list = []

    with open(input_file, 'r', newline='') as infile:
        csv_reader = csv.reader(infile)
        next(csv_reader, None)

        for row in csv_reader:
            repo_name = row[0].strip()
            url = row[1].strip()
            last_commit_sha = row[7]
            data_list.append((repo_name, url, last_commit_sha))

    with open(output_file, 'a', newline='') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["Repository Name", "Image URL", "Repo Creation Date", "Commit SHA", "Author Name", "Author Email", "Date", "Message", "Repo Commits Until This Date"])

        for repo_name, url, last_commit_sha in data_list:
            time.sleep(4)
            print(f"Repository: {repo_name}")
            print(f"URL: {url}")

            url_parts = url.split("/")

            if url_parts[2] == "github.com":
                image_repo_owner = url_parts[3]
                image_repo_name = url_parts[4]
                url_parts = url_parts[7:]

                image_path = "/".join(url_parts)
                image_path = image_path.replace('%20', ' ')
                print(image_path)
                get_image_commit_history(repo_name, f"{image_repo_owner}/{image_repo_name}", url, image_path, last_commit_sha)

        print("-" * 40)
