import csv

def filter_uml_static(csv_filename):
    try:
        # Open and read the CSV file
        with open(csv_filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Filter rows based on conditions
            filtered_rows = [row for row in reader if 
                           "UML" in row.get('Architectural Notation', '').split(',') and 
                           "static" in row.get('Behavior', '').split(',')]
            
            # Print the filtered rows
            for row in filtered_rows:
                print(f"Repository: {row['Repository Name']}")
                print(f"Image URL: {row['Image URL']}")
                print(f"Architecture Scope: {row['Architecture Scope']}")
                print(f"Behavior: {row['Behavior']}")
                print("-" * 80)
                
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
filter_uml_static('data_extraction_framework.csv')