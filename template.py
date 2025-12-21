import os
import logging

from pathlib import Path

def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

    src_file_name = "VideoSharingApp"

    # List of files and directories that need to be created or amended with new files
    list_of_files = [
        f"src/{src_file_name}/__init__.py",
        f"src/{src_file_name}/app.py",
        f"src/{src_file_name}/database.py",
        f"src/{src_file_name}/images.py",
        f"src/{src_file_name}/schemas.py",
        f"src/{src_file_name}/users.py",
        f"main.py",
        f"frontend.py",
    ]

    # Iterate through each file path
    for filepath in list_of_files:
        filepath = Path(filepath)
        filedir, _ = os.path.split(filepath)
        
        # Create the directory if it doesn't already exist
        if filedir != "":
            os.makedirs(filedir, exist_ok=True)
            logging.info(f'Creating directory: {filedir}')
        
        # Create the file if it doesn't exist or is currently empty
        if not filepath.exists() or filepath.stat().st_size == 0:
            filepath.touch()
            logging.info(f"Created empty file: {filepath}")
        else:
            logging.info(f"File already exists: {filepath}")


if __name__ == "__main__":
    main()
    