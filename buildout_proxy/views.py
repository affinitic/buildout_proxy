# -*- coding: utf-8 -*-

from buildout_proxy import utils
from pyramid.view import view_config
from zc.buildout.buildout import Buildout
from zc.buildout.buildout import print_

import io


@view_config(route_name="home", renderer="templates/mytemplate.jinja2")
def my_view(request):
    return {"project": "buildout_proxy"}


@view_config(route_name="resource", renderer="text")
def resource_view(request):
    utils.allowed_route(request, "resource")
    url = utils.compose_url(request)
    f_path = utils.get_cache_file(request, url)
    with open(f_path, "r") as f:
        return f.read()


@view_config(route_name="merged", renderer="text")
def merged_view(request):
    utils.allowed_route(request, "merged")
    url = utils.compose_url(request)
    f_path = utils.get_cache_file(request, url)
    return get_merged_buildout(f_path)


@view_config(route_name="merged_section", renderer="text")
def merged_section_view(request):
    utils.allowed_route(request, "merged_section")
    url = utils.compose_url(request)
    section = request.matchdict.get("section")
    f_path = utils.get_cache_file(request, url)
    return get_merged_buildout(f_path, section=section)


def get_merged_buildout(f_path, section=None):
    output = io.StringIO()
    buildout = Buildout(f_path, [])
    data = buildout._annotated
    if section is not None:
        sections = [section]
    else:
        sections = list(data.keys())
    for section in sections:
        print_(file=output)
        print_("[%s]" % section, file=output)
        keys = list(data[section].keys())
        keys.sort()
        for key in keys:
            sectionkey = data[section][key]
            lines = sectionkey.value.splitlines()
            if len(lines) == 1:
                print_("{0} = {1}".format(key, lines[0]), file=output)
            else:
                print_("{0} =".format(key), file=output)
                for line in lines:
                    print_(line, file=output)
    output.seek(0)
    return output.read()
