#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import logging
import subprocess
from sanji.core import Sanji
from sanji.core import Route
from sanji.connection.mqtt import Mqtt
from sanji.model_initiator import ModelInitiator


logger = logging.getLogger()


class Watchdog(Sanji):

    def init(self, *args, **kwargs):
        path_root = os.path.abspath(os.path.dirname(__file__))
        self.model = ModelInitiator("watchdog", path_root)
        subprocess.call("monit quit", shell=True)
        subprocess.call("monit -c data/monitrc -d 2", shell=True)
        self.processes = []

    def monit_reload(self):
        try:
            fd = open("/etc/monit/monitrc", "w")
            for process in self.processes:
                fd.write("check process %s\n" % process["process"])
                fd.write("\tmatching \"%s\"\n" % process["process"])
                fd.write("\tstart program = \"%s\"\n"
                         % process["path"])
                fd.write("\tstop program = \"/usr/bin/killall -9 %s\"\n"
                         % process["process"])

            fd.closed()
            subprocess.call("monit quit", shell=True)
            subprocess.call("monit -c data/monitrc -d 2", shell=True)
            return True
        except Exception:
                logger.debug("Open error")
                return False

    @Route(methods="get", resource="/system/watchdog")
    def get_root(self, message, response):
            return response(code=200, data=self.processes)

    @Route(methods="put", resource="/system/watchdog")
    def put_root(self, message, response):
        if not hasattr(message, "data"):
            return response(code=400, data={"message": "Invalid Input."})

        if "process" in message.data and "path" in message.data:
            for process in self.processes:
                logger.debug("Process name: %s" % process["process"])
                if message.data["process"] == process["process"]:
                    logger.debug("Process already register")
                    return response(code=400, data={
                        "message": "Process already register"})
            self.processes.append({
                "id": len(self.processes)+1,
                "path": message.data["path"],
                "process": message.data["process"]})
            self.monit_reload()
            return response(code=200)

    @Route(methods="delete", resource="/system/watchdog/:id")
    def delete_root(self, message, response):
        if "id" in message.param:
            if int(message.param["id"]) <= len(self.processes):
                del self.processes[int(message.param["id"]) - 1]
                self.monit_reload()
                return response(code=200)

        return response(code=400)

if __name__ == "__main__":
    FORMAT = "%(asctime)s - %(levelname)s - %(lineno)s - %(message)s"
    logging.basicConfig(level=0, format=FORMAT)
    logger = logging.getLogger("Sanji Watchdog")

    watchdog = Watchdog(connection=Mqtt())
    watchdog.start()
