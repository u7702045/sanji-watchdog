#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import logging
import unittest

from sanji.connection.mockup import Mockup
from sanji.message import Message
from mock import patch
from mock import mock_open

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
    from watchdog import Watchdog
except ImportError as e:
    print os.path.dirname(os.path.realpath(__file__)) + "/../"
    print sys.path
    print e
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)

dirpath = os.path.dirname(os.path.realpath(__file__))


class TestWatchdogClass(unittest.TestCase):

    def setUp(self):
        def zombiefn():
            pass
        self.watchdog = Watchdog(connection=Mockup())

    def tearDown(self):
        self.watchdog = None

    @patch("watchdog.subprocess")
    def test1_put(self, subprocess):
        subprocess.check_output.return_value = True
        subprocess.call.return_value = True
        test_msg = {
            "id": 12345,
            "method": "put",
            "resource": "/system/watchdog"
        }

        # case 1: no data attribute
        def resp1(code=200, data=None):
            self.assertEqual(400, code)
            self.assertEqual(data, {"message": "Invalid Input."})
        message = Message(test_msg)
        self.watchdog.put_root(message, response=resp1, test=True)

        # case 2: data dict is empty or no enable exist
        def resp2(code=200, data=None):
            self.assertEqual(200, code)
        test_msg["data"] = dict()
        message = Message(test_msg)
        self.watchdog.put_root(message, response=resp2, test=True)

        # case 3: data
        def resp3(code=200, data=None):
            self.assertEqual(200, code)
        test_msg["data"] = {"path": "abcde"}
        message = Message(test_msg)
        self.watchdog.put_root(message, response=resp3, test=True)

    def test2_put(self):
        test_msg = {
            "id": 1,
            "method": "put",
            "resource": "/system/watchdog"
            }

        # case 1: data
        def resp1(code=200, data=None):
            self.assertEqual(200, code)
        test_msg["data"] = {"path": "somewhere", "process": "hello_world"}
        message = Message(test_msg)
        self.watchdog.put_root(message, response=resp1, test=True)

        # case 2: data
        def resp2(code=200, data=None):
            self.assertEqual(200, code)
        self.watchdog.get_root(message, response=resp2, test=True)

    def test_get(self):
        test_msg = {
            "id": 1,
            "method": "get",
            "resource": "/system/watchdog"
            }

        # case 1: data
        def resp1(code=200, data=None):
            self.assertEqual(200, code)
        message = Message(test_msg)
        self.watchdog.get_root(message, response=resp1, test=True)

    def test_delete(self):
        test_msg = {
            "id": 1,
            "method": "delete",
            "resource": "/system/watchdog/1",
            "param": {"id": 1}
            }

        # case 1: data
        def resp1(code=200, data=None):
            self.assertEqual(400, code)
        message = Message(test_msg)
        self.watchdog.delete_root(message, response=resp1, test=True)

        # case 2: data
        def resp2(code=200, data=None):
            self.assertEqual(200, code)
        self.watchdog.processes = [1, 2, 3]
        message = Message(test_msg)
        self.watchdog.monit_reload()
        self.watchdog.delete_root(message, response=resp2, test=True)

    def test_monit_reload(self):
        m = mock_open()
        with patch("watchdog.open", m, create=True):
            rc = self.watchdog.monit_reload()
            self.assertEqual(rc, True)

    def test_init(self):
        with patch("watchdog.ModelInitiator") as model:
            model.return_value.db.__getitem__.return_value = 1
            self.watchdog.init()

if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=20, format=FORMAT)
    logger = logging.getLogger("Watchdog Test")
    unittest.main()
