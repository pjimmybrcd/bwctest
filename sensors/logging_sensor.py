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
        # Jan  1 07:26:35 ZTP_Campus_ICX7750 MAC Authentication failed for [406c.8f38.4fb7 ] on port 2/1/33 (Invalid User)
        regex = re.compile('(^\w+\s+\d+\s\d+:\d+:\d+ )([\w_-]+)( MAC Authentication failed for \[)([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})( \] on port )(\d+/\d+/\d+)( .*)')
        match = regex.match(line)
        if match:
                payload = {
                        'device': match.group(2),
                        'mac': match.group(4), 
                        'port': match.group(6)
                }
                # check to see if this exists in DB
                connection = pymysql.connect(
                   host="127.0.0.1",
                   user="root",
                   passwd="password",
                   db='users')
                cursor = connection.cursor()

                # Check to make sure this isn't already logged for tracking
                sql = "select count(*) from failed_macs where mac='%s' and device='%s' and port='%s'" % (match.group(6),match.group(2),match.group(4)) 
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                if count==0:
                    trigger = 'campus_ztp.rpvlan_new_mac_auth_failure'
                    self.sensor_service.dispatch(trigger=trigger, payload=payload)
                cursor.close()
                connection.close()
