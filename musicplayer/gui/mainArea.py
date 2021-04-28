from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QResizeEvent
from PyQt5.QtWidgets import (QFrame, QWidget, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QStackedWidget, QScrollArea, QScrollBar,
                             QLayout, QSizePolicy, QGridLayout)

from musicplayer.gui import Line, FlowLayout, MediaWidget, SongWidget, clearLayout

ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)

scrollBarStyle = ("QScrollBar:vertical {"
                  "    background-color: #141414;"
                  "    width: 7px;"
                  "}"
                  "QScrollBar::handle:vertical {"
                  "    background-color: #303030;"
                  "    min-height: 5px;"
                  "    border-radius: 4px;"
                  "}"
                  "QScrollBar::handle:hover {"
                  "    background-color: #454545;"
                  "    width: 25px;"
                  "}"
                  "QScrollBar::add-line:vertical {"
                  "    background-color: #141414;"
                  "    height: 10px;"
                  "    width: 7px;"
                  "    subcontrol-position: bottom;"
                  "    subcontrol-origin: margin;"
                  "    margin: 3px 0px 3px 0px;"
                  "}"
                  "QScrollBar::sub-line:vertical {"
                  "    background-color: #141414;"
                  "    height: 10px;"
                  "    width: 7px;"
                  "    subcontrol-position: top;"
                  "    subcontrol-origin: margin;"
                  "    margin: 3px 0px 3px 0px;"
                  "}"
                  "QScrollBar::add-page:vertical,"
                  "QScrollBar::sub-page:vertical {"
                  "    background-color: none;"
                  "}"
                  "QScrollBar::sub-line:vertical:hover,"
                  "QScrollBar::sub-line:vertical:on {"
                  "    subcontrol-position: top;"
                  "    subcontrol-origin: margin;"
                  "}"
                  "QScrollBar::add-line:vertical:hover,"
                  "QScrollBar::add-line:vertical:on {"
                  "    subcontrol-position: bottom;"
                  "    subcontrol-origin: margin;"
                  "}"
                  )

location = r"musicplayer\resources\\"

artistPixmap = location + "artist.png"
albumPixmap = location + "album.png"
playlistPixmap = location + "playlist.png"
activePixmap = location + "active.png"


class UpperBox(QWidget):
    """A container for the layouts providing access to artists and albums and the layout providing
    access to songs for the selected artist/album/playlist."""

    def __init__(self, control, window) -> None:
        super().__init__()
        self.control = control
        self.window = window
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 5, 0)
        self.setLayout(self.layout)
        self.songList = SongList(self.control, self)
        self.mainBox = MainBox(self.control, self)
        self.line = Line(self.window, QFrame.VLine, self.mainBox, self.songList)
        self.layout.addWidget(self.mainBox, stretch=1)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.songList)


class MainBox(QWidget):
    """A class responsible for organizing artist/album/playlist/now playing tabs
    and generally access to library contents."""

    def __init__(self, control, upperBox: UpperBox) -> None:
        super().__init__()
        self.control = control
        self.songListArea = upperBox.songList
        self.layout = QVBoxLayout()
        self.buttons = QWidget()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.buttons)
        self.buttonLayout = QHBoxLayout()
        self.labels = {"Artists": QPushButton(), "Albums": QPushButton(),
                       "Playlists": QPushButton(), "Now Playing": QPushButton()}
        self.setButtons()
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(line)
        self.mainArea = QStackedWidget()
        self.layout.addWidget(self.mainArea)

        self.artistScrollArea = QScrollArea()
        self.artistScrollBar = QScrollBar(Qt.Vertical, self.artistScrollArea)
        self.artistArea = QWidget()
        self.artistLayout = FlowLayout()
        self.artistScrollBar.setStyleSheet(scrollBarStyle)
        self.artistScrollArea.setVerticalScrollBar(self.artistScrollBar)
        self.artistArea.setLayout(self.artistLayout)
        self.artistScrollArea.setWidget(self.artistArea)
        self.mainArea.insertWidget(0, self.artistScrollArea)

        self.albumScrollArea = QScrollArea()
        self.albumScrollBar = QScrollBar(Qt.Vertical, self.albumScrollArea)
        self.albumScrollBar.setStyleSheet(scrollBarStyle)
        self.albumScrollArea.setVerticalScrollBar(self.albumScrollBar)
        self.albumArea = QWidget()
        self.albumLayout = FlowLayout()
        self.albumArea.setLayout(self.albumLayout)
        self.albumScrollArea.setWidget(self.albumArea)
        self.mainArea.insertWidget(1, self.albumScrollArea)

        self.playlistScrollArea = QScrollArea()
        self.playlistScrollBar = QScrollBar(Qt.Vertical, self.playlistScrollArea)
        self.playlistScrollBar.setStyleSheet(scrollBarStyle)
        self.playlistScrollArea.setVerticalScrollBar(self.playlistScrollBar)
        self.playlistScrollArea.setFrameShape(QFrame.NoFrame)
        self.playlistArea = QWidget()
        self.playlistLayout = FlowLayout()
        self.playlistArea.setLayout(self.playlistLayout)
        self.playlistScrollArea.setWidget(self.playlistArea)
        self.mainArea.insertWidget(2, self.playlistScrollArea)

        self.nowPlayingScrollArea = QScrollArea()
        self.nowPlayingScrollBar = QScrollBar(Qt.Vertical, self.nowPlayingScrollArea)
        self.nowPlayingScrollBar.setStyleSheet(scrollBarStyle)
        self.nowPlayingScrollArea.setVerticalScrollBar(self.nowPlayingScrollBar)
        self.nowPlayingArea = QWidget()
        self.nowPlayingLayout = QGridLayout()
        self.nowPlayingLayout.setAlignment(Qt.AlignTop)
        self.nowPlayingLayout.setHorizontalSpacing(0)
        self.nowPlayingLayout.setVerticalSpacing(0)
        self.nowPlayingLayout.setContentsMargins(0, 0, 0, 0)
        self.nowPlayingLayout.setColumnStretch(0, 1)
        self.nowPlayingLayout.setColumnStretch(1, 1)
        self.nowPlayingLayout.setColumnStretch(3, 2)
        self.nowPlayingArea.setLayout(self.nowPlayingLayout)
        self.nowPlayingScrollArea.setWidget(self.nowPlayingArea)
        self.mainArea.insertWidget(3, self.nowPlayingScrollArea)

        self.nowPlayingSong = None
        self.garbageProtector = {}

        self.pixmaps = {"artist": artistPixmap,
                        "album": albumPixmap,
                        "playlist": playlistPixmap}

        self.activePixmaps = []
        self.index = 0
        for n in range(1, 8):
            self.activePixmaps.append(QPixmap(f"{location}active{n}.png"))

        for scrollArea in [self.artistScrollArea, self.albumScrollArea,
                           self.playlistScrollArea, self.nowPlayingScrollArea]:
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scrollArea.setWidgetResizable(True)
            scrollArea.setFrameShape(QFrame.NoFrame)

    def setButtons(self) -> None:
        """Creates buttons for switching between tabs."""
        self.buttonLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.buttonLayout.setSpacing(20)
        self.buttons.setLayout(self.buttonLayout)
        self.buttons.setFixedHeight(45)
        for label in self.labels:
            button = self.labels[label]
            button.setText(label)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            button.setFont(font)
            button.setStyleSheet("color:#afafaf;"
                                 "text-align:top;"
                                 "border-style: none;"
                                 "background-color:#141414;")
            button.setFixedHeight(25)
            self.buttonLayout.addWidget(button)
        self.labels["Artists"].clicked.connect(lambda x: self.showArea(0))
        self.labels["Albums"].clicked.connect(lambda x: self.showArea(1))
        self.labels["Playlists"].clicked.connect(lambda x: self.showArea(2))
        self.labels["Now Playing"].clicked.connect(lambda x: self.showArea(3))

    def setAreas(self, library) -> None:
        """Called after the GUI has been shown, draws widgets for all
        artists/albums/playlists in the library."""
        self.setMainAreaArtists(library)
        self.setMainAreaAlbums(library)
        self.setMainAreaPlaylists(library)
        self.setNowPlayingArea(library)

    def updateView(self, library) -> None:
        areas = {self.artistLayout: library.artists,
                 self.albumLayout: library.albums,
                 self.playlistLayout: library.playlists}
        types = {self.artistLayout: "artist",
                 self.albumLayout: "album",
                 self.playlistLayout: "playlist"}
        for area in areas:
            fieldNames = []
            toBeRemoved = []
            for field in area.items:
                fieldNames.append(field.widget().name)
                if field.widget().name not in areas[area]:
                    toBeRemoved.append(field)
            if len(toBeRemoved):
                for field in toBeRemoved:
                    area.removeItem(field)
                    field.widget().hide()
                    field.widget().deleteLater()
            for libraryItem in areas[area]:
                if libraryItem not in fieldNames:
                    self.addItemToLayout(area, types[area], libraryItem)
                    fieldNames.append(libraryItem)

    def addItemToLayout(self, layout: QLayout, isType: str, name: str) -> None:
        item = MediaWidget(self.control, isType, name)
        item.setFixedSize(160, 195)
        itemLayout = QVBoxLayout()
        item.setLayout(itemLayout)
        label = QLabel()
        label.setFixedSize(150, 150)
        label.setPixmap(QPixmap(self.pixmaps[isType]))
        label.setScaledContents(True)
        itemLayout.addWidget(label)
        label = QLabel(name)
        label.setFixedWidth(150)
        label.setStyleSheet("color:#afafaf;"
                            "font-size: 12px;"
                            "font-weight: bold;")
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        itemLayout.addWidget(label)
        layout.addWidget(item)

    def setMainAreaArtists(self, library) -> None:
        clearLayout(self.artistLayout)
        if library is not None:
            for artist in library.artists:
                self.addItemToLayout(self.artistLayout, "artist", artist)

    def setMainAreaAlbums(self, library) -> None:
        clearLayout(self.albumLayout)
        if library is not None:
            for album in library.albums:
                self.addItemToLayout(self.albumLayout, "album", album)

    def setMainAreaPlaylists(self, library) -> None:
        clearLayout(self.playlistLayout)
        if library is not None:
            for playlist in library.playlists:
                self.addItemToLayout(self.playlistLayout, "playlist", playlist)

    def setNowPlayingArea(self, library, clearOnly: bool = False) -> None:
        clearLayout(self.nowPlayingLayout)
        self.garbageProtector = {}
        self.nowPlayingSong = None
        if library is not None:
            column = 0
            row = 0
            for fieldName in ["Artist", "Album",
                              "Track", "Title", "", "Length"]:
                field = QLabel(fieldName)
                field.setStyleSheet("QWidget {"
                                    "    color:#afafaf;"
                                    "    font-size: 15px;"
                                    "    font-weight: bold;"
                                    "    border-style: none none solid none;"
                                    "    border-width: 2px;"
                                    "    border-color: #afafaf;"
                                    "}")
                self.nowPlayingLayout.addWidget(field, row, column)
                column += 1
            row += 1
            if clearOnly:
                return
            for n in range(self.control.playlist.mediaCount()):
                media = self.control.playlist.media(n)
                song = media.request().url().toLocalFile().replace("/", "\\")
                if song in library.library:
                    column = 0
                    self.garbageProtector[song] = []
                    for field in [ARTIST, ALBUM, TRACK, NAME, "pixmap",  LENGTH]:
                        songWidget = SongWidget(self.control, song, True)
                        songWidget.setLayout(QHBoxLayout())
                        songWidget.setStyleSheet("QLabel {"
                                                 "    color:#afafaf;"
                                                 "    font-size: 12px;"
                                                 "    border-style: none none solid none;"
                                                 "    border-width: 0.5px;"
                                                 "    border-color: #3c3c3c;"
                                                 "}")
                        label = QLabel()
                        if field != "pixmap":
                            label.setText(library.library[song][field])
                            if field == LENGTH:
                                label.setAlignment(Qt.AlignRight)
                        else:
                            label.setFixedSize(15, 15)
                            label.setScaledContents(True)
                        songWidget.layout().addWidget(label)
                        songWidget.layout().setContentsMargins(0, 15, 0, 0)
                        self.garbageProtector[song].append(label)
                        self.nowPlayingLayout.addWidget(songWidget, row, column)
                        column += 1
                    row += 1

    def updateActiveSong(self, currentIndex: int) -> None:
        """Shows a small image on the currently playing song for visual feedback."""
        if self.nowPlayingSong is not None:
            self.nowPlayingSong.clear()
            self.nowPlayingSong = None
        if (item := self.nowPlayingLayout.itemAtPosition(currentIndex + 1, 4)) is not None:
            label = item.widget().layout().itemAt(0).widget()
            self.nowPlayingSong = label

    def activeSongPixmap(self) -> None:
        if self.nowPlayingSong is not None:
            self.nowPlayingSong.setPixmap(self.activePixmaps[self.index])
            if self.index < 6:
                self.index += 1
            else:
                self.index = 0

    def showArea(self, area: int) -> None:
        self.mainArea.setCurrentIndex(area)


class SongList(QWidget):
    """A class responsible for creating and updating the right-hand side panel
    that contains the songs for the currently selected artist/album/playlist."""

    def __init__(self, control, parentWidget: QWidget) -> None:
        super().__init__()
        self.setMaximumWidth(500)
        self.setMinimumWidth(300)
        self.parentWidget = parentWidget
        self.preferredWidth = None
        self.control = control
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 2, 0)
        self.setLayout(self.layout)

        self.buttonOrderBy = QPushButton(text="Year")
        self.buttonOrderBy.clicked.connect(self.orderBy)
        self.buttonOrderReverse = QPushButton(text=chr(0x25b2))
        self.buttonOrderReverse.clicked.connect(self.reverseOrder)
        self.buttons = QWidget()
        self.buttons.setStyleSheet("QPushButton {"
                                   "    background-color:#141414;"
                                   "    color:#afafaf;"
                                   "    border-style: none;"
                                   "    font-size: 17px;"
                                   "    font-weight: bold;"
                                   "    text-align: left;"
                                   "}")
        self.buttons.setLayout(QHBoxLayout())
        self.buttons.layout().setAlignment(Qt.AlignLeft)
        self.buttons.layout().setContentsMargins(5, 0, 5, 0)
        self.buttons.layout().addWidget(self.buttonOrderBy)
        self.buttons.layout().addWidget(self.buttonOrderReverse)
        self.layout.addWidget(self.buttons)

        self.scrollArea = QScrollArea()
        self.scrollBar = QScrollBar(Qt.Vertical, self.scrollArea)
        self.scrollBar.setStyleSheet(scrollBarStyle)
        self.scrollArea.setVerticalScrollBar(self.scrollBar)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.scrollArea)
        self.songArea = QWidget()
        self.scrollArea.setWidget(self.songArea)
        self.songLayout = QVBoxLayout()
        self.songLayout.setSpacing(0)
        self.songLayout.setAlignment(Qt.AlignTop)
        self.songArea.setLayout(self.songLayout)
        self.garbageProtector = {}  # Necessary for preventing C++ from deleting the objects
        self.nowPlayingSong = None
        self.displayedType = None
        self.activePixmaps = []
        self.index = 0
        for n in range(1, 8):
            self.activePixmaps.append(QPixmap(f"{location}active{n}.png"))

    def orderBy(self) -> None:
        text = self.buttonOrderBy.text()

        if self.displayedType == "artist":
            if text == "Album":
                self.buttonOrderBy.setText("Year")
            elif text == "Year":
                self.buttonOrderBy.setText("Album")

        elif self.displayedType == "playlist":
            if text == "Artist":
                self.buttonOrderBy.setText("Album")
            elif text == "Album":
                self.buttonOrderBy.setText("Year")
            elif text == "Year":
                self.buttonOrderBy.setText("Artist")

        self.control.getSongs(None, None)

    def validateSortingButtonText(self) -> None:
        text = self.buttonOrderBy.text()

        if self.displayedType == "album":
            self.buttonOrderBy.setText("Track number")

        elif self.displayedType == "artist":
            if text not in ["Album", "Year"]:
                self.buttonOrderBy.setText("Year")

        elif self.displayedType == "playlist":
            if text not in ["Artist", "Album", "Year"]:
                self.buttonOrderBy.setText("Artist")

    def reverseOrder(self):
        text = self.buttonOrderReverse.text()
        if text == chr(0x25b2):
            self.buttonOrderReverse.setText(chr(0x25bc))
        elif text == chr(0x25bc):
            self.buttonOrderReverse.setText(chr(0x25b2))
        self.control.getSongs(None, None)

    def updateSongList(self, songList: list, library, currentSong: str, isPlaylist: str, isType: str) -> None:
        """Clear and recreate the contents when user changes selection."""
        # TODO add context menus for album titles
        style = ("color:#afafaf;"
                 "font-size: 13px;")
        self.displayedType = isType
        currentAlbum = None
        nowPlayingIncluded = False
        clearLayout(self.songLayout)
        self.garbageProtector = {}
        for song in songList:
            albumName = f"{library[song][ALBUM]} ({library[song][YEAR]})"
            if albumName != currentAlbum:
                albumLabel = QLabel(albumName)
                albumLabel.setWordWrap(True)
                albumLabel.setStyleSheet(style + "font-weight: bold;font-size: 18px;")
                self.songLayout.addWidget(albumLabel)
                currentAlbum = f"{library[song][ALBUM]} ({library[song][YEAR]})"
            songName = QLabel(f"{library[song][TRACK]} - {library[song][NAME]}")
            songName.setAlignment(Qt.AlignLeft)
            songName.setStyleSheet(style)
            songName.setWordWrap(True)
            songLength = QLabel(library[song][LENGTH])
            songLength.setAlignment(Qt.AlignRight)
            songLength.setStyleSheet(style)
            songLength.setFixedWidth(33)
            songLabel = SongWidget(self.control, song, playlist=isPlaylist)
            songLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,
                                                QSizePolicy.Maximum,
                                                QSizePolicy.Label))
            songLabel.setStyleSheet("background-color:#141414;"
                                    "color:#afafaf;"
                                    "border-style: none;")
            playIcon = QLabel()
            playIcon.setFixedSize(10, 10)
            playIcon.setScaledContents(True)
            playIcon.setAlignment(Qt.AlignRight)
            if song == currentSong and self.control.player.state() > 0:
                self.nowPlayingSong = playIcon
                nowPlayingIncluded = True
            buttonLayout = QHBoxLayout()
            songLabel.setLayout(buttonLayout)

            buttonLayout.addWidget(songName)
            buttonLayout.addWidget(playIcon)
            buttonLayout.addWidget(songLength)
            self.garbageProtector[song] = playIcon
            self.songLayout.addWidget(songLabel)
        if not nowPlayingIncluded:
            self.nowPlayingSong = None
        self.validateSortingButtonText()

    def updateActiveSong(self, currentSong: str) -> None:
        """Shows a small image on the currently playing song for visual feedback."""
        if self.nowPlayingSong is not None:
            self.nowPlayingSong.clear()
            self.nowPlayingSong = None
        if currentSong in self.garbageProtector:
            self.nowPlayingSong = self.garbageProtector[currentSong]

    def activeSongPixmap(self) -> None:
        if self.nowPlayingSong is not None:
            self.nowPlayingSong.setPixmap(self.activePixmaps[self.index])
            if self.index < 6:
                self.index += 1
            else:
                self.index = 0

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.preferredWidth is not None:
            self.parentWidget.line.resizeWidgets(self.width() - self.preferredWidth)
