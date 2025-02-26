import os
import subprocess
import openai
import pandas as pd
import csv
import re

# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    return match.group(1) + "/" if match else link

# Read OpenAI API key from file
with open("openai_key.txt", "r") as file:
    openai.api_key = file.read().strip()

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

def get_plantuml_from_summary(summary, repo_name, error_message=None):
    system_content = "You are an expert at creating PlantUML  diagrams. Generate a PlantUML diagram based on the following repository summary. Include only the PlantUML code without any explanation. Ensure the code is syntax error free."
    
    if error_message:
        system_content += "\nThe previous code generated had errors. Here's the error message: " + error_message
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": summary}
            ],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def save_plantuml_code(puml_code, repo_name):
    os.makedirs("plantumlcode", exist_ok=True)
    clean_repo_name = repo_name.replace('/', '_').replace('\\', '_').rstrip('_')
    file_path = os.path.join("plantumlcode", f"{clean_repo_name}.puml")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("@startuml\n")
        file.write(puml_code)
        file.write("\n@enduml")
    return file_path

def compile_plantuml(input_path, output_dir="../output_images"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Run PlantUML and capture output
    result = subprocess.run(["plantuml", "-o", output_dir, input_path], 
                          capture_output=True, text=True)
    
    return result.returncode == 0, result.stderr

def process_repository(link, writer):
    if pd.notna(link):
        repo_url = extract_repo_url(link)
        summary = get_chatgpt_response(repo_url)
        writer.writerow([repo_url, summary])
        
        repo_name = repo_url.split('github.com/')[-1].rstrip('/')
        
        # Generate and compile PlantUML code with retry mechanism
        max_retries = 3
        attempt = 0
        while attempt < max_retries:
            # Generate PlantUML code
            puml_code = get_plantuml_from_summary(summary, repo_name, 
                                                error_message=None if attempt == 0 else error_message)
            
            # Save the code
            file_path = save_plantuml_code(puml_code, repo_name)
            
            # Try to compile
            success, error_message = compile_plantuml(file_path)
            
            if success:
                print(f"Successfully processed repo {repo_url}")
                print(f"PlantUML diagram generated at {file_path}")
                break
            else:
                print(f"Attempt {attempt + 1}: Error in generating PlantUML for {repo_url}")
                print(f"Error message: {error_message}")
                attempt += 1
                
        if attempt == max_retries:
            print(f"Failed to generate valid PlantUML for {repo_url} after {max_retries} attempts")

def main():
    input_csv = "data_extraction_framework.csv"
    output_csv = "output.csv"
    column_name = "Image URL"

    df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(10)

    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in CSV file.")
        return

    with open(output_csv, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Repo URL", "Summary"])

        for index, row in df.iterrows():
            process_repository(row[column_name], writer)

    print(f"Results saved in {output_csv}")

if __name__ == "__main__":
    main() 