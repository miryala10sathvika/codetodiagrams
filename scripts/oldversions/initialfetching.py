import openai
import pandas as pd
import csv
import re
import os

# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    return match.group(1) + "/" if match else link

# Read OpenAI API key from file
with open("openai_key.txt", "r") as file:
    openai.api_key = file.read().strip()

# Function to send link to ChatGPT and get a response
def get_chatgpt_response(link):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the following GitHub repository link and summarize it."},
                {"role": "user", "content": link}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def get_plantuml_from_summary(summary, repo_name):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at creating PlantUML diagrams. Generate a PlantUML diagram based on the following repository summary. Include only the PlantUML code without any explanation."},
                {"role": "user", "content": summary}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def save_plantuml_code(puml_code, repo_name):
    # Create plantumlcode directory if it doesn't exist
    os.makedirs("plantumlcode", exist_ok=True)
    
    # Clean repo name to create valid filename
    clean_repo_name = repo_name.replace('/', '_').replace('\\', '_').rstrip('_')
    
    # Save the PlantUML code to a file
    file_path = os.path.join("plantumlcode", f"{clean_repo_name}.puml")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("@startuml\n")
        file.write(puml_code)
        file.write("\n@enduml")
    return file_path

# File paths
input_csv = "data_extraction_framework.csv"  # Input CSV file
output_csv = "output.csv"  # Output CSV file
column_name = "Image URL"  # Column containing GitHub links

# Load CSV file
df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(10)

# Ensure column exists
if column_name not in df.columns:
    print(f"Error: Column '{column_name}' not found in CSV file.")
    exit()

# Open CSV file for writing results
with open(output_csv, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Repo URL", "Summary"])  # Write header row

    for index, row in df.iterrows():
        link = row[column_name]
        if pd.notna(link):  # Check if the link is not empty
            repo_url = extract_repo_url(link)
            summary = get_chatgpt_response(repo_url)
            writer.writerow([repo_url, summary])  # Write repo URL and summary to CSV
            
            # Extract repo name from URL
            repo_name = repo_url.split('github.com/')[-1].rstrip('/')
            
            # Generate and save PlantUML code
            puml_code = get_plantuml_from_summary(summary, repo_name)
            file_path = save_plantuml_code(puml_code, repo_name)
            print(f"Processed repo {repo_url}")
            print(f"PlantUML code saved to {file_path}")

print(f"Results saved in {output_csv}")
