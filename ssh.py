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

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        response(data={"enable": self.model.db["enable"]})

    '''
    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        if hasattr(message, "data"):
            self.message = message.data["enable"]
            logger.debug("in put function")
            logger.debug(" put_data:%s" % db_data["enable"])
            # insert data to db
            # if update db success
                # if enable = 1
                    # restart ssh
                     #if restart success
                        #return 200
                # else
                    # stop ssh
                        # if stop db success
            # else
                # (print log message)update db failed            
            return response()
        return response(code=400, data={"message": "Invaild Input."})
    '''
    # def recover_db_from_factory(self):
    #     cmd = "cp %s %s" % (self.model_profile["model_factory_db"],
    #           self.model_profile["model_db"])
    #     subprocess.call(cmd, shell=True)

    def start_model(self):
        cmd = "service ssh start"
        subprocess.call(cmd, shell=True)
        rc = self.check_ssh()
        if rc is True:
            logger.info("ssh daemon start successfully.")
        else:
            logger.info("ssh daemon start failed.")

    def check_ssh(self):
        cmd = "ps aux | grep ssh"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   shell=True)
        grep_rc = process.communicate()[0]
        if grep_rc.find("/usr/sbin/sshd") != -1:
            return True
        else:
            return False

if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("ssh")

    ssh = Ssh(connection=Mqtt())
    ssh.start()
