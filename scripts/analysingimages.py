import os
import csv
import base64
import openai
from pathlib import Path
import json

# def encode_image_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

# def analyze_image_pair(initial_image_path, output_image_path):
#     # Encode both images
#     initial_base64 = encode_image_to_base64(initial_image_path)
#     output_base64 = encode_image_to_base64(output_image_path)
    
#     # Prepare the messages for the API
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Compare these two images. Analyze the differences."
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{initial_base64}",
#                     "detail": "low",
#                     }
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{output_base64}",
#                        "detail": "low", 
#                     }
#                 }
#             ]
#         }
#     ]

#     # Make the API call
#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         max_tokens=350
#     )
    
#     return response.choices[0].message['content']

# def main():
#     # Set OpenAI API key
#     with open("openai_key.txt", "r") as file:
#         openai.api_key = file.read().strip()
    
#     # Create new analysis JSONL file
#     with open('analysis.jsonl', 'w', encoding='utf-8') as jsonl_file:
#         initial_folder = "initial_images"
#         output_folder = "output_images"
        
#         initial_images = set(os.listdir(initial_folder))
#         output_images = set(os.listdir(output_folder))
#         common_images = initial_images.intersection(output_images)
        
#         for image_name in common_images:
#             initial_path = os.path.join(initial_folder, image_name)
#             output_path = os.path.join(output_folder, image_name)
            
#             # Extract repo info from image name
#             parts = image_name.rsplit('.', 1)[0].split('_')
#             if len(parts) >= 2:
#                 username = parts[0]
#                 repo = parts[1]
#                 repo_url = f"https://github.com/{username}/{repo}"
#             else:
#                 continue  # Skip if we can't determine the repo URL
            
#             try:
#                 # Get image analysis
#                 analysis = analyze_image_pair(initial_path, output_path)
#                 analysis_str = str(analysis).strip()
                
#                 # Create result dictionary
#                 result = {
#                     'repo_url': repo_url,
#                     'analysis': analysis_str
#                 }
                
#                 # Write to JSONL file
#                 jsonl_file.write(json.dumps(result) + '\n')
#                 print(f"Processed: {image_name}")
                
#             except Exception as e:
#                 print(f"Error processing {image_name}: {str(e)}")

# if __name__ == "__main__":
#     main()

import PIL.Image
import google.generativeai as genai

def load_image(image_path):
    return PIL.Image.open(image_path)

def analyze_image_pair(initial_image_path, output_image_path):
    # Load both images using PIL
    initial_image = load_image(initial_image_path)
    output_image = load_image(output_image_path)
    
    # Initialize Gemini API client
    genai.configure(api_key="your_api_key")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    # Generate content using the model
    response = model.generate_content([
        '''Please compare the two provided images and analyze the differences in detail. Your analysis should include:

    Overview of Each Image:
        Summarize the main content, themes, or subjects in each image.

    Visual Elements Comparison:
        Identify and describe differences in color schemes, shapes, textures, and patterns.
        Highlight variations in layout, composition, and design elements.

    Context and Style:
        Note any differences in artistic style, mood, or visual tone.
        Discuss any context-specific elements or details that set the images apart.

    Subtle Differences:
        Point out any minor or nuanced differences that may not be immediately obvious.

Your response should be structured, detailed, and focus solely on comparing and contrasting the two images based on the aspects mentioned above.''',
        initial_image,
        output_image
    ])
    
    return response.text if hasattr(response, 'text') else "Error: No response text received."



def main():
    
    # Create new analysis JSONL file
    with open('gemini_analysis.jsonl', 'w', encoding='utf-8') as jsonl_file:
        initial_folder = "initial_images"
        output_folder = "gemini_output_images"
        
        initial_images = set(os.listdir(initial_folder))
        output_images = set(os.listdir(output_folder))
        common_images = initial_images.intersection(output_images)
        
        for image_name in common_images:
            initial_path = os.path.join(initial_folder, image_name)
            output_path = os.path.join(output_folder, image_name)
            
            # Extract repo info from image name
            parts = image_name.rsplit('.', 1)[0].split('_')
            if len(parts) >= 2:
                username = parts[0]
                repo = parts[1]
                repo_url = f"https://github.com/{username}/{repo}"
            else:
                continue  # Skip if we can't determine the repo URL
            
            try:
                # Get image analysis
                analysis = analyze_image_pair(initial_path, output_path)
                analysis_str = str(analysis).strip()
                
                # Create result dictionary
                result = {
                    'repo_url': repo_url,
                    'analysis': analysis_str
                }
                
                # Write to JSONL file
                jsonl_file.write(json.dumps(result) + '\n')
                print(f"Processed: {image_name}")
                
            except Exception as e:
                print(f"Error processing {image_name}: {str(e)}")

if __name__ == "__main__":
    main()