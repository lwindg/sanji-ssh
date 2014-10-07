#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
import uuid
from sanji.core import Sanji
from sanji.core import Route
from sanji.model_initiator import ModelInitiator
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()


class Ssh(Sanji):

    def init(self, *args, **kwargs):
        path_root = os.path.abspath(os.path.dirname(__file__))
        self.model = ModelInitiator("ssh", path_root)
        if self.model.db["enable"] == 1:
            self.start_model()

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        return response(data={"enable": self.model.db["enable"]})

    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        if hasattr(message, "data"):
            enable = message.data["enable"]
            self.model.db["enable"] = message.data["enable"]
            self.model.save_db()
            self.update_ssh(enable, message, response)

    def start_model(self):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is True:
            logger.info("ssh daemon start successfully.")
        else:
            logger.info("ssh daemon start failed.")

    def check_ssh(self):
        find_process = None
        cmd = "ps aux | grep ssh"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   shell=True)
        grep_rc = process.communicate()[0]
        find_process = grep_rc.find("/usr/sbin/sshd")
        if find_process != -1:
            return True
        else:
            return False

    def start_ssh(self, message, response):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is True:
            logger.info("ssh daemon start successfully.")
            return response(data=message.data)
        else:
            logger.info("ssh daemon start failed.")
            return response(code=400,
                            data={"message": "ssh daemon start failed"})

    def stop_ssh(self, message, response):
        cmd = "service ssh stop"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is False:
            logger.info("ssh daemon stop successfully.")
            return response(data=message.data)
        else:
            logger.info("ssh daemon stop failed.")
            return response(code=400,
                            data={"message": "ssh daemon stop failed"})

    def update_ssh(self, enable, message, response):
        if enable == 1:
            self.start_ssh(message, response)
        else:
            self.stop_ssh(message, response)


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("ssh")

    ssh = Ssh(connection=Mqtt())
    ssh.start()
