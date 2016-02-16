#!/usr/bin/env python3

import sensors

class SmManager:
    chips=[] #1 domension only
    chipsVal=[]

    def start(self):
        sensors.init()
        for i in sensors.iter_detected_chips():
            for j in i:
                self.chips.append(j)
                self.chipsVal.append(j.get_value())

    def stop(self):
        sensors.cleanup()
        self.chips=[]
        self.chipsVal=[]

    def restart(self):
        self.stop()
        self.start()
