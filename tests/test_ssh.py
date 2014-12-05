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
        message = Message({"data": {"enable": 56}})
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
        update_ssh.return_value = True
        self.ssh.rsp["code"] = 200
        self.ssh.rsp["data"] = {"enable": 1}
        mock_fun = Mock(code=400, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 200)
        self.assertEqual(mock_fun.call_args_list[0][1]["data"], {"enable": 1})

    @patch("ssh.Ssh.update_ssh")
    def test_do_put_with_update_ssh_failed_should_return_code_400(self, update_ssh):

        # arrange
        message = Message({"data": {"enable": 1}})
        update_ssh.return_value = False
        mock_fun = Mock(code=200, data=None)

        # act
        Ssh.do_put(self.ssh, message=message, response=mock_fun)

        # assert
        self.assertEqual(len(mock_fun.call_args_list), 1)
        self.assertEqual(mock_fun.call_args_list[0][1]["code"], 400)

    @patch("ssh.subprocess")
    def test_check_ssh_should_return_True(self, subprocess):

        # arrange
        subprocess.call.return_value = 0

        # act
        rc = self.ssh.check_ssh()

        # assert
        self.assertEqual(rc, True)

    @patch("ssh.subprocess")
    def test_check_ssh_should_return_False(self, subprocess):

        # arrange
        subprocess.call.return_value = 1

        # act
        rc = self.ssh.check_ssh()

        # assert
        self.assertEqual(rc, False)

    @patch("ssh.Ssh.check_ssh")
    @patch("ssh.subprocess")
    def test_start_ssh_with_check_ssh_success_should_return_code_200(self, subprocess, check_ssh):

        # arrange
        subprocess.call.return_value = 0
        check_ssh.return_value = True

        # act
        rc = self.ssh.start_ssh()

        # assert
        self.assertEqual(self.ssh.rsp["code"], 200)
        self.assertEqual(rc, True)

    @patch("ssh.Ssh.check_ssh")
    @patch("ssh.subprocess")
    def test_start_ssh_with_check_ssh_failed_should_return_code_400(self, subprocess, check_ssh):

        # arrange
        subprocess.call.return_value = 0
        check_ssh.return_value = False

        # act
        rc = self.ssh.start_ssh()

        # assert
        self.assertEqual(self.ssh.rsp["code"], 400)
        self.assertEqual(rc, False)

    @patch("ssh.Ssh.check_ssh")
    @patch("ssh.subprocess")
    def test_stop_ssh_with_check_ssh_success_should_return_code_200(self, subprocess, check_ssh):

        # arrange
        subprocess.call.return_value = 0
        check_ssh.return_value = False

        # act
        rc = self.ssh.stop_ssh()

        # assert
        self.assertEqual(self.ssh.rsp["code"], 200)
        self.assertEqual(rc, True)

    @patch("ssh.Ssh.check_ssh")
    @patch("ssh.subprocess")
    def test_stop_ssh_with_check_ssh_failed_should_return_code_400(self, subprocess, check_ssh):

        # arrange
        subprocess.call.return_value = 0
        check_ssh.return_value = True

        # act
        rc = self.ssh.stop_ssh()

        # assert
        self.assertEqual(self.ssh.rsp["code"], 400)
        self.assertEqual(rc, False)

    @patch("ssh.Ssh.start_ssh")
    def test_update_ssh_with_start_ssh_should_return_true(self, start_ssh):

        # arrange
        self.ssh.model.db["enable"] = 1
        start_ssh.return_value = True

        # act
        rc = self.ssh.update_ssh()

        # assert
        self.assertEqual(rc, True)

    @patch("ssh.Ssh.stop_ssh")
    def test_update_ssh_with_stop_ssh_should_return_true(self, stop_ssh):

        # arrange
        self.ssh.model.db["enable"] = 0
        stop_ssh.return_value = True

        # act
        rc = self.ssh.update_ssh()

        # assert
        self.assertEqual(rc, True)


if __name__ == "__main__":
    unittest.main()
