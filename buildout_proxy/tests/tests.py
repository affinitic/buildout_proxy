# -*- coding: utf-8 -*-

from pyramid import testing

import unittest


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from buildout_proxy.views import my_view

        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info["project"], "buildout_proxy")


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from buildout_proxy import main

        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get("/", status=200)
        self.assertTrue(b"Affinitic" in res.body)
