# Flix Dialogue Relink

This is a script to fetch panels with media objects.

## Prerequisites

You need Flix Server >= 6.3.4.

This script requires a minimum Python version of 3.7

You will also need to install these libraries:

* requests=2.21.0

You can install them using pip (https://pip.pypa.io/en/stable/installing/)

```python3 -m pip install -r requirements.txt```


### Getting Started

1. Start your Flix server.

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

The server URL is the hostname of your server (http://localhost:8080), user and password have to be from an **Admin** user.


### Examples

To fetch panels from Show 2, episode 1, sequence 2, revision 3:
```
python3 main.py --server http://127.0.0.1:8080  --user admin --password admin --showid 2 --episodeid 1  --sequenceid 2  --revisionid 3 
```

### Finding IDs
To find ID of sequence revision you are looking for follow the steps below:
- Open Flix Client
- Open Developer dev tools in Flix client by clicking top menu => View => Dev Tools
- On Dev tools click on Network tab
- In Flix client navigate to the Sequence Revision that needs to be updated
- Check Revision number In Flix top bar e.g [Revision 7]
- In the Network tab click on the revision number, e.g 7
- After clicked make sure Header tab is selected
- In the Header tab under General section, Requested URL should be visible e.g: http://localhost:8080/show/1/episode/2/sequence/3/revision/7
- In the example above Show ID is 1, Episode ID is 2, Sequence ID is 3 and revision ID is 7