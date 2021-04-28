from typing import Any

from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import (QColor, QPalette, QCursor, QMouseEvent,
                         QPixmap, QResizeEvent, QCloseEvent, QKeyEvent)
from PyQt5.QtWidgets import (QFrame, QWidget, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QMenu, QVBoxLayout, QSizeGrip,
                             QScrollArea, QScrollBar, QFileDialog, QDialog)

from musicplayer.gui import ClickLabel
from musicplayer.gui.mainArea import UpperBox
from musicplayer.gui.bottom import BottomBox


ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)


minMaxButtonStyle = ("QPushButton:!hover {"
                     "    border-style: none;"
                     "}"
                     "QPushButton:hover {"
                     "    background-color: #252525;"
                     "}")

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
        self.mainWidget = MainWidget(self.control, self, screens)
        color = QPalette()
        color.setColor(QPalette.Background, QColor(20, 20, 20))
        self.setPalette(color)
        self.setCentralWidget(self.mainWidget)
        self.menuBar = self.mainWidget.menus
        self.setMinimumSize(1000, 800)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

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
        self.pressedForMenuBar = False
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Sets one of the directional variables to True, to allow
        ensuring that the window is only resized to/from that direction."""
        if event.pos().x() < 5:
            self.left = True
        elif event.pos().x() > self.width() - 5:
            self.right = True
        elif event.pos().y() < 5:
            if self.isMaximized():
                self.pressedForMenuBar = True
                self.menuBar.mousePressEvent(event)
            else:
                self.up = True
        elif event.pos().y() > self.height() - 5:
            self.down = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        rect = self.rect()
        self.grips[1].move(rect.right() - self.gripSize, 0)
        self.grips[2].move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.grips[3].move(0, rect.bottom() - self.gripSize)
        self.centralWidget().upperBox.line.resizeWidgets()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Checks if a directional variable, and only one at a time, is True,
        allows resizing only to/from that direction."""
        if self.isMaximized() or self.pressedForMenuBar:
            self.menuBar.mouseMoveEvent(event)
        else:
            if self.left and not any([self.right, self.up, self.down]):
                geo = self.geometry()
                geo.setLeft(geo.left() + event.pos().x())
                if geo.right() - geo.left() > self.minimumWidth():
                    self.setGeometry(geo)
            elif self.right and not any([self.left, self.up, self.down]):
                self.resize(event.pos().x(), self.height())
            elif self.up and not any([self.left, self.right, self.down]):
                geo = self.geometry()
                geo.setTop(geo.top() + event.pos().y())
                if geo.bottom() - geo.top() > self.minimumHeight():
                    self.setGeometry(geo)
            elif self.down and not any([self.left, self.right, self.up]):
                self.resize(self.width(), event.pos().y())

    def mouseReleaseEvent(self, event: Any) -> None:
        self.right = self.left = self.up = self.down = False
        self.pressedForMenuBar = False

    def closeEvent(self, event: QCloseEvent) -> None:
        self.control.close()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Space:
            self.control.playButtonClick(False)
        elif event.key() == Qt.Key_MediaNext:
            self.control.playlist.next()
        elif event.key() == Qt.Key_MediaPrevious:
            self.control.playlist.previous()
        elif event.key() in [Qt.Key_MediaPlay, Qt.Key_MediaPause, Qt.Key_MediaTogglePlayPause]:
            self.control.playButtonClick(False)
        elif event.key() == Qt.Key_MediaStop:
            self.control.stopButtonClick()


class MainWidget(QWidget):
    """A container for child widgets responsible for general layout."""

    def __init__(self, control, window: QMainWindow, screens: list) -> None:
        super().__init__()
        self.control = control
        self.window = window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.menus = MenuBar(self.window, self.control, screens)
        self.layout.addWidget(self.menus)
        self.upperBox = UpperBox(self.control, self.window)
        self.layout.addWidget(self.upperBox)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(line)
        self.bottomBox = BottomBox(self.parent, self.upperBox.songList)
        self.layout.addWidget(self.bottomBox)


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


class Icon(QLabel):
    """A QLabel sub-class that serves as an icon to the gui and a menu button."""

    def __init__(self, window: QMainWindow, control, image: str) -> None:
        super().__init__(parent=window)
        self.window = window
        self.control = control
        self.setPixmap(QPixmap(image))
        self.setScaledContents(True)
        self.menu = QMenu()
        self.menu.setStyleSheet(menuStyle)
        self.menu.addAction("Add folder", self.addFolder)
        self.menu.addAction("Manage watched folders", self.manageFolders)
        self.menu.addSeparator()
        self.menu.addAction("Settings", self.showSettings)
        self.menu.addSeparator()
        self.menu.addAction("Help", self.showHelp)
        self.foldersDialog = None
        self.closeOnly = False

    def enterEvent(self, event: Any) -> None:
        if self.menu.isVisible():
            self.closeOnly = True
        else:
            self.closeOnly = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.closeOnly:
            position = self.pos()
            position.setY(position.y() + 30)
            position.setX(position.x() + 10)
            self.menu.move(self.mapToGlobal(position))
            self.menu.show()
            self.closeOnly = True

    def addFolder(self) -> None:
        if self.foldersDialog is None:
            self.foldersDialog = FoldersDialog(self.window, self, self.control)
        self.foldersDialog.addFolder()

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

        self.logo = Icon(self.window, self.control, logo)
        self.logo.setFixedSize(30, 30)
        self.layout.addWidget(self.logo)
        self.title = QLabel("My player")
        self.title.setAlignment(Qt.AlignRight)
        self.title.setStyleSheet("font-size:18pt")
        self.layout.addWidget(self.title)
        self.layout.setSpacing(0)
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
        buttonSize = 35

        self.closeButton = QPushButton(chr(0x1f5d9))
        self.closeButton.clicked.connect(self.window.close)
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
        if event.pos().y() < 5:
            self.pressedForParent = True
            self.window.mousePressEvent(event)
        else:
            self.start = self.mapToGlobal(event.pos())
            self.mousePressed = True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.pressedForParent:
            self.window.mouseReleaseEvent(event)
        self.mousePressed = self.pressedForParent = False

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
                        self.window.setGeometry(self.window.pos().x() + self.movement.x(),
                                                self.window.pos().y() + self.movement.y(),
                                                self.window.width(),
                                                self.window.height())
                        self.start = self.end

