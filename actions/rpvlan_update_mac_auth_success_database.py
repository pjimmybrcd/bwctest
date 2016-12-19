from st2actions.runners.pythonrunner import Action

import pymysql.cursors
import json

class RpvlanUpdateMacAuthFailureDatabaseAction(Action):
  def __init__(self,config):
     super(RpvlanUpdateMacAuthFailureDatabaseAction, self).__init__(config)

  def run(self,device,mac,port):

     self.process_mac_failure(device,port,mac)

     # TODO: Report errors like database failure!
     return (True)

  def process_mac_failure(self,device,port,mac):

        connection = pymysql.connect(
             host="127.0.0.1", 
             user="root",      
             passwd="password",  
             db='users')        

        #Remove the mac addr tuple in table may not be in there but it's fine
	cursor = connection.cursor()
	sql = "delete from authorized_macs where mac='%s'" % (mac)
        cursor.execute(sql)
        connection.commit()
	cursor.close()

	#Insert new row.
	cursor = connection.cursor()
        sql = "insert into access_points (mac, device, port) values('%s','%s','%s')" % (mac,device,port)
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        connection.close()
	
	#TODO Update VLAN on ICX port
