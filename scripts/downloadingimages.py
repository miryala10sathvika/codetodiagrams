import pandas as pd
import requests
import os
import re
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image  # Pillow library for image processing

def convert_github_url_to_raw(url):
    """Convert GitHub repository URL to raw content URL"""
    # Check if it's already a raw URL
    if 'raw.githubusercontent.com' in url:
        return url
        
    # Convert github.com URL to raw.githubusercontent.com
    if 'github.com' in url:
        # Replace github.com with raw.githubusercontent.com
        url = url.replace('github.com', 'raw.githubusercontent.com')
        # Replace /blob/ with /
        url = url.replace('/blob/', '/')
        return url
        
    return url

def extract_repo_info(url):
    # Extract username and repo name from GitHub URL
    match = re.search(r"github(?:usercontent)?\.com/([^/]+)/([^/]+)", url)
    if match:
        username, repo_name = match.groups()
        # Clean the repo name by removing any trailing slashes or .git
        repo_name = repo_name.rstrip('/').replace('.git', '')
        return f"{username}_{repo_name}"
    return None

def convert_image_to_png(file_path):
    """Convert an image file to PNG format and return the new file path."""
    try:
        # Open the image file using Pillow
        with Image.open(file_path) as img:
            # Define new file path with .png extension
            new_file_path = os.path.splitext(file_path)[0] + ".png"
            # Convert and save as PNG
            img.convert("RGBA").save(new_file_path, "PNG")
        # Optionally remove the original file
        os.remove(file_path)
        return True, new_file_path
    except Exception as e:
        return False, str(e)

def download_image(url, folder_path):
    try:
        # Convert GitHub URL to raw content URL
        raw_url = convert_github_url_to_raw(url)
        
        # Create a response object with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(raw_url, stream=True, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the file extension from the URL
        ext = os.path.splitext(urlparse(raw_url).path)[1]
        if not ext:
            ext = '.png'  # Default extension if none is found
            
        # Create filename from repo info
        repo_info = extract_repo_info(url)
        if not repo_info:
            # If can't extract repo info, use a hash of the URL
            repo_info = str(hash(url))[-10:]
            
        filename = f"{repo_info}{ext}"
        file_path = os.path.join(folder_path, filename)
        
        # Write the image to file
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        
        # If the file is not in PNG format, convert it to PNG
        if ext.lower() != ".png":
            success, new_path_or_error = convert_image_to_png(file_path)
            if success:
                return True, new_path_or_error
            else:
                return False, new_path_or_error
        
        return True, file_path
    except Exception as e:
        return False, str(e)

def main():
    # Create the initial_images directory if it doesn't exist
    output_folder = "initial_images"
    os.makedirs(output_folder, exist_ok=True)
    
    # Read the CSV file
    input_csv = "./dataset/filtered_output_uml.csv"
    image_column = "Image URL"
    
    try:
        # Read CSV file with semicolon delimiter
        df = pd.read_csv(input_csv, delimiter=";", encoding="utf-8", on_bad_lines="skip").head(16)
        
        # Check if required column exists
        if image_column not in df.columns:
            print(f"Error: Column '{image_column}' not found in CSV file.")
            return
        
        # Download each image
        for index, row in df.iterrows():
            image_url = row[image_column]
            
            if pd.notna(image_url):
                print(f"Downloading image from: {image_url}")
                success, result = download_image(image_url, output_folder)
                
                if success:
                    print(f"Successfully downloaded and converted image: {result}")
                else:
                    print(f"Failed to download image: {result}")
            
        print("Download process completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
