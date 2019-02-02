# -*- coding: utf-8 -*-
"""
"""

images = {
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET'],
    # 'allow_unknown': True,
    'datasource': {
        'projection': {
            'md5': 0,
            'original_filename': 0,
            'file': 0
        }
    },
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'file_name'
    },
    'schema': {
        'md5': {
            'type': 'string'
        },
        'original_filename': {
            'type': 'string'
        },
        'file_name': {
            'type': 'string'
        },
        'path': {
            'type': 'string'
        },
        'file': {
            'type': 'media'
        }
    }
}

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
# RESOURCE_METHODS = ['GET', 'POST']


# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
# ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']


# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_DBNAME = 'image_storage'
_MONGO_DBNAME_TEST = 'test_image_storage'

# Skip these if your db has no auth. But it really should.
# MONGO_USERNAME = '<your username>'
# MONGO_PASSWORD = '<your password>'
# MONGO_AUTH_SOURCE = 'admin'  # needed if --auth mode is enabled


_UPLOAD_DIRECTORY = ''

_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tif'])
_ZIP_EXTENSIONS = set(['zip'])
_ALLOWED_EXTENSIONS = _IMAGE_EXTENSIONS.union(_ZIP_EXTENSIONS)
_SECRET_KEY = 'xyz'
_FILE_KEY = 'file'

_COLLECTION = 'images'
_RAW_IMAGE_ROUTE = 'images/raw'

DOMAIN = {_COLLECTION: images}
