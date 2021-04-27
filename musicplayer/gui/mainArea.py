from PyQt5.QtCore import QSize, Qt, QPoint, QRect, pyqtSignal, QEvent
from PyQt5.QtGui import (QFont, QMouseEvent, QPixmap, QResizeEvent,
                         QContextMenuEvent)
from PyQt5.QtWidgets import (QFrame, QWidget, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QMenu, QVBoxLayout, QStackedWidget,
                             QScrollArea, QScrollBar, QLayout, QSizePolicy,
                             QDialog, QGridLayout, QLayoutItem, QLineEdit)

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


menuStyle = ("QMenu {"
             "    background-color: #202020;"
             "    color: #afafaf;"
             "    margin: 0px;"
             "}"
             "QMenu::item:selected {"
             "    background: #404040;"
             "}"
             "QMenu::separator {"
             "    height: 1px;"
             "    background: #303030;"
             "}")

location = r"musicplayer\resources\\"

artistPixmap = location + "artist.png"
albumPixmap = location + "album.png"
playlistPixmap = location + "playlist.png"
activePixmap = location + "active.png"


class Line(QWidget):
    """A separator that can be used to resize adjacent widgets while respecting
    the maximum/minimum size properties of the right-hand side widget. Sets
    the maximum width for the left-hand side widget while resizing in order
    to prevent it being wrapped under the right widget."""

    def __init__(self, window: QMainWindow, orientation: [QFrame.VLine, QFrame.HLine],
                 leftWidget: QWidget, rightWidget: QWidget) -> None:
        super().__init__()
        self.window = window
        self.line = QFrame()
        self.line.setFrameShape(orientation)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.line)
        self.leftWidget = leftWidget
        self.rightWidget = rightWidget

    def enterEvent(self, event: QEvent) -> None:
        self.setCursor(Qt.SizeHorCursor)

    def leaveEvent(self, event: QEvent) -> None:
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.resizeWidgets(event.pos().x())

    def resizeWidgets(self, move: int = None) -> None:
        """Sets geometry of self, and both adjacent widgets."""
        if move is None:
            move = self.rightWidget.geometry().width() + 5
        geo = self.geometry()
        if self.rightWidget.minimumWidth() < self.rightWidget.width() - move < self.rightWidget.maximumWidth():
            self.setGeometry(geo.x() + move, geo.y(), geo.width(), geo.height())

            leftGeo = self.leftWidget.geometry()
            self.leftWidget.setGeometry(QRect(leftGeo.x(), leftGeo.y(), leftGeo.width() + move, leftGeo.height()))
            rightGeo = self.rightWidget.geometry()
            self.rightWidget.preferredWidth = rightGeo.width() - move
            self.leftWidget.setMaximumWidth(self.window.width() - self.rightWidget.preferredWidth - 15)
            self.rightWidget.setGeometry(rightGeo.x() + move, rightGeo.y(), rightGeo.width() - move, rightGeo.height())


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


class FlowLayout(QLayout):
    """A Qt example class translated from C++ that is able to dynamically
    adjust widget placement based on available space. Original accessible here:
    https://doc.qt.io/qt-5/qtwidgets-layouts-flowlayout-example.html"""

    def __init__(self, parent=None, margin: int = 0, spacing: int = -1) -> None:
        super().__init__(parent)
        self.parent = parent
        self.margin = margin
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.spacing = spacing
        self.items = []

    def addItem(self, item: QLayoutItem) -> None:
        self.items.append(item)

    def itemAt(self, index: int) -> QLayoutItem:
        if index in range(0, len(self.items)):
            return self.items[index]

    def takeAt(self, index) -> QLayoutItem:
        if index in range(0, len(self.items)):
            return self.items.pop(index)

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.margin, 2 * self.margin)
        return size

    def setGeometry(self, rect: QRect) -> None:
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def doLayout(self, rect: QRect, forTestOnly: bool) -> int:
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.items:
            spaceX = self.spacing + item.widget().style().layoutSpacing(QSizePolicy.DefaultType,
                                                                        QSizePolicy.DefaultType,
                                                                        Qt.Horizontal)
            spaceY = self.spacing + item.widget().style().layoutSpacing(QSizePolicy.DefaultType,
                                                                        QSizePolicy.DefaultType,
                                                                        Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not forTestOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

    def count(self) -> int:
        return len(self.items)


class PlaylistDialog(QDialog):
    """QDialog sub-class to supplant a QInputDialog as it can't be styled to have a look
    that is coherent with the rest of the program."""

    def __init__(self, optionalText: str = "") -> None:
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Enter playlist name:"))
        self.edit = QLineEdit()
        self.edit.setMaxLength(30)
        self.edit.setFrame(False)
        self.edit.setText(optionalText)
        self.edit.returnPressed.connect(self.accept)
        self.layout().addWidget(self.edit)
        self.setStyleSheet("QDialog {"
                           "    background-color: #141414;"
                           "    border-style: solid;"
                           "    border-width: 3px;"
                           "    border-color: #303030;"
                           "}"
                           "QLabel {"
                           "    color: #afafaf;"
                           "    font-size: 12px;"
                           "    font-weight: bold;"
                           "}"
                           "QLineEdit {"
                           "    background-color: #303030;"
                           "    border-color: #000000;"
                           "    border-width: 2px;"
                           "    color: #afafaf;"
                           "    font-size: 12px;"
                           "}")
        self.text = None

    def accept(self) -> None:
        self.text = self.edit.text()
        super().accept()


class MediaWidget(QWidget):
    """A class with click and double-click events implemented to ensure proper reactions.
    Click displays songs for the particular artist, album, or playlist,
    double click puts these to the QMediaPlaylist and starts playback."""

    click = pyqtSignal(str, str)
    doubleClick = pyqtSignal()

    def __init__(self, control, isType: str, name: str) -> None:
        super().__init__()
        self.control = control
        self.name = name
        self.click.connect(self.control.getSongs)
        self.type = isType
        self.doubleClick.connect(self.control.playSongList)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.click.emit(self.type, self.name)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.doubleClick.emit()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()
        menu.setStyleSheet(menuStyle)
        menu.addAction("Play", self.play)
        menu.addAction("Add to now playing", self.addToNowPlaying)
        menu.addAction("Play next", self.addAfterCurrent)
        if self.type != "playlist":
            subMenu = QMenu("Add to playlist")
            subMenu.setStyleSheet(menuStyle)
            subMenu.addAction("New playlist", self.createNewPlaylist)
            subMenu.addSeparator()
            for playlist in self.control.library.playlists:
                subMenu.addAction(playlist, self.addToExistingPlaylist)
            menu.addMenu(subMenu)
        else:
            menu.addAction("Rename", self.renamePlaylist)
            menu.addAction("Delete", self.deletePlaylist)
        menu.move(event.globalX(), event.globalY())
        menu.exec()

    def play(self) -> None:
        self.control.playMediaWidget(self.type, self.name, True, False)

    def addToNowPlaying(self) -> None:
        self.control.playMediaWidget(self.type, self.name, False, False)

    def addAfterCurrent(self) -> None:
        self.control.playMediaWidget(self.type, self.name, False, True)

    def createNewPlaylist(self) -> None:
        inputDialog = PlaylistDialog()
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.createPlaylist(inputDialog.text)
            self.addToExistingPlaylist(inputDialog.text)

    def addToExistingPlaylist(self, playlistName: str = None) -> None:
        if playlistName is None:
            playlistName = self.sender().text()
        self.control.addToExistingPlaylist(playlistName, self.name, self.type)

    def renamePlaylist(self) -> None:
        inputDialog = PlaylistDialog(self.name)
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.renamePlaylist(self.name, inputDialog.text)

    def deletePlaylist(self) -> None:
        self.control.deletePlaylist(self.name)


def clearLayout(layout: QLayout) -> None:
    """Used to remove widgets from various layouts"""
    if layout.count():
        while (item := layout.takeAt(0)) is not None:
            layout.removeItem(item)
            item.widget().hide()
            item.widget().deleteLater()


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
        self.artistScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.artistScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        if library is not None:
            for artist in library.artists:
                self.addItemToLayout(self.artistLayout, "artist", artist)

    def setMainAreaAlbums(self, library) -> None:
        clearLayout(self.albumLayout)
        self.albumScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.albumScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        if library is not None:
            for album in library.albums:
                self.addItemToLayout(self.albumLayout, "album", album)

    def setMainAreaPlaylists(self, library) -> None:
        clearLayout(self.playlistLayout)
        self.playlistScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.playlistScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        if library is not None:
            for playlist in library.playlists:
                self.addItemToLayout(self.playlistLayout, "playlist", playlist)

    def setNowPlayingArea(self, library, clearOnly: bool = False) -> None:
        clearLayout(self.nowPlayingLayout)
        self.garbageProtector = {}
        self.nowPlayingSong = None
        self.nowPlayingScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nowPlayingScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
            if not clearOnly:
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


class SongWidget(QWidget):
    """A class representing a song in the Now Playing/right-hand side panel.
    Allows for double-clicking in either area to jump playback to the particular song.
    Argument isNowPlaying is used to determine the placement of the widget,
    isPlaylist is used to determine whether the widget represents a song in a playlist."""

    doubleClick = pyqtSignal(str)

    def __init__(self, control, song: str, isNowPlaying: bool = False, playlist: str = None) -> None:
        super().__init__()
        self.control = control
        self.song = song
        self.isNowPlaying = isNowPlaying
        self.playlist = playlist
        if isNowPlaying:
            self.doubleClick.connect(self.control.playFromNowPlaying)
        else:
            self.doubleClick.connect(self.control.playSongList)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.doubleClick.emit(self.song)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu()
        menu.setStyleSheet(menuStyle)
        if not self.isNowPlaying:
            menu.addAction("Play", self.play)
            menu.addAction("Add to now playing", self.addToNowPlaying)
        else:
            menu.addAction("Add to end of the queue", self.addToNowPlaying)
            menu.addAction("Remove from now playing", self.removeFromNowPlaying)
        menu.addAction("Play next", self.addAfterCurrent)
        if self.playlist is None:
            subMenu = QMenu("Add to playlist")
            subMenu.setStyleSheet(menuStyle)
            subMenu.addAction("New playlist", self.createNewPlaylist)
            subMenu.addSeparator()
            for playlist in self.control.library.playlists:
                subMenu.addAction(playlist, self.addToExistingPlaylist)
            menu.addMenu(subMenu)
        else:
            menu.addSeparator()
            menu.addAction("Remove from the playlist", self.removeFromPlaylist)
        menu.move(event.globalX(), event.globalY())
        menu.exec()

    def play(self) -> None:
        self.control.playSongList(self.song)

    def addToNowPlaying(self) -> None:
        self.control.playSongWidget(self.song)

    def removeFromNowPlaying(self) -> None:
        self.control.removeFromNowPlaying(self)

    def addAfterCurrent(self) -> None:
        self.control.playSongWidget(self.song, True)

    def createNewPlaylist(self) -> None:
        inputDialog = PlaylistDialog()
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.createPlaylist(inputDialog.text)
            self.addToExistingPlaylist(inputDialog.text)

    def addToExistingPlaylist(self, playlistName: str = None) -> None:
        if playlistName is None:
            playlistName = self.sender().text()
        self.control.addToExistingPlaylist(playlistName, self.song, None)

    def removeFromPlaylist(self) -> None:
        self.control.removeFromPlaylist(self.playlist, self.song)


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
