#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import unittest
import logging

from sanji.connection.mockup import Mockup
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
        # self.ssh.check_ssh = fake_ssh(False)
        # self.ssh.start_model()

        # case 2: ssh start success
        self.ssh.check_ssh = fake_ssh(True)
        self.ssh.start_model()

    def test_get(self):
        # case 1: code
        def resp(code=200, data=None):
            self.assertEqual(code, 200)
        self.ssh.get(message=None, response=resp, test=True)
        # TODO: key "enable"

        # TODO: Value in (0, 1)

    '''
    def test_put(self):
        message = Message({"data": {"enable": 1}})
        print "in test_put"

        # case 1: put successfully
        def resp(code=200, data=None):
            self.assertEqual(self.ssh.message, 1)
    '''
    def test_start_model(self):
        # TODO: this method need to write test code
        with patch("ssh.Ssh.check_ssh") as check_ssh:
            # case 1: rc = True
            check_ssh.return_value = True
            self.ssh.start_model()

            # case 2: rc = False
            check_ssh.return_value = False
            self.ssh.start_model()

    def test_check_ssh(self):
        # TODO: this method need to write test code
        with patch("ssh.subprocess") as subprocess:
            subprocess.Popen.return_value.returncode = 999
            self.ssh.check_ssh()


if __name__ == "__main__":
    unittest.main()
