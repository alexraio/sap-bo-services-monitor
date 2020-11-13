# sap-bo-services-monitor
Python Script to monitor the status of the SAP Business Object servers
## Intro
sap-bo-services-agent.py is a command line tool to check the status of SAP Business Object servers (CMS, WEBI, CRYSTAL, etc.) on one or more nodes and check how many of them are running. 
The script parse a CSV file where is defined the ServerName, how many server should run and the minimum number of server before to rise a Warning or an Error.
# Licence
This script is free. You can use it under the terms of GPLv2, see LICENSE.

# Development
I would like to add some functionalities as:
 * Logging to file or syslog
 * Possibility to send e-mails
 * Integration with Nagios
 
# For the community 
Feel free to contribute so that this little project can grow.

# About me
I am not a software developer so be patient if the script present errors or is not really nice to read. 
At the same time I hope to help the community as the community make with me. 
