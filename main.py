from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QAudio, QMediaContent
from musicplayer import gui, library

ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)


class Control:
    """A class that handles the logic behind the program by manipulating the GUI classes
    and calling their methods in response to received signals."""

    def __init__(self, screens: list) -> None:
        self.player = QMediaPlayer()
        self.player.setAudioRole(QAudio.MusicRole)
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.mainWindow = gui.MainWindow(self, screens)
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

        self.connections = [self.player.currentMediaChanged.connect(self.updateCurrentSong),
                            self.player.durationChanged.connect(self.updateSongProgressRange),
                            self.player.stateChanged.connect(self.playerStatusChanged),
                            self.bottomBox.previousButton.click.connect(self.playlist.previous),
                            self.bottomBox.repeatButton.click.connect(self.repeatButtonClick),
                            self.bottomBox.stopButton.click.connect(self.stopButtonClick),
                            self.bottomBox.playButton.click.connect(self.playButtonClick),
                            self.bottomBox.randomButton.click.connect(self.randomButtonClick),
                            self.bottomBox.nextButton.click.connect(self.playlist.next),
                            self.bottomBox.muteButton.click.connect(self.mute),
                            self.bottomBox.songProgress.sliderMoved.connect(self.songProgressMove),
                            self.bottomBox.volumeControl.sliderMoved.connect(self.volumeChange)]

        self.volumeChange(self.volume)
        self.bottomBox.volumeControl.setValue(self.volume)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateSongProgress)
        self.timer.start()

        self.setUpTimer = QTimer()
        self.setUpTimer.setInterval(20)
        self.setUpTimer.setSingleShot(True)
        self.setUpTimer.timeout.connect(self.updateView)
        self.setUpTimer.start()

    def updateView(self) -> None:
        """Called after the GUI is created to provide user with a feedback
        that the program is running in case a larger amount of songs will be added
        when the Library class is initialized."""
        # TODO add a tooltip that will notify the user larger amount of songs is being loaded
        #  (freezes the program as the execution moves to the Library class.)
        #  Also try threading to prevent the block.
        self.library = library.Library()
        self.mainBox.updateView(self.library)
        self.setUpTimer.deleteLater()
        self.setUpTimer = None

    def updateCurrentSong(self) -> None:
        """Update all areas that may display information about the currently
        playing song - SongList, Now Playing tab, BottomBox"""
        media = self.player.currentMedia()
        self.currentSong = media.request().url().toLocalFile().replace("/", "\\")
        if self.currentSong in self.library.library:
            self.songList.updateActiveSong(self.currentSong)
            self.mainBox.updateActiveSong(self.currentSong)
            songEntry = self.library.library[self.currentSong]
            self.bottomBox.updateSongInfo(f"{songEntry[ARTIST]} - {songEntry[NAME]}")

    def updateSongProgressRange(self) -> None:
        """Updates the range of the slider that represents the song position."""
        self.bottomBox.updateSongProgressRange(self.player.duration())

    def playerStatusChanged(self) -> None:
        """Used to properly update the player look after the current playlist has finished."""
        pass
        index = self.playlist.currentIndex()
        if index == -1:
            self.stopButtonClick()

    def getArtist(self, artist: str) -> None:
        """Retrieves the songs for a given artist and passes the resulting list
        to the SongList class."""
        self.songList.updateSongList(self.library.getSongsForArtist(artist),
                                     self.library.library,
                                     self.currentSong)

    def getAlbum(self, album: str) -> None:
        """Same functionality for albums."""
        self.songList.updateSongList(self.library.getSongsForAlbum(album),
                                     self.library.library,
                                     self.currentSong)

    def getPlaylist(self, playlist: str) -> None:
        """Same functionality for playlists."""
        self.songList.updateSongList(self.library.getSongsForPlaylist(playlist),
                                     self.library.library,
                                     self.currentSong)

    def playPlaylist(self, song: str = None) -> None:
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
        self.player.setPlaylist(self.playlist)
        self.player.play()
        if index > 0:
            self.playlist.setCurrentIndex(index)
        self.playing = True
        self.bottomBox.playButton.updatePictures(gui.pausePixmap, gui.pauseHoverPixmap, False)
        self.mainBox.setNowPlayingArea(self.library)
        self.mainBox.updateActiveSong(self.currentSong)

    def playFromNowPlaying(self, song: str) -> None:
        """Called when user double-clicks on a song in the Now Playing tab."""
        for n in range(self.playlist.mediaCount()):
            media = self.playlist.media(n)
            if song == media.request().url().toLocalFile().replace("/", "\\"):
                self.playlist.setCurrentIndex(n)
                return

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
            self.songList.updateSongList([], [], "")
            self.player.stop()
            self.playlist.clear()
            self.bottomBox.updateSongInfo("")
            self.songList.previousActive = None
            self.mainBox.nowPlayingSong = None
            self.playing = False
            self.bottomBox.updatePlayButton(self.playing, False)

    def playButtonClick(self) -> None:
        if not self.playing:
            self.playing = True
            self.player.play()
        else:
            self.playing = False
            self.player.pause()
        self.bottomBox.updatePlayButton(self.playing)
        self.mainBox.updateActiveSong(self.currentSong)
        self.songList.updateActiveSong(self.currentSong)

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
        if self.songList.previousActive is not None:
            self.songList.previousActive.clear()
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
            else:
                self.bottomBox.updateSongProgress(0)

    def close(self):
        self.player.stop()
        # TODO
        # for connection in self.connections:
        #     disconnect
        # save current state
        self.mainWindow.close()