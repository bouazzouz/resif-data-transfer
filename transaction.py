
import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom import minidom

class Transaction():
  """
  Create, parse, modify an XML file associated to a transaction.
  """
  root = None
  
  def set_transaction_id( self, id):
    node = self.root.find('id')
    node.text = id

  def set_status( self, status):
    node = self.root.find('status')
    node.text = status
      
  def set_resif_node( self, nodename):
    node = self.root.find('resif_node')
    node.text = nodename
  
  def set_data_type( self, datatype):
    node = self.root.find('datatype')
    node.text = datatype

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
    
  def write(self,filename):
     # FIXME implement atomic write
     f = open ( filename, 'w' )
     ElementTree(self.root).write(f,encoding='UTF-8')
     f.close()
        
  def __init__(self, filename=None):
    # build blank XML tree
    if not filename:
        self.root = Element("transaction")
        SubElement(self.root, "id")
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
    
    #def set_client_size( self, size):
    #  node = self.root.find('sent_files/size_on_client')
    #  node.text = size
        
    # sent_files = SubElement(self.root,"sent_files")
    # SubElement(sent_files,"size_on_client")
    # SubElement(sent_files,"filelist")
      
  if __name__ == "__main__":
    pass
  
  
