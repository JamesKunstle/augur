#SPDX-License-Identifier: MIT
"""
Provides shared functions that do not fit in a class of their own
"""
import os
import re
import inspect
import types
import sys
import beaker

from flask import request

__ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data_path(path):
    """
    Returns data path of given object

    :param path: given path of object
    """
    return os.path.join(__ROOT, 'data', path)

# Default cache is in memory
__memory_cache = None
def get_cache(namespace, cache_manager=None):
    """
    Returns cache of object called 'namespace'

    :param namespace: name associated with the targeted cache
    """
    global __memory_cache
    if cache_manager is None:
        if __memory_cache is None:
            cache_opts = beaker.util.parse_cache_config_options({
                'cache.type': 'memory',
                'cache.lock_dir': '/tmp/augur/'
            })
            __memory_cache = beaker.cache.CacheManager(**cache_opts)
        cache_manager = __memory_cache
    return cache_manager.get_cache(namespace)

"""
This is a decorator that defines a metric. It adds is_metric and the type to the function meatadata.
These is used by the loop in api/metrics/__init__.py to determine which wether a function should be added 
to the metrics class. It is also used in api/routes/__init__.py to determine which method to call when it 
is looping through the methods on the class Metrics.  
"""
metric_metadata = []
def register_metric(metadata=None, **kwargs):
    """
    Register a function as being a metric
    """
    if metadata is None:
        metadata = {}
    def decorate(function):
        if not hasattr(function, 'metadata'):
            function.metadata = {}
            metric_metadata.append(function.metadata)

        if not hasattr(function, 'is_metric'):
            function.is_metric = True

        function.metadata.update(dict(kwargs))

        function.metadata['tag'] = re.sub('_', '-', function.__name__).lower()
        function.metadata['endpoint'] = function.metadata['tag']
        function.metadata['name'] = re.sub('_', ' ', function.__name__).title()
        function.metadata['model'] = re.sub(r'(.*\.)', '', function.__module__)

        if kwargs.get('type', None):
            function.metadata['type'] = kwargs.get('type')
        else:
            function.metadata['type'] = "standard"

        function.metadata.update(metadata)

        return function
    return decorate

""" 
    Extract authorization token by type from request header
"""
def get_token(token_type):
    auth = request.headers.get("Authorization")
    if auth:
        tokens = auth.split(",")
        for token in tokens:
            if f"{token_type} " in token:
                return token.replace(f"{token_type}", "").strip()

""" 
    Extract Bearer token from request header
"""
def get_bearer_token():
    return get_token("Bearer")

""" 
    Extract Client token from request header
"""
def get_client_token():
    return get_token("Client")
    