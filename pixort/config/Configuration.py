
import os

"""
Loads, stores, and saves pixort configuration.
"""
class Configuration:
    PROGRAM_TITLE               = "Pixort"
    DEFAULT_CONFIG_FILE_PATH    = "~/.pixortrc"
    DEFAULT_BROWSER_PATH        = "chromium"
    DEFAULT_TRASH_PATH          = "~/.local/share/Trash/files/"

    def __init__(self, config_path = None):
        if config_path is None:
            self.config_file_path   = Configuration.DEFAULT_CONFIG_FILE_PATH
        else:
            self.config_file_path   = config_path
        # set default paths
        self.browser_path   = Configuration.DEFAULT_BROWSER_PATH
        self.trash_path     = Configuration.DEFAULT_TRASH_PATH
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
    
    def get_trash_path():
        return self.trash_path
    
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

