import os
import csv
import base64
import openai
from pathlib import Path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_pair(initial_image_path, output_image_path):
    # Encode both images
    initial_base64 = encode_image_to_base64(initial_image_path)
    output_base64 = encode_image_to_base64(output_image_path)
    
    # Prepare the messages for the API
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Compare these two images. Analyze the differences."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{initial_base64}",
                    "detail": "low",
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{output_base64}",
                       "detail": "low", 
                    }
                }
            ]
        }
    ]

    # Make the API call
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=350
    )
    
    return response.choices[0].message['content']

def main():
    # Set OpenAI API key
    with open("openai_key.txt", "r") as file:
        openai.api_key = file.read().strip()
    
    # Define paths
    initial_folder = "initial_images"
    output_folder = "output_images"
    
    # Create output CSV file
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['image_name', 'repo_url', 'username', 'repo', 'analysis'])
        
        # Get list of images in both folders
        initial_images = set(os.listdir(initial_folder))
        output_images = set(os.listdir(output_folder))
        
        # Find common images
        common_images = initial_images.intersection(output_images)
        
        for image_name in common_images:
            # Construct full paths
            initial_path = os.path.join(initial_folder, image_name)
            output_path = os.path.join(output_folder, image_name)
            
            # Extract information from image name
            # Assuming image name format: username_repo_filename.extension
            parts = image_name.rsplit('.', 1)[0].split('_')
            if len(parts) >= 2:
                username = parts[0]
                repo = parts[1]
                repo_url = f"https://github.com/{username}/{repo}"
            else:
                username = "unknown"
                repo = "unknown"
                repo_url = "unknown"
            
            try:
                # Get analysis from OpenAI
                analysis = analyze_image_pair(initial_path, output_path)
                
                # Convert analysis to string and strip any potential whitespace
                analysis_str = str(analysis).strip()
                
                # Write to CSV
                csvwriter.writerow([image_name, repo_url, username, repo, analysis_str])
                print(f"Processed: {image_name}")
                
            except Exception as e:
                print(f"Error processing {image_name}: {str(e)}")

if __name__ == "__main__":
    main()
