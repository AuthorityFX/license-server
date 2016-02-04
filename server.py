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
import subprocess
import sys
import datetime
import smtplib
import string
import os
import threading
import Queue

#Email server
class SendMail:

    def __init__(self):
        try:
            self._server = smtplib.SMTP("smtp.gmail.com", 587)
            self._server.ehlo()
            self._server.starttls()
            self._server.ehlo()
            self._server.login("username", "password")
        except Exception, e:
            raise Exception("Could connect to pop server - " + str(e))

    def send_mail(self, receipient, subject, message):

        sender = "licensing@authorityfx.com"

        body = string.join((
        "From: %s" % sender,
        "To: %s" % receipient,
        "Subject: %s" % subject,
        "", message
        ), "\r\n")

        try:
            self._server.sendmail(sender, [receipient], body)
        except Exception, e:
            raise Exception("Could not send email - " + str(e))

    def __del__(self):
        self._server.quit()

#LicenseServer
class LicenseServer:

    def __init__(self):
        self._HOST = ''
        self._PORT = 31568
        self._ADDR = (self._HOST, self._PORT)
        self._BUFSIZE = 4096

        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(self._ADDR,)

            self._client_pool = Queue.Queue(0)

            self._running = True
        except Exception, e:
            print str(e)


    def start(self):

        print "*********************************"
        print "Authority FX - Web License Server"
        print "*********************************"
        print
        print "listening..."
        print

        #Set running
        self._running = True

        #Loop while running
        while self._running == True:
            try:
                self._server.listen(5)
                self._client_pool.put(self._server.accept())
            except Exception, e:
                print e
                mail = SendMail()
                mail.send_mail('licensing@authorityfx.com', 'License server shutdown - ' + str(r), 'License server shutdown - ' + str(r))
            except KeyboardInterrupt:
                self.stop()


    def get_client(self):
        return self._client_pool.get()

    def task_done(self):
        self._client_pool.task_done()

    def get_buffer_size(self):
        return self._BUFSIZE

    def is_running(self):
        return self._running

    def stop(self):
        self._running = False
        #Allow client threads to finish before shutdown
        self._client_pool.join()
        #Close socket
        try:
            self._server.close()
            print "Stopped."
        except:
            print "No server running to close"

    def __del__(self):
        self.stop()


#Client thread
class ClientThread(threading.Thread):

    def run(self):

        while server.is_running() == True:
            try:
                #Block here until queue has connection
                self._client = server.get_client()
                if self._client != None:

                    self._conn = self._client[0]
                    self._addr = self._client[1]
                    if self.check_client() == 0:
                        self.get_license()
            except Exception, e:
                print 'Client error: ' + str(e)
            finally:
                #Tell parse pool task is done
                server.task_done()

    def check_client(self):

        #conn_ip = str(socket.gethostbyaddr("www.licensing.authorityfx.com")[2])
        conn_ip = '199.115.119.195'
        if conn_ip.find(self._addr[0]) >= 0 or 1 == 1: #TODO remove this 1==1
            return 0
        else:
            self.close_connection() #close connection!
            msg = "Connection refused: " + str(self._addr) + " at " + str(datetime.datetime.now())
            sefl.log_msg(msg)
            mail = SendMail()
            mail.send_mail('plugins@authorityfx.com', msg, msg)
            return 1

    def get_license(self):

        try:

            license_req = self._conn.recv(server.get_buffer_size())

            licensegen = subprocess.Popen(['./generator', license_req], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            license, err = licensegen.communicate()

            #If error from license generator
            if (err):
                msg = "Licensing Error - " + err + " at - " + str(datetime.datetime.now()) + "\n" + license_req + "\n"
            else:
                msg = "License sent to web portal at - " + str(datetime.datetime.now()) + "\n" + license_req + "\n"
        except Exception, e:
            msg = "Licensing Error - " + str(e) + " at - " + str(datetime.datetime.now()) + "\n" + license_req + "\n"
        finally:
            self.log_msg(msg)
            self._conn.send(license)
            self._conn.close()
            mail = SendMail()
            mail.send_mail('plugins@authorityfx.com', msg, msg)

    def close_connection(self):
        try:
            self._conn.close()
        except:
            print "No connection open to close"

    def log_msg(self, msg):
        print msg
        f = open('server.log', 'a')
        f.write(msg + "\n")
        f.close()


#Main___________________________________________


#Create license server
server = LicenseServer()

#Client Threads
client_threads = []
num_threads = 4

#Start client threads
for i in range(num_threads):
    client_threads.append(ClientThread())
    client_threads[i].setDaemon(True)
    client_threads[i].start()

#Start server
server.start()
