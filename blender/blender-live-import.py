#
# Copyright (C) Foundry 2020
#

bl_info = {
    "name": "Flix",
    "blender": (2, 80, 0),
    "category": "3D View",
}

import asyncio
import bpy
import json
from typing import List, Set, Coroutine
import os
import websockets
import uuid
import tempfile

class CurrentImageToFlix(bpy.types.Operator):
    """Current Image"""
    bl_idname = "flix.current_image"
    bl_label = "Current Image"
    bl_options = {'REGISTER'}

    def execute(self, context) -> Set[str]:
            filepaths = []
            filepaths.append(generate_snapshot())
            # Start connection / send filepaths
            asyncio.get_event_loop().run_until_complete(live_import(filepaths))

            return {'FINISHED'}

class ReplaceImageInFlix(bpy.types.Operator):
    """Replace Image"""
    bl_idname = "flix.replace_image"
    bl_label = "Replace Image"
    bl_options = {'REGISTER'}

    def execute(self, context) -> Set[str]:
            filepaths = []
            filepaths.append(generate_snapshot())
            asyncio.get_event_loop().run_until_complete(live_replace(filepaths))

            return {'FINISHED'}

def handshake(ws: websockets.WebSocketClientProtocol) -> Coroutine:
    """handshake send a handshake to client's websocket"""
    handshake_message = {
        'data': {
            'app': 'photoshop',
            'id': 'a8dcd02f',
            'version': '6.4.0'
        }
    }
    return ws.send(json.dumps(handshake_message))

def send_files(ws: websockets.WebSocketClientProtocol, filepaths: List[str]) -> Coroutine:
    """send_files will format a messages to import files and send the message through websocket"""
    file_import_message = {
        'data': {
            'command': 'DEFAULT_ACTION',
            'action': 'IMPORT_CURRENT',
            'data': {
                'paths': filepaths,
                'origin': 'Blender'
            }
        }
    }
    return ws.send(json.dumps(file_import_message))

async def live_import(filepaths: List[str]) -> None:
    """live_import will make a websocket connection and send files"""
    try:
        async with websockets.connect('ws://localhost:54242') as websocket:
            # Handshake with client's websocket
            await handshake(websocket)

            # Send files import through websocket
            await send_files(websocket, filepaths)
    except OSError as err:
        print('could not connect to Flix client, ensure it is up and running and open the sequence in which you want to import panels')

def send_replace(ws: websockets.WebSocketClientProtocol, filepaths: List[str]) -> Coroutine:
    """send_replace will format a messages to replace a file and send the message through websocket"""
    file_import_message = {
        'data': {
            'command': 'DEFAULT_ACTION',
            'action': 'REPLACE_CURRENT',
            'data': {
                'artwork': filepaths,
                'origin': 'Blender'
            }
        }
    }
    return ws.send(json.dumps(file_import_message))

async def live_replace(filepaths: List[str]) -> None:
    """live_replace will make a websocket connection and send files to replace panels in flix"""
    try:
        async with websockets.connect('ws://localhost:54242') as websocket:
            # Handshake with client's websocket
            await handshake(websocket)

            # Send files replace through websocket
            await send_replace(websocket, filepaths)
    except OSError as err:
        print('could not connect to Flix client, ensure it is up and running and open the sequence in which you want to import panels')


def retrieve_filepaths(paths: List[str]) -> List[str]:
    """retrieve_filepaths will ensure the paths are correct"""
    received_filepaths = []
    for path in paths:
        if os.path.isfile(path):
            received_filepaths.append(os.path.abspath(path))
        else:
            print('invalid path: "{0}"'.format(path))
    return received_filepaths


def generate_snapshot() -> str:
    """generate_snapshot will generate a png file from the render"""
    C = bpy.context
    scene = C.scene
    settings = scene.render.image_settings
    old_format = settings.file_format
    old_quality = settings.quality
    settings.file_format = 'JPEG'
    settings.quality = 90

    filename = str(uuid.uuid4()) + ".png"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    bpy.ops.render.render()

    img = bpy.data.images['Render Result']
    img.save_render(filepath, scene=scene)

    settings.file_format = old_format
    settings.quality = old_quality
    return filepath

class VIEW3D_MT_FlixMenu(bpy.types.Menu):
    bl_label = "Flix"
    bl_idname = "VIEW3_MT_flix_menu"

    def draw(self, context) -> None:
        layout = self.layout
        layout.operator(CurrentImageToFlix.bl_idname)
        layout.operator(ReplaceImageInFlix.bl_idname)

def draw_menu(self, context) -> None:
    self.layout.menu(VIEW3D_MT_FlixMenu.bl_idname)


def register() -> None:
    bpy.utils.register_class(CurrentImageToFlix)
    bpy.utils.register_class(ReplaceImageInFlix)
    bpy.utils.register_class(VIEW3D_MT_FlixMenu)
    bpy.types.VIEW3D_MT_editor_menus.append(draw_menu)

def unregister() -> None:
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_menu)
    bpy.utils.unregister_class(VIEW3D_MT_FlixMenu)
    bpy.utils.unregister_class(CurrentImageToFlix)
    bpy.utils.unregister_class(ReplaceImageInFlix)

if __name__ == '__main__':
    register()
