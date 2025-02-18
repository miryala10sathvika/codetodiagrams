import openai
import pandas as pd
import csv
import re

# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    return match.group(1) + "/" if match else link


with open("openai_key.txt", "r") as file:
    openai.api_key = file.read().strip()



def get_chatgpt_response(link):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3",
            messages=[
                {"role": "system", "content": "Analyze the following link and summarize it."},
                {"role": "user", "content": link}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"


input_csv = "data_extraction_framework.csv"  
output_txt = "output.txt"
column_name = "Image URL" 


df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(5)


if column_name not in df.columns:
    print(f"Error: Column '{column_name}' not found in CSV file.")
    exit()


with open(output_txt, "w", encoding="utf-8") as file:
    for index, row in df.iterrows():
        link = row[column_name]
        if pd.notna(link):  
            repo_url = extract_repo_url(link)
            response = get_chatgpt_response(repo_url)
            file.write(f"Repo: {repo_url}\nResponse:\n{response}\n\n")
            print(f"Processed repo {repo_url}")

print(f"Results saved in {output_txt}")
