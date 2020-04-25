# -*- coding: utf-8 -*-
from urllib.parse import urljoin
from urllib.parse import urlsplit
from zc.buildout.configparser import parse
from pyramid.httpexceptions import HTTPNotFound

import hashlib
import io
import os
import re
import requests
import time


def compose_url(request):
    """ Compose the url from route parameters """
    domain = request.matchdict.get('domain')
    settings = request.registry.settings
    allowed_hosts = [
        e for e in settings.get('buildout_proxy.allow.hosts').splitlines()
        if e
    ]
    if '*' not in allowed_hosts:
        match_hosts = [re.match(h.replace('*', '.{1,}'), domain)
                       for h in allowed_hosts]
        if len([r for r in match_hosts if r]) == 0:
            raise ValueError('Not allowed host {0}'.format(domain))
    passwords = settings.get('buildout_proxy.hosts.passwords')
    if domain in passwords:
        domain = '{password}@{domain}'.format(
            password=passwords[domain],
            domain=domain,
        )
    url = '{protocol}://{domain}/{path}'.format(
        protocol=request.matchdict.get('protocol'),
        domain=domain,
        path='/'.join(request.matchdict.get('path')),
    )
    return url


def get_cache_path(directory, url):
    """ Return the path to the cache directory """
    if os.path.exists(directory) is False:
        os.mkdir(directory)
    return os.path.join(
        directory,
        hashlib.md5(url.encode('utf8')).hexdigest(),
    )


def get_cache_file(request, url):
    """ Return the cached file for a given request and url """
    settings = request.registry.settings
    f_path = get_cache_path(
        settings.get('buildout_proxy.directory') or '/tmp',
        url,
    )
    if not os.path.exists(f_path):
        cache_file(request, url, f_path)
    else:
        f_stat = os.stat(f_path)
        domain = urlsplit(url).netloc
        match_hosts = [h for h in settings['buildout_proxy.cache'].keys()
                       if re.match(h.replace('*', '.{1,}'), domain)]
        if match_hosts:
            duration = settings['buildout_proxy.cache'].get(match_hosts[0])
        else:
            duration = settings['buildout_proxy.cache'].get('default')
        if duration == 'ever':
            print('get from cache {0}'.format(url))
            return f_path
        if duration == 'never':
            duration = 5
        if f_stat.st_mtime > (time.time() - int(duration)):
            print('get from cache {0}'.format(url))
            return f_path
        else:
            tmp_path = '{0}_tmp'.format(f_path)
            os.rename(f_path, tmp_path)
            result = cache_file(request, url, f_path)
            if result is None:  # In case of an error
                os.rename(tmp_path, f_path)
            else:
                os.remove(tmp_path)
    return f_path


def cache_file(request, url, f_path):
    """ Get a buildout file from is url and stores it in cache """
    print('get {0}'.format(url))
    r = requests.get(url)
    if r.status_code != 200:
        print('cannot get {0}'.format(url))
        return
    content = r.content.decode('utf8')
    parser = parse(io.StringIO(content), None)
    extends = parser.get('buildout', {}).get('extends', '')
    base_url = get_base_url(request)
    new_extends = []
    for extend in extends.splitlines():
        if not extend.startswith('http'):
            extend = urljoin(url, extend)
        get_cache_file(request, extend)
        new_extends.append(update_url(base_url, extend))
    if extends:
        content = smart_section_replacer(
            content,
            'extends',
            extends.splitlines(),
            new_extends,
        )
    with open(f_path, 'w') as f:
        print('cache {0}'.format(url))
        f.write(content)
    return f_path


def get_base_url(request):
    """Return the base url extracted from the given request"""
    return '{0}://{1}'.format(
        request.environ.get('wsgi.url_scheme'),
        request.environ.get('HTTP_HOST'),
    )


def update_url(base_url, url):
    """ Update an url to use the buildout_proxy cache """
    replacements = (
        ('http://', '{0}/r/http/'.format(base_url)),
        ('https://', '{0}/r/https/'.format(base_url)),
    )
    for old, new in replacements:
        if url.startswith(old):
            url = url.replace(old, new)
            break
    return url


def smart_section_replacer(text, section, old_elements, new_elements):
    """
    Function that replace a list of elements with a new list of elements
    by avoiding mistake during replacement
    """
    start = text.find('{0} ='.format(section))
    end = text.find('=', start + 10)
    new_text = text[start:end]
    position = 0
    for old, new in zip(old_elements, new_elements):
        position = new_text.find(old, position)
        new_text = '{0}{1}'.format(
            new_text[0:position],
            new_text[position:].replace(old, new, 1),
        )
        position += len(new) - len(old)
    return text.replace(text[start:end], new_text)


def allowed_route(request, name):
    """ Verify if the given route name is allowed or raise an error """
    settings = request.registry.settings
    if name not in settings['buildout_proxy.allow.routes']:
        raise HTTPNotFound()
