import os
import sys
from PyQt5.QtWidgets import QApplication
from musicplayer.main import Control

if __name__ == "__main__":
    if sys.platform == "win32":
        os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
    app = QApplication(sys.argv)
    control = Control(app.screens())
    app.exec()
