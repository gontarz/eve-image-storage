#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os

from eve import Eve
from flask import request, redirect, url_for, flash, send_from_directory

from api.store_image import ImageStorage


def create_app(settings=None):
    if settings is None:
        settings = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')
    app = Eve(__name__, settings=settings)
    app.secret_key = app.config['_SECRET_KEY']

    @app.route('/images', methods=['POST'])
    def upload_file():
        """
        uploads images to destination directory and insert images info to mongodb
        """
        info = '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
                <p><input type=file name=file>
                <input type=submit value=Upload>
            </form>
            '''
        file_key = app.config['_FILE_KEY']

        if request.method == 'POST':
            # check if the post request has the file part
            if file_key not in request.files:
                return info
            file = request.files[file_key]
            # if user does not select file, browser also
            # submit a empty part without filename
            if not file.filename:
                return info
            if images_storage.store(file):
                return redirect(url_for('%s|resource' % app.config['_COLLECTION']))
        return info

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

images_storage = ImageStorage(app)

if __name__ == '__main__':
    app.run(debug=True)
