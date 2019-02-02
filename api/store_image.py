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

from flask import Flask, abort, redirect, url_for
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

        self._upload_path = self.app.config['_UPLOAD_DIRECTORY']
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
            fd, temp_file_path = tempfile.mkstemp()
            try:
                image.save(temp_file_path)
                image_type = check_image(temp_file_path)
                if image_type and image_type in self.app.config['_IMAGE_EXTENSIONS']:
                    file_path = self.add_item(image.filename, temp_file_path, image_type)
                    if file_path:
                        copy(temp_file_path, file_path)
                    # self.app.logger.debug('image added: %s' % image)
            finally:
                os.close(fd)
                os.remove(temp_file_path)

    def add_item(self, original_file_name, temp_file_path, file_type):
        """
        name file as it content hex md5 representation, insert info into mongodb and move to storage location
        :param original_file_name
        :param temp_file_path
        :param file_type
        """
        file_doc = self.document_template()
        hashed_content = get_md5(temp_file_path)
        file_name = secure_filename('.'.join((hashed_content, file_type)))
        file_path = os.path.join(self._upload_path, file_name)

        file_doc['original_filename'] = original_file_name
        file_doc['md5'] = hashed_content
        file_doc['file_name'] = file_name
        file_doc['path'] = '%s/%s' % (self.app.config['_RAW_IMAGE_ROUTE'], file_name)

        collection = self.get_collection(self.app.config['_COLLECTION'])
        item_id = collection.insert_one(file_doc).inserted_id
        # app.logger.debug(item_id)

        return file_path

    # def store(self, file):
    #     """
    #     main method to store image
    #     :param file: file-like object
    #     """
    #     images = self.process_source(file)
    #     self.add_items(images)
    #     return True

    def hook_it(self, resource, request):
        """
        hook pre_POST image post request, perform file insert process, abort orginal request process
        """
        file_key = self.app.config['_FILE_KEY']
        if file_key not in request.files:
            abort(422)

        file = request.files[file_key]
        images = self.process_source(file)
        if not images:
            abort(415)

        self.add_items(images)
        abort(redirect(url_for('%s|resource' % resource)))

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
    chceck if file extension is in allowed extensions
    :param filename: name of file
    :param extensions: allowed files extensions
    :return: True if extension is correct else False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


def check_image(file_path, content = None):
    """
    Tests the image data contained in the file named by filename, and returns a string describing the image type.
    :param file_path: filepath
    :return: image type str or None
    """
    return imghdr.what(file_path, content)


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
    :return: file-like objects generator
    """
    with ZipFile(file) as myzip:
        for name in myzip.namelist():
            if allowed_file(name, allowed):
                raw_file = myzip.open(name)
                yield FileStorage(stream=raw_file, filename=name)
