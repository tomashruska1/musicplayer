from PyQt5.QtCore import QSize, Qt, QPoint, QRect, pyqtSignal, QEvent
from PyQt5.QtGui import (QMouseEvent, QContextMenuEvent)
from PyQt5.QtWidgets import (QFrame, QWidget, QLabel, QMainWindow,
                             QMenu, QVBoxLayout, QLayout, QSizePolicy,
                             QDialog, QLayoutItem, QLineEdit)

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


def clearLayout(layout: QLayout) -> None:
    """Used to remove widgets from various layouts"""
    if layout.count():
        while (item := layout.takeAt(0)) is not None:
            layout.removeItem(item)
            item.widget().hide()
            item.widget().deleteLater()


class ClickLabel(QLabel):
    """A class that implements the ability to accepts mouse clicks on a QLabel."""

    click = pyqtSignal(QLabel)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.click.emit(self)


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
