import csv
import requests

def check_url_accessibility(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def filter_valid_rows(input_file, output_file):
    with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        
        header = next(reader)
        writer.writerow(header)
        
        for row in reader:
            image_url = row[2]  # Assuming Image URL is the third column
            if check_url_accessibility(image_url):
                writer.writerow(row)

# Usage Example
input_csv = "data_extraction_framework.csv"  # Replace with your actual input file name
output_csv = "filtered_output.csv"
filter_valid_rows(input_csv, output_csv)
