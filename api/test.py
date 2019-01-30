#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import unittest
import os
import io
import types
import json
import datetime

# from eve.tests import TestMinimal
# from eve.tests.endpoints import TestEndPoints

from api.store_image import ImageStorage, allowed_file, read_zip, get_md5
from api.main import create_app
from api.settings import _ALLOWED_EXTENSIONS, _IMAGE_EXTENSIONS, _COLLECTION

from werkzeug.datastructures import FileStorage
from zipfile import ZipFile
from pymongo import MongoClient


class TestStorageMethods(unittest.TestCase):
    def test1_validate(self):
        self.assertRaises(TypeError, ImageStorage.__init__, ImageStorage)

    def test2_validate(self):
        self.assertRaises(TypeError, ImageStorage.__init__, ImageStorage, '')

    def test3_validate(self):
        my_app = create_app()
        image_storage = ImageStorage(my_app)
        image_storage.app.config['_UPLOAD_DIRECTORY'] = None
        self.assertRaises(KeyError, image_storage.validate)

    def test1_process_source(self):
        cwd = os.getcwd()
        test_zip = open(cwd + '/tests/test_imgs.zip')
        file = FileStorage(stream=test_zip, filename='test.zip')

        my_app = create_app()
        image_storage = ImageStorage(my_app)
        result = image_storage.process_source(file)

        self.assertIsInstance(result, types.GeneratorType)

    def test2_process_source(self):
        my_app = create_app()
        image_storage = ImageStorage(my_app)

        for ext in _IMAGE_EXTENSIONS:
            file = FileStorage(filename='test.%s' % ext)
            result = image_storage.process_source(file)
            self.assertIsInstance(result, list)

    def test1_allowed_file(self):
        filename1 = 'a.zip'
        allowed = allowed_file(filename1, _ALLOWED_EXTENSIONS)
        self.assertTrue(allowed)

    def test2_allowed_file(self):
        filename1 = 'a.zi'
        allowed = allowed_file(filename1, _ALLOWED_EXTENSIONS)
        self.assertFalse(allowed)

    def test1_get_md5(self):
        cwd = os.getcwd()
        self.assertEqual(get_md5(cwd + '/tests/test1.jpeg'), get_md5(cwd + '/tests/test1.jpeg'))

    def test2_get_md5(self):
        cwd = os.getcwd()
        self.assertNotEqual(get_md5(cwd + '/tests/test1.jpeg'), get_md5(cwd + '/tests/test2.jpeg'))

    # def test1_add_item(self):
    #     my_app = create_app()
    #     my_app = my_app.test_client()
    #     my_app.config['MONGO_DBNAME'] = my_app.config['_MONGO_DBNAME_TEST']
    #
    #     client = MongoClient(my_app.config['MONGO_HOST'], my_app.config['MONGO_PORT'])
    #
    #     db = client[my_app.config['MONGO_DBNAME']]
    #
    #     image_storage = ImageStorage(my_app)
    #     pass

    # def test_get_collection(self):
    #     my_app = create_app()
    #     image_storage = ImageStorage(my_app)
    #     tested_db = image_storage.get_collection(my_app.config['_COLLECTION'])
    #
    #     driver = image_storage.app.data
    #     px = driver.current_mongo_prefix(image_storage.config['_COLLECTION'])
    #     db = driver.pymongo(prefix=px).db[image_storage.config['_COLLECTION']]
    #
    #     self.assertEqual(tested_db, db)

    # def test_read_zip(self):
    #     cwd = os.getcwd()
    #     test_zip = open(cwd+'/tests/test_imgs.zip')
    #     file = FileStorage(stream=test_zip, filename='test_imgs.zip')
    #     file=cwd + '/tests/test_imgs.zip'
    #     gen = read_zip(file, _ALLOWED_EXTENSIONS)
    #     test_file1 = open(cwd+'/tests/test1.jpeg')
    #     test_file2 = open(cwd + '/tests/test2.jpeg')
    #
    #     files = [FileStorage(stream=test_file1.read(), filename='test1.jpeg'),
    #              FileStorage(stream=test_file2.read(), filename='test2.jpeg')]
    #     for i, f in enumerate(gen):
    #         self.assertEqual(f, files[i])


class ClientAppsTests(unittest.TestCase):
    def setUp(self):
        my_app = create_app()

        my_app.config['MONGO_DBNAME'] = my_app.config['_MONGO_DBNAME_TEST']
        my_app.config['TESTING'] = True

        client = MongoClient(my_app.config['MONGO_HOST'], my_app.config['MONGO_PORT'])

        self.db = client[my_app.config['MONGO_DBNAME']]

        self.app = my_app.test_client()
        self.config = my_app.config

        # new_app = dict()
        # self.db.client_apps.insert(new_app)

        # self.image_storage = ImageStorage(my_app)

    def tearDown(self):
        self.db.client_apps.remove()

    def test1_connection(self):
        res = self.app.get('/')
        assert res.status_code == 200

    def test2_connection(self):
        res = self.app.get('/%s' % _COLLECTION)
        assert res.status_code == 200

    def test3_connection(self):
        res = self.app.get('/notvalidresource')
        assert res.status_code == 404

    def test_empty_db_response(self):
        resp = self.app.get('/')
        resp_obj = json.loads(resp.get_data())

        expect = {
            "_links": {
                "child": [
                    {
                        "href": "images",
                        "title": "images"
                    }
                ]
            }
        }

        self.assertEqual(resp_obj, expect)

    # def test_doc_insert(self):
    #     data = {
    #         "file_name": "c29bb130a677fc8e3a3fe66221eec68e.jpeg",
    #         "path": "images/raw/c29bb130a677fc8e3a3fe66221eec68e.jpeg",
    #         "_links": {
    #             "self": {
    #                 "title": "Image",
    #                 "href": "images/5c5215e8a6877f7ec6662002"
    #             }
    #         }
    #     }
    #     cwd = os.getcwd()
    #     test_img = open(cwd + '/tests/test1.jpeg', "rb")
    #
    #     # my_data['file'] = test_img
    #
    #     img_data = (io.BytesIO(test_img.read()), 'test1.jpeg')
    #
    #
    #     resp = self.app.post('/%s' % _COLLECTION, data={'file':img_data}, follow_redirects=True, content_type='multipart/form-data')
    #
    #     resp_obj = json.loads(resp.get_data())
    #
    #     item = resp_obj['_items'][0]
    #
    #     mybool = all([v==item[k] for k,v in data])
    #     self.assertTrue(mybool)


if __name__ == '__main__':
    unittest.main()
