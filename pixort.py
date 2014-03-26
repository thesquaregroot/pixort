#!/usr/bin/python

# Picture Sorter
#
# Author:
#   Andrew Groot

# TODO:
#  Undo History
#  Handling large numbers of directories

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess
import shutil # for file operations
import sys
import os

BROWSER        = "chromium"
TRASH_LOCATION = "~/.local/share/Trash/files/"

class MoveButton(QPushButton):
    def __init__(self, path):
        QPushButton.__init__(self)
        self.path = path
    
    def mousePressEvent(self, event):
        self.emit(SIGNAL("clicked"), self.path)

class Pixort(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Pixort")
        self.setMinimumWidth(800)
        
        # config file
        try:
            f = open(os.path.expanduser("~/.pixortrc"), "r")
            
            # unsorted directory
            self.unsorted = os.path.expanduser(f.readline().strip())
            self.files = sorted([(os.path.expanduser(self.unsorted + i), i) \
                                    for i in os.listdir(self.unsorted) \
                                    if os.path.isfile(os.path.expanduser(self.unsorted + i))])
            self.file = self.files[0][0]     # get full path
            self.name = self.files.pop(0)[1] # get name and remove
            # new line
            f.readline()
            
            # get directories
            self.dirs = []
            f = [i.strip() for i in f.readlines()]
            while len(f) > 0:
                d = f.pop(0)
                files = []  # "files" is the set of directories within "d"
                while len(f) > 0:
                    if f[0] != "":
                        files.append(f.pop(0))
                    else:
                        # get rid of empty string
                        f.pop(0)
                        break
                # store dir/files
                self.dirs.append((d, files))
        except:
            print("ERROR: No ~/.pixortrc found.  Please create one to continue.")
            sys.exit()
        
        # undo history
        self.moved = []
        
        self.main_frame = QWidget()
        self.__create_main()
        
        self.setCentralWidget(self.main_frame)
        
        # set focus to name
        self.save_as.selectAll()
        self.save_as.setFocus()
    
    def __create_main(self):
        layout = QHBoxLayout()
        
        ### left column
        # picture display
        self.scene = QGraphicsScene()
        self.image = QPixmap(self.file)
        self.scene.addPixmap(self.image)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        
        self.__draw_image()
        
        self.img_box = QVBoxLayout()
        self.img_box.addWidget(self.view)
        
        # image info
        self.info_box = QGroupBox("Image Properties")
        info = QGridLayout()
        info.setVerticalSpacing(1)
        info.setHorizontalSpacing(8)
        
        self.file_name = QLabel()
        info.addWidget(QLabel("File Name: "), 0, 0)
        info.addWidget(self.file_name, 0, 1)
        
        self.dim = QLabel()
        info.addWidget(QLabel("Dimensions: "), 1, 0)
        info.addWidget(self.dim, 1, 1)
        
        self.browser = QPushButton("Open in Browser")
        self.connect(self.browser, SIGNAL("clicked()"), self.__browser)
        info.addWidget(self.browser, 0, 2, 2, 2)
        
        self.info_box.setLayout(info)
        self.img_box.addWidget(self.info_box)
        
        ### right column
        self.right = QWidget()
        self.right.setMaximumWidth(200)
        self.nav = QVBoxLayout()
        self.right.setLayout(self.nav)
        ## file name & extention
        self.save_as = QLineEdit(self.name[:self.name.find('.')])
        self.extention = QLabel(self.name[self.name.find('.'):])
        # arrange
        horiz = QHBoxLayout()
        horiz.addWidget(self.save_as)
        horiz.addWidget(self.extention)
        self.nav.addLayout(horiz)
        
        self.__update_info()

        # make buttons for each of the possible destination directories
        for d,files in sorted(self.dirs):
            group = QGroupBox(d)
            body = QVBoxLayout()
            for i in sorted(files):
                b = MoveButton(d + i)
                b.setText(i)
                self.connect(b, SIGNAL("clicked"), self.__move)
                body.addWidget(b)
            group.setLayout(body)
            self.nav.addWidget(group)
        
        ### Combine
        layout.addLayout(self.img_box)
        layout.addWidget(self.right)
        
        self.main_frame.setLayout(layout)
    
    def __draw_image(self):
        # load image
        self.image.load(self.file)
        self.scene.clear()
        self.scene.addPixmap(self.image)
        self.scene.setSceneRect(0.0, 0.0, float(self.image.width()), float(self.image.height()))
    
    def __update_info(self):
        self.file_name.setText(self.file) 
        self.save_as.setText(self.name[:self.name.find('.')])
        self.extention.setText(self.name[self.name.find('.'):])
        self.save_as.selectAll()
        self.save_as.setFocus()
        self.dim.setText(str(self.image.width()) + "x" + str(self.image.height()))
    
    def __browser(self):
       subprocess.call([BROWSER, self.file])
    
    def __move(self, d):
        dest = os.path.expanduser(d + self.save_as.text() + self.extention.text())
        print("Moving " + self.file + "\n\t to " + dest)

        reply = QMessageBox.Yes
        if os.path.exists(dest):
            # file exists, check for overwrite
            reply = QMessageBox.question(self, 'Warning!', 'Destination file already exists, overwrite?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # move file
            shutil.move(self.file, dest)
            # save file for undoing
            self.moved.insert(0, (self.file, self.name, dest) )
            # get next file
            self.file = self.files[0][0]     # get full path
            self.name = self.files.pop(0)[1] # get name and remove
            self.__draw_image()
            self.__update_info()
    
    def __undo(self, d):
        src = self.moved[0][0]      # get source location
        name = self.move[0][1]      # get orignal name
        curr = self.moved.pop(0)[2] # get current location
        # move back and reset
        shutil.move(curr, src)
        self.files.insert(0, (self.file, self.name) )
        self.file = src
        self.name = name
        self.__draw_image()
        self.__update_info()
    
    def __delete(self, d):
        self.__move(TRASH_LOCATION)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Pixort()
    window.show()
    app.exec_()
    sys.exit()

