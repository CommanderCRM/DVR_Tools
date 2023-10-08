import argparse
import sys
from pathlib import Path
from datetime import datetime
import zipfile
import os
import requests

def parse_arguments() -> argparse.Namespace:
    """Arguments parser"""

    desc = 'Tools for working with DVR memory card'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--drive', type=str, help='Drive letter')
    parser.add_argument('--delete_events', action='store_true', help='Delete all files in EVENT')
    parser.add_argument('--update_db', action='store_true', help='Download DB update')
    parser.add_argument('--dvr_model', type=str, help='Inspector DVR model')

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    return args

def get_drive_path(drive_letter: str) -> Path:
    """Return drive root by its letter"""

    return Path(f"{drive_letter}:\\")

def delete_event_files(drive_path: Path):
    """Delete all files in EVENT"""

    event_folder = drive_path / 'EVENT'
    if event_folder.exists() and event_folder.is_dir():
        for file in event_folder.iterdir():
            if file.is_file():
                file.unlink()

def download_and_extract_db(drive_path: Path, dvr_model: str) -> None:
    """Download DB update (archive number = current week number)"""

    now = datetime.now()
    week_number = now.strftime("%V")

    url = f"https://www.inspector-update.me/SOFT/DB/{dvr_model}DB_{week_number}.zip"
    response = requests.get(url)

    with open('temp.zip', 'wb') as f:
        f.write(response.content)

    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall(drive_path)

    os.remove('temp.zip')

def main():
    """Call main functions"""

    args = parse_arguments()
    drive_path = get_drive_path(args.drive)
    dvr_model = args.dvr_model

    if args.delete_events:
        delete_event_files(drive_path)

    if args.update_db:
        download_and_extract_db(drive_path, dvr_model)

if __name__ == "__main__":
    main()
