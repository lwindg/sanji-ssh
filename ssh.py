#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt

logger = logging.getLogger()

class Ssh(Sanji):

    def init(self):
        self.message = "Hello SSH!"

    @Route(methods="get", resource="/network/ssh")
    def get(self, message, response):
        logger.debug("in get function !!")
        #self.get_row()
        response(data={"message": self.message})

    '''
    @Route(methods="put", resource="/network/ssh")
    def put(self, message, response):
        if hasattr(message, "data"):
            self.message = message.data["message"]
            return response()
        return response(code=400, data={"message": "Invaild Input."})

    @Route(methods="post", resource="/network/ssh")
    def post(self, message, response):
        if hasattr(message, "data"):
            self.message = {"id": 53}
            return response(data=self.message)
        return response(code=400, data={"message": "Invalid Post Input."})

    @Route(methods="delete", resource="/network/ssh")
    def delete(self, message, response):
        if hasattr(message, "param"):
            if "id" in message.param:
                self.message = "delete index: %s" % message.param["id"]
                return response()

        return response(code=400, data={"message": "Invalid Delete Input."})
    '''

if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(lineno)s - %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger('ssh')

    ssh = Ssh(connection=Mqtt())
    ssh.start()
