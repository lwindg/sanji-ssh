#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import unittest
import logging

from sanji.connection.mockup import Mockup
from sanji.message import Message
from mock import patch

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from ssh import Ssh
except ImportError as e:
    print "Please check the python PATH for import test module. (%s)" \
        % __file__
    exit(1)


class TestSshClass(unittest.TestCase):

    def setUp(self):
        self.ssh = Ssh(connection=Mockup())

    def tearDown(self):
        self.ssh.stop()
        self.ssh = None

    def test_init(self):
        def fake_ssh(rc):
            def _fake_ssh():
                return rc
            return _fake_ssh

        # case 1: ssh start failed
        self.ssh.check_ssh = fake_ssh(False)
        self.ssh.start_model()

        # case 2: ssh start success
        self.ssh.check_ssh = fake_ssh(True)
        self.ssh.start_model()

    def test_get(self):
        # case 1: check code
        def resp(code=200, data=None):
            self.assertEqual(code, 200)
        self.ssh.get(message=None, response=resp, test=True)

        # case 2: check data enable = 1
        def resp1(code=200, data=None):
            self.assertEqual(data, {"enable": 1})
        self.ssh.model.db["enable"] = 1
        self.ssh.model.save_db()
        print("model db:%s" % self.ssh.model.db["enable"])
        self.ssh.get(message=None, response=resp1, test=True)

        # case 3: check data enable = 0
        def resp2(code=200, data=None):
            self.assertEqual(data, {"enable": 0})
        self.ssh.model.db["enable"] = 0
        self.ssh.model.save_db()
        self.ssh.get(message=None, response=resp2, test=True)

    def test_put(self):
        # case 1: message donsn't has data attribute
        message = Message({})

        def resp(code=200, data=None):
            self.assertEqual(code, 400)
            self.assertEqual(data, {"message": "Invaild Input"})
        self.ssh.put(message=message, response=resp, test=True)

        # case 2: update_ssh return True
        # case 2.1: ssh start success
        message = Message({"data": {"enable": 1}})

        def resp1(code=200, data=None):
            self.assertEqual(code, 200)
            self.assertEqual(data, {"enable": 1})
            print ("[resp1]data:%s" % data)
        self.ssh.put(message=message, response=resp1, test=True)

        # case 2.2: ssh stop success
        message = Message({"data": {"enable": 0}})
        print("[resp2]message:%s" % message.data["enable"])

        def resp2(code=200, data=None):
            self.assertEqual(code, 200)
            self.assertEqual(data, {"enable": 0})
        self.ssh.put(message=message, response=resp2, test=True)
        # case 3: update_ssh return False
        # case 3.1: ssh start failed
        # case 3.2: ssh stop failed

    '''
    def test_start_model(self):
        with patch("ssh.Ssh.check_ssh") as check_ssh:
            # case 1: rc = True
            check_ssh.return_value = True
            self.ssh.start_model()

            # case 2: rc = False
            check_ssh.return_value = False
            self.ssh.start_model()

    def test_check_ssh(self):
        with patch("ssh.subprocess") as subprocess:
            subprocess.Popen.return_value = 999
            self.ssh.check_ssh()
    '''

if __name__ == "__main__":
    unittest.main()
