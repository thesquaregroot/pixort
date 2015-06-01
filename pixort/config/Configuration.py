
import os

"""
Loads, stores, and saves pixort configuration.
"""
class Configuration:
    # pixort
    PROGRAM_TITLE               = "Pixort"
    DEFAULT_CONFIG_FILE_PATH    = "~/.pixortrc"
    # system
    DEFAULT_BROWSER_PATH        = "chromium"
    DEFAULT_TRASH_PATH          = "~/.local/share/Trash/files/"
    # wallpapers
    DEFAULT_MIN_WALLPAPER_WIDTH = 800
    DEFAULT_MIN_WALLPAPER_HEIGHT = 500
    DEFAULT_MIN_WALLPAPER_RATIO = 1.2
    DEFAULT_MAX_WALLPAPER_RATIO = 2.5

    def __init__(self, config_path = None):
        if config_path is None:
            self.config_file_path   = Configuration.DEFAULT_CONFIG_FILE_PATH
        else:
            self.config_file_path   = config_path
        # set defaults
        self.browser_path   = Configuration.DEFAULT_BROWSER_PATH
        self.trash_path     = Configuration.DEFAULT_TRASH_PATH
        self.min_wallpaper_width  = Configuration.DEFAULT_MIN_WALLPAPER_WIDTH
        self.min_wallpaper_height = Configuration.DEFAULT_MIN_WALLPAPER_HEIGHT
        self.min_wallpaper_ratio  = Configuration.DEFAULT_MIN_WALLPAPER_RATIO
        self.max_wallpaper_ratio  = Configuration.DEFAULT_MAX_WALLPAPER_RATIO
        # load config file
        self.__load_config()
    
    def get_config_path(self):
        return self.config_file_path
    
    def get_unsorted_directory(self):
        return self.unsorted_directory
    
    """ Returns tuples of base directory and its subdirectories. """
    def get_destination_directories(self):
        return self.destination_directories
    
    def get_browser_path(self):
        return self.browser_path
    
    def get_trash_path(self):
        return self.trash_path
    
    def get_min_wallpaper_width(self):
        return self.min_wallpaper_width
    
    def get_min_wallpaper_height(self):
        return self.min_wallpaper_height
    
    def get_min_wallpaper_ratio(self):
        return self.min_wallpaper_ratio
    
    def get_max_wallpaper_ratio(self):
        return self.max_wallpaper_ratio
    
    def __load_config(self):
        f = open(os.path.expanduser(self.config_file_path), "r")
        
        # get unsorted directory
        self.unsorted_directory = os.path.expanduser(f.readline().strip())
        # new line
        f.readline()
        # get destination directories
        self.destination_directories = []
        directories = [directory.strip() for directory in f.readlines()]
        while len(directories) > 0:
            base = directories.pop(0)
            subdirectories = []  # "files" is the set of directories within "d"
            while len(base) > 0:
                if directories[0] == "":
                    # get rid of empty string
                    directories.pop(0)
                    break
                else:
                    subdirectories.append(directories.pop(0))
            # store directory/subdirectories
            self.destination_directories.append((base, subdirectories))

