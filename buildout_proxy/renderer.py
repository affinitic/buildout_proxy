# -*- coding: utf-8 -*-

from pyramid.compat import string_types


def string_renderer_factory(info):
    def _render(value, system):
        if not isinstance(value, string_types):
            value = str(value)
        request = system.get("request")
        if request is not None:
            response = request.response
            ct = response.content_type
            if ct == response.default_content_type:
                response.content_type = "text"
        return value

    return _render
