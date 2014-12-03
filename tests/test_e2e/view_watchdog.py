#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging

from sanji.core import Sanji
from sanji.connection.mqtt import Mqtt


REQ_RESOURCE = "/system/watchdog"


class View(Sanji):

    # This function will be executed after registered.
    def run(self):

        # Add new resource A to watchdog
        print "PUT %s" % REQ_RESOURCE
        res = self.publish.put(REQ_RESOURCE,
                               data={"process": "process_D",
                                     "path": "/home/moxa/test-process.sh"})
        if res.code != 200:
            print "GET should reply code 200 instead of %s" % res.code
            self.stop()
        else:
            print res.to_json()

        # Add new resource B to watchdog
        print "PUT %s" % REQ_RESOURCE
        res = self.publish.put(REQ_RESOURCE,
                               data={"process": "test-process.sh",
                                     "path": "/home/moxa/test-process.sh"})
        if res.code != 200:
            print "GET should reply code 200 instead of %s" % res.code
            self.stop()
        else:
            print res.to_json()

        # Get resource from watchdog
        print "GET %s" % REQ_RESOURCE
        res = self.publish.get(REQ_RESOURCE)
        if res.code != 200:
            print "GET should reply code 200"
        else:
            print res.to_json()
            self.stop()

        # Delete resource A from watchdog
        print "DELETE %s/1" % REQ_RESOURCE
        res = self.publish.delete(REQ_RESOURCE+"/1")
        if res.code != 200:
            print "DELETE should reply code 200"
            self.stop()
        else:
            print res.to_json()

        # Delete same resource A from watchdog
        print "DELETE %s/1" % REQ_RESOURCE
        res = self.publish.delete(REQ_RESOURCE+"/1")
        if res.code == 200:
            print "DELETE should not reply code 200"
            self.stop()
        else:
            print res.to_json()

        print "GET AGAIN %s" % REQ_RESOURCE
        res = self.publish.get(REQ_RESOURCE)
        if res.code != 200:
            print "GET should reply code 200"
            self.stop()
        else:
            print res.to_json()


if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("Watchdog")

    view = View(connection=Mqtt())
    view.start()
