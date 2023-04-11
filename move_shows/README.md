# Move sequence between shows script
This script will move a sequence, and all associated data and media, from one show to another.

## Requirements
The script needs access and permission to connect to the Flix database and read/write permission on the asset directory.

The script is tested to run with Python 3.10:
```bash
python src/main.py
```

To run the script you will need to install the Python requirements:
```bash
python -m pip install -r requirements.txt
```

You may also need to install the MySQL Python connector to the OS. This can be done via the OS package manager; for
example here is the command for a Debian based system:
```bash
sudo apt install mysql-connector-python
```

### Recommendations
It is recommended that this script be run "out of hours" when activity on the Flix Server is minimal, or zero.

## Steps
The script will go through the following steps when moving a sequence:
 - Attempt to connect to the database
 - Ask user to select the items to transfer
    - Show (to and from)
    - Sequence
 - Fetch all media object paths from the source sequence
 - Update all database rows with the destination show ID, held in transaction
 - Copy all files from the source Show sub-directory to the destination show sub-directory
 - **Ask user to confirm committal of data change**
    - Changes before this step will be undone if the user responds with `n` here 
 - Delete original files
 - Commit database transaction