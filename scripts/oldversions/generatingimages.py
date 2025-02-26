import os
import subprocess


input_dir = "plantumlcode"  
output_dir = "../output_images" 
error_log = "error_log.txt" 

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all .puml files in the input directory
puml_files = [f for f in os.listdir(input_dir) if f.endswith(".puml")]

if not puml_files:
    print("No .puml files found in the directory.")
else:
    with open(error_log, "w") as log_file:
        for puml_file in puml_files:
            input_path = os.path.join(input_dir, puml_file)

            # Run PlantUML and capture output
            result = subprocess.run(["plantuml", "-o", output_dir, input_path], 
                                    capture_output=True, text=True)

            # Check if there was an error
            if result.returncode != 0:
                error_message = f"Error in {puml_file}:\n{result.stderr}\n"
                log_file.write(error_message)
                print(f"Error in {puml_file}. Check '{error_log}' for details.")
            else:
                print(f"Successfully generated image for: {puml_file}")

    print(f"Processing complete. Errors (if any) saved in '{error_log}'")
