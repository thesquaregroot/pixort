
from .MoveButton import MoveButton
from pixort.config import Configuration
from pixort.util import ImageUtil
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
            # image util
            self.image_util = ImageUtil(self.config)
            # get list of normal files within unsorted directory
            self.__load_unsorted_files()
            first_file = self.__get_next_file()
            if first_file is None:
                QMessageBox.information(self, 'No images to sort.', 'There are no images to sort.')
                sys.exit()
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
        self.view = QGraphicsView(self.scene)
        self.image = QPixmap(self.current_file)
        self.scene.addPixmap(self.image)
        
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

        flags_box = QWidget()
        # animated flag
        self.animated_flag = QLabel("Animated File")
        self.animated_flag.setStyleSheet("QLabel { border: 2px solid purple; color: purple; text-align: center; }")
        # wallpaper flag
        self.wallpaper_flag = QLabel("Potential Wallpaper")
        self.wallpaper_flag.setStyleSheet("QLabel { border: 2px solid green; color: green; text-align: center; }")
        # shrunk flag
        self.shrunk_flag = QLabel("Shrunk Image")
        self.shrunk_flag.setStyleSheet("QLabel { border: 2px solid blue; color: blue; text-align: center; }")
        # layout
        flags = QHBoxLayout()
        flags.addWidget(self.animated_flag)
        flags.addWidget(self.wallpaper_flag)
        flags.addWidget(self.shrunk_flag)

        flags_box.setLayout(flags)
        info.addWidget(flags_box, 2, 0, 1, 4)
        
        self.info_box.setLayout(info)
        self.img_box.addWidget(self.info_box)

        ### right column
        self.right = QWidget()
        self.right.setMaximumWidth(250)
        self.nav = QVBoxLayout()
        self.nav.setAlignment(Qt.AlignTop)
        self.right.setLayout(self.nav)
        ## file name & extension
        self.save_as = QLineEdit(self.current_name[:self.current_name.find('.')])
        self.extention = QLabel(self.current_name[self.current_name.find('.'):])
        # arrange
        name_container = QHBoxLayout()
        name_container.addWidget(self.save_as)
        name_container.addWidget(self.extention)
        self.nav.addLayout(name_container)
        ## non-move actions
        action_container = QHBoxLayout()
        # undo
        self.undo_button = QPushButton("Undo \u21BA")
        self.undo_button.setStyleSheet("QPushButton { color: blue; }")
        self.connect(self.undo_button, SIGNAL("clicked()"), self.__undo)
        # delete
        self.delete_button = QPushButton("Delete \u232B")
        self.delete_button.setStyleSheet("QPushButton { color: red; }")
        self.connect(self.delete_button, SIGNAL("clicked()"), self.__delete)
        # set up
        action_container.addWidget(self.undo_button)
        action_container.addWidget(self.delete_button)
        self.nav.addLayout(action_container)

        ## separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.nav.addSpacing(10)
        self.nav.addWidget(separator)
        self.nav.addSpacing(10)
        
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
    
    def resizeEvent(self, event):
        super(PixortWindow, self).resizeEvent(event)
        self.__draw_image()
        self.__update_info()

    def __draw_image(self):
        # load image
        self.image.load(self.current_file)
        self.scene.clear()
        self.scene.setSceneRect(0.0, 0.0, float(self.image.width()), float(self.image.height()))
        self.scene.addPixmap(self.image)
        self.__fit_image()
    
    def __update_info(self):
        self.file_name.setText(self.current_file)
        self.save_as.setText(self.current_name[:self.current_name.find('.')])
        self.extention.setText(self.current_name[self.current_name.find('.'):])
        self.save_as.selectAll()
        self.save_as.setFocus()
        self.dim.setText(str(self.image.width()) + "x" + str(self.image.height()))
        # check for animated
        self.animated_flag.setVisible(self.image_util.is_animated(self.current_file))
        # check for wallpaper
        self.wallpaper_flag.setVisible(self.image_util.is_wallpaper(self.current_file))
        self.undo_button.setEnabled(len(self.move_history) > 0)
        # check for shrunk
        self.shrunk_flag.setVisible(self.__image_too_large())
    
    def __browser(self):
       subprocess.call([self.config.get_browser_path(), self.current_file])
    
    def __move(self, d):
        dest_dir = os.path.expanduser(d)
        if not os.path.isdir(dest_dir):
            QMessageBox.warning(self, 'Invalid directory.', dest_dir + ' is not a valid directory.')
            return
        
        dest = dest_dir + str(self.save_as.text() + self.extention.text())
        print("Moving", self.current_file, "\n\t to", dest)
        
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
            next_file = self.__get_next_file()
            if next_file is None:
                QMessageBox.information(self, 'Nothing to sort!', 'All files are sorted.')
                sys.exit()
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
        if len(self.files) == 0:
            return None
        file = self.files.pop(0)
        if self.image_util.is_image(file[0]):
            return file
        else:
            print("Skipping", file[0], "as it is not an image.")
            return self.__get_next_file()
    
    def __put_back_file(self, path, name):
        self.files.insert(0, (path, name))
    
    def __undo(self):
        prev_file = self.move_history.pop(0)
        src     = prev_file[0] # get source location
        name    = prev_file[1] # get original name
        curr    = prev_file[2] # get current location
        # move back and reset
        shutil.move(curr, src)
        self.__put_back_file(self.current_file, self.current_name)
        self.current_file = src
        self.current_name = name
        self.__draw_image()
        self.__update_info()
        print("Undoing move to", curr, "\n\tfrom", src)
    
    def __delete(self):
        self.__move(self.config.get_trash_path())

    def __image_too_large(self):
        return self.view.geometry().width() < self.image.width() \
            or self.view.geometry().height() < self.image.height()

    def __fit_image(self):
        scene_rect = self.scene.sceneRect()
        if self.__image_too_large():
            self.view.fitInView(scene_rect, Qt.KeepAspectRatio)

