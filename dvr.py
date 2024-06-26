from pathlib import Path
from datetime import datetime
import zipfile
import os
import logging
import requests
import click


@click.group()
@click.option("--debug", is_flag=True, default=False)
def cli(debug):
    """Command-line interface of DVR Tools"""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option("--drive", type=str, help="Drive letter")
@click.option("--delete_events", is_flag=True, help="Delete all files in EVENT")
@click.option("--update_db", is_flag=True, help="Download DB update")
@click.option("--dvr_model", type=str, help="Inspector DVR model")
def main(drive, delete_events, update_db, dvr_model):
    """Tools for working with DVR"""
    drive_path = get_drive_path(drive)

    if delete_events:
        logging.debug("Got delete events argument, will proceed to delete")
        delete_event_files(drive_path)

    if update_db:
        logging.debug("Got update db argument, will proceed to update")
        download_and_extract_db(drive_path, dvr_model)


def get_drive_path(drive_letter: str) -> Path:
    """Return drive root by its letter"""

    logging.debug("Got drive letter %s", drive_letter)
    return Path(f"{drive_letter}:\\")


def delete_event_files(drive_path: Path):
    """Delete all files in EVENT"""

    event_folder = drive_path / "EVENT" / "100MEDIA"
    if event_folder.exists() and event_folder.is_dir():
        if not any(event_folder.iterdir()):
            logging.info("No files in %s, nothing to remove", event_folder)
        else:
            logging.info("Removing all files in %s", event_folder)
            for file in event_folder.iterdir():
                if file.is_file():
                    try:
                        file.unlink()
                    except PermissionError:
                        logging.warning("Can't remove file %s due to permission problems", file)

def download_and_extract_db(drive_path: Path, dvr_model: str) -> None:
    """Download DB update (archive number = current week number)"""

    now = datetime.now()
    week_number = now.strftime("%V")
    logging.debug("Current week is %s", week_number)

    url = f"https://www.inspector-update.me/SOFT/DB/{dvr_model}DB_{week_number}.zip"
    logging.debug("Formed %s link", url)

    response = requests.get(url, timeout=100)

    with open("temp.zip", "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile("temp.zip", "r") as zip_ref:
        zip_ref.extractall(drive_path)

    os.remove("temp.zip")


if __name__ == "__main__":
    cli()
