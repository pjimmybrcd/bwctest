# Campus ZTP Integration Pack
The following pack piggy backs off of the Campus ZTP Integration Pack available online on GitHub.
https://github.com/tbrawly/campus_ztp

This integration pack works with Brocade Workflow Composer (BWC) to enhance Zero Touch Provisioning (ZTP) to reliably setup ICX campus access Ethernet switches.

BWC is a platform for integration and automation across services and tools. It ties together your existing infrastructure and application environment so you can more easily automate that environment. It has a particular focus on taking actions in response to events.

## Overview
The following BWC pack monitors a syslog file on the local machine to determine whether a tigger needs to be set off. To do so, all syslog messages are compared with a Regular Expression in the logging watch sensor. In the event of an mac auth failure in the following syslog format: 
	"Jan 1 07:26:35 ZTP_Campus_ICX7750 172.20.40.243 MACAUTH: Port 1/1/48 Mac 406c.8f38.4fb7 - authentication failed since RADIUS server rejected"
the mac address is compared to the list of authorized macs in the the database. If there is a match, a action chain is issued which first changes the configuration on the switch then updated the table in the database. If the mac is not an entry in the authorized table, the information will be stored in the failures table for reference if need be.

In the event of a port disable or shutdown, a syslog of the format:
	"Dec 19 17:10:17 RSOC-TEST-STACK 172.20.40.243 System: Interface ethernet 2/1/29, state down"
is matched then the sensor will check to see if the port on the switch was authorized. If it was, then the template will be sent to the switch removing the configuration changes that were made previously.

## Getting Started

Follow these steps to get started with this integration pack.

1. You will need to have BWC already installed. Follow these steps here: https://bwc-docs.brocade.com/install/bwc.html
2. You have access to the gitlab monte project.
3. You have rsyslog installed on the BWC machine.
4. You have MySQL-Server installed on the BWC machine.
5. BWC architecture can be an all in one on a single box or with separate nodes for work and sensor nodes. Either way these nodes will need network connectivity to the management network with the switches being provisioned.
6. ZTP relies on a TFTP and DHCP server which will also need to have network connectivity to the switches.

##Prereqs:
The following pack requires a MySQL database where authorized devices can be stored. It also requires syslogs to be appended to a log file through rsyslogd

To install MySQL do the following:
1. Run: sudo apt-get install mysql-server
2. Run: sudo mysql_secure_installation

Create the database and tables
1. Run: mysql -u <username> -p
2. Run: CREATE database users;
3. Run: USE users;
4. Run: CREATE table failures (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	mac varchar(20),
	device VARCHAR(11),
	port varchar (10)	
	);
5. Run: CREATE table authorized (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	mac varchar(20),
	device VARCHAR(11),
	port varchar (10)	
	);
6. Add your authorized macs to the authorized table. Writing a script to do this would be the most effecient way to do this. But the command below demonstrates how this can be done in mysql:
	ex: INSERT INTO authorized (mac) values('0000.0000.0000');

To install rsyslog
1. Run: sudo apt-get install rsyslog
2. Configure rsyslog to store logs in: "/var/log/syslog"

## Installation of Campus ZTP Pack

1. Run: st2 pack install https://github.com/monterey/monte.git
2. Run: st2ctl reload
3. Open: BWC GUI on your browser

# Campus ZTP
Edit the config.yaml for your environment

* `templates` - directory where templates are stored
* `excel` - location of excel spreadsheet of configuration data
* `config_backup_dir` - location of switches backup files
* `tmp_dir` - location where configuration file will be temporary stored before SCP

## Setting Username and Encrypted passwords in datastore

Ensure that you've set up BWC for encrypted datastore. See https://docs.stackstorm.com/datastore.html

And then add the following items (replacing it with your username and password)

```
st2 key set campus_ztp.username '<switch_username>'
st2 key set campus_ztp.password '<switch_password>' --encrypt
st2 key set campus_ztp.enable_username '<switch_username>'
st2 key set campus_ztp.enable_password '<switch_password>' --encrypt
```

## Additional Notes:
The sensor being used, LoggingWatchSensor, tails a log file on the BWC machine.
In the config.yaml file the LoggingWatchSensor and SyslogWatchSensor are set to look at the "/var/log/syslog" log file. You will need to rename this file if you are logging ot a different file.

## Removal of Campus ZTP Pack

1. Run: st2 pack remove campus_ztp
2. Run: st2ctl reload

## License

Campus_ZTP is released under the APACHE 2.0 license. See ./LICENSE for more information.
