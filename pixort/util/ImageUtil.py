
from pixort.config import Configuration
from PIL import Image

class ImageUtil:
    def __init__(self, config):
        self.config = config

    def is_image(self, file):
        try:
            img = Image.open(file)
            return True
        except:
            return False

    def is_animated(self, file):
        img = Image.open(file)
        try:
            img.seek(1)
        except EOFError:
            is_animated = False
        else:
            is_animated = True
        img.seek(0)
        return is_animated

    def is_wallpaper(self, file):
        img = Image.open(file)
        width = img.size[0]
        height = img.size[1]
        ratio = float(width) / height
        # perform check and return truth value
        return (
            width >= self.config.get_min_wallpaper_width() and
            height >= self.config.get_min_wallpaper_height() and
            ratio >= self.config.get_min_wallpaper_ratio() and
            ratio <= self.config.get_max_wallpaper_ratio()
                )

