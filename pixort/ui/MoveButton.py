
from PyQt4.QtGui import *

"""
Represents a button that stores
a destination path.

When clicked, reports its path
a 'clicked' signal.
"""
class MoveButton(QPushButton):
    def __init__(self, path):
        QPushButton.__init__(self)
        self.path = path
    
    def mousePressEvent(self, event):
        self.emit(SIGNAL("clicked"), self.path)

