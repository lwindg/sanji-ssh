#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
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
        self.rsp = {}
        self.rsp["code"] = 0
        self.rsp["data"] = None

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        return response(data={"enable": self.model.db["enable"]})

    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        if hasattr(message, "data"):
            self.model.db["enable"] = message.data["enable"]
            self.model.save_db()
            self.update_ssh()
            return response(code=self.rsp["code"], data=self.rsp["data"])
        return response(code=400, data={"message": "Invaild Input"})

    def start_model(self):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is True:
            logger.info("ssh daemon start successfully.")
        else:
            logger.info("ssh daemon start failed.")

    def check_ssh(self):
        cmd = "ps aux | grep -v grep | grep ssh"
        rc = subprocess.call(cmd, shell=True)
        return True if rc == 0 else False

    def start_ssh(self):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is True:
            logger.info("ssh daemon start successfully.")
            self.rsp["code"] = 200
            self.rsp["data"] = {"enable": self.model.db["enable"]}
            return True
        else:
            logger.info("ssh daemon start failed.")
            self.rsp["code"] = 400
            self.rsp["data"] = {"message": "ssh daemon start failed"}
            return False

    def stop_ssh(self):
        cmd = "service ssh stop"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is False:
            logger.info("ssh daemon stop successfully.")
            self.rsp["code"] = 200
            self.rsp["data"] = {"enable": self.model.db["enable"]}
            return True
        else:
            logger.info("ssh daemon stop failed.")
            self.rsp["code"] = 400
            self.rsp["data"] = {"message": "ssh daemon stop failed"}
            return False

    def update_ssh(self):
        if self.model.db["enable"] == 1:
            return self.start_ssh()
        elif self.model.db["enable"] == 0:
            return self.stop_ssh()


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("ssh")

    ssh = Ssh(connection=Mqtt())
    ssh.start()
