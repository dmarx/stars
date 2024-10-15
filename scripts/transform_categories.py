import json
from pathlib import Path
from loguru import logger

def commit_and_push(file_to_commit):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "action@github.com"], check=True)
        subprocess.run(["git", "add", file_to_commit], check=True)
        subprocess.run(["git", "commit", "-m", f"Update {file_to_commit}"], check=True)
        subprocess.run(["git", "push"], check=True)
        logger.info(f"Changes to {file_to_commit} committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operations: {e}")
        logger.warning("Exiting early due to potential conflict.")
        raise

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
