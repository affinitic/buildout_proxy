FROM python:3.6
MAINTAINER Martin Peeters (@mpeeters)

RUN mkdir /buildout_proxy
RUN mkdir /buildout_proxy/cache
RUN mkdir /buildout_proxy/config

COPY setup.py /buildout_proxy
COPY CHANGES.rst /buildout_proxy
COPY README.rst /buildout_proxy
COPY requirements.txt /buildout_proxy
COPY buildout_proxy /buildout_proxy/buildout_proxy
RUN rm -rf /buildout_proxy/buildout_proxy/tests

RUN pip install -e /buildout_proxy -c /buildout_proxy/requirements.txt

VOLUME /buildout_proxy/cache
VOLUME /buildout_proxy/config

EXPOSE 6543

CMD ["pserve", "/buildout_proxy/config/app.ini"]
