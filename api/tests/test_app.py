#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import pytest
import json
import os

from pymongo import MongoClient

from .. import main
from .test_settings import test_sets
from ..settings import _COLLECTION, _UPLOAD_DIRECTORY


class TestClass(object):
    @pytest.fixture
    def client(self):
        test_sets['RESOURCE_METHODS'] = ['GET', 'POST']
        app = main.create_app(test_sets)
        testing_client = app.test_client()

        # Establish an application context before running the tests.
        ctx = app.app_context()
        ctx.push()

        yield testing_client  # this is where the testing happens!

        client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
        db = client[app.config['MONGO_DBNAME']]
        db.images.remove()

        ctx.pop()

    def test_empty_db(self, client):
        """Start with a blank database."""
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'{"_links": {"child": [{"href": "images", "title": "images"}]}}' == resp.data

    def test_jpeg_insert(self, client):
        """Start with a blank database."""
        test_data = {
            "file_name": "c29bb130a677fc8e3a3fe66221eec68e.jpeg",
            "path": "images/raw/c29bb130a677fc8e3a3fe66221eec68e.jpeg",
        }

        cwd = os.getcwd()
        test_file = open(cwd + '/api/tests/c29bb130a677fc8e3a3fe66221eec68e.jpeg', 'rb')

        data = {'file': test_file}
        resp = client.post('/%s' % test_sets['_COLLECTION'], data=data, follow_redirects=True,
                           content_type='multipart/form-data')

        resp_obj = json.loads(resp.get_data())

        item = resp_obj['_items'][0]
        mybool = all([v == item[k] for k, v in test_data.items()])
        assert mybool is True

        name1 = '/c29bb130a677fc8e3a3fe66221eec68e.jpeg'

        resp = client.get('/%s%s' % (test_sets['_RAW_IMAGE_ROUTE'], name1))
        assert resp.status_code == 200

        test_file = open(cwd + '/api/tests/c29bb130a677fc8e3a3fe66221eec68e.jpeg', 'rb')
        assert resp.data == test_file.read()

        img1 = _UPLOAD_DIRECTORY + name1
        imgs_exists_flag = (os.path.isfile(img1))

        if imgs_exists_flag:
            os.remove(img1)

        assert imgs_exists_flag is True

    def test_zip_insert(self, client):
        """Start with a blank database."""

        resp = client.get('/images')
        assert resp.status_code == 200

        test_data = {
            "file_name": "c29bb130a677fc8e3a3fe66221eec68e.jpeg",
            "path": "images/raw/c29bb130a677fc8e3a3fe66221eec68e.jpeg",
        }

        cwd = os.getcwd()
        test_zip = open(cwd + '/api/tests/test_imgs.zip', 'rb')

        data = {'file': test_zip}
        resp = client.post('/%s' % test_sets['_COLLECTION'], data=data, follow_redirects=True,
                           content_type='multipart/form-data')
        resp_obj = json.loads(resp.get_data())

        # print(resp_obj)
        item = resp_obj['_items'][1]
        mybool = all([v == item[k] for k, v in test_data.items()])
        assert mybool is True

        name1 = '/c29bb130a677fc8e3a3fe66221eec68e.jpeg'
        name2 = '/6dddeade02138cb1b0f035f692580c98.jpeg'

        resp = client.get('/%s%s' % (test_sets['_RAW_IMAGE_ROUTE'], name1))
        assert resp.status_code == 200

        resp = client.get('/%s%s' % (test_sets['_RAW_IMAGE_ROUTE'], name2))
        assert resp.status_code == 200

        img1 = _UPLOAD_DIRECTORY + name1
        img2 = _UPLOAD_DIRECTORY + name2

        imgs_exists_flag = (os.path.isfile(img1) and os.path.isfile(img2))

        if imgs_exists_flag:
            os.remove(img1)
            os.remove(img2)

        assert imgs_exists_flag is True
