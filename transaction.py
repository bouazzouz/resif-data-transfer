
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom import minidom

import os
import random
import string
import time

class Transaction():
  """
  Create, parse, modify an XML file associated to a transaction.
  """
  root = None
  transactionID = None
  __DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
  
  def get_transaction_id( self ):
    return self.root.get("id")
        
  def set_status( self, status):
    node = self.root.find('status_code')
    node.text = status.strip()
      
  def set_resif_node( self, nodename):
    node = self.root.find('resif_node')
    node.text = nodename.strip()
  
  def set_data_type( self, datatype):
    node = self.root.find('datatype')
    node.text = datatype.strip()

  def get_data_type ( self ):
    node = self.root.find('datatype')
    return ( node.text )
    
  def set_last_updated( self ):
    now = time.strftime(self.__DATE_FORMAT,time.gmtime())
    node = self.root.find('last_updated')
    node.text = now
  
  def set_client_size( self, size):
    node = self.root.find('client_size')
    node.text = size

  def set_comment( self, comment):
    node = self.root.find('status_comment')
    node.text = comment.strip()

  def set_filelist( self, files):
    node = self.root.find('filelist')
    for f in files:
        filenode =  SubElement(node,"relativepath")
        filenode.text = f
        
  def add_process_result ( self, identifier, comment, rank, returncode, files_with_errors=None ):
    myprocess = SubElement(self.root,"process_result")
    myprocess.set ( "id", identifier.strip() )
    myprocess.set ( "rank", str(rank) )    
    myprocess.set ("returncode", returncode.strip() )
    mycomment = SubElement(myprocess,"comment")
    mycomment.text = comment.strip()
    myerror = SubElement(myprocess,"rejected_files")    
    for f in files_with_errors:
        filenode =  SubElement(myerror,"relativepath")
        filenode.text = f
    
  def write(self,filename, last_updated = True):
     """write XML tree to filename, atomically. This guarantees that any 
     client downloading the XML file will get a sane content.
     """
     if last_updated: self.set_last_updated()
     f = open ( filename + '.tmp', 'w' )
     ElementTree(self.root).write(f,encoding='UTF-8')
     f.close()
     os.rename ( filename + '.tmp', filename )
        
  def __init__(self, filename=None):
    # build blank XML tree
    if not filename:
        # compute new transaction id
        self.transactionID = '%s%s' % ( 
            ''.join( [random.choice(string.ascii_uppercase) for x in range(4)]), 
            ''.join( [random.choice(string.digits) for x in range(4)]) )   
        self.root = Element("transaction")
        self.root.set ("id", self.transactionID) 
        SubElement(self.root,"resif_node")
        SubElement(self.root,"datatype")
        SubElement(self.root,"status_code")
        SubElement(self.root,"status_comment")
        SubElement(self.root,"last_updated")
        SubElement(self.root,"client_size")
        SubElement(self.root,"filelist")
        
    # load existing XML from file
    else:
        tree = xml.etree.ElementTree.parse(filename)
        self.root = tree.getroot()
        self.transactionID = self.get_transaction_id()
          
  if __name__ == "__main__":
    pass
  
  
