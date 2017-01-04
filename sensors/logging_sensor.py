import os,re

import pymysql

from logshipper.tail import Tail

from st2reactor.sensor.base import Sensor


class LoggingWatchSensor(Sensor):
    def __init__(self, sensor_service, config=None):
        super(LoggingWatchSensor, self).__init__(sensor_service=sensor_service,
                                              config=config)
        self._config = self._config['logging_watch_sensor']

        self._file_paths = self._config.get('logging_paths', [])
        self._trigger_ref = 'campus_ztp.logging_watch.line'
        self._tail = None

    def setup(self):
        if not self._file_paths:
            raise ValueError('No file_paths configured to monitor')

        self._tail = Tail(filenames=self._file_paths)
        self._tail.handler = self._handle_line
        self._tail.should_run = True

    def run(self):
        self._tail.run()

    def cleanup(self):
        if self._tail:
            self._tail.should_run = False

            try:
                self._tail.notifier.stop()
            except Exception:
                pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass

    def _handle_line(self, file_path, line):
        #Dec 19 17:10:17 RSOC-TEST-STACK 172.20.40.243 System: Interface ethernet 2/1/29, state down
        regex = re.compile('(^\w+\s+\d+\s\d+:\d+:\d+ )([\w_-]+ )(\d+\.\d+\.\d+\.\d+)( System: Interface ethernet )(\d+\/\d+\/\d+)(, state down)')
        match = regex.match(line)
        if match:
                payload = {
                        'device': match.group(3),
                        'port': match.group(5)
                }
                # check to see if this port is being used
                connection = pymysql.connect(
                   host="127.0.0.1",
                   user="root",
                   passwd="brocade",
                   db='users')
                cursor = connection.cursor()

                # Check to make sure this port was previously authorized
                sql = "select count(*) from authorized where port='%s'" % (payload["port"]) 
                
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                if count!=0:
                    print "port should be reverted"
                    trigger = 'campus_ztp.rpvlan_port_down'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                cursor.close()
                connection.close()
                return

        #Jan  4 14:00:49 ING-135-01 172.20.41.44 MAC Authentication failed for [f8e7.1e0f.9083 ] on port 8/1/36 (Invalid User)
        regex = re.compile('(^\w+\s+\d+\s\d+:\d+:\d+ )([\w_-]+ )(\d+\.\d+\.\d+\.\d+)( MAC Authentication failed for \[)([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})( \] on port )(\d+\/\d+\/\d+)( \(Invalid User\).*)')
        match = regex.match(line)
        if match:
                payload = {
                        'device': match.group(3),
                        'mac': match.group(5), 
                        'port': match.group(7)
                }
                # check to see if this exists in DB
                connection = pymysql.connect(
                   host="127.0.0.1",
                   user="root",
                   passwd="brocade",
                   db='users')
                cursor = connection.cursor()

                # Check to make sure this isn't already logged for tracking
                sql = "select count(*) from authorized where mac='%s'" % (payload["mac"]) 
                
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                if count==0:
                    print "should not allow"
                    trigger = 'campus_ztp.rpvlan_new_mac_auth_failure_do_not_allow'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                else:
                    print "should allow"
                    trigger = 'campus_ztp.rpvlan_new_mac_auth_failure'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                cursor.close()
                connection.close()
                return


        # Jan 1 07:26:35 ZTP_Campus_ICX7750 172.20.40.243 MACAUTH: Port 1/1/48 Mac 406c.8f38.4fb7 - authentication failed since RADIUS server rejected
        regex = re.compile('(^\w+\s+\d+\s\d+:\d+:\d+ )([\w_-]+ )(\d+\.\d+\.\d+\.\d+)( MACAUTH: Port )(\d+\/\d+\/\d+)( Mac )([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})( - authentication failed.*)')
        match = regex.match(line)
        if match:
                payload = {
                        'device': match.group(3),
                        'mac': match.group(7), 
                        'port': match.group(5)
                }
                # check to see if this exists in DB
                connection = pymysql.connect(
                   host="127.0.0.1",
                   user="root",
                   passwd="brocade",
                   db='users')
                cursor = connection.cursor()

                # Check to make sure this isn't already logged for tracking
                sql = "select count(*) from authorized where mac='%s'" % (payload["mac"]) 
                
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                if count==0:
                    print "should not allow"
                    trigger = 'campus_ztp.rpvlan_new_mac_auth_failure_do_not_allow'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                else:
                    print "should allow"
                    trigger = 'campus_ztp.rpvlan_new_mac_auth_failure'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                cursor.close()
                connection.close()
                return






