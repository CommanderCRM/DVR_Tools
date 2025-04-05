import zipfile
from unittest.mock import patch, MagicMock
from pathlib import Path
import requests
import pytest

from dvr import (
    InvalidDriveError,
    DownloadError,
    ExtractionError,
    get_drive_path,
    delete_event_files,
    download_and_extract_db,
)


def test_get_drive_path_valid():
    with patch("os.path.exists", return_value=True):
        drive_letter = "D"
        expected_path = Path("D:\\")

        result = get_drive_path(drive_letter)
        assert result == expected_path


def test_get_drive_path_invalid():
    with patch("os.path.exists", return_value=False):
        drive_letter = "Z"

        with pytest.raises(InvalidDriveError):
            get_drive_path(drive_letter)


def test_delete_event_files():
    with (
        patch("pathlib.Path.iterdir") as mock_iterdir,
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.is_dir", return_value=True),
    ):
        mock_file = MagicMock()
        mock_file.is_file.return_value = True

        mock_iterdir.return_value = [mock_file] * 3

        drive_path = Path("D:\\EVENT\\100MEDIA")
        delete_event_files(drive_path)

        assert mock_file.unlink.call_count == 3


def test_download_and_extract_db_success():
    with (
        patch("requests.get") as mock_requests,
        patch("zipfile.ZipFile") as mock_zipfile,
        patch("os.remove") as mock_remove,
    ):
        mock_requests.return_value = MagicMock(status_code=200, content=b"Some content")
        mock_zipfile.return_value = MagicMock()

        drive_path = Path("D:\\")
        dvr_model = "some_model"

        download_and_extract_db(drive_path, dvr_model)

        mock_requests.assert_called_once()
        mock_zipfile.assert_called_once()
        mock_remove.assert_called_once()


def test_download_and_extract_db_failure():
    with patch("requests.get") as mock_requests:
        mock_requests.side_effect = requests.exceptions.RequestException(
            "Download failed"
        )

        drive_path = Path("D:\\")
        dvr_model = "some_model"

        with pytest.raises(DownloadError):
            download_and_extract_db(drive_path, dvr_model)


def test_download_and_extract_db_extraction_failure():
    with (
        patch("zipfile.ZipFile") as mock_zipfile,
        patch("os.remove") as mock_remove,
        patch("requests.get") as mock_get,
    ):
        mock_response = MagicMock()
        mock_response.content = b"Some content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        mock_zipfile.side_effect = zipfile.BadZipFile("Bad zip file")

        drive_path = Path("D:\\")
        dvr_model = "some_model"

        with pytest.raises(ExtractionError):
            download_and_extract_db(drive_path, dvr_model)

        mock_remove.assert_called_once()
