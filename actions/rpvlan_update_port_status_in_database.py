from st2actions.runners.pythonrunner import Action

import pymysql.cursors

class RpvlanUpdateMacAuthFailureDatabaseAction(Action):
  def __init__(self,config):
     super(RpvlanUpdateMacAuthFailureDatabaseAction, self).__init__(config)

  def run(self,device,port,vlan,action):

     if action=='add':
         self.process_add_port(device,port,vlan)

     if action=='remove':
         self.process_remove_port(device,port,vlan)

     # TODO: Report errors like database failure!
     return (True)

  def process_add_port(self,device,port,vlan):

        connection = pymysql.connect(
             host="10.0.0.43", 
             user="nps_remote",      
             passwd="password",  
             db='nps') 

        with connection.cursor() as cursor:
            # TODO: Check if mac is already in database and see if it's moved, etc
            # Write failed mac to database
            sql = "insert into ports values (%d,'%s','%s',NOW())" % (vlan,device,port)
            print(sql)
            cursor.execute(sql)
            connection.commit()

        connection.close()

  def process_remove_port(self,device,port,vlan):

        connection = pymysql.connect(
             host="10.0.0.43", 
             user="nps_remote",      
             passwd="password",  
             db='nps') 

        with connection.cursor() as cursor:
            # Delete port from database
            sql = "delete from ports where device='%s' and port='%s' and vlan_id=%d" % (device, port, vlan)
            print(sql)
            cursor.execute(sql)
            connection.commit()

            # Delete any un-auth macs from port from database
            sql = "delete from failed_mac_locations where device='%s' and port='%s'" % (device, port)
            print(sql)
            cursor.execute(sql)
            connection.commit()

            # Are there any more ports left in this vlan
            sql = "select count(*) from ports where vlan_id=%d" % (vlan)
            print(sql)
            cursor.execute(sql)
	    if cursor.fetchone()[0]==0:
                 # Remove user from vlan
                 sql = "update vlans set vlan_name='',user_id=0 where vlan_id=%d" % (vlan)
                 print(sql)
                 cursor.execute(sql)
                 connection.commit()
		
        connection.close()

