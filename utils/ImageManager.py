import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config
# Saves images in the /uploads folder and returns the path / URL
class ImageManager():
    def save_images(self, images:list=[]):
        image_urls = []
        for index, image in enumerate(images):
            if not image or not image.filename:
                continue
            filename = f'/{index}-{time.time()}-{image.filename}'
            filepath =  Config.USER_IMAGES_UPLOAD_FOLDER + filename
            image.save(filepath)
            image_urls.append(filename)
        return image_urls