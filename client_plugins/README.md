# Flix Plugin Examples

The following folders contain examples of plugins that modify the behaviour of the Flix Client (version 8.0.0 and above).
These plugins leverage the [Chrome Extension Support](https://www.electronjs.org/docs/latest/api/extensions) built into Electron.
The examples here can be taken and added into Flix, either directly or with some modifications.

## Installation

To install these plugins, simply add the plugin files to a new folder in the Flix Client Plugins folder, located at:

- Windows: `%APPDATA%/Flix/plugins`
- MacOS: `~/Library/Application Support/Flix/plugins`

The Flix Client will automatically load plugins from this folder on start, and will monitor for new plugins being added at run time.
Loaded plugins can be managed via the Plugins & Extensions management window.

Note: Each extension must be unpacked into its own folder. Flix does not support packaged `.crx` extensions.

## Plugin Development

To build your own plugin, start by defining an [extension manifest file](https://developer.chrome.com/docs/extensions/reference/manifest) in `manifest.json`.
(Note: Electron only supports a [subset of the manifest file properties](https://www.electronjs.org/docs/latest/api/extensions#supported-manifest-keys).)

To modify the Flix Client DOM, you will need to register a content script that runs on paths matching `file://*`,  due to the way pages are loaded in Electron.
Since Flix uses the Angular framework, navigation is done via the URL hash.
When determining which page is active, this should be used instead of the URL path name which will not change.

For more details see the [Chrome Extensions development documentation](https://developer.chrome.com/docs/extensions/get-started).
However, only a [subset of the extension APIs](https://www.electronjs.org/docs/latest/api/extensions#supported-extensions-apis) are available for use within Flix Plugins.

## Examples

- [Version Up Away](https://github.com/TheFoundryVisionmongers/flix-scripts/tree/main/client_plugins/version_up_away) - Removes the version up button from the panel browser