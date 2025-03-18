import os
import subprocess
import openai
import pandas as pd
import csv
import re
import json
import google.generativeai as genai
# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    return match.group(1) + "/" if match else link

genai.configure(api_key="your_api_key")

def get_chatgpt_response(link):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            [
                "Analyze the following GitHub repository link and summarize it. Analyze each and every file in the repository and include it in the summary. It should also concentrate on the overall high-level architecture of the system.",
                link
            ]
        )
        return response.text if hasattr(response, 'text') else "Error: No response text received."
    except Exception as e:
        return f"Error: {e}"

def get_plantuml_from_summary(summary, repo_name, error_message=None):
    system_content = "You are an expert at creating PlantUML diagrams. Generate a PlantUML component diagram based on the following repository summary. Include only the PlantUML code without any explanation. Ensure the code is syntax error free."
    
    if error_message:
        system_content += f"\nThe previous code generated had errors. Here's the error message: {error_message}"
    
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content([system_content, summary])
        return response.text if hasattr(response, 'text') else "Error: No response text received."
    except Exception as e:
        return f"Error: {e}"

def save_plantuml_code(puml_code, repo_name):
    os.makedirs("gemini_plantumlcode", exist_ok=True)
    clean_repo_name = repo_name.replace('/', '_').replace('\\', '_').rstrip('_')
    file_path = os.path.join("plantumlcode", f"{clean_repo_name}.puml")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("@startuml\n")
        file.write(puml_code)
        file.write("\n@enduml")
    return file_path

def compile_plantuml(input_path, output_dir="../gemini_output_images"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Run PlantUML and capture output
    result = subprocess.run(["plantuml", "-o", output_dir, input_path], 
                          capture_output=True, text=True)
    
    return result.returncode == 0, result.stderr

def process_repository(link):
    if pd.notna(link):
        repo_url = extract_repo_url(link)
        summary = get_chatgpt_response(repo_url)
        
        # Return dictionary instead of writing to CSV
        result = {
            "repo_url": repo_url,
            "summary": summary
        }
        
        repo_name = repo_url.split('github.com/')[-1].rstrip('/')
        
        # Generate and compile PlantUML code with retry mechanism
        max_retries = 3
        attempt = 0
        
        # Open log file in append mode
        with open("error.log", "a", encoding="utf-8") as log_file:
            while attempt < max_retries:
                puml_code = get_plantuml_from_summary(summary, repo_name, 
                                                    error_message=None if attempt == 0 else error_message)
                
                file_path = save_plantuml_code(puml_code, repo_name)
                success, error_message = compile_plantuml(file_path)
                
                if success:
                    log_file.write(f"Successfully processed repo {repo_url}\n")
                    log_file.write(f"PlantUML diagram generated at {file_path}\n")
                    break
                else:
                    log_file.write(f"Attempt {attempt + 1}: Error in generating PlantUML for {repo_url}\n")
                    log_file.write(f"Error message: {error_message}\n")
                    attempt += 1
                    
            if attempt == max_retries:
                log_file.write(f"Failed to generate valid PlantUML for {repo_url} after {max_retries} attempts\n")
        
        return result

def main():
    input_csv = "./dataset/filtered_output_uml.csv"
    output_jsonl = "gemini_output.jsonl"
    column_name = "Image URL"

    df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(16)

    if column_name not in df.columns:
        print(f"Error: Column '{column_name}' not found in CSV file.")
        return

    with open(output_jsonl, "w", encoding="utf-8") as file:
        for index, row in df.iterrows():
            result = process_repository(row[column_name])
            if result:
                file.write(f"{result}\n")

    print(f"Results saved in {output_jsonl}")

if __name__ == "__main__":
    main() 