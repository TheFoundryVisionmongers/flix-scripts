# Flix License Management

This is a script to help manage the license / seats used from Flix Server.

It will show you haw many seats you have in total and how many are in used.

You are able to revoke access to some users to free a seat.

## Prerequisites

This script requires a minimum Python version of 3.7

You will also need to install these libraries:

* requests=2.21.0

* urllib3=1.24.1

You can install them using pip (https://pip.pypa.io/en/stable/installing/)

```python3 -m pip install -r requirements.txt```


### Getting Started

Start your Flix server.

Run ```python3 main.py --help```:

```
usage: main.py [--help] --server SERVER --user USER --password PASSWORD
               (--info | --revoke [REVOKE [REVOKE ...]])

optional arguments:
  --help

required arguments:
  --server SERVER       Flix 6 server url
  --user USER           Flix 6 client username
  --password PASSWORD   Flix 6 client password
  --info                Show seats and logged in users
  --revoke [REVOKE [REVOKE ...]]
                        Revoke user from access key
```

The server URL is the hostname of your server (http://localhost:1234), user and password have to be from an **Admin** user.

You can either do a `--info` or `--revoke X` command to list / show information of seats in use with users or to revoke access.


### Examples

To retrieve informations about seats and seats in use:
```
python3 main.py --server http://localhost:1234 --user admin --password admin --info
Seats in use: 2 / Maximum seats: 3
----------------------------------------------------------------------------------------------------
access_key          |user id|            username|                   expiry_date
----------------------------------------------------------------------------------------------------
53sg46eQC9z7dDF6fxDf|      1|               admin|          2020-06-26T10:32:17Z
tC6PdpZKMRHKLqGP68Cj|      3|               test1|          2020-06-27T10:32:06Z
```

To revoke an access key and free a seat:
```
python3 main.py --server http://localhost:1234 --user admin --password admin --revoke tC6PdpZKMRHKLqGP68Cj
```

You can as well revoke multiple seats in one command:
```
python3 main.py --server http://localhost:1234 --user admin --password admin --revoke tC6PdpZKMRHKLqGP68Cj 53sg46eQC9z7dDF6fxDf
```
