# -*- coding: utf-8 -*-
"""
"""

from ..settings import _MONGO_DBNAME_TEST, _COLLECTION, _RAW_IMAGE_ROUTE, _FILE_KEY, _UPLOAD_DIRECTORY

test_sets = {
    'DOMAIN': {
        'images': {
            'resource_methods': ['GET'],
            # 'item_methods': ['GET'],
            # 'allow_unknown': True,
            # 'datasource': {
            #     'projection': {
            #         'md5': 0,
            #         'original_filename': 0
            #     }
            # },
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
                'upload_date': {
                    'type': 'datetime'
                },
                'file_name': {
                    'type': 'string'
                },
                'path': {
                    'type': 'string'
                }
            }
        }
    },
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': _MONGO_DBNAME_TEST,
    'RESOURCE_METHODS': ['GET', 'POST'],

    '_SECRET_KEY': 'xyz',
    '_COLLECTION': _COLLECTION,
    '_RAW_IMAGE_ROUTE': _RAW_IMAGE_ROUTE,
    '_FILE_KEY': _FILE_KEY,
    '_UPLOAD_DIRECTORY': _UPLOAD_DIRECTORY

}
