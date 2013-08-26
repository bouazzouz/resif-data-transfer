#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom import minidom

import argparse
import os
import random
import string
import sys
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
    self.root.set ("status", status.strip()) 

  def get_status( self ):
    return self.root.get ("status") 
              
  def set_resif_node( self, nodename):
    self.root.set ("resifnode", nodename.strip()) 
      
  def set_data_type( self, datatype):
    self.root.set ("datatype", datatype.strip()) 

  def get_data_type ( self ):
    return self.root.get("datatype")
    
  def set_last_updated( self ):
    now = time.strftime(self.__DATE_FORMAT,time.gmtime())
    node = self.root.find('lastupdated')
    node.text = now
  
  def set_client_size( self, size):
    node = self.root.find('clientsize')
    node.text = size

  def set_comment( self, comment):
    node = self.root.find('comment')
    node.text = comment.strip()

  def set_filelist( self, files):
    node = self.root.find('filelist')
    for f in files:
        filenode =  SubElement(node,"relativepath")
        filenode.text = f
  
  def get_process_returncode( self, processID ):
    for process in self.root.findall('process[@id=\''+processID+'\']'):
        return process.attrib.get('returncode') 
    return ''
    
  def get_process_rejectedfiles( self, processID ):
    l=[]
    for path in self.root.findall('process[@id=\''+processID+'\']/rejectedfiles/relativepath'):
        l.append(path.text)
    return '\n'.join(sorted(l)) if l else ''  
        
  def get_filelist ( self ):
    node = self.root.find('filelist')
    l=[]
    for f in node.iter('relativepath'): l.append(f.text)
    return '\n'.join(sorted(l)) if l else ''
        
  def add_process_result ( self, identifier, comment, rank, returncode, files_with_errors=None ):
    myprocess = SubElement(self.root,"process")
    myprocess.set ( "id", identifier.strip() )
    myprocess.set ( "rank", str(rank) )    
    myprocess.set ("returncode", returncode.strip() )
    mycomment = SubElement(myprocess,"comment")
    mycomment.text = comment.strip()
    myerror = SubElement(myprocess,"rejectedfiles")    
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
        SubElement(self.root,"comment")
        SubElement(self.root,"lastupdated")
        SubElement(self.root,"clientsize")
        SubElement(self.root,"filelist")      
    # load existing XML from file
    else:
        tree = xml.etree.ElementTree.parse(filename)
        self.root = tree.getroot()
        self.transactionID = self.get_transaction_id()
          
if __name__ == "__main__":

    # build command line parser
    parser = argparse.ArgumentParser(description='Helper script to parse/flatten RESIF transaction XML file. XML is read from stdin.', epilog='Prints data on stdout, returns 1 if error detected, else 0. Warning: empty string may be returned on badly formatted files or empty results (even though 0 is returned).')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--print-transaction-id", help='Prints transaction identifier', action='store_true')
    group.add_argument("--print-status", help='Prints transaction status code', action='store_true')
    group.add_argument("--print-datatype", help='Prints data type', action='store_true')
    group.add_argument("--print-filelist", help='Prints file list initially submitted', action='store_true')
    group.add_argument("--print-process-returncode", help='Prints return code for process identified by processID', metavar='processID')
    group.add_argument("--print-process-rejectedfiles", help='Prints rejected files for process identified by processID', metavar='processID')
    args = parser.parse_args()

    # prints nothing if mystring if void
    def shellprint ( mystring ):
        if mystring: sys.stdout.write(mystring)

    # reads xml from stdin
    mytree = Transaction(sys.stdin)  
  
    if args.print_transaction_id: shellprint(mytree.get_transaction_id())
    if args.print_status: shellprint(mytree.get_status())
    if args.print_datatype: shellprint(mytree.get_data_type())
    if args.print_filelist: shellprint(mytree.get_filelist())
    if args.print_process_returncode: shellprint(mytree.get_process_returncode(args.print_process_returncode))
    if args.print_process_rejectedfiles: shellprint(mytree.get_process_rejectedfiles(args.print_process_rejectedfiles))

    exit(0)

