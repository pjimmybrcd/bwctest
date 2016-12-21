from st2actions.runners.pythonrunner import Action

import pymysql.cursors

class RpvlanUpdateMacAuthFailureDatabaseAction(Action):
  def __init__(self,config):
     super(RpvlanUpdateMacAuthFailureDatabaseAction, self).__init__(config)

  def run(self,device,port,action):

     if action=='add':
         self.process_add_port(device,port)

     if action=='remove':
         self.process_remove_port(device,port)

     # TODO: Report errors like database failure!
     return (True)

  def process_add_port(self,device,port,vlan):

        connection = pymysql.connect(
             host="127.0.0.1", 
             user="root",      
             passwd="brocade",  
             db='users') 

        cursor = connection.cursor()

        # TODO: Check if mac is already in database and see if it's moved, etc
        # Write failed mac to database
        sql = "update authorized values (%d,'%s','%s',NOW())" % (vlan,device,port)
        print(sql)
        cursor.execute(sql)
        connection.commit()
        connection.close()

  def process_remove_port(self,device,port):
        connection = pymysql.connect(
             host="127.0.0.1", 
             user="root",      
             passwd="brocade",  
             db='users')
        
        cursor = connection.cursor()
        sql = "update authorized set device='NULL', port='NULL' where port='%s'" % (port)
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        cursor = connection.cursor()
	sql = "delete from failures where port='%s'" % (port)
        cursor.execute(sql)
        cursor.close()
        connection.commit()
        connection.close()

