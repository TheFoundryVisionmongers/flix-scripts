# Flix Contact Sheet Generation

This is an example of Contact Sheet Generation using the API

### Prerequisites

You need python3 and pip3.
You can install the dependencies by running:
```
pip3 install -r requirements.txt
```

### Getting Started

You need an instance of Flix server running

After installing the dependencies, you can start `python3 main.py`

You can now enter your Flix credentials and press login

A list of shows (episodic or not), sequences and sequences revisions will be filled

Select an export path (where the contact sheet will be generated)

You can select a font, font size, how many rows or columns you wants and click on Generate

### Documentation

Generated documentation can be found in the form of `.html` files can be found in the `./docs` directory. This covers all methods and classes.

To re-generate documentation you will need to install `pdoc3` (https://pypi.org/project/pdoc3/) and run this command:

```
pdoc3 --html *.py
```

### Packaging

To package this into a MacOS app, use `virtualenv` and `pyinstaller`

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller -w -i icons/flix-contact-sheet.icns -n "Flix Contact Sheet" -F main.py
```

Then run the new MacOS app:
```
open "dist/Flix Contact Sheet.app"
```

