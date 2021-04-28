from typing import Any

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap, QKeyEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QSlider

from musicplayer.gui import ClickLabel
from musicplayer.gui.mainArea import SongList

ARTIST, ALBUM, YEAR, NAME, TRACK, DISC, LENGTH = range(7)


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

location = r"musicplayer\resources\\"

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


class MediaButton(QWidget):
    """A class that provides the responses to the user's clicks
    as well as visual feedback."""

    click = pyqtSignal()

    def __init__(self, size: tuple, picture: str, hoverPicture: str) -> None:
        super().__init__()
        self.setFixedSize(*size)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap(picture))
        self.normalPicture = picture
        self.hoverPicture = hoverPicture
        self.layout.addWidget(self.label)

    def mousePressEvent(self, ignore: Any) -> None:
        self.click.emit()

    def enterEvent(self, ignore: Any) -> None:
        self.label.setPixmap(QPixmap(self.hoverPicture))

    def leaveEvent(self, ignore: Any) -> None:
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        newPosition = int(event.pos().x() / self.geometry().width() * self.maximum())
        self.setSliderPosition(newPosition)
        self.sliderMoved.emit(newPosition)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Right:
            newPosition = self.sliderPosition() + (self.maximum() // 100)
            self.setSliderPosition(newPosition)
            self.sliderMoved.emit(newPosition)
        elif event.key() == Qt.Key_Left:
            newPosition = self.sliderPosition() - (self.maximum() // 100)
            self.setSliderPosition(newPosition)
            self.sliderMoved.emit(newPosition)


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
        self.volumeControl.setMinimum(5)
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
