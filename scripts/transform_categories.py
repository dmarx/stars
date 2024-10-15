import json
from pathlib import Path
from utils import commit_and_push

def transform_categories(data):
    for paper_id, paper_info in data.items():
        if 'categories' in paper_info:
            paper_info['categories'] = [cat['@term'] for cat in paper_info['categories']]
    return data

def main():
    file_path = Path('arxiv_metadata.json')
    
    # Read the JSON file
    with file_path.open('r') as f:
        data = json.load(f)
    
    # Transform the data
    transformed_data = transform_categories(data)
    
    # Write the transformed data back to the file
    with file_path.open('w') as f:
        json.dump(transformed_data, f, indent=2)
    
    # Commit and push changes
    commit_and_push(file_path)

if __name__ == "__main__":
    main()
