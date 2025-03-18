import os
import subprocess
import openai
import pandas as pd
import re
import json
import base64
from pathlib import Path

# Function to extract repository URL from a GitHub file URL
def extract_repo_url(link):
    match = re.match(r"(https://github\.com/[^/]+/[^/]+)", link)
    return match.group(1) + "/" if match else link

# Function to get all file paths with GitHub links
def get_all_files_with_links(root_dir, repo_url):
    file_links = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            relative_path = os.path.relpath(os.path.join(dirpath, file), root_dir)
            # Construct GitHub link (assuming branch "main"; adjust as necessary)
            github_link = f"{repo_url}/blob/main/{relative_path.replace(os.sep, '/')}"
            file_links[relative_path] = github_link
    return file_links

# Read OpenAI API key from file
with open("openai_key.txt", "r") as file:
    openai.api_key = file.read().strip()

# Function to summarize a single file with its GitHub link included
def summarize_file(file_path, github_link, repo_dir):
    try:
        full_path = os.path.join(repo_dir, file_path)
        if not os.path.exists(full_path):
            return f"File [{file_path}]({github_link}) not found"
        
        if os.path.getsize(full_path) > 1000000:  # Skip files larger than 1MB
            return f"File [{file_path}]({github_link}) is too large to summarize (>1MB)"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"File [{file_path}]({github_link}) appears to be binary"
        
        if not content.strip():
            return f"File [{file_path}]({github_link}) is empty"
        
        # Call OpenAI API with GitHub link included in the prompt
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarize the following code file. Provide a concise overview of its functionality."},
                {"role": "user", "content": f"File: {github_link}\n\n{content}"}
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error summarizing [{file_path}]({github_link}): {str(e)}"

# Function to summarize all files using the file links
def summarize_directory(file_links, repo_dir):
    summaries = {}
    for file_path, github_link in file_links.items():
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.py', '.js', '.java', '.c', '.cpp', '.h', '.go', '.rs', '.php', '.rb', 
                   '.md', '.txt', '.html', '.css', '.json', '.xml', '.yml', '.yaml', '.toml']:
            summaries[file_path] = summarize_file(file_path, github_link, repo_dir)
    return summaries

# Function to read and encode the callgraph image as base64
def get_callgraph_base64():
    callgraph_path = "./callgraph.png"
    if os.path.exists(callgraph_path):
        with open(callgraph_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string
    return None

# Generate overall repository summary using file summaries and callgraph image (base64)
def generate_overall_summary(hierarchical_summary, repo_url, repo_dir):
    """
    Generate a high-level summary using the file summaries and the callgraph image.
    This version truncates the aggregated text if it is too long.
    """
    # Aggregate file summaries as "filename: summary"
    summaries_list = [f"{file}: {summary}" for file, summary in hierarchical_summary.items()]
    all_text = "\n".join(summaries_list)
    
    # Truncate the text if it exceeds a character threshold
    max_chars = 3000  # Adjust threshold as needed (this is roughly equivalent to a couple thousand tokens)
    if len(all_text) > max_chars:
        all_text = all_text[:max_chars] + "\n... (truncated)"
    
    # Get callgraph image as base64
    # callgraph_b64 = get_callgraph_base64()
    # if callgraph_b64:
    #     image_text = f"CallGraph (Base64 Encoded): {callgraph_b64}"
    # else:
    #     image_text = "CallGraph image not found."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "Summarize this GitHub repository based on the provided file summaries and call graph image. "
                    "Include a high-level overview of its purpose, architecture, and key components. "
                    "The file summaries might be truncated due to token limits."
                )},
                {"role": "user", "content": f"Repository: {repo_url}\n\n{all_text}"}
            ],
            temperature=0.5,
            max_tokens=800
        )
        
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Error generating overall summary: {str(e)}"


# Save hierarchical summary to JSON and markdown files
def save_hierarchical_summary(summary, repo_name):
    os.makedirs("summaries", exist_ok=True)
    clean_repo_name = repo_name.replace('/', '_').replace('\\', '_').rstrip('_')
    
    # Save JSON structure
    json_path = os.path.join("summaries", f"{clean_repo_name}_structure.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    # Save markdown summary
    md_path = os.path.join("summaries", f"{clean_repo_name}_summary.md")
    
    def generate_markdown(summary_dict, level=0):
        markdown = ""
        if summary_dict:
            markdown += f"{'#' * (level+1)} Summary for {os.path.basename(summary_dict.get('path', 'Unknown'))}\n\n"
            markdown += f"{summary_dict.get('summary', '')}\n\n"
            if "files" in summary_dict and summary_dict["files"]:
                markdown += "**File Summaries:**\n\n"
                for file, file_summary in summary_dict["files"].items():
                    markdown += f"- **{file}**: {file_summary}\n"
                markdown += "\n"
            if "children" in summary_dict:
                for child_name, child_info in summary_dict["children"].items():
                    markdown += generate_markdown(child_info, level+1)
        return markdown
    
    # For this example, we're just converting the hierarchical file summary into markdown text.
    # Depending on your structure, you may adjust this.
    markdown_content = generate_markdown({"summary": "Repository File Summaries", "files": summary})
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return json_path, md_path

# Process repository: use file paths with GitHub links and include base64 callgraph image
def process_repository(link=None, repo_dir=None):
    if not link or not repo_dir:
        return {"error": "Repository link and local path are required"}
    
    repo_url = extract_repo_url(link)
    
    # Get file paths and corresponding GitHub links
    file_links = get_all_files_with_links(repo_dir, repo_url)
    
    # Summarize each file
    hierarchical_summary = summarize_directory(file_links, repo_dir)
    
    # Generate overall repository summary with the callgraph image in base64
    overall_summary = generate_overall_summary(hierarchical_summary, repo_url, repo_dir)
    
    repo_name = os.path.basename(repo_dir)
    json_path, md_path = save_hierarchical_summary(hierarchical_summary, repo_name)
    
    return {
        "repo_url": repo_url,
        "summary": overall_summary,
        "file_summaries": hierarchical_summary,
        "hierarchical_summary_json": json_path,
        "hierarchical_summary_md": md_path
    }

def main():
    """Main function to process repositories from CSV or directly from arguments"""
    input_csv = "./dataset/dataonlywithstaticanduml.csv"
    output_jsonl = "output.jsonl"
    column_name = "Image URL"
    
    if os.path.exists(input_csv):
        try:
            df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(1)
            if column_name not in df.columns:
                print(f"Error: Column '{column_name}' not found in CSV file.")
                return
            with open(output_jsonl, "w", encoding="utf-8") as file:
                for index, row in df.iterrows():
                    print(f"Processing repository {index+1}/{len(df)}...")
                    result = process_repository(link=row[column_name], repo_dir="./repos/example_repo")
                    if result:
                        file.write(json.dumps(result) + "\n")
            print(f"Results saved in {output_jsonl}")
        except Exception as e:
            print(f"Error processing CSV: {e}")
    else:
        print("CSV input not found. Please provide a valid CSV file.")

if __name__ == "__main__":
    main()
