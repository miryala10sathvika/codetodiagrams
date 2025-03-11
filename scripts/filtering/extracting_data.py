import csv

def filter_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=';')
        header = next(reader)  # Read the header
        
        filtered_rows = [row for row in reader if row[4] == "boxes_and_arrows" and row[6] == "general"]
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter=';')
            writer.writerow(header)  # Write the header first
            writer.writerows(filtered_rows)  # Write the filtered rows

# Example usage
input_csv = "filtered_output.csv"  
output_csv = "concern_general.csv"
filter_csv(input_csv, output_csv)
print(f"Filtered rows saved to {output_csv}")
