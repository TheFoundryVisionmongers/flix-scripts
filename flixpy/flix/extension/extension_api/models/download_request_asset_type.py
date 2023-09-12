from enum import Enum


class DownloadRequestAssetType(str, Enum):
    AAF = "aaf"
    ANNOTATION = "annotation"
    ARTWORK = "artwork"
    AUDIO = "audio"
    CONTACTSHEET = "contactsheet"
    DIALOGUE = "dialogue"
    FULLRES = "fullres"
    LOGO = "logo"
    MASTER = "master"
    MOVIE = "movie"
    PUBLISH = "publish"
    SCALED = "scaled"
    SHOW_THUMBNAIL = "show-thumbnail"
    SOURCE_FILE = "source_file"
    SOURCE_MEDIA = "source_media"
    THUMBNAIL = "thumbnail"
    WATERMARK = "watermark"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
