# DVR_Tools

> :warning: Currently supports only Inspector DVRs

- Getting drive root by its letter
- Deleting all files inside EVENT folder
- Downloading and unpacking most recent DB update

## Python package
```pip install dvr-tools```

## Logging

There are some informational messages by default. To increase logging verbosity, add `--debug` argument.
Example: `python3 dvr.py --debug`

## Testing

`pytest` tests are supported. 
Use `python -m pytest test.py`, for example.

## Help

```text
Usage: dvr.py [OPTIONS] COMMAND [ARGS]...

  Command-line interface of DVR Tools

Options:
  --debug
  --help   Show this message and exit.

Commands:
  delete  Delete event files
  update  Download and extract DB
```
