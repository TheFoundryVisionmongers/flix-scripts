# Flix Dialogue Relink

This is a script to help relink missing dialogue to the panels.

Retrieves sequence revision data from Flix server.

Creates a new sequence revision replacing missing dialogue for each panel.

## Prerequisites

You need Flix Server >= 6.3.4.

This script requires a minimum Python version of 3.7

You will also need to install these libraries:

* requests=2.21.0

You can install them using pip (https://pip.pypa.io/en/stable/installing/)

```python3 -m pip install -r requirements.txt```


### Getting Started

Start your Flix server.

Run ```python3 main.py --help```:

```
usage: main.py [--help] 
              --server SERVER 
              --user USER 
              --password PASSWORD
              --showid SHOW ID
              --episodeid EPISODE ID
              --sequenceid SEQUENCE ID
              --revisionid REVISION ID
              --comment COMMENT

optional arguments:
  --help

required arguments:
  --server SERVER       Flix 6 server url
  --user USER           Flix 6 client username
  --password PASSWORD   Flix 6 client password
  --showid SHOW ID to update
  --sequenceid SEQUENCE ID to update
  --revisionid REVISION ID to update
      
  
```

The server URL is the hostname of your server (http://localhost:1234), user and password have to be from an **Admin** user.


### Examples

To update Show 2, episode 1, sequence 2, revision 3 with a comment:
```
python3 main.py --server http://127.0.0.1:8080  --user admin --password admin --showid 2 --episodeid 1  --sequenceid 2  --revisionid 3 --comment 'My new sequence revision'

