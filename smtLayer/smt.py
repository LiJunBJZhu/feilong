#  Copyright Contributors to the Feilong Project.
#  SPDX-License-Identifier: Apache-2.0

# Daemon for Systems Management Ultra Thin Layer
#
# Copyright 2017 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from time import time

from smtLayer.ReqHandle import ReqHandle
from zvmsdk import config
from zvmsdk import log


version = '1.0.0'         # Version of this function.


class SMT(object):
    """
    Systems Management Ultra Thin daemon.
    """

    def __init__(self, **kwArgs):
        """
        Constructor

        Input:
           cmdName=<Name of command> -
              Specifies the name of the command that drives SMT.
           captureLogs=<True|False>
              Enables or disables log capture for all requests.
        """

        self.reqIdPrefix = int(time() * 100)
        self.reqCnt = 0           # Number of requests so far

        logger = log.Logger('SMT')
        logger.setup(log_dir=config.CONF.logging.log_dir,
                          log_level='logging.DEBUG',
                          log_file_name='smt.log')
        self.logger = logger.getlog()

        # Initialize the command name associated with this SMT instance.
        if 'cmdName' in kwArgs.keys():
            self.cmdName = kwArgs['cmdName']
        else:
            self.cmdName = ""

        # Setup the log capture flag.
        if 'captureLogs' in kwArgs.keys():
            self.captureLogs = kwArgs['captureLogs']
        else:
            self.captureLogs = False  # Don't capture & return Syslog entries

    def disableLogCapture(self):
        """
        Disable capturing of log entries for all requests. """

        self.captureLogs = False   # Don't capture Syslog entries

    def enableLogCapture(self):
        """
        Enable capturing of log entries for all requests. """

        self.captureLogs = True   # Begin capturing & returning Syslog entries

    def request(self, requestData, **kwArgs):
        """
        Process a request.

        Input:
           Request as either a string or a list.
           captureLogs=<True|False>
              Enables or disables log capture per request.
              This overrides the value from SMT.
           requestId=<id> to pass a value for the request Id instead of
              using one generated by SMT.

        Output:
           Dictionary containing the results.  See ReqHandle.buildReturnDict()
              for information on the contents of the dictionary.
        """

        self.reqCnt = self.reqCnt + 1

        # Determine whether the request will be capturing logs
        if 'captureLogs' in kwArgs.keys():
            logFlag = kwArgs['captureLogs']
        else:
            logFlag = self.captureLogs

        # Pass along or generate a request Id
        if 'requestId' in kwArgs.keys():
            requestId = kwArgs['requestId']
        else:
            requestId = str(self.reqIdPrefix) + str(self.reqCnt)

        rh = ReqHandle(
            requestId=requestId,
            captureLogs=logFlag,
            smt=self)

        rh.parseCmdline(requestData)
        if rh.results['overallRC'] == 0:
            rh.printSysLog("Processing: " + rh.requestString)
            rh.driveFunction()

        return rh.results
