import datetime
import gzip
import os
import re
import struct
from typing import Any
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class Library:
    """Provides access to music collection,
    as well as returning lists of songs that fit the given criteria.
    The typical song entry is {songPath: [artist, album, year, title, track number, genre, length]}"""

    ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)

    MAGIC = b"\x01\xff"
    TIME_FORMAT = "%Y%m%d%H%M%S"

    def __init__(self) -> None:
        self._folders = []
        self._files = {}
        self.libraryFile = r"musicplayer\Library.lib"
        self.timestamp = datetime.datetime.min
        self._playlists = {}
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
        for playlist in self._playlists:
            for song in self._playlists[playlist]:
                if song not in self.tempFiles:
                    self._playlists[playlist].remove(song)
                    self.changed = True
        self.tempFiles.clear()
        if self.changed:
            self._save()
            self.timestamp = datetime.datetime.now()
            self.changed = False

    def _load(self) -> bool:
        """Loads data form a binary gzip file on program startup.
        The file contains all data from the library as at the
        last time the library was loaded."""
        print("Loading data from library file...")
        try:
            with gzip.open(self.libraryFile, "rb") as fh:
                if not fh.read(2) == self.MAGIC:
                    return False
                temp = {}
                folderCount = fh.read(2)
                folderCount = struct.unpack("<h", folderCount)[0]
                timestamp = fh.read(14)
                timestamp = struct.unpack("<14s", timestamp)[0].decode()
                for n in range(folderCount):
                    length = fh.read(2)
                    length = struct.unpack("<h", length)[0]
                    folder = fh.read(struct.Struct(f"<{length}s").size)
                    folder = struct.unpack(f"<{length}s", folder)[0].decode("utf8")
                    self._folders.append(folder)
                if not fh.read(2) == self.MAGIC:
                    return False
                while True:
                    length = fh.read(2)
                    if length == self.MAGIC:
                        break
                    length = struct.unpack("<h", length)[0]
                    path = fh.read(struct.Struct(f"<{length}s").size)
                    path = struct.unpack(f"<{length}s", path)[0].decode("utf8")
                    attributes = []
                    for n in range(7):
                        length = fh.read(2)
                        length = struct.unpack("<h", length)[0]
                        attrib = fh.read(struct.Struct(f"<{length}s").size)
                        attrib = struct.unpack(f"<{length}s", attrib)[0].decode("utf8")
                        attributes.append(attrib)
                    temp[path] = attributes
                    if not fh.read(2) == self.MAGIC:
                        print("file corrupted...")
                        return False
                length = fh.read(2)
                length = struct.unpack("<h", length)[0]
                if length > 0:
                    for _ in range(length):
                        length = fh.read(2)
                        length = struct.unpack("<h", length)[0]
                        playlist = fh.read(struct.Struct(f"<{length}s").size)
                        playlist = struct.unpack(f"<{length}s", playlist)[0].decode("utf8")
                        self._playlists[playlist] = []
                        while True:
                            length = fh.read(2)
                            if length == self.MAGIC:
                                break
                            length = struct.unpack("<h", length)[0]
                            song = fh.read(struct.Struct(f"<{length}s").size)
                            song = struct.unpack(f"<{length}s", song)[0].decode("utf8")
                            if os.path.exists(song):
                                self._playlists[playlist].append(song)
            self._files = temp
            self.timestamp = datetime.datetime.strptime(timestamp, Library.TIME_FORMAT)
            return True
        except Exception:
            return False

    def _save(self) -> None:
        """Saves current data to a binary gzip file that will be loaded
        on the next start-up."""
        print("Saving data to library file...")
        with gzip.open(self.libraryFile, "wb") as fh:
            fh.write(self.MAGIC)
            fh.write(struct.pack("<h", len(self._folders)))
            fh.write(struct.pack("<14s", datetime.datetime.now().strftime(Library.TIME_FORMAT).encode()))
            for folder in self._folders:
                toBeWritten = struct.pack(f"<h{len(folder.encode())}s", len(folder.encode()), folder.encode())
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
            fh.write(struct.pack("<h", len(self._playlists)))
            for playlist in self._playlists:
                toBeWritten = struct.pack(f"<h{len(playlist.encode())}s", len(playlist.encode()), playlist.encode())
                fh.write(toBeWritten)
                for song in self._playlists[playlist]:
                    toBeWritten = struct.pack(f"<h{len(song.encode())}s", len(song.encode()), song.encode())
                    fh.write(toBeWritten)
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
                        elif key == "date":
                            if not re.fullmatch(r"\d{4}", value):
                                if match := re.match(r"\d{4}", value):
                                    value = match.group(0)
                        elif key == "title" and value == "Unknown":
                            value = dirEntry.name
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
        self._playlists[newPlaylist] = []
        self.changed = True

    def deletePlaylist(self, playlist: str) -> None:
        if playlist in self._playlists:
            del self._playlists[playlist]
            self.changed = True

    def renamePlaylist(self, playlist: str, newPlaylistName: str) -> None:
        if playlist in self._playlists:
            self._playlists[newPlaylistName] = self._playlists[playlist]
            del self._playlists[playlist]
            self.changed = True

    def addToPlaylist(self, playlist: str, song: str) -> None:
        if playlist not in self._playlists:
            self._playlists[playlist] = []
        self._playlists[playlist].append(song)
        self.changed = True

    def deleteFromPlaylist(self, playlist: str, song: str) -> None:
        if playlist in self._playlists:
            if song in self._playlists[playlist]:
                self._playlists[playlist].remove(song)
                self.changed = True

    def getSongsForArtist(self, artist: str, orderBy: str = None, reverse: bool = False) -> list:
        """Returns a list of all song paths for a given artist with optional sorting new first."""
        songs = []
        for song in self._files:
            if os.path.exists(song):
                if self._files[song][self.ARTIST].lower() == artist.lower():
                    songs.append(song)
        songs.sort(key=lambda x: (self._files[x][self.ALBUM], self._files[x][self.DISC],
                                  self._files[x][self.TRACK]))
        if orderBy == "Year" or orderBy is None:
            songs.sort(key=lambda x: self._files[x][self.YEAR], reverse=reverse)
        elif orderBy == "Album":
            songs.sort(key=lambda x: self._files[x][self.ALBUM], reverse=reverse)
        return songs

    def getSongsForAlbum(self, album: str, ignored: Any = None, reverse: bool = False) -> list:
        songs = []
        for song in self._files:
            if os.path.exists(song):
                if self._files[song][self.ALBUM].lower() == album.lower():
                    songs.append(song)
        return sorted(songs, reverse=reverse)

    def getSongsForPlaylist(self, playlist: str, orderBy: str = None, reverse: bool = False) -> list:
        if playlist not in self._playlists:
            return []
        elif orderBy == "Year":
            return sorted(self._playlists[playlist],
                          key=lambda x: (self._files[x][self.YEAR],
                                         self._files[x][self.ALBUM],
                                         self._files[x][self.DISC]),
                          reverse=reverse)
        elif orderBy == "Album":
            return sorted(self._playlists[playlist],
                          key=lambda x: (self._files[x][self.ALBUM], self._files[x][self.DISC]),
                          reverse=reverse)
        elif orderBy == "Artist":
            return sorted(self._playlists[playlist],
                          key=lambda x: (self._files[x][self.ARTIST],
                                         self._files[x][self.YEAR],
                                         self._files[x][self.ALBUM],
                                         self._files[x][self.DISC]),
                          reverse=reverse)
        return self._playlists[playlist]
