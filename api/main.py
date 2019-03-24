#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os

from eve import Eve
from flask import send_from_directory

from api.store_image import ImageStorage


def create_app(settings=None):
    return App(settings).app


class App():
    def __init__(self, settings=None):
        if settings is None:
            settings = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')

        self.app = Eve(__name__, settings=settings)
        self.app.secret_key = self.app.config['_SECRET_KEY']

        images_storage = ImageStorage(self.app)
        self.app.on_pre_POST += images_storage.hook_it

        self.app.route('/%s/<filename>' % self.app.config['_RAW_IMAGE_ROUTE'])(self.uploaded_file)

    @staticmethod
    def uploaded_file(filename):
        """
        return image
        :param filename: name of file to fetch
        """
        return send_from_directory(app.config['_UPLOAD_DIRECTORY'],
                                   filename)


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
