import pandas as pd

# Load the dataset
file_path = "data_extraction_framework.csv"  # Change this to the actual file path
df = pd.read_csv(file_path, delimiter=';')  # Assuming the delimiter is semicolon (;)

# Get unique value counts for each column
stats = {}
for column in df.columns:
    unique_values = df[column].unique()
    value_counts = df[column].value_counts().to_dict()
    stats[column] = {
        "unique_count": len(unique_values),
        "value_counts": value_counts
    }

# Print statistics
for column, data in stats.items():
    print(f"Column: {column}")
    print(f"  Unique values count: {data['unique_count']}")
    print("  Value occurrences:")
    for value, count in data["value_counts"].items():
        print(f"    {value}: {count}")
    print("-")
