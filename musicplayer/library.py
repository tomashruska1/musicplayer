import datetime
import gzip
import os
import re
import struct
from collections import defaultdict
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class Library:
    """Provides access to music collection,
    as well as returning lists of songs that fit the given criteria.
    The typical song entry is {songPath: [artist, album, year, title, track number, genre, length]}"""

    ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)

    MAGIC = b"\x01\xff"
    format_spec = "%Y%m%d%H%M%S"

    def __init__(self) -> None:
        self._folders = []
        self._files = {}
        self.libraryFile = r"musicplayer\Library.lib"
        self.timestamp = datetime.datetime.min
        self._playlists = defaultdict(list)
        self.tempFiles = set()
        self.changed = False
        self._load()
        self.update()

    def update(self) -> None:
        """Go through files in the library folders looking for:
        a) files that were changed after the library was last updated,
        b) files that were removed after the library was last loaded."""
        for folder in self._folders:
            self._getFiles(folder)
        temp = [file for file in self._files]
        for file in temp:
            if file not in self.tempFiles:
                del self._files[file]
                self.changed = True
        self.tempFiles.clear()
        if self.changed:
            self._save()

    def _load(self) -> bool:
        """Loads data form a binary gzip file on program startup.
        The file contains all data from the library as at the
        last time the library was loaded."""
        print("Loading data from library file...")
        try:
            with gzip.open(self.libraryFile, "rb") as fh:
                if not fh.read(2) == self.MAGIC:
                    print("file corrupted!")
                    return False
                temp = {}
                structRead = struct.Struct("<h")
                folderCount = fh.read(structRead.size)
                folderCount = struct.unpack("<h", folderCount)[0]
                timestamp = fh.read(14)
                timestamp = struct.unpack("<14s", timestamp)[0].decode()
                for n in range(folderCount):
                    length = fh.read(structRead.size)
                    length = struct.unpack("<h", length)[0]
                    folder = fh.read(struct.Struct(f"<{length}s").size)
                    folder = struct.unpack(f"<{length}s", folder)[0].decode("utf8")
                    self._folders.append(folder)
                if not fh.read(2) == self.MAGIC:
                    print("file corrupted...")
                    return False
                while True:
                    length = fh.read(structRead.size)
                    if length == self.MAGIC:
                        print("Done!")
                        break
                    length = struct.unpack("<h", length)[0]
                    path = fh.read(struct.Struct(f"<{length}s").size)
                    path = struct.unpack(f"<{length}s", path)[0].decode("utf8")
                    attributes = []
                    for n in range(7):
                        length = fh.read(structRead.size)
                        length = struct.unpack("<h", length)[0]
                        attrib = fh.read(struct.Struct(f"<{length}s").size)
                        attrib = struct.unpack(f"<{length}s", attrib)[0].decode("utf8")
                        attributes.append(attrib)
                    temp.update({path: [*attributes]})
                    if not fh.read(2) == self.MAGIC:
                        print("file corrupted...")
                        return False
            self._files = temp
            self.timestamp = datetime.datetime.strptime(timestamp, Library.format_spec)
            return True
        except (EOFError, FileNotFoundError, PermissionError):
            return False

    def _save(self) -> None:
        """Saves current data to a binary gzip file that will be loaded
        on the next start-up."""
        print("Saving data to library file...")
        with gzip.open(self.libraryFile, "wb") as fh:
            fh.write(self.MAGIC)
            fh.write(struct.pack("<h", len(self._folders)))
            fh.write(struct.pack("<14s", datetime.datetime.now().strftime(Library.format_spec).encode()))
            for folder in self._folders:
                toBeWritten = struct.pack(f"<h{len(folder)}s", len(folder), folder.encode())
                fh.write(toBeWritten)
            fh.write(self.MAGIC)
            for song in self._files:
                toBeWritten = struct.pack(f"<h{len(song.encode())}s", len(song.encode()), song.encode())
                fh.write(toBeWritten)
                for attrib in self._files[song]:
                    toBeWritten = struct.pack(f"<h{len(attrib.encode())}s", len(attrib.encode()), attrib.encode())
                    fh.write(toBeWritten)
                fh.write(self.MAGIC)
            fh.write(self.MAGIC)

    def _getFiles(self, folder: [str, os.DirEntry]) -> None:
        """A recursive function that loops through files in a the given folder
        looking for files that have last-changed timestamp higher than the library
        timestamp -> these were changed after the library was last loaded."""
        keyList = ["artist", "album", "date", "title", "tracknumber", "discnumber"]
        for dirEntry in os.scandir(folder):
            if dirEntry.name.lower().endswith(".mp3"):
                self.tempFiles.add(dirEntry.path)
                stat = dirEntry.stat()
                modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                if modified > self.timestamp or dirEntry.path not in self._files:
                    song = EasyID3(dirEntry.path)
                    value_list = []
                    for key in keyList:
                        try:
                            if song[key]:
                                value = song[key][0]
                            else:
                                value = "Unknown"
                        except KeyError:
                            value = "Unknown"
                        if key == "tracknumber":
                            if not re.fullmatch(r"\d\d", value):
                                if match := re.match(r"\d\d?", value):
                                    if match2 := re.fullmatch(r"\d", match.group(0)):
                                        value = f"{match2.group(0):0>2}"
                                    else:
                                        value = match.group(0)
                        if key == "date":
                            if not re.fullmatch(r"\d{4}", value):
                                if match := re.match(r"\d{4}", value):
                                    value = match.group(0)
                        value_list.append(value)
                    length = round(MP3(dirEntry.path).info.length)
                    length = f"{length // 60 :02}:{length % 60 :02}"
                    self._files.update({dirEntry.path: [*value_list, length]})
                    self.changed = True
            elif dirEntry.is_dir():
                self._getFiles(dirEntry)

    @property
    def library(self) -> dict:
        """Returns the entire dictionary with all data. Used mainly for lookups."""
        return self._files

    @property
    def playlists(self) -> dict:
        """Returns a list of all available playlists."""
        return self._playlists

    @property
    def folders(self) -> list:
        """Returns a list of all folders in the library."""
        return self._folders

    @property
    def artists(self) -> list:
        """Returns a list of all artists in the library."""
        return sorted(list(set(self._files[song][self.ARTIST] for song in self._files)))

    @property
    def albums(self) -> list:
        """Returns a list of all albums in the library."""
        return sorted(list(set(self._files[song][self.ALBUM] for song in self._files)))

    def addFolder(self, newFolder: str) -> None:
        self._folders.append(newFolder)
        self.update()

    def deleteFolder(self, folder: str) -> None:
        if folder in self._folders:
            self._folders.remove(folder)
            self.update()

    def createPlaylist(self, newPlaylist: str) -> None:
        self._playlists.update(newPlaylist)

    def deletePlaylist(self, playlist: str) -> None:
        if playlist in self._playlists:
            del self._playlists[playlist]

    def addToPlaylist(self, playlist: str, song: str) -> None:
        self.playlists[playlist].append(song)

    def deleteFromPlaylist(self, playlist: str, song: str) -> None:
        if playlist in self._playlists:
            if song in self._playlists[playlist]:
                self._playlists[playlist].remove(song)

    def getSongsForArtist(self, artist: str, newFirst: bool = False) -> list:
        """Returns a list of all song paths for a given artist with optional sorting new first."""
        songs = []
        for song in self._files:
            if self._files[song][self.ARTIST].lower() == artist.lower():
                songs.append(song)
        songs.sort(key=lambda x: (self._files[x][self.ALBUM], self._files[x][self.DISC],
                                  self._files[x][self.TRACK]))
        songs.sort(key=lambda x: self._files[x][self.YEAR], reverse=newFirst)
        return songs

    def getSongsForAlbum(self, album: str) -> list:
        return [song for song in self._files
                if self._files[song][self.ALBUM].lower() == album.lower()]

    def getSongsForPlaylist(self, playlist: str) -> list:
        # TODO
        return []
