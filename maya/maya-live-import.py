#
# Copyright (C) Foundry 2020
#

#!/usr/bin/env python2
 
import json
import maya.OpenMaya as api
import maya.OpenMayaUI as apiUI
import os
import tempfile
import uuid
from websocket import create_connection


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
                'origin': 'Maya'
            }
        }
    }
    return ws.send(json.dumps(file_import_message))


def live_import(filepaths):
    """live_import will make a websocket connection and send files"""
    try:
        ws = create_connection("ws://localhost:54242")
        # Handshake with client's websocket
        handshake(ws)
        # Send files import through websocket
        send_files(ws, filepaths)
    except OSError as err:
        print('could not connect to Flix client, ensure it is up and running and open the sequence in which you want to import panels')


def generate_snapshot():
    """generate_snapshot will make a snapshot of the active view"""
    view = apiUI.M3dView.active3dView()
    image = api.MImage()
    view.readColorBuffer(image, True)
    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    image.writeToFile(filepath, ".png")
    return filepath


# Retreive new file paths from snapshot
filepaths = [generate_snapshot()]
# Import filepaths to Flix Client
live_import(filepaths)