# -*- coding: utf-8 -*-
from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'buildout_proxy.hosts.passwords' in settings:
        with open(settings['buildout_proxy.hosts.passwords'], 'r') as f:
            settings['buildout_proxy.hosts.passwords'] = {
                d.strip(): p.strip() for d, p
                in [l.split('=') for l in f.read().splitlines() if l]
            }
    else:
        settings['buildout_proxy.hosts.passwords'] = {}
    if 'buildout_proxy.cache' in settings:
        lines = settings['buildout_proxy.cache'].splitlines()
        settings['buildout_proxy.cache'] = {
            h.strip(): d.strip() for h, d
            in [l.split(';') for l in lines if l]
        }
        settings['buildout_proxy.cache']['default'] = settings.get(
            'buildout_proxy.cache.default',
        ) or 86400
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_renderer(
        'text',
        'buildout_proxy.renderer.string_renderer_factory',
    )
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('resource', '/r/{protocol}/{domain}/*path')
    config.add_route('merged', '/m/{protocol}/{domain}/*path')
    config.add_route(
        'merged_section',
        '/ms/{section}/{protocol}/{domain}/*path',
    )
    config.scan()
    return config.make_wsgi_app()
