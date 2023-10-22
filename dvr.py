import argparse
import sys
from pathlib import Path
from datetime import datetime
import zipfile
import os
import logging
import requests

if os.environ.get('LOG_LEVEL') == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def parse_arguments() -> argparse.Namespace:
    """Arguments parser"""

    desc = 'Tools for working with DVR memory card'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--drive', type=str, help='Drive letter')
    parser.add_argument('--delete_events', action='store_true', help='Delete all files in EVENT')
    parser.add_argument('--update_db', action='store_true', help='Download DB update')
    parser.add_argument('--dvr_model', type=str, help='Inspector DVR model')

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    logging.debug('Got args %s', args)

    return args

def get_drive_path(drive_letter: str) -> Path:
    """Return drive root by its letter"""

    logging.debug('Got drive letter %s', drive_letter)
    return Path(f"{drive_letter}:\\")

def delete_event_files(drive_path: Path):
    """Delete all files in EVENT"""

    event_folder = drive_path / 'EVENT' / '100MEDIA'
    if event_folder.exists() and event_folder.is_dir():
        logging.info('Removing all files in %s', event_folder)
        for file in event_folder.iterdir():
            if file.is_file():
                file.unlink()

def download_and_extract_db(drive_path: Path, dvr_model: str) -> None:
    """Download DB update (archive number = current week number)"""

    now = datetime.now()
    week_number = now.strftime("%V")
    logging.debug('Current week is %s', week_number)

    url = f"https://www.inspector-update.me/SOFT/DB/{dvr_model}DB_{week_number}.zip"
    logging.debug('Formed %s link', url)

    response = requests.get(url, timeout=100)

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
        logging.debug('Got delete events argument, will proceed to delete')
        delete_event_files(drive_path)

    if args.update_db:
        logging.debug('Got update db argument, will proceed to update')
        download_and_extract_db(drive_path, dvr_model)

if __name__ == "__main__":
    main()
