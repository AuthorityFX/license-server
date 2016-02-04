# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2012-2016, Ryan P. Wilson
#
#     Authority FX, Inc.
#     www.authorityfx.com

#!/usr/bin/env python

import socket
import sys

class licenceFormat:

    def __init__(self):
        self._plugins = ""
        self._num_plugs = 0

    def set_mac(self, mac):
        self._mac = mac

    def set_hdd(self, hdd):
        self._hdd = hdd

    def add_plugin(self, name, l_type, count, floating):
        self._plugins += name + "[" + str(l_type) + "," + str(count) + "," + str(floating) + "]"
        self._num_plugs += 1

    def format_license(self):
        return "num_plugs={" + str(self._num_plugs) + "}plugins={" + self._plugins + "}uuid1={" + self._mac + "}uuid2={" + self._hdd + "}"

class licenseClient:

    def __init__(self, host, port):
        self._HOST = host
        self._PORT = port
        self._ADDR = (self._HOST, self._PORT)
        self._BUFSIZE = 4096

        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._client.connect(self._ADDR,)

    def get_license(self, license):

        self._client.send(license)
        license = self._client.recv(self._BUFSIZE)
        return license

    def __del__(self):
        self._client.close()


try:
    license = licenceFormat()

    #Plugin id, license type, count
    license.add_plugin("glow", 0, 1, 0)
    license.add_plugin("lens_glow", 0, 1, 0)
    license.add_plugin("soft_clip", 0, 1, 0)
    license.set_mac("bh87fyiugf")
    license.set_hdd("uytgid7t12uf7t12d")

    client = licenseClient("67.70.80.214", 31568)
    ciph = client.get_license(license.format_license())
    print ciph

except Exception, e:
    print str(e)
