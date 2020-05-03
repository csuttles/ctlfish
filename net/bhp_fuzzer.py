#/usr/bin/env python3

import random
from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator

from java.util import List, ArrayList


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        callbacks.registerIntruderPayloadGeneratorFactory(self)

    def getGeneratorName(self):
        return "ctlfish blackhatpython payload generator"

    def createNewInstance(self, attack):
        return BHPFuzzer(self, attack)


class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        self.max_payloads = 10
        self.num_iterations = 0

        return

    def hasMorePayloads(self):
        if self.num_iterations == self.max_payloads:
            return False
        return True

    def getNextPayload(self, current_payload):
        # convert to string
        payload = ''.join(chr(x) for x in current_payload)
        # call simple mutator to FUZZ the POST
        payload = self.mutate_paylaod(payload)
        # increase iteration count
        self.num_iterations += 1
        return payload

    def reset(self):
        self.num_iterations = 0

    def mutate_paylaod(self, original_payload):
        # here we execute a simple mutator or call a script, whatever you like
        # picker will randomize the FUZZ operations
        picker = random.randint(1, 3)

        # select a random offset in the payload to mutate
        offset = random.randint(0, len(original_payload)-1)
        payload = original_payload[:offset]

        # use picker to choose an attack schtuyle!
        if picker == 1:
            # sql injection check lulz
            payload += "'"

        if picker == 2:
            # jam in a XSS attempt lulz
            payload += '<script>alert("ctlfish!");</script>'

        if picker == 3:
            # repeat random chunk of original payload, a random number of times (let's get weird!)
            chunk_length = random.randint(len(payload[offset:]), len(payload)-1)
            repeater = random.randint(1, 10)

            for _ in range(repeater):
                payload += original_payload[offset:offset+chunk_length]

        # add the remaining payload bits
        payload += original_payload[offset:]

        return payload

