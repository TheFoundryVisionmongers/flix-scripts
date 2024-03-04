# Experimental Python SDK for Flix

This project aims to provide a fully-featured Python SDK for interacting with [Flix](https://www.foundry.com/products/flix),
the story development hub from Foundry.
It also comes with a command line utility for performing some common actions from the terminal.

## Requirements

This version of the SDK requires:
* Flix 7.0.0 or later
* Python 3.10 or later

## Installing

Install the SDK using `pip`, or the package manager of your choice:
```
$ pip install flix-sdk
```
after which the CLI utility can be accessed as `flix` or `python -m flix`.

## Usage

### As a command-line utility

This package comes with a `flix` CLI utility that lets you perform some common actions.
At the moment you can use it to perform basic cURL-like requests, as well as to manage webhook.

```
$ flix --help
Usage: flix [OPTIONS] COMMAND [ARGS]...

Options:
  -s, --server TEXT    The URL of the Flix server.
  -u, --username TEXT  The username to authenticate with.
  -p, --password TEXT  The password to authenticate with.
  --help               Show this message and exit.

Commands:
  config        Set default configuration values.
  contactsheet  Manage contact sheet templates.
  curl          Perform cURL-like requests to a Flix server.
  logout        Log out the user from Flix by removing any active access...
  webhook       Manage webhooks.
```

To use the `flix` utility, you should configure what server and credentials to use.
This is best done either using environment variables, or the `flix config` command.

To use environment variables, you need to set the `FLIX_SERVER`, `FLIX_USERNAME`, and `FLIX_PASSWORD` variables:
```
$ export FLIX_SERVER=http://localhost:8080
$ export FLIX_USERNAME=admin
$ export FLIX_PASSWORD=admin
$ flix curl /servers
Not signed in, attempting to authenticate...
{"servers": ...}
```

You can also tell `flix` to remember your information using `flix config`:
```
$ flix config -s http://localhost:8080 -u admin -p admin
$ flix curl /servers
Not signed in, attempting to authenticate...
{"servers": ...}
```

Alternatively, you can provide the information directly to the `flix` command:
```
$ flix -s http://localhost:8080 -u admin -p admin curl /servers
Not signed in, attempting to authenticate...
{"servers": ...}
```

If you do not configure your credentials, `flix` will ask for them when attempting to log in:
```
$ flix -s http://localhost:8080 curl /servers
Not signed in, attempting to authenticate...
Username: admin
Password:
{"servers": ...}
```

### As a library

This package also comes with an asyncio-based library to help you interact with Flix from your own Python scripts.
See the `examples` folder for examples of how to use it.

## Versioning policy

The Flix SDK follows semantic versioning:
* The major version is increased if a breaking change is introduced, either at the Flix API level, or in the Flix SDK itself.
* The minor version is increased if new features are added without breaking existing functionality, with a note in the documentation explaining what Flix version is required for the new features.
* The patch version is increased if a bug fix is made without changing functionality.

To ensure that an update will not break existing applications, we recommend specifying a dependency on `flix-sdk` in the form of `^1.2.3` or, equivalently, `>=1.2.3 <2.0.0`.

## Development

This project makes use of [Poetry](https://python-poetry.org/) for packaging and dependency management.
You can install a local development copy along with all dependencies using the `poetry´ command:
```
$ pip install poetry
$ poetry install
```
