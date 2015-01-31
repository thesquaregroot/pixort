
from .MoveButton import MoveButton
from pixort.config import Configuration
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import subprocess # for opening browser
import traceback # for debugging stack traces
import shutil # for file operations
import sys
import os

class PixortWindow(QMainWindow):
    def __debug(self, msg, error = None):
        if error is None:
            print("[DEBUG]> %s" % msg)
        else:
            print("[ERROR]> %s: %s" % (msg, error))
            traceback.print_exc()

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle(Configuration.PROGRAM_TITLE)
        self.setMinimumWidth(800)
        
        # config file
        try:
            self.config = Configuration()
            # get list of normal files within unsorted directory
            self.__load_unsorted_files()
            first_file = self.__get_next_file()
            self.current_file = first_file[0]
            self.current_name = first_file[1]
        except FileNotFoundError as e:
            self.__debug("Could not find configuration.", e)
            QMessageBox.critical(self, 'Create %s' % self.config.get_config_path(), 'No %s found.  Please create one to continue.' % self.config.get_config_path())
            sys.exit()
        except Exception as e:
            self.__debug("Could not load configuration.", e)
            QMessageBox.critical(self, 'Invalid configuration', 'Invalid pixortrc.')
            sys.exit()
        
        # undo history
        self.move_history = []
        # build gui
        self.main_frame = QWidget()
        self.__create_main()
        self.setCentralWidget(self.main_frame)
        # set focus to editable file name text box
        self.save_as.selectAll()
        self.save_as.setFocus()
    
    def __create_main(self):
        layout = QHBoxLayout()
        
        ### left column
        # picture display
        self.scene = QGraphicsScene()
        self.image = QPixmap(self.current_file)
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
        ## file name & extension
        self.save_as = QLineEdit(self.current_name[:self.current_name.find('.')])
        self.extention = QLabel(self.current_name[self.current_name.find('.'):])
        # arrange
        horiz = QHBoxLayout()
        horiz.addWidget(self.save_as)
        horiz.addWidget(self.extention)
        self.nav.addLayout(horiz)
        
        self.__update_info()
        
        # make buttons for each of the possible destination directories
        for dest_dir,subdirs in sorted(self.config.get_destination_directories()):
            group = QGroupBox(dest_dir)
            body = QVBoxLayout()
            for subdir in sorted(subdirs):
                button = MoveButton(dest_dir + subdir)
                button.setText(subdir)
                self.connect(button, SIGNAL("clicked"), self.__move)
                body.addWidget(button)
            group.setLayout(body)
            self.nav.addWidget(group)
        
        ### Combine
        layout.addLayout(self.img_box)
        layout.addWidget(self.right)
        
        self.main_frame.setLayout(layout)
    
    def __draw_image(self):
        # load image
        self.image.load(self.current_file)
        self.scene.clear()
        self.scene.addPixmap(self.image)
        self.scene.setSceneRect(0.0, 0.0, float(self.image.width()), float(self.image.height()))
    
    def __update_info(self):
        self.file_name.setText(self.current_file)
        self.save_as.setText(self.current_name[:self.current_name.find('.')])
        self.extention.setText(self.current_name[self.current_name.find('.'):])
        self.save_as.selectAll()
        self.save_as.setFocus()
        self.dim.setText(str(self.image.width()) + "x" + str(self.image.height()))
    
    def __browser(self):
       subprocess.call([self.config.get_browser_path(), self.current_file])
    
    def __move(self, d):
        dest_dir = os.path.expanduser(d)
        if not os.path.isdir(dest_dir):
            QMessageBox.warning(self, 'Invalid directory.', dest_dir + ' is not a valid directory.')
            return
        
        dest = dest_dir + str(self.save_as.text() + self.extention.text())
        print("Moving " + self.current_file + "\n\t to " + dest)
        
        reply = QMessageBox.Yes
        if os.path.exists(dest):
            # file exists, check for overwrite
            reply = QMessageBox.question(self, 'Warning!', 'Destination file already exists, overwrite?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # move file
            shutil.move(self.current_file, dest)
            # save file for undoing
            self.move_history.insert(0, (self.current_file, self.current_name, dest) )
            # get next file
            next_file = self.__get_next_file(self)
            self.current_file = next_file[0] # get full path
            self.current_name = next_file[1] # get name
            self.__draw_image()
            self.__update_info()

    def __load_unsorted_files(self):
        unsorted_directory = self.config.get_unsorted_directory()
        self.files = sorted([(os.path.expanduser(unsorted_directory + file), file) \
                                for file in os.listdir(unsorted_directory) \
                                if os.path.isfile(os.path.expanduser(unsorted_directory + file))])

    def __get_next_file(self):
        return self.files.pop(0)
    
    def __put_back_file(self, path, name):
        self.files.insert(0, (path, name))
    
    def __undo(self, d):
        prev_file = self.move_history.pop(0)
        src     = prev_file[0] # get source location
        name    = prev_file[1] # get original name
        curr    = prev_file[2] # get current location
        # move back and reset
        shutil.move(curr, src)
        self.__put_back_file(self, self.current_file, self.current_name)
        self.current_file = src
        self.current_name = name
        self.__draw_image()
        self.__update_info()
    
    def __delete(self):
        self.__move(self.config.get_trash_path())

