# DVR_Tools

> :warning: Currently supports only Inspector DVRs

* Getting drive root by its letter
* Deleting all files inside EVENT folder
* Downloading and unpacking most recent DB update

## Logging

There are some informational messages by default. To increase logging verbosity, set ```LOG_LEVEL``` environment variable to ```DEBUG```.

## Help

```text
usage: dvr.py [-h] [--drive DRIVE] [--delete_events] [--update_db] [--dvr_model DVR_MODEL]

Tools for working with DVR memory card

options:
  -h, --help            show this help message and exit
  --drive DRIVE         Drive letter
  --delete_events       Delete all files in EVENT
  --update_db           Download DB update
  --dvr_model DVR_MODEL Inspector DVR model
```
