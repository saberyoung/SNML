import numpy as np
import pylab as pl
import subprocess
import string

####################################################

def getconnection(site):
   import util
   connection={#        CHANGE THIS LINE WITH THE INFO ON THE NEW DATABASE
               'sql3170009':{}}

   connection[site]['database'] = util.readpass['database']
   connection[site]['hostname'] = util.readpass['hostname']
   connection[site]['username'] = util.readpass['mysqluser']
   connection[site]['passwd']   = util.readpass['mysqlpasswd']
   return  connection[site]['hostname'],connection[site]['username'],connection[site]['passwd'],connection[site]['database']

def dbConnect(lhost, luser, lpasswd, ldb):
   import sys
   import MySQLdb,os,string
   try:
      conn = MySQLdb.connect (host = lhost,
                              user = luser,
                            passwd = lpasswd,
                                db = ldb)
      conn.autocommit(True)
   except MySQLdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
      sys.exit (1)
   return conn

try:
   hostname, username, passwd, database = getconnection('sql3170009')
   conn = dbConnect(hostname, username, passwd, database)
except:   
   conn=''
   print '\### warning: problem with the database'

def insert_values(connection,table,values):
    import sys,string,os,re
    import MySQLdb,os,string
    def dictValuePad(key):
        return '%(' + str(key) + ')s'

    def insertFromDict(table, dict):
        """Take dictionary object dict and produce sql for 
        inserting it into the named table"""
        sql = 'INSERT INTO ' + table
        sql += ' ('
        sql += ', '.join(dict)
        sql += ') VALUES ('
        sql += ', '.join(map(dictValuePad, dict))
        sql += ');'
        return sql

    sql = insertFromDict(table, values)
    try:
        cursor = connection.cursor (MySQLdb.cursors.DictCursor)
        cursor.execute(sql, values)
        resultSet = cursor.fetchall ()
        if cursor.rowcount == 0:
            pass
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)
        
def query(command,connection):
   import MySQLdb,os,string,MySQLdb.cursors
   lista=''
   try:
        cursor = connection.cursor (MySQLdb.cursors.DictCursor)
        for i in command:
            cursor.execute (i)
            lista = cursor.fetchall ()
            if cursor.rowcount == 0:
                pass
        cursor.close ()
   except MySQLdb.Error, e: 
        print "Error %d: %s" % (e.args[0], e.args[1])
   return lista
