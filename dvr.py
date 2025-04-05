import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
import tempfile

import click
import requests


class InvalidDriveError(Exception):
    pass


class DownloadError(Exception):
    pass


class ExtractionError(Exception):
    pass


dvr_models = ["MarlinS"]
dvr_models_joined = ", ".join(dvr_models)


@click.group()
@click.option("--debug", is_flag=True, default=False)
def cli(debug):
    """Command-line interface of DVR Tools"""
    if debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@cli.command()
@click.option("--drive", type=str, required=True, help="Drive letter")
@click.option("--delete_events", is_flag=True, help="Delete all files in EVENT")
def delete(drive, delete_events):
    """Delete event files"""
    drive_path = get_drive_path(drive)
    if delete_events:
        logging.debug("Got delete events argument, will proceed to delete")
        delete_event_files(drive_path)


@cli.command()
@click.option("--drive", type=str, required=True, help="Drive letter")
@click.option(
    "--dvr_model",
    type=str,
    required=True,
    help=f"Inspector DVR model. Supported models: {dvr_models_joined}",
)
def update(drive, dvr_model):
    """Download and extract DB"""
    drive_path = get_drive_path(drive)
    logging.debug("Got update db argument, will proceed to update")
    download_and_extract_db(drive_path, dvr_model)


def get_drive_path(drive_letter: str) -> Path:
    """Return drive root by its letter"""

    logging.debug("Got drive letter %s", drive_letter)
    if not os.path.exists(f"{drive_letter}:\\"):
        raise InvalidDriveError(f"Invalid drive letter: {drive_letter}")
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
                        logging.warning(
                            "Can't remove file %s due to permission problems", file
                        )


def download_and_extract_db(drive_path: Path, dvr_model: str) -> None:
    """Download DB update (archive number = current week number)"""

    now = datetime.now()
    week_number = int(now.strftime("%V"))
    logging.debug("Current week is %s", week_number)

    # Search for previous weeks if current one is not available
    max_attempts = 4
    for attempt in range(max_attempts):
        current_week = week_number - attempt
        if current_week < 1:
            current_week += 52

        current_week_str = f"{current_week:02}"
        url = f"https://www.inspector-update.me/SOFT/DB/{dvr_model}DB_{current_week_str}.zip"
        logging.debug("Formed %s link", url)

        try:
            response = requests.get(url, timeout=100)
            response.raise_for_status()
            logging.info(
                "Successfully downloaded database update for week %s", current_week
            )
            break
        except requests.exceptions.RequestException as e:
            logging.warning(
                "Failed to download database update for week %s: %s", current_week, e
            )
            if attempt == max_attempts - 1:
                raise DownloadError(
                    f"Failed to download database update after {max_attempts} attempts."
                ) from e

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_file_name = tmp_file.name
        tmp_file.write(response.content)

    try:
        with zipfile.ZipFile(temp_file_name, "r") as zip_ref:
            zip_ref.extractall(drive_path)
    except zipfile.BadZipFile as e:
        raise ExtractionError(f"Failed to extract database update: {e}") from e
    finally:
        os.remove(temp_file_name)


if __name__ == "__main__":
    cli()
