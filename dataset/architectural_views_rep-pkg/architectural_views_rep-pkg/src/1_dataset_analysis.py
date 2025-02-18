#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script executes the main steps of the dataset analysis.
"""
import matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

matplotlib.use('Agg')
from tabulate import tabulate

def calculate_statistics(file_path, column_name):
    df = pd.read_csv(file_path)
    column1 = df[column_name]
    mean1 = column1.mean()
    median1 = column1.median()
    std_dev1 = column1.std()
    count1 = column1.count()
    min_val1 = column1.min()
    max_val1 = column1.max()

    print(f"statistics for : {column1}")
    print(f"Mean: {mean1}")
    print(f"Median: {median1}")
    print(f"Standard Deviation: {std_dev1}")
    print(f"Count: {count1}")
    print(f"Minimum Value: {min_val1}")
    print(f"Maximum Value: {max_val1}")

def print_table(file_path, column_name):
    df = pd.read_csv(file_path)
    column1 = df[column_name]
    value_counts = column1.value_counts()
    table = tabulate(value_counts.reset_index(), headers=[column_name, 'Frequency'], tablefmt='pretty')
    with open('table.txt', 'w') as file:
        file.write(table)

def count_occurrencies(file_path, column_name):
    df = pd.read_csv(file_path, sep=';')
#   filter_column = 'Granularity' # column to filter if we want to combine results
#   df = df[df[filter_column].str.contains('dynamic', na=False)] # add filter string

    df.dropna(subset=[column_name], inplace=True)
    all_codes = []
    for codes_list in df[column_name]:
       all_codes.extend(codes_list.split(', '))

    codes_counts = pd.Series(all_codes).value_counts()

    for code, count in codes_counts.items():
       print(f'{code}: {count}')


def violin_plot(file_path, column_to_plot):
    df = pd.read_csv(file_path)
    # Plot the bar chart
    plt.figure(figsize=(10, 2))
    sns.violinplot(data=df[column_to_plot], inner=None, linewidth=1, color='grey', cut=0, zorder=2)
    plt.setp(plt.gca().artists, edgecolor='black', facecolor='black')  # Set box plot edge and face color
    sns.boxplot(data=df[column_to_plot], showmeans=False, showfliers=False, medianprops={'color': 'white', 'linewidth':2}, color='black', linewidth=1, whis=1.5,
                whiskerprops=dict(linestyle='-', color='black'), width=0.01, boxprops=dict(edgecolor='black'))
    plt.grid(True, alpha=0.3, zorder=1)
    plt.ylabel('', fontsize=14, labelpad=10)
    plt.yticks(fontsize=11)
    plt.xlabel('')
    plt.xticks([])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.savefig('violin.png', bbox_inches='tight')


def creation_analysis():
    df = pd.read_csv('images_dataset_all.csv')
    column_to_check = 'Difference Between I View Commit and I Repo Commit'
    rows = df[df[column_to_check]>=0]
    rows.to_csv('difference.csv', index=False)
    calculate_statistics('difference.csv', 'Difference Between I View Commit and I Repo Commit')
    df['% Of Repo Commits When The Views Is Introduced'] = (df['Repo Commits When The View Is Introduced'] / df['Repo Commits']) * 100
    df['% Of Repo Commits When The Views Is Introduced'] = df['% Of Repo Commits When The Views Is Introduced'].round(2)
    df.to_csv('percentage_commits_introduction.csv', index=False)
    calculate_statistics('percentage_commits_introduction.csv', '% Of Repo Commits When The Views Is Introduced')


def maintenance_analysis():
    df = pd.read_csv('commit_history.csv')
    df['% Of Repo Commits'] = (df['Repo Commits at this moment'] / df['Repo Commits']) * 100
    df['% Of Repo Commits'] = df['% Of Repo Commits'].round(2)
    df.to_csv('percentage_commits.csv', index=False)
    images_file = 'images_dataset_all.csv'
    commits_file = 'percentage_commits.csv'
    output_file = 'time_span.csv'
    add_columns(images_file, commits_file, output_file)
    calculate_statistics('time_span.csv', 'Time span')


def add_columns(images_file, commits_file, output_file):
    try:
        images_df = pd.read_csv(images_file)
        commits_df = pd.read_csv(commits_file)

        # Group commits by Repository Name and Image URL and get the minimum and maximum values
        commits_first = commits_df.groupby(['Repository Name', 'Image URL'])['% Of Repo Commits'].min()
        commits_last = commits_df.groupby(['Repository Name', 'Image URL'])['% Of Repo Commits'].max()

        # Merge the DataFrames based on Repository Name and Image URL
        merged_df = pd.merge(images_df, commits_first, on=['Repository Name', 'Image URL'], how='left')
        merged_df = pd.merge(merged_df, commits_last, on=['Repository Name', 'Image URL'], how='left')

        # Rename the columns appropriately
        merged_df.rename(columns={'% Of Repo Commits_x': '% Of Repo Commits First',
                                  '% Of Repo Commits_y': '% Of Repo Commits Last'},
                         inplace=True)

        # Calculate the time span
        merged_df['Time Span'] = (merged_df['% Of Repo Commits Last'] - merged_df['% Of Repo Commits First']).round(2)

        # Write the merged DataFrame to a new CSV file
        merged_df.to_csv(output_file, index=False)

    except Exception as e:
        print("An error occurred:", str(e))

def contributors_analysis():
    df = pd.read_csv('images_dataset_all.csv')
    column_to_check = 'Contributors'
    rows = df[df[column_to_check]>0]
    rows.to_csv('contri.csv')
    df = pd.read_csv('contri.csv')
    column_to_check = 'View Contributors'
    rows = df[df[column_to_check]>0]
    rows.to_csv('contri.csv')
    df = pd.read_csv('contri.csv')
    df['% Contributors'] = (df['View Contributors'] / df['Contributors']) * 100
    df['% Contributors'] = df['% Contributors'].round(2)
    df.to_csv('contri.csv', index=False)
    calculate_statistics('contri.csv', '% Contributors')

if __name__ == "__main__":
    calculate_statistics('images_dataset_unique_repo.csv', 'Stars')
    calculate_statistics('images_dataset_unique_repo.csv', 'Contributors')
    calculate_statistics('images_dataset_unique_repo.csv', 'Forks')
    calculate_statistics('images_dataset_unique_repo.csv', 'Repo Commits')
    print_table('images_dataset_unique_repo.csv', 'Language')
    #count_occurrencies('data_extraction_framework.csv', 'Behavior')
    #violin_plot('', '')
    creation_analysis()
    calculate_statistics('images_dataset_all.csv', 'View Commits')
    maintenance_analysis()
    calculate_statistics('images_dataset_all.csv', 'View Contributors')
    contributors_analysis()








