
from PyQt4.QtGui import QApplication
from pixort.ui import PixortWindow
import sys

"""
Starts pixort as a QApplication.
"""
def exec():
    app = QApplication(sys.argv)
    window = PixortWindow()
    window.show()
    # run app, get return value
    exitVal = app.exec_()
    # clean up memory and return
    app.deleteLater()
    return exitVal

