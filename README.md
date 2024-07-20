# DVR_Tools

> :warning: Currently supports only Inspector DVRs

- Getting drive root by its letter
- Deleting all files inside EVENT folder
- Downloading and unpacking most recent DB update

## Python package
```pip install dvr-tools==1.0.3```

## Logging

There are some informational messages by default. To increase logging verbosity, add `--debug` argument.
Example: `python3 dvr.py --debug`

## Help

```text
Usage: dvr.py main [OPTIONS]

  Tools for working with DVR

Options:
  --drive TEXT      Drive letter
  --delete_events   Delete all files in EVENT
  --update_db       Download DB update
  --dvr_model TEXT  Inspector DVR model
  --help            Show this message and exit.
```
