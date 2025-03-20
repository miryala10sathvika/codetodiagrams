import os
import subprocess
import openai
import pandas as pd
import csv
import re
import json
import shutil
import google.generativeai as genai
# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    print(match.group(1))
    return match.group(1) + "/" if match else link

genai.configure(api_key="your_api_key")

TOKEN_LIMIT = 50000  # Approximate max tokens per request (adjust as needed)

def chunk_text(text, max_tokens=TOKEN_LIMIT):
    """Splits text into chunks of max_tokens length."""
    words = text.split()  # Split by words to avoid cutting in the middle of a word
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def clone_repository(link):
    """Clones a GitHub repository to a local directory and returns the path."""
    try:
        repo_name = link.split('github.com/')[-1].rstrip('/')
        local_repo_path = f"./{repo_name.replace('/', '_')}"

        # Remove the existing repository if it exists
        if os.path.exists(local_repo_path):
            shutil.rmtree(local_repo_path)

        # Clone the repository
        clone_cmd = ["git", "clone", link, local_repo_path]
        clone_result = subprocess.run(clone_cmd, capture_output=True, text=True)

        if clone_result.returncode != 0:
            raise Exception(f"Error: Failed to clone repository {link}")

        return local_repo_path
    except Exception as e:
        return f"Error: {e}"

def extract_contents(root_folder):
    """Extracts the contents of all code files in the repository and returns as a string."""
    extracted_data = []
    
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Only extract text/code files
            if filename.endswith(('.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', '.md', '.json', '.xml', '.yaml', '.yml', '.sh', '.ts')):
                extracted_data.append(f"--- File: {file_path} ---\n")
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        extracted_data.append(file.read())
                except Exception as e:
                    extracted_data.append(f"Error reading file: {e}\n")
                extracted_data.append("\n\n")
    return "\n".join(extracted_data)

def get_chatgpt_response(repo_link):
    """Generates a structured analysis of the GitHub repository using its contents, with chunking."""
    try:
        # Step 1: Clone the Repository
        repo_path = clone_repository(repo_link)
        if "Error" in repo_path:
            return repo_path  # Return error message if cloning failed

        # Step 2: Extract Repository Structure
        try:
            if os.name == "nt":  # Windows
                structure_result = subprocess.run(["tree", "/F", repo_path], capture_output=True, text=True, shell=True)
            else:  # Linux/Mac
                structure_result = subprocess.run(["tree", "-L", "3", repo_path], capture_output=True, text=True)

            repo_structure = structure_result.stdout
        except Exception as e:
            repo_structure = f"Error generating repository structure: {e}"

        # Step 3: Extract Code File Contents
        repo_contents = extract_contents(repo_path)

        # Step 4: Split Contents if Too Large
        chunks = chunk_text(repo_contents, max_tokens=TOKEN_LIMIT)
        partial_summaries = []

        model = genai.GenerativeModel("gemini-2.0-flash")

        # Step 5: Process Each Chunk Separately
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")  # Log progress
            chunk_prompt = f"""
            This is part {i+1} of {len(chunks)} from the GitHub repository analysis.

            Repository Structure:
            {repo_structure}

            Repository Contents (Chunk {i+1}):
            {chunk}

            Please analyze this part and generate a summary that includes:
            - Key functionalities and components
            - Important files and their roles
            - Architectural insights (if relevant)
            - Any notable design patterns

            This is only one part of the full repository. Keep your response modular so that it can be merged with other parts.
            """
            try:
                response = model.generate_content([chunk_prompt])
                partial_summaries.append(response.text if hasattr(response, 'text') else "Error: No response text received.")
            except Exception as e:
                partial_summaries.append(f"Error processing chunk {i+1}: {e}")

        # Step 6: Combine All Partial Summaries
        final_summary = "\n\n".join(partial_summaries)

        # Step 7: Generate Final Merged Summary
        final_prompt = f"""
        The following are partial summaries from an analysis of a GitHub repository:

        {final_summary}

        Please merge these summaries into a single, well-structured report. Ensure that:
        - There is no repetition
        - The information flows logically
        - The final report provides a cohesive overview of the repository's structure, functionality, and architecture.
        """
        final_response = model.generate_content([final_prompt])

        return final_response.text if hasattr(final_response, 'text') else "Error: No response text received."

    except Exception as e:
        return f"Error: {e}"


def get_plantuml_from_summary(summary, repo_name, error_message=None):
    system_content = '''You are an expert in creating PlantUML diagrams. Based on the following repository summary, please generate a syntactically correct PlantUML component diagram. Your output should include only the PlantUML code and no additional explanation or commentary. Make sure that:

    The diagram accurately represents the components described in the repository summary.
    All components and their relationships (e.g., dependencies, interactions) are clearly represented.
    The generated PlantUML code is free of syntax errors and can be directly used with PlantUML.'''
    
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
    file_path = os.path.join("gemini_plantumlcode", f"{clean_repo_name}.puml")
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