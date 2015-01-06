#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import unittest
import logging

from sanji.connection.mockup import Mockup
from sanji.message import Message
from mock import patch
from mock import Mock

logger = logging.getLogger()

try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    from ssh import Ssh
    from ssh import SshError
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

    @patch("ssh.logger")
    @patch("ssh.Ssh.update_ssh")
    def test_run_with_SshError(self, update_ssh, logger):

        # arrange
        update_ssh.side_effect = SshError("SshError")

        # act
        Ssh.run(self.ssh)

        # assert
        assert logger.warning.called

    @patch("ssh.logger")
    @patch("ssh.Ssh.update_ssh")
    def test_run_with_update_ssh_exception(self, update_ssh, logger):

        # arrange
        update_ssh.side_effect = Exception("ssh exception")

        # act
        Ssh.run(self.ssh)

        # assert
        assert logger.error.called

    def test_do_get_should_return_db(self):

        # arrange
        self.ssh.model.db = {"enable": 1}
        mock_fun = Mock()

        # act
        Ssh.do_get(self.ssh, message=None, response=mock_fun)

        # assert
        _, kwargs = mock_fun.call_args
        self.assertEqual(kwargs["code"], 200)
        self.assertEqual(kwargs["data"], {"enable": 1})

    def test_do_put_with_invalid_message_should_return_code_400(self):

        # arrange
        message = Message({"data": {"enable": 2}})
        mock_fun = Mock()

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        _, kwargs = mock_fun.call_args
        self.assertEqual(kwargs["code"], 400)

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_should_return_code_200(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.return_value = None
        mock_fun = Mock()

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        _, kwargs = mock_fun.call_args
        self.assertEqual(kwargs["code"], 200)

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_SshError_should_return_code_400(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.side_effect = SshError("ssh failed")
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        _, kwargs = mock_fun.call_args
        self.assertEqual(kwargs["code"], 400)

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_update_ssh_failed_should_return_code_400(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.side_effect = Exception("ssh failed")
        mock_fun = Mock()

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        _, kwargs = mock_fun.call_args
        self.assertEqual(kwargs["code"], 400)
        self.assertEqual(kwargs["data"], {"message": "Fatal error"})

    @patch("ssh.subprocess")
    def test_is_ssh_running_should_return_True(self, subprocess):

        # arrange
        subprocess.call.return_value = 0

        # act
        rc = self.ssh.is_ssh_running()

        # assert
        self.assertEqual(rc, True)

    @patch("ssh.subprocess")
    def test_is_ssh_running_should_return_False(self, subprocess):

        # arrange
        subprocess.call.return_value = 1

        # act
        rc = self.ssh.is_ssh_running()

        # assert
        self.assertEqual(rc, False)

    @patch("ssh.Ssh.is_ssh_running")
    @patch("ssh.subprocess")
    def test_start_ssh_should_raise_SshError(self, subprocess, is_ssh_running):

        # arrange
        subprocess.call.return_value = 0
        is_ssh_running.return_value = False

        # act and assert
        self.assertRaises(SshError, self.ssh.start_ssh)

    @patch("ssh.Ssh.is_ssh_running")
    @patch("ssh.subprocess")
    def test_stop_ssh_should_raise_SshError(self, subprocess, is_ssh_running):

        # arrange
        subprocess.call.return_value = 0
        is_ssh_running.return_value = True

        # act and assert
        self.assertRaises(SshError, self.ssh.stop_ssh)

    @patch("ssh.Ssh.start_ssh")
    def test_update_ssh_with_start_ssh_failed_should_raise_SshError(self, start_ssh):

        # arrange
        self.ssh.model.db["enable"] = 1
        start_ssh.side_effect = SshError("ssh start failed")

        # act and assert
        self.assertRaises(SshError, self.ssh.update_ssh)

    @patch("ssh.Ssh.stop_ssh")
    def test_update_ssh_with_stop_ssh_failed_should_raise_SshError(self, stop_ssh):

        # arrange
        self.ssh.model.db["enable"] = 0
        stop_ssh.side_effect = SshError("ssh stop failed")

        # act and assert
        self.assertRaises(SshError, self.ssh.update_ssh)


if __name__ == "__main__":
    unittest.main()
