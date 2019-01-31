# -*- coding: utf-8 -*-
"""
"""

from .. settings import _MONGO_DBNAME_TEST

test_sets = {
            'MONGO_HOST': 'localhost',
            'MONGO_PORT': 27017,
            'MONGO_DBNAME': _MONGO_DBNAME_TEST,
            'RESOURCE_METHODS': ['GET', 'POST'],
            'DOMAIN': {
                'images': {
                    # 'resource_methods': ['GET', 'POST'],
                    # 'allow_unknown': True,
                    'schema': {
                        'file_name': {
                            'type': 'string'
                        },
                        'path': {
                            'type': 'string'
                        }
                    }
                }
            },
            '_SECRET_KEY': 'xyz'
        }