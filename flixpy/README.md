# WARNING: These scripts are intended for Flix 6.5 and will not work as intended with earlier versions

This project aims to provide a fully-featured Python SDK for interacting with Flix,
along with a command line utility providing commands for some of the most common actions.

# Installing

TBA

# Usage

## As a command-line utility

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
  config   Set default configuration values.
  curl     Perform cURL-like requests to a Flix server.
  webhook  Manage webhooks.
```

There are four ways of authenticating with the `flix` utility:

1. Supply credentials when prompted:
```
$ flix curl http://localhost:8080/servers
Not signed in, attempting to authenticate...
Username: admin
Password:
{"servers": ...}
```
2. Specify using command-line flags:
```
$ flix -u admin -p admin curl http://localhost:8080/servers
Not signed in, attempting to authenticate...
{"servers": ...}
```
3. Specify using environment variables:
```
$ FLIX_USERNAME=admin FLIX_PASSWORD=admin flix curl http://localhost:8080/servers
Not signed in, attempting to authenticate...
{"servers": ...}
```
4. Add to configuration:
```
$ flix config -u admin -p admin
$ flix curl http://localhost:8080/servers
Not signed in, attempting to authenticate...
{"servers": ...}
```

You should also configure what server to use by default:
```
$ flix config -s http://localhost:8080
$ flix curl /servers
{"servers": ...}
```

## As a library

This package also comes with an asyncio-based library to help you interact with Flix from your own Python scripts.
See the `examples` folder for examples of how to use it.

# Development

This project makes use of [Poetry](https://python-poetry.org/) for packaging and dependency management.
You can install a local development copy along with all dependencies using the `poetry´ command:
```
$ pip install poetry
$ poetry install
```
