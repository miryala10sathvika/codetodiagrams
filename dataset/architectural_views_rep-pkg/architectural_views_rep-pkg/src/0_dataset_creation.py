#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: Anonymous
Email: Anonymous

This script executes all the steps of dataset creation.
"""
import shutil
import subprocess
from pathlib import Path

if __name__ == "__main__":
    print('\n\n########## Step 0: running query_github script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.00_github_view_extraction"],
                   cwd=Path(__file__).parent.parent)

    print('\n\n########## Step 1: running filter_multi_dev_dataset script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.01_cleaning"],
                   cwd=Path(__file__).parent.parent)

    print('\n\n########## Step 2: running filter_lifespan_dataset script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.02_filter"],
                   cwd=Path(__file__).parent.parent)

    print('\n\n########## Step 3: running detect_dc_dataset script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.03_image_commits_extraction"],
                   cwd=Path(__file__).parent.parent)
    
    print('\n\n########## Step 4: running detect_dc_dataset script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.04_image_commits_analysis"],
                   cwd=Path(__file__).parent.parent)
    
    print('\n\n########## Step 5: running detect_dc_dataset script ##########\n')
    subprocess.run(["python3", "-m", "src.dataset_creation.05_sampling"],
                   cwd=Path(__file__).parent.parent)

   
   
