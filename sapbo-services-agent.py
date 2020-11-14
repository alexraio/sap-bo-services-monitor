#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

"""
This script get Information about the status of the SAP servers (CMS, WEBI,
CRYSTAL, etc.) on a node or a cluster and check how many of them are running
or not. It rise an Warning or an Error if one or more servers are not running.
The information about witch server should run and when to rise an event are
stored in a separate CSV file.
"""

from subprocess import Popen, PIPE
import platform
import os
import re
import glob
import csv

# This variable "CHECK_TAKEOVER" is usefull only in an AIX PowerHA enviroment
# with an Active/Passive Filesystem configuration.
# CHECK_TAKEOVER="/export/pgm$"
"""
-> Probably it would be a good idea to define all the variable into the
boadmin user enviroment.
"""
CHECKDIR = "/pgm/os/bo/"
CMS_PID = "/opt/bobj/sap_bobj/serverpids/*.CentralManagementServer.pid"
BASICRESOURCE = "resources.services.sapbo"
servicefile = "boservices.csv"
clustername = "BO_cluster_test"
bo_admin = os.environ.get('BO_ADMIN')
bo_passwd = os.environ.get('BO_PASSWD')
bo_host = os.environ.get('VBO_HOST')
cms_port = os.environ.get('CMS_PORT')

###########################################################################
#
# Function
#
###########################################################################


def getServiceName(clustername):
    return BASICRESOURCE + "." + clustername + "."


def executeCMD(thecmd):
    obj = Popen(thecmd, stdout=PIPE)
    output, stderr = obj.communicate()
    returncode = obj.returncode
    return output, stderr, returncode


########################################################
#
# MAIN
#
########################################################

"""
We support only Linux (I tested it on AIX and it is working).
Could be it is working even with Windows but I did not test it.
On all other systems the agent can run but it does not return anything
so it is esier to roll-out.
"""

if (platform.system() != 'Linux'):
    quit()

"""
The agent make sense only on SAP-BO Systems.
We check a Filesystem that exist only on SAP-BO Systems.
"""

if (not os.path.exists(CHECKDIR)):
    quit()

"""
The script schould run only on one SAP-BO cluster node,
so we check a filesystem that is only available on one side of a AIX
PowerHA Cluster.
-> This is only an example how I solve this challenge.
Try to find your own way to solve this Problem in a BO clustered enviroment.
"""

# cmd=["df"]
# output,stderr,returncode=executeCMD(cmd)
# matchTakeoverDir = re.search(CHECK_TAKEOVER, output, re.M)
# if not matchTakeoverDir:
#   quit()
# else:
#   print(matchTakeoverDir.group())

"""
The agent should not run if BO is Stopped.
With "glob" I can search for a file with regex,
then I can check if the file exist.
"""

checkCmsPid = glob.glob(CMS_PID)
if (not os.path.exists(checkCmsPid[0])):
    quit()

# ----------------------------evaluate sensor-data---------------------------

cmd = ["ccm.sh", "-display", "-cms", bo_host + ":" + cms_port, "-username", bo_admin, "-password", bo_passwd, "-authentication", "secEnterprise"]

output, stderr, returncode = executeCMD(cmd)
baseResorurce = getServiceName(clustername)

"""
In python 2.7 the output was per default utf-8 encoded.
In python 3.9 looks like that the standard is "bytes-like". As workaround
I convert the output with the decode function.
"""
output = output.decode("utf-8")

"""
The agent schould not run if there is an "Error" into the Std Output.
"""
if (returncode != 0):
    quit()

matchError = re.search("Error:", output, re.M)
if matchError:
    print(matchError.group())
    quit()
#else:
#    print("No Error: string found")

#print("XXX" + baseResorurce)
#print("ZZZ" + output)
#print("ZZZ" + str(stderr))
#print("ZZZ" + str(returncode))

with open(servicefile, 'r') as data_file:
    csv_data = csv.reader(data_file)

    """
    We don't want headers or first line of bad data when reading the csv file.
    So we use the function "next".
    """
    next(csv_data)

    # We start parsing the csv file.
    for line in csv_data:
        servicename = line[0]
        servicetorun = line[1]
        servicealarm = line[2]
        print(f'ServiceName: {servicename}, TotalServiceToRun: {servicetorun}, MinimumServiceToRunAlarm: {servicealarm}')

        outputfile = output.split("\n")
        servicecounter = 0
        runningCounter = 0
        serviceNotRunningList = []
        msg = ""
        currentService = ""
        inService = False

        # counting similar group of BO services and how many are running
        for line in outputfile:
            if line.startswith("Server Name:"):
                service = line.split(":", 1)[1]
                #print("XXX" + service)

                if servicename in service:
                    inService = True
                    servicecounter += 1
                else:
                    inService = False
            if inService:
                line = line.strip()
                if line.startswith("State:"):
                    if ("running" in line.lower()):
                        runningCounter += 1
                    else:
                        serviceNotRunningList.append(service)

        msg = str(runningCounter) + " of " + str(servicecounter) + " are running, it should be " + str(servicetorun) + " *** NOT RUNNING: " + "***".join(serviceNotRunningList)

        print("ZZZ " + baseResorurce + servicename + " *** " + msg)

        if (runningCounter < int(servicetorun)):
            print("severity: WARN")
        if (runningCounter <= int(servicealarm)):
            print("severity ERROR")
