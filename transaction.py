
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom import minidom

import os
import random
import string

class Transaction():
  """
  Create, parse, modify an XML file associated to a transaction.
  """
  root = None
  transactionID = None
  
  def get_transaction_id( self ):
    node = self.root.find('id')
    return ( node.text )
    
  def set_status( self, status):
    node = self.root.find('status')
    node.text = status
      
  def set_resif_node( self, nodename):
    node = self.root.find('resif_node')
    node.text = nodename
  
  def set_data_type( self, datatype):
    node = self.root.find('datatype')
    node.text = datatype

  def get_data_type ( self ):
    node = self.root.find('datatype')
    return ( node.text )
    
  def set_last_updated( self, date):
    node = self.root.find('last_updated')
    node.text = date
  
  def set_client_size( self, size):
    node = self.root.find('client_size')
    node.text = size

  def set_comment( self, comment):
    node = self.root.find('comment')
    node.text = comment

  def set_filelist( self, files):
    node = self.root.find('filelist')
    node.text = files

  def set_process_result ( self, comment, files_with_error=None ):
    myprocess = SubElement(self.root,"process_result")
    mycomment = SubElement(myprocess,"comment")
    myerror = SubElement(myprocess,"files_with_error")
    mycomment.text = comment
    myerror.text = files_with_error
      
  def write(self,filename):
     """write XML tree to filename, atomically. This guarantees that any 
     client downloading the XML file will get a sane content.
     """
     f = open ( filename + '.tmp', 'w' )
     ElementTree(self.root).write(f,encoding='UTF-8')
     f.close()
     os.rename ( filename + '.tmp', filename )
        
  def __init__(self, filename=None):
    # build blank XML tree
    if not filename:
        # compute new transaction id
        self.transactionID = '%s%s' % ( 
            ''.join( [random.choice(string.ascii_uppercase) for x in range(3)]), 
            ''.join( [random.choice(string.digits) for x in range(5)]) )   
        self.root = Element("transaction")
        node = SubElement(self.root, "id")
        node.text = self.transactionID
        SubElement(self.root, "resif_node")
        SubElement(self.root,"datatype")
        SubElement(self.root,"status")
        SubElement(self.root,"last_updated")
        SubElement(self.root,"comment")
        SubElement(self.root,"client_size")
        SubElement(self.root,"filelist")
        
    # load existing XML from file
    else:
        tree = xml.etree.ElementTree.parse(filename)
        self.root = tree.getroot()
        self.transactionID = self.get_transaction_id()
    
    #def set_client_size( self, size):
    #  node = self.root.find('sent_files/size_on_client')
    #  node.text = size
        
    # sent_files = SubElement(self.root,"sent_files")
    # SubElement(sent_files,"size_on_client")
    # SubElement(sent_files,"filelist")
      
  if __name__ == "__main__":
    pass
  
  
