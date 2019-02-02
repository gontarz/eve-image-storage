#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os

from eve import Eve
from flask import send_from_directory

from api.store_image import ImageStorage


def create_app(settings=None):
    if settings is None:
        settings = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')
    app = Eve(__name__, settings=settings)
    app.secret_key = app.config['_SECRET_KEY']

    images_storage = ImageStorage(app)
    app.on_pre_POST += images_storage.hook_it


    @app.route('/%s/<filename>' % app.config['_RAW_IMAGE_ROUTE'])
    def uploaded_file(filename):
        """
        return image
        :param filename: name of file to fetch
        """
        return send_from_directory(app.config['_UPLOAD_DIRECTORY'],
                                   filename)


    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
