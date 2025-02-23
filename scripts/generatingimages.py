import os
import subprocess

# Input directory where .puml files are stored
input_dir = "plantumlcode"  # Change this to your directory containing .puml files
output_dir = "../output_images"  # Directory to store generated images

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all .puml files in the input directory
puml_files = [f for f in os.listdir(input_dir) if f.endswith(".puml")]

if not puml_files:
    print("No .puml files found in the directory.")
else:
    for puml_file in puml_files:
        input_path = os.path.join(input_dir, puml_file)

        # Run PlantUML to generate images
        subprocess.run(["plantuml", "-o", output_dir, input_path])

        print(f"Generated image for: {puml_file}")

    print(f"All images saved in '{output_dir}'")
