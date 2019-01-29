# -*- coding: utf-8 -*-
"""
"""

import os
import datetime
import hashlib
import tempfile
import imghdr
from shutil import copy
from zipfile import ZipFile

from flask import Flask
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from eve.io.mongo import Mongo


class ImageStorage(object):
    """
    The File System class to store files into disk.
    Use _UPLOAD_DIRECTORY configuration value.
    """

    def __init__(self, app=None):
        """Constructor.
        :param app: the flask application (eve itself). This can be used by
        the class to access, amongst other things, the app.config object to
        retrieve class-specific settings.
        """
        self.app = app
        self._upload_path = self.app.config['_UPLOAD_DIRECTORY']
        self.validate()
        self._images_collection = {}

    def validate(self):
        """
        Make sure that the application data layer is a eve.io.mongo.Mongo
        instance.
        """
        if self.app is None:
            raise TypeError('Application object cannot be None')

        if not isinstance(self.app, Flask):
            raise TypeError('Application object must be a Eve application')

        if not self._upload_path:
            raise KeyError('_UPLOAD_DIRECTORY is not configured on app settings')

    def get_collection(self, resource=None):
        """
        Provides the instance-level Mongo collection to save the data associated
        to saved filesystem, instantiating it if needed.
        :param app: eve application object
        :param collection: collection name
        """
        driver = self.app.data
        if driver is None or not isinstance(driver, Mongo):
            raise TypeError("Application data object must be of eve.io.Mongo ")

        px = driver.current_mongo_prefix(resource)

        if px not in self._images_collection:
            self._images_collection[px] = driver.pymongo(prefix=px).db[resource]

        return self._images_collection[px]

    def process_source(self, file):
        """
        check file extension and choose proper function
        :param file: werkzeug file-like object
        :return: True if ok else None
        """
        if file and allowed_file(file.filename, self.app.config['_ALLOWED_EXTENSIONS']):

            if allowed_file(file.filename, self.app.config['_ZIP_EXTENSIONS']):
                images_to_store = read_zip(file, self.app.config['_IMAGE_EXTENSIONS'])

            else:
                images_to_store = [file]

            return images_to_store

    def add_items(self, images):
        """
        iter image list, validate picture content and add item to storage and db
        :param images: list of werkzeug file-like objects
        """
        for image in images:
            fd, fp = tempfile.mkstemp()
            try:
                image.save(fp)
                image_type = check_image(fp)
                if image_type and image_type in self.app.config['_IMAGE_EXTENSIONS']:
                    self.add_item(image.filename, fp)
                    # self.app.logger.debug('image added: %s' % image)
            finally:
                os.close(fd)
                os.remove(fp)

    def add_item(self, file_name, temp_file_path):
        """
        save file to temp location, insert to mongodb and move to storage location
        :param file_name: name of file
        """
        file_doc = self.document_template()

        file_doc['original_filename'] = file_name

        file_doc['md5'] = get_md5(temp_file_path)

        file_name = '.'.join((file_doc['md5'], file_doc['original_filename'].split('.')[-1]))
        file_doc['file_name'] = secure_filename(file_name)

        file_doc['path'] = '%s/%s' % (self.app.config['_RAW_IMAGE_ROUTE'], file_name)

        file_path = os.path.join(self._upload_path, file_doc['file_name'])

        collection = self.get_collection(self.app.config['_COLLECTION'])
        item_id = collection.insert_one(file_doc).inserted_id
        # app.logger.debug(item_id)

        copy(temp_file_path, file_path)

    def store(self, file):
        """
        main method to store image
        :param file: file-like object
        """
        images = self.process_source(file)
        self.add_items(images)
        return True

    @staticmethod
    def document_template():
        """
        create document dict template
        :return: dict template
        """
        return {
            'md5': None,
            'original_filename': None,
            '_created': datetime.datetime.utcnow(),
            'file_name': None,
            'path': None
        }


def allowed_file(filename, extensions):
    """
    chceck if file extension i  in allowed extensions
    :param filename: name of file
    :param extensions: allowed files extensions
    :return: True if extension is correct else False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


def check_image(file_path):
    """
    Tests the image data contained in the file named by filename, and returns a string describing the image type.
    :param file_path: filepath
    :return: image type str or None
    """
    return imghdr.what(file_path)


def get_md5(file_path):
    """Calculate MD5 value for a given file.
    :param file_path: File path.
    """
    BLOCKSIZE = 104857600
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_zip(file, allowed):
    """
    read zip and for allowed files returns file-like objects generator
    :param file:
    :param allowed: allowed extensions
    :return:
    """
    with ZipFile(file) as myzip:
        for name in myzip.namelist():
            if allowed_file(name, allowed):
                raw_file = myzip.open(name)
                yield FileStorage(stream=raw_file, filename=name)
