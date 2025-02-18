# Architectural Views: The State of Practice in Open-Source Software Projects
This repository is a companion page for the following paper:
> Anonymous 2024. Architectural Views: The State of Practice in Open-Source Software Projects

The full dataset including raw data, mining scripts, and analysis scripts produced during the study are available below.
  

## Quick start
Brief documentation on how to use the replication material.

### Requirements

- Python 3.10

### Preliminary

- Clone the repo in the directory you want (we refer to it as `{CLONE_DIR}`):

  ```
  git clone * {CLONE_DIR}
  ```

- Install all the Python package required:

  ```
  pip install -r src/requirements.txt
  ```

### Experiment

- Set GitHub access token in <code>config.py</code>

- Set the output folder for downloaded images in <code>config.py</code>

- Run the dataset creation file:

  ```
  python src.0_dataset_creation
  ```

- Run the dataset analysis file:

  ```
  python src.1_dataset_analysis 
  ```


## Repository Structure
This is the root directory of the repository. The directory is structured as follows:

    architectural_views_rep-pkg
    .
    |
    |
    |--- data/                                   Data used in the paper
    |      |
    |      |--- analysis/                        Data extraction framework and other analysis data
    |      |--- dataset/                         Dataset data
    |--- src/             	                     Source code used in the paper
    |      |--- dataset_creation/                Scripts relating to steps of the creation of the dataset
    |      |--- 0_dataset_creation.py            Datasets
    |      |--- 1_dataset_analysis.py            Analysis
    |      |--- config.py                        Configurations
    |      |--- requirements.txt                 Requirements
```

## License
The source code is licensed under the MIT license, which you can find in the [LICENSE file](LICENSE).
