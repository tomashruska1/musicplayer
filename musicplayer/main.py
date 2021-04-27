import gzip
import struct
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio, QMediaContent
from musicplayer import library
from musicplayer.gui import bottom
from musicplayer.gui import window


ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)


class Control:
    """A class that handles the logic behind the program by manipulating the GUI classes
    and calling their methods in response to received signals."""

    MAGIC = b"\x01\xff"

    def __init__(self, screens: list) -> None:
        self.player = QMediaPlayer()
        self.player.setAudioRole(QAudio.MusicRole)
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.mainWindow = window.MainWindow(self, screens)
        self.mainBox = self.mainWindow.centralWidget().upperBox.mainBox
        self.songList = self.mainWindow.centralWidget().upperBox.songList
        self.bottomBox = self.mainWindow.centralWidget().bottomBox
        self.mainWindow.show()
        self.library = None
        self.currentSong = None
        self.playing = False
        self.random = False
        self.repeat = 0
        self.volume = 50

        self.volumeChange(self.volume)
        self.bottomBox.volumeControl.setValue(self.volume)

        self.mainTimer = QTimer()
        self.mainTimer.setInterval(100)
        self.mainTimer.timeout.connect(self.updateSongProgress)
        self.mainTimer.start()

        self.libraryUpdateTimer = QTimer()
        self.libraryUpdateTimer.setInterval(15_000)
        self.libraryUpdateTimer.timeout.connect(self.updateLibrary)
        self.libraryUpdateTimer.start()

        self.connections()

        self.displayedType = None
        self.displayedName = None
        self.types = None
        self.songListWidth = None
        values = self.load()
        if values:
            self.mainWindow.setGeometry(*values)
            self.volumeChange(self.volume)
            self.bottomBox.volumeControl.setValue(self.volume)

        self.setUpTimer = QTimer()
        self.setUpTimer.setInterval(20)
        self.setUpTimer.setSingleShot(True)
        self.setUpTimer.timeout.connect(self.setAreas)
        self.setUpTimer.start()

    def connections(self):
        self.player.currentMediaChanged.connect(self.updateCurrentSong)
        self.player.durationChanged.connect(self.updateSongProgressRange)
        self.player.stateChanged.connect(self.playerStatusChanged)
        self.bottomBox.previousButton.click.connect(self.playlist.previous)
        self.bottomBox.repeatButton.click.connect(self.repeatButtonClick)
        self.bottomBox.stopButton.click.connect(self.stopButtonClick)
        self.bottomBox.playButton.click.connect(self.playButtonClick)
        self.bottomBox.randomButton.click.connect(self.randomButtonClick)
        self.bottomBox.nextButton.click.connect(self.playlist.next)
        self.bottomBox.muteButton.click.connect(self.mute)
        self.bottomBox.songProgress.sliderMoved.connect(self.songProgressMove)
        self.bottomBox.volumeControl.sliderMoved.connect(self.volumeChange)

    def setAreas(self) -> None:
        """Called after the GUI is created to provide user with a feedback
        that the program is running in case a larger amount of songs will be added
        when the Library class is initialized."""
        # TODO add a tooltip that will notify the user larger amount of songs is being loaded
        #  (freezes the program as the execution moves to the Library class.)
        self.library = library.Library()
        self.types = {"artist": self.library.getSongsForArtist,
                      "album": self.library.getSongsForAlbum,
                      "playlist": self.library.getSongsForPlaylist}
        self.mainBox.setAreas(self.library)
        self.setUpTimer.deleteLater()
        self.setUpTimer = None
        self.getSongs(self.displayedType, self.displayedName)
        if self.songListWidth is not None:
            songListGeometry = self.songList.geometry()
            self.songList.preferredWidth = songListGeometry.width() - self.songListWidth
            self.mainWindow.centralWidget().upperBox.line.resizeWidgets(songListGeometry.width() - self.songListWidth)

    def updateLibrary(self) -> None:
        self.library.update()
        self.mainBox.updateView(self.library)

    def updateCurrentSong(self) -> None:
        """Update all areas that may display information about the currently
        playing song - SongList, Now Playing tab, BottomBox"""
        media = self.player.currentMedia()
        self.currentSong = media.request().url().toLocalFile().replace("/", "\\")
        if self.currentSong in self.library.library:
            self.songList.updateActiveSong(self.currentSong)
            self.mainBox.updateActiveSong(self.playlist.currentIndex())
            songEntry = self.library.library[self.currentSong]
            self.bottomBox.updateSongInfo(f"{songEntry[ARTIST]} - {songEntry[NAME]}")

    def updateSongProgressRange(self) -> None:
        """Updates the range of the slider that represents the song position."""
        self.bottomBox.updateSongProgressRange(self.player.duration())

    def playerStatusChanged(self) -> None:
        """Used to properly update the player look after the current playlist has finished."""
        index = self.playlist.currentIndex()
        if index == -1:
            self.stopButtonClick()

    def getSongs(self, isType: str, name: str) -> None:
        """Retrieves the songs for a given artist, album or playlist based on type
        and passes the resulting list to the SongList class."""
        if isType is None:
            isType = self.displayedType
        if name is None:
            name = self.displayedName
        orderBy = self.songList.buttonOrderBy.text()
        reverse = True if self.songList.buttonOrderReverse.text() == chr(0x25bc) else False
        listForType = self.types[isType](name, orderBy, reverse)
        playlist = None
        if isType == "playlist":
            playlist = name
        if len(listForType) == 0:
            artists = self.library.artists
            if len(artists):
                listForType = self.library.getSongsForArtist(artists[0])
        self.songList.updateSongList(listForType,
                                     self.library.library,
                                     self.currentSong,
                                     playlist,
                                     isType)
        self.displayedType = isType
        self.displayedName = name

    def playSongList(self, song: str = None) -> None:
        """Called when user double-clicks on an artist/album/playlist widget or a song
        in right-hand side panel."""
        self.playlist.clear()
        index = 0
        loopIndex = 0
        for songPath in self.songList.garbageProtector:
            if song == songPath:
                index = loopIndex
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(songPath)))
            loopIndex += 1
        if self.playlist.isEmpty():
            return
        self.player.play()
        if index > 0:
            self.playlist.setCurrentIndex(index)
        self.playing = True
        self.bottomBox.playButton.updatePictures(bottom.pausePixmap,
                                                 bottom.pauseHoverPixmap, False)
        self.mainBox.setNowPlayingArea(self.library)
        self.mainBox.updateActiveSong(self.playlist.currentIndex())

    def playSongWidget(self, songPath: str, afterCurrent: bool = False) -> None:
        if afterCurrent:
            index = self.playlist.currentIndex() + 1
            self.playlist.insertMedia(index, QMediaContent(QUrl.fromLocalFile(songPath)))
        else:
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(songPath)))
        self.mainBox.setNowPlayingArea(self.library)
        self.mainBox.updateActiveSong(self.playlist.currentIndex())
        self.playing = True

    def removeFromNowPlaying(self, widget) -> None:
        if self.playlist.mediaCount() > 1:
            for row in range(self.mainBox.nowPlayingLayout.rowCount()):
                for column in range(self.mainBox.nowPlayingLayout.columnCount()):
                    if self.mainBox.nowPlayingLayout.itemAtPosition(row, column).widget() is widget:
                        self.playlist.removeMedia(row - 1)
                        break
                else:
                    continue
                break
        else:
            self.stopButtonClick()
            self.playlist.clear()
        self.mainBox.setNowPlayingArea(self.library)
        if self.playing:
            self.mainBox.updateActiveSong(self.playlist.currentIndex())

    def playMediaWidget(self, isType: str, target: str, startOver: bool, afterCurrent: bool) -> None:
        """Called from MediaWidget - plays all songs for MediaWidget's type and name."""
        if startOver:
            self.playlist.clear()
        if afterCurrent:
            index = self.playlist.currentIndex() + 1
            for songPath in self.types[isType](target):
                self.playlist.insertMedia(index, QMediaContent(QUrl.fromLocalFile(songPath)))
                index += 1
        else:
            for songPath in self.types[isType](target):
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(songPath)))
        if startOver:
            self.player.play()
            self.playing = True
            self.bottomBox.playButton.updatePictures(bottom.pausePixmap,
                                                     bottom.pauseHoverPixmap, False)
        self.mainBox.setNowPlayingArea(self.library)
        self.mainBox.updateActiveSong(self.playlist.currentIndex())

    def playFromNowPlaying(self, song: str) -> None:
        """Called when user double-clicks on a song in the Now Playing tab."""
        for n in range(self.playlist.mediaCount()):
            media = self.playlist.media(n)
            if song == media.request().url().toLocalFile().replace("/", "\\"):
                self.playlist.setCurrentIndex(n)
                if not self.playing:
                    self.player.play()
                    self.playing = True
                return

    def createPlaylist(self, playlistName: str) -> None:
        self.library.createPlaylist(playlistName)
        self.mainBox.setMainAreaPlaylists(self.library)

    def addToExistingPlaylist(self, playlist: str, songOrWidget: str, isType: str) -> None:
        if isType in self.types:
            for song in self.types[isType](songOrWidget):
                self.library.addToPlaylist(playlist, song)
        else:
            self.library.addToPlaylist(playlist, songOrWidget)
        self.library.update()

    def removeFromPlaylist(self, playlist: str, song: str) -> None:
        self.library.deleteFromPlaylist(playlist, song)
        self.mainBox.setMainAreaPlaylists(self.library)
        self.library.update()
        self.getSongs("playlist", playlist)

    def renamePlaylist(self, playlistName: str, newPlaylistName: str) -> None:
        self.library.renamePlaylist(playlistName, newPlaylistName)
        self.mainBox.setMainAreaPlaylists(self.library)
        self.library.update()

    def deletePlaylist(self, playlistName: str) -> None:
        self.library.deletePlaylist(playlistName)
        self.mainBox.setMainAreaPlaylists(self.library)
        self.library.update()

    def addWatchedFolder(self, folder: str) -> None:
        """Adds a folder to the Library class. all mp3 files within the folder
        and its sub-folders will be added to the library and accessible to the player."""
        self.library.addFolder(folder.replace("/", "\\"))
        self.mainBox.updateView(self.library)

    def removeWatchedFolder(self, folder: str) -> None:
        """Removes folder from the library, updates view and stops playback if
        the current song was in the now-removed folder."""
        self.library.deleteFolder(folder)
        self.mainBox.updateView(self.library)
        if self.currentSong not in self.library.library:
            self.songList.updateSongList([], [], "", "")
            self.player.stop()
            self.playlist.clear()
            self.bottomBox.updateSongInfo("")
            self.songList.nowPlayingSong = None
            self.mainBox.nowPlayingSong = None
            self.playing = False
            self.bottomBox.updatePlayButton(self.playing, False)

    def playButtonClick(self, passMove: bool = True) -> None:
        if not self.playing:
            if self.playlist.isEmpty():
                self.playSongList()
                return
            self.playing = True
            self.player.play()
            self.mainBox.updateActiveSong(self.playlist.currentIndex())
            self.songList.updateActiveSong(self.currentSong)
        else:
            self.playing = False
            self.player.pause()
        self.bottomBox.updatePlayButton(self.playing, passMove)

    def repeatButtonClick(self) -> None:
        if self.repeat == 0:
            self.repeat = 1
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        elif self.repeat == 1:
            self.repeat = 2
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        elif self.repeat == 2:
            self.repeat = 0
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        self.bottomBox.updateRepeatButton(self.repeat)

    def randomButtonClick(self) -> None:
        if not self.random:
            self.random = True
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self.random = False
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        self.bottomBox.updateRandomButton(self.random)

    def stopButtonClick(self) -> None:
        self.playing = False
        self.player.stop()
        if self.songList.nowPlayingSong is not None:
            self.songList.nowPlayingSong.clear()
        if self.mainBox.nowPlayingSong is not None:
            self.mainBox.nowPlayingSong.clear()
        self.bottomBox.updatePlayButton(self.playing, False)

    def mute(self) -> None:
        if not self.player.isMuted():
            self.player.setMuted(True)
            self.bottomBox.showMute()
        else:
            self.player.setMuted(False)
            self.volumeChange(self.volume)

    def volumeChange(self, volume: int) -> None:
        logVolume = QAudio.convertVolume(volume / 100,
                                         QAudio.LogarithmicVolumeScale,
                                         QAudio.LinearVolumeScale) * 100
        self.player.setVolume(logVolume)
        self.volume = volume
        self.bottomBox.updateVolumeBar(volume)

    def songProgressMove(self, position: int) -> None:
        self.player.setPosition(position)

    def updateSongProgress(self) -> None:
        position = self.player.position()
        if 0 <= position < 2_000_000_000:
            if self.player.state() > 0:
                self.bottomBox.updateSongProgress(position)
                if self.playing:
                    self.songList.activeSongPixmap()
                    self.mainBox.activeSongPixmap()
            else:
                self.bottomBox.updateSongProgress(0)

    def close(self) -> None:
        self.player.stop()
        self.mainTimer.stop()
        self.save()

    def save(self) -> None:
        """Called on exit, saves current view, geometry and volume."""
        with gzip.open(r"musicplayer\mpdata", "wb") as fh:
            fh.write(self.MAGIC)
            toBeWritten = struct.pack(f"<h{len(self.displayedType.encode())}s",
                                      len(self.displayedType.encode()),
                                      self.displayedType.encode())
            fh.write(toBeWritten)
            fh.write(self.MAGIC)
            toBeWritten = struct.pack(f"<h{len(self.displayedName.encode())}s",
                                      len(self.displayedName.encode()),
                                      self.displayedName.encode())
            fh.write(toBeWritten)
            fh.write(self.MAGIC)
            geo = self.mainWindow.geometry()
            toBeWritten = struct.pack("<4h", geo.x(), geo.y(), geo.width(), geo.height())
            fh.write(toBeWritten)
            toBeWritten = struct.pack("<h", self.volume)
            fh.write(toBeWritten)
            toBeWritten = struct.pack("<h", self.songList.width())
            fh.write(toBeWritten)

    def load(self) -> [bool, tuple]:
        """Called on startup, loads view, geometry and volume saved on previous run."""
        try:
            with gzip.open(r"musicplayer\mpdata", "rb") as fh:
                if not fh.read(2) == self.MAGIC:
                    return False
                length = fh.read(2)
                length = struct.unpack("<h", length)[0]
                displayedType = fh.read(length)
                displayedType = struct.unpack(f"<{length}s", displayedType)[0].decode("utf8")
                if displayedType in ["artist", "album", "playlist"]:
                    self.displayedType = displayedType
                if not fh.read(2) == self.MAGIC:
                    return False
                length = fh.read(2)
                length = struct.unpack("<h", length)[0]
                displayedName = fh.read(length)
                displayedName = struct.unpack(f"<{length}s", displayedName)[0].decode("utf8")
                if not fh.read(2) == self.MAGIC:
                    return False
                self.displayedName = displayedName
                variables = []
                for n in range(6):
                    var = fh.read(2)
                    var = struct.unpack("<h", var)[0]
                    variables.append(var)
                x, y, width, height, volume, songListWidth = variables
                self.volume = volume
                self.songListWidth = songListWidth
                return x, y, width, height
        except Exception:
            return False
