#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
import jsonschema

from sanji.core import Sanji
from sanji.core import Route
from sanji.model_initiator import ModelInitiator
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()

PUT_SCHEMA = {
    "type": "object",
    "properties": {
        "enable": {
            "type": "integer",
            "maximum": 1,
            "minimum": 0
        }
    },
    "required": ["enable"],
    "additionalProperties": False
}


class Ssh(Sanji):

    def init(self, *args, **kwargs):
        path_root = os.path.abspath(os.path.dirname(__file__))
        self.model = ModelInitiator("ssh", path_root, backup_interval=1)

        self.rsp = {}
        self.rsp["code"] = 0
        self.rsp["data"] = None

    def run(self):

        try:
            self.update_ssh()
        except SshError as e:
            logger.debug("SshError exception: %s" % e)
        except Exception as f:
            logger.error("Exception error: %s" % f)

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        return self.do_get(message, response)

    def do_get(self, message, response):
        return response(data={"enable": self.model.db["enable"]})

    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        return self.do_put(message, response)

    def do_put(self, message, response):
        try:
            jsonschema.validate(message.data, PUT_SCHEMA)
        except Exception as e:
            logger.debug("Invalid Input: %s" % e)
            return response(code=400, data={"message": "Invalid Input"})

        self.model.db["enable"] = message.data["enable"]
        self.model.save_db()

        try:
            self.update_ssh()
        except SshError as e:
            logger.debug("SshError exception: %s" % e)
            return response(code=400, data={"message": e})
        except Exception as f:
            logger.error("Exception error: %s" % f)
            return response(code=400, data={"message": f})
        return response(code=200, data=self.model.db)

    def ssh_is_running(self):
        cmd = "ps aux | grep -v grep | grep /usr/sbin/sshd"
        rc = subprocess.call(cmd, shell=True)
        return rc == 0

    def start_ssh(self):
        cmd = "service ssh restart"
        subprocess.call(cmd, shell=True)
        if not self.ssh_is_running():
            raise SshError("start ssh error")

    def stop_ssh(self):
        cmd = "service ssh stop"
        subprocess.call(cmd, shell=True)
        if self.ssh_is_running():
            raise SshError("stop ssh error")

    def update_ssh(self):

        enable = self.model.db["enable"]
        assert enable == 0 or enable == 1

        if enable:
            self.start_ssh()
        else:
            self.stop_ssh()


class SshError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def main():
    ssh = Ssh(connection=Mqtt())
    ssh.start()

if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("ssh")
    main()
