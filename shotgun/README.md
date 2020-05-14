# Flix Production Handoff

This is an example of the Flix Production Handoff.

### Prerequisites

You need python3 and pip3

You can run this command to install the needed dependencies:
```
pip3 install -r requirements.txt
```

### Getting Started

You need an instance of Flix server running

After installing the dependencies, you can start `python3 main.py`

You can now enter your Flix credentials and press login

A list of shows (episodic or not) and sequences will be filled

Pick the one you want to export and select your choice or production handoff:

- Local Export

    You will be asked to select an export path, destination where folders will be created for show, episode and sequence

    Once the export path set, you can click `Export Latest`, it will retrieve the latest sequence revision, export a quicktime per shots
    and download your artwork and thumbnails to the export path

- Shotgun Export

    You will be asked your credentials of Shotgun (username and hostname, the password will be asked later)

    Once the credentials set, you can click `Export Latest`, it will retrieve the latest sequence revision, export a quicktime per shots and download the thumbnails

    It will login to Shotgun and will start creating / reusing a project, a Sequence, Shots and Revisions by uploading the quicktime