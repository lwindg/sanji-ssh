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
        self.model = ModelInitiator("ssh", path_root, backup_interval=1)

        self.rsp = {}
        self.rsp["code"] = 0
        self.rsp["data"] = None

    def run(self):
        rc = self.update_ssh()
        if rc is False:
            logger.debug("model init error")

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        return self.do_get(message, response)

    def do_get(self, message, response):
        return response(data={"enable": self.model.db["enable"]})

    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        return self.do_put(message, response)

    def do_put(self, message, response):
        if not(hasattr(message, "data")):
            logger.debug("Invalid Input")
            return response(code=400, data={"message": "Invalid Input"})

        if ("enable" not in message.data) or ((message.data["enable"] != 0)
                                              and (message.data["enable"] != 1)
                                              ):
            logger.debug("Invalid Data ")
            return response(code=400, data={"message": "Invalid Data"})

        self.model.db["enable"] = message.data["enable"]
        self.model.save_db()

        rc = self.update_ssh()

        if rc is False:
            return response(code=400, data={"message": "update_ssh failed"})
        return response(code=self.rsp["code"], data=self.rsp["data"])

    def check_ssh(self):
        cmd = "ps aux | grep -v grep | grep /usr/sbin/sshd"
        rc = subprocess.call(cmd, shell=True)
        return True if rc == 0 else False

    def start_ssh(self):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()

        if rc is True:
            logger.info("ssh start success")
            self.rsp["code"] = 200
            self.rsp["data"] = {"enable": self.model.db["enable"]}
            return True
        else:
            logger.info("ssh start failed.")
            self.rsp["code"] = 400
            self.rsp["data"] = {"message": "ssh start failed"}
            return False

    def stop_ssh(self):
        cmd = "service ssh stop"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()

        if rc is False:
            logger.info("ssh stop success")
            self.rsp["code"] = 200
            self.rsp["data"] = {"enable": self.model.db["enable"]}
            return True
        else:
            logger.info("ssh stop failed.")
            self.rsp["code"] = 400
            self.rsp["data"] = {"message": "ssh stop failed"}
            return False

    def update_ssh(self):

        # start or stop ssh by enable
        if self.model.db["enable"] == 1:
            return self.start_ssh()
        elif self.model.db["enable"] == 0:
            return self.stop_ssh()


def main():
    ssh = Ssh(connection=Mqtt())
    ssh.start()

if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("ssh")
    main()
