import csv
# Function to store table data as CSV
def store_table_as_csv(data, filename):
    fieldnames = data[0].keys()
    with open(f"data/{filename}", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f'{filename} stored with {len(data)} records')
