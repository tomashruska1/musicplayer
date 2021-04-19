from PyQt5.QtCore import (QSize, Qt, QPoint, QTimer, QRect, pyqtSignal, QEvent)
from PyQt5.QtGui import (QColor, QFont, QPalette, QCursor,
                         QMouseEvent, QPixmap, QResizeEvent,
                         QContextMenuEvent)
from PyQt5.QtWidgets import (QFrame, QWidget, QApplication,
                             QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QMenu, QVBoxLayout,
                             QSizeGrip, QSlider, QStackedWidget,
                             QScrollArea, QScrollBar, QLayout,
                             QSizePolicy, QFileDialog, QDialog,
                             QGridLayout, QLayoutItem, QInputDialog)

ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)

minMaxButtonStyle = ("QPushButton:!hover {"
                     "    border-style: none;"
                     "}"
                     "QPushButton:hover {"
                     "    background-color: #252525;"
                     "}")

scrollBarStyle = ("QScrollBar:vertical {"
                  "    background: #141414;"
                  "    width: 5px;"
                  "}"
                  "QScrollBar::handle:vertical {"
                  "    background: #303030;"
                  "}"
                  "QScrollBar::add-line:vertical {"
                  "    background: #141414;"
                  "    subcontrol-position: bottom;"
                  "    subcontrol-origin: margin;"
                  "}"
                  "QScrollBar::sub-line:vertical {"
                  "    background: #141414;"
                  "    subcontrol-position: top;"
                  "    subcontrol-origin: margin;"
                  "}"
                  "QScrollBar::add-page:vertical,"
                  "QScrollBar::sub-page:vertical {"
                  "    background: none;"
                  "}"
                  )

sliderStyle = ("QSlider::groove:horizontal {"
               "    border: 1px solid #999999;"
               "    height: 8px;"
               "    background: #afafaf;"
               "    border-radius: 4px;"
               "    margin: 0px 0;"
               "}"
               "QSlider::handle:horizontal {"
               "    background: #afafaf;"
               "    border: 1px solid #5c5c5c;"
               "    width: 10px;"
               "    margin-top: -2px;"
               "    margin-bottom: -2px;"
               "    border-radius: 4px;"
               "}"
               "QSlider::handle:horizontal:hover {"
               "    width: 12px;"
               "    margin-top: -3px;"
               "    margin-bottom: -3px;"
               "    border-radius: 6px;"
               "}"
               "QSlider::sub-page:horizontal {"
               "    background: #00a8f3;"
               "    border-radius: 4px;"
               "}")

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

if __name__ == '__main__':
    location = r"resources\\"
else:
    location = r"musicplayer\resources\\"


artistPixmap = location + "artist.png"
albumPixmap = location + "album.png"
playlistPixmap = location + "playlist.png"
activePixmap = location + "active.png"
pausePixmap = location + "pause.png"
pauseHoverPixmap = location + "pause hover.png"
previousPixmap = location + "previous.png"
previousHoverPixmap = location + "previous hover.png"
repeatPixmap = location + "repeat.png"
repeatHoverPixmap = location + "repeat hover.png"
stopPixmap = location + "stop.png"
stopHoverPixmap = location + "stop hover.png"
playPixmap = location + "play.png"
playHoverPixmap = location + "play hover.png"
randomPixmap = location + "random.png"
randomHoverPixmap = location + "random hover.png"
nextPixmap = location + "next.png"
nextHoverPixmap = location + "next hover.png"
repeatSongHoverPixmap = location + "repeat song hover.png"
speakerVLowPixmap = location + "speaker very low.png"
speakerLowPixmap = location + "speaker low.png"
speakerMediumPixmap = location + "speaker medium.png"
speakerFullPixmap = location + "speaker full.png"
speakerMutePixmap = location + "speaker mute.png"
logo = location + "logo.png"


class MainWindow(QMainWindow):
    """Initializes the main window and provides logic for resizing
    because the standard frame is not used. Argument "control" is a custom class
    that only serves as a receiving end of signals and for calling appropriate methods
    in other classes as well as initializing of the GUI."""

    def __init__(self, control, screens: list) -> None:
        super().__init__(flags=Qt.FramelessWindowHint)
        self.setWindowTitle("My player")
        self.control = control
        self.mainWidget = MainWidget(self, self.control, screens)
        color = QPalette()
        color.setColor(QPalette.Background, QColor(20, 20, 20))
        self.setPalette(color)
        self.setCentralWidget(self.mainWidget)
        self.menuBar = self.mainWidget.bar()
        self.setMinimumSize(1200, 950)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.getMousePos)
        self.timer.start()

        self.move((screens[0].geometry().width() - self.width()) // 2,
                  (screens[0].geometry().height() - self.height()) // 2)

        self.right = self.left = self.up = self.down = False
        self.start = QPoint(0, 0)
        self.gripSize = 10
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.setStyleSheet("background-color: transparent")
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

    def getMousePos(self) -> None:
        if not self.isMaximized():
            if self.mapFromGlobal(QCursor.pos()).x() < 5:
                self.setCursor(Qt.SizeHorCursor)
            elif self.mapFromGlobal(QCursor.pos()).x() > self.width() - 5:
                self.setCursor(Qt.SizeHorCursor)
            elif self.mapFromGlobal(QCursor.pos()).y() < 5:
                self.setCursor(Qt.SizeVerCursor)
            elif self.mapFromGlobal(QCursor.pos()).y() > self.height() - 5:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, 0)
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # TODO add check for which side the mouse is at, only allow drag if near that side
        if not self.isMaximized():
            if event.pos().x() < 5 or self.left:
                self.left = True
                geo = self.geometry()
                geo.setLeft(geo.left() + event.pos().x())
                if geo.right() - geo.left() > self.minimumWidth():
                    self.setGeometry(geo)
            elif event.pos().x() > self.width() - 5 or self.right:
                self.right = True
                self.resize(event.pos().x(), self.height())
            elif 5 > event.pos().y() or self.up:
                self.up = True
                geo = self.geometry()
                geo.setTop(geo.top() + event.pos().y())
                if geo.bottom() - geo.top() > self.minimumHeight():
                    self.setGeometry(geo)
            elif event.pos().y() > self.height() - 5 or self.down:
                self.down = True
                self.resize(self.width(), event.pos().y())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.right = self.left = self.up = self.down = False


class MainWidget(QWidget):
    """A container for child widgets responsible for general layout."""

    def __init__(self, window: QMainWindow, control, screens: list) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.window = window
        self.control = control
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.menus = MenuBar(self.window, self.control, screens)
        self.layout.addWidget(self.menus)
        self.upperBox = UpperBox(self.control)
        self.layout.addWidget(self.upperBox)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(line)
        self.bottomBox = BottomBox(self.parent, self.upperBox.songList)
        self.layout.addWidget(self.bottomBox)

    def bar(self) -> QWidget:
        return self.menus


class FoldersDialog(QDialog):
    """A dialog window responsible for providing access to adding/removing folders for the library class."""

    removeSignal = pyqtSignal(str)

    def __init__(self, window: QMainWindow, parent: QLabel, control) -> None:
        super().__init__(parent=parent, flags=Qt.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModal)
        self.window = window
        self.parent = parent
        self.setFixedSize(500, 300)
        self.control = control
        self.activeDialog = None
        self.highlightedLabel = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scrollArea = QScrollArea()
        self.scrollBar = QScrollBar(Qt.Vertical, self.scrollArea)
        self.scrollBar.setStyleSheet(scrollBarStyle)
        self.scrollArea.setVerticalScrollBar(self.scrollBar)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.scrollArea)
        self.folders = QWidget()
        self.scrollArea.setWidget(self.folders)
        self.foldersLayout = QVBoxLayout()
        self.foldersLayout.setAlignment(Qt.AlignTop)
        self.folders.setLayout(self.foldersLayout)

        self.buttons = QWidget()
        self.buttonsLayout = QHBoxLayout()
        self.buttons.setLayout(self.buttonsLayout)
        self.layout.addWidget(self.buttons)

        self.add = QPushButton()
        self.add.setText("Add")
        self.add.clicked.connect(self.addFolder)
        self.remove = QPushButton()
        self.remove.setText("Remove")
        self.remove.clicked.connect(self.removeFolder)
        self.cancel = QPushButton()
        self.cancel.setText("Done")
        self.cancel.clicked.connect(self.reject)
        for button in [self.add, self.remove, self.cancel]:
            self.buttonsLayout.addWidget(button)

        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        self.layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet("QDialog {"
                           "    background-color: #141414;"
                           "    border-style: solid;"
                           "    border-width: 8px;"
                           "    border-color: #202020;"
                           "}"
                           "QLabel {"
                           "    background-color: #141414;"
                           "    font-size: 12px"
                           "}")
        self.move(self.mapToGlobal(self.window.pos()) + QPoint(150, 150))

        self.fileDialog = QFileDialog()
        self.fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        self.fileDialog.setFileMode(QFileDialog.Directory)
        self.fileDialog.setWindowModality(Qt.WindowModal)
        self.fileDialog.Options(QFileDialog.ShowDirsOnly)
        if hasattr(self.control, "library"):
            self.fileDialog.fileSelected.connect(self.control.addWatchedFolder)
            self.fileDialog.fileSelected.connect(self.updateFolders)
            self.removeSignal.connect(self.control.removeWatchedFolder)
            for folder in self.control.library.folders:
                field = ClickLabel()
                field.setText(folder)
                field.setFixedHeight(15)
                field.click.connect(self.highlightLabel)
                self.foldersLayout.addWidget(field)

    def highlightLabel(self, label: QLabel) -> None:
        if self.highlightedLabel is not None:
            self.highlightedLabel.setStyleSheet("QLabel {"
                                                "    background-color: #141414;"
                                                "}")
            if self.highlightedLabel == label:
                self.highlightedLabel = None
                return
        label.setStyleSheet("QLabel {"
                            "    background-color: #353535;"
                            "}")
        self.highlightedLabel = label

    def addFolder(self) -> None:
        self.fileDialog.show()

    def updateFolders(self, folder: str) -> None:
        field = ClickLabel()
        field.setText(folder.replace("/", "\\"))
        field.setFixedHeight(15)
        field.click.connect(self.highlightLabel)
        self.foldersLayout.addWidget(field)

    def removeFolder(self) -> None:
        if self.highlightedLabel is not None:
            self.foldersLayout.removeWidget(self.highlightedLabel)
            self.removeSignal.emit(self.highlightedLabel.text())
            self.highlightedLabel.deleteLater()
            self.highlightedLabel = None


class MenuLabel(QLabel):
    """A QLabel sub-class that serves as an icon to the gui and a menu button."""

    def __init__(self, window: QMainWindow, control, image: str) -> None:
        super().__init__(parent=window)
        self.window = window
        self.control = control
        self.setPixmap(QPixmap(image))
        self.setScaledContents(True)
        self.menu = QMenu()
        self.menu.setStyleSheet(menuStyle)
        self.menu.addAction("Open file", self.openFile)
        self.menu.addAction("Manage watched folders", self.manageFolders)
        self.menu.addSeparator()
        self.menu.addAction("Settings", self.showSettings)
        self.menu.addSeparator()
        self.menu.addAction("Help", self.showHelp)
        self.foldersDialog = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        position = self.pos()
        position.setY(position.y() + 30)
        position.setX(position.x() + 10)
        self.menu.move(self.mapToGlobal(position))
        self.menu.show()

    def openFile(self) -> None:
        # TODO
        pass

    def manageFolders(self) -> None:
        if self.foldersDialog is None:
            self.foldersDialog = FoldersDialog(self.window, self, self.control)
        self.foldersDialog.open()

    def showSettings(self) -> None:
        # TODO
        pass

    def showHelp(self) -> None:
        # TODO
        pass


class MenuBar(QWidget):
    """A class responsible for providing the logic of standard drag-and-move window behaviour."""

    def __init__(self, window: QMainWindow, control, screens: list) -> None:
        super().__init__(parent=window)
        self.window = window
        self.control = control
        self.screens = screens
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:#141414;"
                           "color:#afafaf;"
                           "font-weight:bold;")

        self.logo = MenuLabel(self.window, self.control, logo)
        self.logo.setFixedSize(30, 30)
        self.layout.addWidget(self.logo)
        self.title = QLabel("My player")
        self.title.setAlignment(Qt.AlignRight)
        self.title.setStyleSheet("color:#afafaf;"
                                 "font-size:18pt")
        self.layout.addWidget(self.title)
        self._createButtons()
        self.start = QPoint(0, 0)
        self.mousePressed = False
        self.pressedForParent = False
        self.screenTops = {}
        for screen in self.screens:
            self.screenTops[(screen.geometry().x(),
                             screen.geometry().x() + screen.geometry().width())] = screen.geometry().y()

    def _createButtons(self) -> None:
        self.buttonsLayout = QHBoxLayout()
        buttonSize = 30

        self.closeButton = QPushButton(chr(0x1f5d9))
        self.closeButton.clicked.connect(self.control.close)
        self.closeButton.setFixedSize(buttonSize, buttonSize)
        self.closeButton.setStyleSheet("QPushButton:!hover {"
                                       "    border-style: none;"
                                       "}"
                                       "QPushButton:hover {"
                                       "    background-color: #ba2d2d;"
                                       "}")

        self.minimizeButton = QPushButton(chr(0x1f5d5))
        self.minimizeButton.clicked.connect(self.window.showMinimized)
        self.minimizeButton.setFixedSize(buttonSize, buttonSize)
        self.minimizeButton.setStyleSheet(minMaxButtonStyle)

        self.maximizeButton = QPushButton(chr(0x1f5d6))
        self.maximizeButton.clicked.connect(self.maximizeButtonClick)
        self.maximizeButton.setFixedSize(buttonSize, buttonSize)
        self.maximizeButton.setStyleSheet(minMaxButtonStyle)

        self.layout.addLayout(self.buttonsLayout)

        self.buttonsLayout.addWidget(self.minimizeButton)
        self.buttonsLayout.addWidget(self.maximizeButton)
        self.buttonsLayout.addWidget(self.closeButton)
        self.buttonsLayout.setAlignment(Qt.AlignRight)

    def maximizeButtonClick(self) -> None:
        if not self.window.isMaximized():
            self.window.showMaximized()
            self.maximizeButton.setText(chr(0x1f5d7))
        elif self.window.isMaximized():
            self.maximizeButton.setText(chr(0x1f5d6))
            self.window.showNormal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if any([event.pos().y() < 5,
                not 5 < event.pos().x() < self.width() - 5,
                self.pressedForParent]):
            self.pressedForParent = True
            self.window.mousePressEvent(event)
        else:
            self.start = self.mapToGlobal(event.pos())
            self.mousePressed = True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mousePressed = self.pressedForParent = False
        self.window.mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.window.isMaximized():
            self.maximizeButton.setText(chr(0x1f5d6))
            self.window.showNormal()
        else:
            self.window.showMaximized()
            self.maximizeButton.setText(chr(0x1f5d7))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.pressedForParent:
            self.window.mouseMoveEvent(event)
        elif self.mousePressed:
            for screen in self.screenTops:
                if screen[0] < QCursor().pos().x() < screen[1]:
                    if QCursor().pos().y() == self.screenTops[screen]:
                        if not self.window.isMaximized():
                            self.window.showMaximized()
                            self.maximizeButton.setText(chr(0x1f5d7))
                    elif self.window.isMaximized():
                        self.maximizeButton.setText(chr(0x1f5d6))
                        self.window.showNormal()
                    else:
                        self.end = self.mapToGlobal(event.pos())
                        self.movement = self.end - self.start
                        self.window.setGeometry(self.mapToGlobal(self.movement).x(),
                                                self.mapToGlobal(self.movement).y(),
                                                self.window.width(),
                                                self.window.height())
                        self.start = self.end


class UpperBox(QWidget):
    """A container for the layouts providing access to artists and albums and the layout providing
    access to songs for the selected artist/album/playlist."""

    def __init__(self, control) -> None:
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.control = control
        self.songList = SongList(self.control)
        self.mainBox = MainBox(self.control, self)
        self.layout.addWidget(self.mainBox)
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        self.layout.addWidget(line)
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
            spaceX = self.spacing + item.widget().style().layoutSpacing(QSizePolicy.PushButton,
                                                                        QSizePolicy.PushButton,
                                                                        Qt.Horizontal)
            spaceY = self.spacing + item.widget().style().layoutSpacing(QSizePolicy.PushButton,
                                                                        QSizePolicy.PushButton,
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


class MediaWidget(QWidget):
    """A class with click and double-click events implemented to ensure proper reactions.
    Click displays songs for the particular artist, album, or playlist,
    double click puts these to the playlist and starts playback."""

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
        inputDialog = QInputDialog()
        inputDialog.setLabelText("Enter playlist name")
        inputDialog.setWindowFlags(Qt.FramelessWindowHint)
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.createPlaylist(inputDialog.textValue())
            self.addToExistingPlaylist(inputDialog.textValue())

    def addToExistingPlaylist(self, playlistName: str = None) -> None:
        if playlistName is None:
            playlistName = self.sender().text()
        self.control.addToExistingPlaylist(playlistName, self.name, self.type)

    def renamePlaylist(self) -> None:
        inputDialog = QInputDialog()
        inputDialog.setLabelText("Enter playlist name")
        inputDialog.setWindowFlags(Qt.FramelessWindowHint)
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.renamePlaylist(self.name, inputDialog.textValue())

    def deletePlaylist(self) -> None:
        self.control.deletePlaylist(self.name)


def clearLayout(layout):
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

        # TODO drag scrollbar to move the view
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
    Allows for double-clicking in either area to jump playback to the particular song."""

    doubleClick = pyqtSignal(str)

    def __init__(self, control, song: str, isNowPlaying: bool = False) -> None:
        super().__init__()
        self.control = control
        self.song = song
        self.isNowPlaying = isNowPlaying
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
        menu.addAction("Play next", self.addAfterCurrent)
        subMenu = QMenu("Add to playlist")
        subMenu.setStyleSheet(menuStyle)
        subMenu.addAction("New playlist", self.createNewPlaylist)
        subMenu.addSeparator()
        for playlist in self.control.library.playlists:
            subMenu.addAction(playlist, self.addToExistingPlaylist)
        menu.addMenu(subMenu)
        menu.move(event.globalX(), event.globalY())
        menu.exec()

    def play(self) -> None:
        self.control.playSongList(self.song)

    def addToNowPlaying(self) -> None:
        self.control.playSongWidget(self.song)

    def addAfterCurrent(self) -> None:
        self.control.playSongWidget(self.song, True)

    def createNewPlaylist(self) -> None:
        inputDialog = QInputDialog()
        inputDialog.setLabelText("Enter playlist name")
        inputDialog.setWindowFlags(Qt.FramelessWindowHint)
        inputDialog.exec()
        if inputDialog.result() == QDialog.Accepted:
            self.control.createPlaylist(inputDialog.textValue())
            self.addToExistingPlaylist(inputDialog.textValue())

    def addToExistingPlaylist(self, playlistName: str = None) -> None:
        if playlistName is None:
            playlistName = self.sender().text()
        self.control.addToExistingPlaylist(playlistName, self.song, None)


class SongList(QWidget):
    """A class responsible for creating and updating the right-hand side panel
    that contains the songs for the currently selected artist/album/playlist."""

    def __init__(self, control) -> None:
        super().__init__()
        # TODO song ordering
        # TODO resizing
        self.setFixedWidth(360)
        # self.setMaximumWidth(400)
        # self.setMinimumWidth(320)
        self.control = control
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 2, 0)
        self.setLayout(self.layout)
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
        self.activePixmaps = []
        self.index = 0
        for n in range(1, 8):
            self.activePixmaps.append(QPixmap(f"{location}active{n}.png"))

    def updateSongList(self, songList: list, library, currentSong: str) -> None:
        """Clear and recreate the contents when user changes selection."""
        style = ("color:#afafaf;"
                 "font-size: 13px;")
        currentAlbum = None
        nowPlayingIncluded = False
        clearLayout(self.songLayout)
        self.garbageProtector = {}
        for song in songList:
            albumName = library[song][ALBUM]
            if albumName != currentAlbum:
                albumLabel = QLabel(albumName)
                albumLabel.setWordWrap(True)
                albumLabel.setStyleSheet(style + "font-weight: bold;font-size: 18px;")
                self.songLayout.addWidget(albumLabel)
                currentAlbum = albumName
            songName = QLabel(f"{library[song][TRACK]} - {library[song][NAME]}")
            songName.setAlignment(Qt.AlignLeft)
            songName.setStyleSheet(style)
            songName.setWordWrap(True)
            songLength = QLabel(library[song][LENGTH])
            songLength.setAlignment(Qt.AlignRight)
            songLength.setStyleSheet(style)
            songLength.setFixedWidth(33)
            songLabel = SongWidget(self.control, song)
            songLabel.setFixedWidth(350)
            songLabel.setStyleSheet("background-color:#141414;"
                                    "color:#afafaf;"
                                    "border-style: none;")
            playIcon = QLabel()
            playIcon.setFixedSize(12, 12)
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


class MediaButton(QWidget):
    """A class that provides the responses to the user's clicks
    as well as visual feedback."""

    click = pyqtSignal()

    def __init__(self, size: tuple, picture: str, hoverPicture: str) -> None:
        super().__init__()
        self.setFixedSize(*size)
        self.setMouseTracking(True)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap(picture))
        self.normalPicture = picture
        self.hoverPicture = hoverPicture
        self.layout.addWidget(self.label)

    def mousePressEvent(self, ignore: QMouseEvent) -> None:
        self.click.emit()

    def enterEvent(self, event: QEvent) -> None:
        self.label.setPixmap(QPixmap(self.hoverPicture))

    def leaveEvent(self, ignore: QMouseEvent) -> None:
        self.label.setPixmap(QPixmap(self.normalPicture))

    def updatePictures(self, picture: str, hoverPicture: str, moveMouse: bool = True) -> None:
        self.normalPicture = picture
        self.hoverPicture = hoverPicture
        self.label.setPixmap(QPixmap(picture))
        if moveMouse:
            self.enterEvent(moveMouse)


class JumpSlider(QSlider):
    """A class that provides the ability to click anywhere on the slider's groove
    to move the handle (native Qt5 class does not support this behaviour)."""

    def __init__(self, orientation: Qt.Orientations) -> None:
        super().__init__(orientation)
        self.pressed = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.pressed = True
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.pressed:
            newPosition = int(event.pos().x() / self.geometry().width() * self.maximum())
            self.setSliderPosition(newPosition)
            self.sliderMoved.emit(newPosition)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.pressed = False


class ClickLabel(QLabel):
    """A class that implements the ability to accepts mouse clicks on a QLabel."""

    click = pyqtSignal(QLabel)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.click.emit(self)


class BottomBox(QWidget):
    """A class that provides media buttons such as play/pause/stop, a slider (JumpSlider)
    that represents the current position of the song as well as showing information
    about the currently playing song - title, artist, length."""

    def __init__(self, control, songListArea: SongList) -> None:
        super().__init__()
        style = "color: #afafaf; font-size: 14px; font-weight: bold;"
        self.control = control
        self.songListArea = songListArea
        self.setFixedHeight(140)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.setLayout(self.layout)

        self.songDetails = QLabel()
        self.songDetails.setStyleSheet(style)
        self.songDetails.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.songDetails)

        self.songTimeContainer = QWidget()
        self.songTimeLayout = QHBoxLayout()
        self.songTimeContainer.setLayout(self.songTimeLayout)
        self.songTimeLayout.setContentsMargins(0, 0, 0, 0)

        self.currentSongTime = QLabel("00:00")
        self.currentSongTime.setStyleSheet(style)
        self.currentSongTime.setAlignment(Qt.AlignLeft)
        self.songProgress = JumpSlider(Qt.Horizontal)
        self.songProgress.setMinimum(0)
        self.songProgress.setMaximum(1000)
        self.songProgress.setStyleSheet(sliderStyle)
        self.songTime = QLabel("00:00")
        self.songTime.setStyleSheet(style)
        self.songTime.setAlignment(Qt.AlignRight)
        self.songTimeLayout.addWidget(self.currentSongTime)
        self.songTimeLayout.addWidget(self.songProgress)
        self.songTimeLayout.addWidget(self.songTime)
        self.layout.addWidget(self.songTimeContainer)

        self.buttons = QWidget()
        self.layout.addWidget(self.buttons)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.buttonLayout = QHBoxLayout()

        fakeButtonForAlignment = QLabel()
        fakeButtonForAlignment.setFixedWidth(100)
        self.buttonLayout.addWidget(fakeButtonForAlignment)

        fakeButtonForAlignment = QLabel()
        fakeButtonForAlignment.setFixedWidth(20)
        self.buttonLayout.addWidget(fakeButtonForAlignment)

        self.buttonLayout.setAlignment(Qt.AlignCenter)
        self.buttons.setLayout(self.buttonLayout)
        self.previousButton = MediaButton((40, 40), previousPixmap,
                                          previousHoverPixmap)
        self.buttonLayout.addWidget(self.previousButton)

        self.repeatButton = MediaButton((40, 40), repeatPixmap,
                                        repeatHoverPixmap)
        self.buttonLayout.addWidget(self.repeatButton)

        self.stopButton = MediaButton((40, 40), stopPixmap,
                                      stopHoverPixmap)
        self.buttonLayout.addWidget(self.stopButton)

        self.playButton = MediaButton((50, 50), playPixmap,
                                      playHoverPixmap)
        self.buttonLayout.addWidget(self.playButton)

        self.randomButton = MediaButton((40, 40), randomPixmap,
                                        randomHoverPixmap)
        self.buttonLayout.addWidget(self.randomButton)

        self.nextButton = MediaButton((40, 40), nextPixmap,
                                      nextHoverPixmap)
        self.buttonLayout.addWidget(self.nextButton)
        fakeButtonForAlignment = QLabel()
        fakeButtonForAlignment.setFixedSize(40, 40)
        self.buttonLayout.addWidget(fakeButtonForAlignment)

        self.muteButton = ClickLabel()
        self.muteButton.setFixedSize(23, 23)
        self.muteButton.setScaledContents(True)

        self.buttonLayout.addWidget(self.muteButton)

        self.volumeControl = JumpSlider(Qt.Horizontal)
        self.volumeControl.setStyleSheet(sliderStyle)
        self.volumeControl.setMinimum(0)
        self.volumeControl.setMaximum(100)
        self.volumeControl.setFixedWidth(100)
        self.buttonLayout.addWidget(self.volumeControl)

    def updatePlayButton(self, playing: bool, move: bool = True) -> None:
        """Changes the look of the play button based on whether music is playing or not."""
        if playing:
            self.playButton.updatePictures(pausePixmap,
                                           pauseHoverPixmap,
                                           move)
        else:
            self.playButton.updatePictures(playPixmap,
                                           playHoverPixmap,
                                           move)

    def updateRepeatButton(self, repeat: int) -> None:
        """Changes the look of repeat button based on whether songs are repeated or not."""
        if repeat == 1:
            self.repeatButton.updatePictures(repeatHoverPixmap,
                                             repeatHoverPixmap)
        elif repeat == 2:
            self.repeatButton.updatePictures(repeatSongHoverPixmap,
                                             repeatSongHoverPixmap)
        elif repeat == 0:
            self.repeatButton.updatePictures(repeatPixmap,
                                             repeatHoverPixmap, False)

    def updateRandomButton(self, random: bool) -> None:
        """Similar as above."""
        if random:
            self.randomButton.updatePictures(randomHoverPixmap,
                                             randomHoverPixmap)
        else:
            self.randomButton.updatePictures(randomPixmap,
                                             randomHoverPixmap, False)

    def updateSongInfo(self, string: str) -> None:
        """Changes the text based on the current song details."""
        self.songDetails.setText(string)

    def updateSongProgressRange(self, duration: int) -> None:
        """Changes the range of the slider to the total duration of the current song.
        Is called on song change."""
        if duration == -1:
            duration = 0
        self.songProgress.setRange(0, duration)
        self.songProgress.setValue(0)
        length = duration // 1000
        self.songTime.setText(f"{length // 60:02}:{length % 60:02}")

    def updateSongProgress(self, value: int) -> None:
        """Periodically sets the slider position to reflect the song position."""
        self.songProgress.setValue(value)
        value //= 1000
        self.currentSongTime.setText(f"{value // 60:02}:{value % 60:02}")

    def updateVolumeBar(self, volume: int) -> None:
        """Updates the volume slider icon based on volume."""
        if volume <= 15:
            self.muteButton.setPixmap(QPixmap(speakerVLowPixmap))
        elif 15 < volume <= 40:
            self.muteButton.setPixmap(QPixmap(speakerLowPixmap))
        elif 40 < volume <= 70:
            self.muteButton.setPixmap(QPixmap(speakerMediumPixmap))
        elif 70 < volume:
            self.muteButton.setPixmap(QPixmap(speakerFullPixmap))

    def showMute(self) -> None:
        """Updates the volume slider icon to a "mute" picture."""
        self.muteButton.setPixmap(QPixmap(speakerMutePixmap))


if __name__ == '__main__':
    # non-functional showcase
    app = QApplication([])
    w = MainWindow(None, app.screens())
    w.show()
    app.exec()
