#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os
import subprocess
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()

path_root = os.path.abspath(os.path.dirname(__file__))

# #Model's profile
# model_profile = {
#     "model_db": path_root + "/db/ssh.json",
#     "model_factory_db": path_root + "/db/ssh.factory.json",
#     "model_backup_db": path_root + "/db/ssh.backup.json",
# }

# model's db data
db_data = {
    "enable": 1,
}


class Ssh(Sanji):

    def init(self, *args, **kwargs):
        self.message = "Hello SSH!"
        # #init model db
        # #chcek if db file exist
        # if os.path.isfile(self.model_profile["model_db"]) is not True:
        #     self.recover_db_from_factory()
        #     self.save_db_to_bacuup()

        # # load data from db file to db_data  
        # load_database_data()

        if db_data["enable"] == 1:
            self.start_model()

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        logger.debug("in get function !!")
        response(data={"enable": db_data["enable"]})

    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        if hasattr(message, "data"):
            self.message = message.data["enable"]
            logger.debug("in put function")
            logger.debug(" put_data:%s" % db_data["enable"])
            return response()
        return response(code=400, data={"message": "Invaild Input."})

    # def recover_db_from_factory(self):
    #     cmd = "cp %s %s" % (self.model_profile["model_factory_db"],
    #           self.model_profile["model_db"])
    #     subprocess.call(cmd, shell=True)

    def start_model(self):
        cmd = "service ssh start"
        subprocess.call(cmd, shell=True)
        rtn_code = self.check_ssh()
        if rtn_code is True:
            logger.info("ssh start success")
        else:
            logger.info("ssh start fail")

    def check_ssh(self):
        cmd = "ps aux | grep ssh"
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   shell=True)
        grep_rtn = process.communicate()
        if grep_rtn[0].find("/usr/sbin/sshd") != -1:
            logger.debug("------------------>check ssh success")
            return True
        else:
            logger.debug("------------------>check ssh fail")
            return False
 
if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger('ssh')

    ssh = Ssh(connection=Mqtt())
    ssh.start()
