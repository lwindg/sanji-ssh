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
        logger.debug.called

    @patch("ssh.logger")
    @patch("ssh.Ssh.update_ssh")
    def test_run_with_update_ssh_exception(self, update_ssh, logger):

        # arrange
        update_ssh.side_effect = Exception("ssh exception")

        # act
        Ssh.run(self.ssh)

        # assert
        logger.called

    def test_do_get_should_return_db(self):

        # arrange
        self.ssh.model.db = {"enable": 1}
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_get(self.ssh, message=None, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["data"], {"enable": 1})

    def test_do_put_with_invalid_input_should_return_code_400(self):

        # arrange
        message = Message({})
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 400)

    def test_do_put_with_invalid_data_should_return_code_400(self):

        # arrange
        message = Message({"data": {"enable": 2}})
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 400)

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_correct_data_should_return_code_200(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.return_value = None
        mock_fun = Mock(code=400, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 200)
        self.assertEqual(mock_fun.call_args_list[0][1]["data"], {"enable": 1})

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_SshError_should_return_code_400(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.side_effect = SshError("ssh failed")
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 400)

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_update_ssh_failed_should_return_code_400(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.side_effect = Exception("ssh failed")
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 400)

    @patch("ssh.subprocess")
    def test_check_ssh_is_running_should_return_True(self, subprocess):

        # arrange
        subprocess.call.return_value = 0

        # act
        rc = self.ssh.ssh_is_running()

        # assert
        self.assertEqual(rc, True)

    @patch("ssh.subprocess")
    def test_check_ssh_is_running_should_return_False(self, subprocess):

        # arrange
        subprocess.call.return_value = 1

        # act
        rc = self.ssh.ssh_is_running()

        # assert
        self.assertEqual(rc, False)

    @patch("ssh.Ssh.ssh_is_running")
    @patch("ssh.subprocess")
    def test_start_ssh_with_ssh_is_running_success(self, subprocess, ssh_is_running):

        # arrange
        subprocess.call.return_value = 0
        ssh_is_running.return_value = True
        exception_flag = 0

        # act
        try:
            self.ssh.start_ssh()
        except Exception:
            exception_flag = 1

        # assert
        self.assertEqual(exception_flag, 0)

    @patch("ssh.Ssh.ssh_is_running")
    @patch("ssh.subprocess")
    def test_start_ssh_with_ssh_is_running_failed(self, subprocess, ssh_is_running):

        # arrange
        subprocess.call.return_value = 0
        ssh_is_running.return_value = False
        exception_flag = 0

        # act
        try:
            self.ssh.start_ssh()
        except Exception:
            exception_flag = 1

        # assert
        self.assertEqual(exception_flag, 1)

    @patch("ssh.Ssh.ssh_is_running")
    @patch("ssh.subprocess")
    def test_stop_ssh_with_ssh_is_running_success(self, subprocess, ssh_is_running):

        # arrange
        subprocess.call.return_value = 0
        ssh_is_running.return_value = False
        exception_flag = 0

        # act
        try:
            self.ssh.stop_ssh()
        except Exception:
            exception_flag = 1


        # assert
        self.assertEqual(exception_flag, 0)

    @patch("ssh.Ssh.ssh_is_running")
    @patch("ssh.subprocess")
    def test_stop_ssh_with_ssh_is_running_failed(self, subprocess, ssh_is_running):

        # arrange
        subprocess.call.return_value = 0
        ssh_is_running.return_value = True
        exception_flag = 0

        # act
        try:
            self.ssh.stop_ssh()
        except Exception:
            exception_flag = 1

        # assert
        self.assertEqual(exception_flag, 1)

    @patch("ssh.Ssh.start_ssh")
    def test_update_ssh_with_start_ssh_failed(self, start_ssh):

        # arrange
        self.ssh.model.db["enable"] = 1
        start_ssh.side_effect = SshError("ssh start failed")
        exception_flag = 0

        # act
        try:
            self.ssh.update_ssh()
        except Exception:
            exception_flag = 1

        # assert
        self.assertEqual(exception_flag, 1)

    @patch("ssh.Ssh.stop_ssh")
    def test_update_ssh_with_stop_ssh_failed(self, stop_ssh):

        # arrange
        self.ssh.model.db["enable"] = 0
        stop_ssh.side_effect = SshError("ssh stop failed")
        exception_flag = 0

        # act
        try:
            self.ssh.update_ssh()
        except Exception:
            exception_flag = 1

        # assert
        self.assertEqual(exception_flag, 1)


if __name__ == "__main__":
    unittest.main()
