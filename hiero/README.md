# Hiero

This is an example of a script for Hiero

### Prerequisites

You need to have Hiero/HieroPlayer installed

### Getting Started

You need an instance of Flix server running

Open Hiero or Hiero Player

Install / execute the script in Hiero/HieroPlayer and Open the new action `Flix` from `Windows` tab

You can now enter your Flix credentials and press login

A list of shows (episodic or not) and sequences will be filled

You have two options:

- Pull Latest

    It will retreive the latest sequence revision and open it in Hiero/HieroPlayer

    Duration, comments, dialogues, shots, images, burnin will be added

- Update in Flix

    It will send the selected sequence from Hiero to Flix, It will not send new panels but will create a new

    sequence revision in Flix and reuse the panels / updating their duration


### Documentation

Generated documentation can be found in the form of `.html` files can be found in the `./docs` directory. This covers all methods and classes.

To re-generate documentation you will need to install `pdoc3` (https://pypi.org/project/pdoc3/) and run this command:

```
pdoc3 --html *.py
```