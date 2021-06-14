#
# Copyright (C) Foundry 2020
#

from PIL import ImageGrab
import tkinter
import asyncio
import json
import websockets
import uuid
import os
import tempfile


def handshake(ws):
    """handshake send a handshake to client's websocket"""
    handshake_message = {
        'data': {
            'app': 'photoshop',
            'id': 'a8dcd02f',
            'version': '6.3.5'
        }
    }
    return ws.send(json.dumps(handshake_message))


def send_files(ws, filepaths):
    """send_files will format a messages to import files and send the message through websocket"""
    file_import_message = {
        'data': {
            'command': 'DEFAULT_ACTION',
            'action': 'IMPORT_CURRENT',
            'data': {
                'paths': filepaths,
                'origin': 'Darwin'
            }
        }
    }
    return ws.send(json.dumps(file_import_message))


async def live_import(filepaths):
    """live_import will make a websocket connection and send files"""
    try:
        async with websockets.connect('ws://localhost:54242') as websocket:
            # Handshake with client's websocket
            await handshake(websocket)

            # Send files import through websocket
            await send_files(websocket, filepaths)
    except OSError as err:
        print('could not connect to Flix client, ensure it is up and running and open the sequence in which you want to import panels')

def save_screenshot():
    root.withdraw()
    root.update()
    img = ImageGrab.grab()
    root.deiconify()
    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    img.save(filepath, 'PNG')
    asyncio.get_event_loop().run_until_complete(live_import([filepath]))

def save_clipboard():
    img = ImageGrab.grabclipboard()
    if img is None:
        print('could not find anything on clipboard')
        return
    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    img.save(filepath, 'PNG')
    asyncio.get_event_loop().run_until_complete(live_import([filepath]))

root = tkinter.Tk()
root.title("Send To Flix")
root.wm_attributes("-topmost", 1)
root.minsize(220, 70)

b1 = tkinter.Button(root, text="Save Screenshot", command=save_screenshot)
b1.pack()
b2 = tkinter.Button(root, text="Save Clipboard", command=save_clipboard)
b2.pack()

root.mainloop()