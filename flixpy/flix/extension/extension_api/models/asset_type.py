from enum import Enum


class AssetType(str, Enum):
    AAF = "aaf"
    ANNOTATION = "annotation"
    ARTWORK = "artwork"
    AUDIO = "audio"
    CONTACTSHEET = "contactsheet"
    DIALOGUE = "dialogue"
    DNXHD = "dnxhd"
    EXTENSION = "extension"
    FULLRES = "fullres"
    LOGO = "logo"
    PUBLISH = "publish"
    PUBLISH_FULLSIZED = "publish_fullsized"
    SCALED = "scaled"
    SHOW_THUMBNAIL = "show-thumbnail"
    SOURCE_FILE = "source_file"
    SOURCE_MEDIA = "source_media"
    STATE_YAML = "state_yaml"
    THUMBNAIL = "thumbnail"
    UNKNOWN = "unknown"
    WATERMARK = "watermark"
    WAV = "wav"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
