# flix-scripts-internal
Internal Flix scripts


For each scripts you'll need to have a Flix client up an running and being on a sequence revision. They all use websocket to send files to the client and let the client import the files (same behaviour as Photoshop with the ws, using the same code).
They are small scripts, they can easily be improved, look at them as examples, not prod ready things, but more as prototypes.
A video to see Blender and Maya working: https://thefoundry.workplace.com/groups/1689933207953903/permalink/2550228475257701

## Clipboard script (using python 3):
The goal of this small script was to make presentation easily into Flix, to be able to send screenshots from your whole screen to Flix or even a part of the screen coming from your clipboard. The clipboard on Catalina is not working / not needed anymore as Catalina has a feature to drag n drop directly. But this script been used a bit to make presentations and stuff.

## Blender (using python 3):
This script aims to send a scene from Blender to Flix. You will need to run the script in Blender to be able to start the process.
You can follow these instructions on how to install / run a script in Blender from there: https://docs.blender.org/manual/en/latest/advanced/scripting/introduction.html

## Maya (using python 2):
This script allow you to send the scene from Maya to Flix. You will need to run the script in Maya to be able to start the process.
You can follow these instructions on how to install / run a script in Maya from there: http://zurbrigg.com/tutorials/beginning-python-for-maya
/!\ You will need to install a python library (websocket-client), to do that you need to use Maya binary to install it.
