
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
    node = self.root.find('sent_files/size_on_client')
    node.text = size

  def set_comment( self, comment):
    node = self.root.find('comment')
    node.text = comment

  def set_sent_files( self, files):
    node = self.root.find('sent_files/filelist')
    node.text = files
    
  def pretty_dump(self):
    """
    returns a pretty-printed XML string
    http://blog.doughellmann.com/2010/03/pymotw-creating-xml-documents-with.html
    """
    rough = ElementTree.tostring(self.root, 'utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="\t")

  def write(self,filename):
    ElementTree(self.root).write(filename,'UTF-8')
    
  def __init__(self):
    self.root = Element("transaction")
    SubElement(self.root, "id")
    SubElement(self.root, "resif_node")
    SubElement(self.root,"datatype")
    SubElement(self.root,"status")
    SubElement(self.root,"last_updated")
    SubElement(self.root,"comment")
    sent_files = SubElement(self.root,"sent_files")
    SubElement(sent_files,"size_on_client")
    SubElement(sent_files,"filelist")
      
  if __name__ == "__main__":
    pass
  
  
