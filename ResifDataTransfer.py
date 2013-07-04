#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard library
import ConfigParser 
from datetime import datetime,timedelta
import getopt
import json
import logging
import os
import random
import shlex
import shutil
import stat
import string
import subprocess
import sys
from sys import stderr
import time
import traceback
import tempfile
import xml.etree.ElementTree as ET

# custom modules
import miscTools
from rsync import Rsync
from transaction import Transaction

# debug mode
myDebug = False

class ResifDataTransfer():
  """ 
  a helper script to transfer data (or logs) to (or from) RESIF datacentre 
  """
    
  # script version (year, julian day)
  APPNAME = 'RESIF data transfer'
  VERSION = (2013, 175)

  # contact string
  CONTACT = 'FIXME'

  # Python versions required : (major,minor)
  # This script does not work yet with the 3.x branch
  # http://www.python.org/download/releases/
  __PYTHON_VERSION_MIN = (2, 6)
  __PYTHON_VERSION_MAX = (2, 7)
  
  # Platforms on which this script is validated
  # http://docs.python.org/library/platform.html
  __VALIDATED_PLATFORM = [ 'Linux' ]

  # Operation modes (bit encoded, so we can possibily combine multiple operations)
  OPERATIONS = dict(
    SEND_DATA = 0b01, 
    RETRIEVE_LOGS = 0b10,
    PRINT_LOGBOOK = 0b100)
  myOperation = None

  # target directory and data type (SEND_DATA)
  myDirectoryName = None
  DATA_TYPES = dict(
    VALIDATED_SEISMIC_DATA = 'seismic_data',
    VALIDATED_SEISMIC_METADATA = 'seismic_metadata')
  myDataType = None
  
  # transactionID (SEND_DATA and RETRIEVE_LOGS)
  myTransactionID = None
  
  # Default configuration file
  myConfigurationFile = os.path.join ( os.path.dirname(__file__), 'ResifDataTransfer.conf' )
  # Configuration registry (with its data types & defaults values)
  __CONFIG = {
    'my resif node': {
        'my node name':[str,None], 'my node password':[str,None]
        },
    'system' : {
        'working directory':[str,'/tmp/'], 'disk usage command auto find':[bool,True], 
        'disk usage command full path':[str,'/usr/bin/du'], 'disk usage command arguments':[str,None]
        },
    'rsync' : {
        'rsync command auto find':[bool,True], 'rsync command full path':[str,'/usr/bin/rsync'], 
        'rsync server':[str,'rsync.resif.fr'],'rsync port':[int,873],'rsync compress':[bool,False],
        'rsync timeout':[int,10], 'rsync extra args':[str,None]
        },
    'logging' : { 'log file':[str,None],'log level':[str,'WARNING'], 'logbook':[str,None] },
    'limits': { 'weekly max size':[int,150], 'bandwidth max':[int,None] } ,
    }
 
  # values for 'my node name'
  __RESIF_NODES = ('IPGP', 'GEOSCOPE', 'RAP', 'RLBP', 'SISMOB', 'TEST' )
  
  # values for debug level
  # http://docs.python.org/2.6/library/logging.html#logging-levels
  __LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

  # transaction file
  TRANSACTION_XML = 'transaction.xml'
   
  # test mode & ignore limits
  myTestOnly = False
  ignoreLimits = False
  
  # rsync class instance
  myRsync = None
  
  # transfer logbook & date format for logs
  myLogbook = []
  __DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
          
  # help text
  from usage import USAGE

  def __init__( self, test = False, configurationFile = None, operation = None, 
    directoryName = None, dataType = None, transactionID = None, ignoreLimits = False ):
    # set internal parameters
    self.myTestOnly = test
    self.ignoreLimits = ignoreLimits
    if configurationFile: self.myConfigurationFile = configurationFile
    self.myOperation = operation
    if directoryName: 
      self.myDirectoryName = directoryName
      self.myDataType = dataType
    if transactionID:  self.myTransactionID = transactionID
    # check arguments
    if not self.myOperation:  
      raise Exception('No operation specified : what would you like to do ? -h for help.')
    if miscTools.bit_count( self.myOperation ) > 1 :
      raise Exception('Only one operation can be provided at the same time. -h for help')
    if self.myOperation == self.OPERATIONS['SEND_DATA'] and ( not directoryName or not dataType ) :
      raise Exception('Missing directory path and/or data type. -h for help')
    if self.myOperation == self.OPERATIONS['RETRIEVE_LOGS'] and not transactionID:
      raise Exception ('Missing transaction ID. -h for help')
    if self.myOperation not in self.OPERATIONS.values():
      raise Exception('Unknown operation specified. -h for help')
    # check system
    if not miscTools.check_python( self.__PYTHON_VERSION_MIN, self.__PYTHON_VERSION_MAX ):
      raise Exception ('Your Python version is not compatible with this script. -h for help')
    if not miscTools.check_platform ( self.__VALIDATED_PLATFORM ):
      raise Exception ('This script is not validated for your operating system.')
    if miscTools.running_under_root() :
      raise Exception ('This script cannot be run under root user.')
    # load configuration file, setup environement
    miscTools.load_registry(self.myConfigurationFile, self.__CONFIG, paranoid = True, ghost = False)
    self.check_and_setup_environement()
    logging.info('%s v%i.%i starting' % (ResifDataTransfer.APPNAME, ResifDataTransfer.VERSION[0], ResifDataTransfer.VERSION[1]) )
          
  def check_and_setup_environement ( self ) :
    """
    check configuration parameters 
    """
    # node name
    if self.__CONFIG['my resif node']['my node name'][1] not in self.__RESIF_NODES: 
      raise Exception ( '\'my node name\' parameter must be in %s'% (self.__RESIF_NODES,) )
    # password not empty
    if not self.__CONFIG['my resif node']['my node password'][1]: 
      raise Exception ( '\'my node password\' is empty' )
    # is working directory writable ?
    if not os.access( self.__CONFIG['system']['working directory'][1], os.W_OK | os.X_OK):
      raise Exception ('working directory %s is not writable.' % self.__CONFIG['system']['working directory'][1])
    # is data type known ?
    if self.myOperation == self.OPERATIONS['SEND_DATA']:  
        if not self.myDataType in self.DATA_TYPES.values():
            raise Exception ('Data type %s unknown.' % self.myDataType)
    # locate 'du' command
    if self.__CONFIG['system']['disk usage command auto find'][1]: path = miscTools.which ( 'du' )
    else: path = miscTools.which ( self.__CONFIG['system']['disk usage command full path'][1] )
    if (not path): raise Exception ( 'disk usage command not found on your system' )
    self.__CONFIG['system']['disk usage command full path'][1] = path
    # locate 'rsync' command
    if self.__CONFIG['rsync']['rsync command auto find'][1]: path = miscTools.which ( 'rsync' )
    else: path = miscTools.which ( self.__CONFIG['rsync']['rsync command full path'][1] )
    if (not path): raise Exception ( 'rsync command not found on your system' )
    self.__CONFIG['rsync']['rsync command full path'][1] = path
    # build rsync instance
    self.myRsync = Rsync (
      server = self.__CONFIG['rsync']['rsync server'][1], 
      module = 'INCOMING_' + self.__CONFIG['my resif node']['my node name'][1],
      port = self.__CONFIG['rsync']['rsync port'][1],
      timeout = self.__CONFIG['rsync']['rsync timeout'][1],
      login = self.__CONFIG['my resif node']['my node name'][1].lower(),
      password = self.__CONFIG['my resif node']['my node password'][1],
      compress = self.__CONFIG['rsync']['rsync compress'][1],
      dryrun = self.myTestOnly,
      command = self.__CONFIG['rsync']['rsync command full path'][1],
      bwlimit = None if self.ignoreLimits else self.__CONFIG['limits']['bandwidth max'][1],
      extraargs = self.__CONFIG['rsync']['rsync extra args'][1]
      )
    # is data directory readable ?
    if ( self.myOperation == self.OPERATIONS['SEND_DATA'] ):
      if not os.access( self.myDirectoryName, os.R_OK | os.X_OK):
        raise Exception ('directory %s does not exist or is not readable.' % self.myDirectoryName)
    # open general log file (IOerror may be raised)
    if self.__CONFIG['logging']['log level'][1] not in self.__LOG_LEVELS: 
      raise Exception ( '\'log level\' parameter must be in %s'% (self.__LOG_LEVELS,) )
    logfile = self.__CONFIG['logging']['log file'][1]
    logging.basicConfig ( 
      filename = self.__CONFIG['logging']['log file'][1], 
      level = eval ( "logging." + self.__CONFIG['logging']['log level'][1] ),
      format = '%(asctime)s [%(process)d] %(message)s', datefmt = self.__DATE_FORMAT )
    # create empty logbook if not exist (IOerror may be raised)
    # or read existing logbook
    path = self.__CONFIG['logging']['logbook'][1]
    try:
        if not os.path.exists ( path ): 
            with open ( path, 'w' ) as f: json.dump ( [], f )
        else: 
            with open ( path, 'r' ) as f: self.myLogbook = json.load ( f ) 
    except: raise Exception('Problem while opening/creating logbook. (path=%s)' % path)
      
  def start ( self ):
    """ dispatches requested operation """
    returncode = 1
    if self.myTestOnly: logging.warning('Running in test mode : no actual transfer will be done.')
    if self.ignoreLimits: logging.warning('Ignoring limits set in configuration file.')
    if self.myOperation == self.OPERATIONS['SEND_DATA']: returncode = self.send_data()
    elif self.myOperation == self.OPERATIONS['RETRIEVE_LOGS']: returncode = self.retrieve_logs()
    elif self.myOperation == self.OPERATIONS['PRINT_LOGBOOK']: returncode = self.print_logbook()    
    return returncode
        
  def logbook_compute_size ( self, offset = None):
    """
    compute total size of transfers done so far.
    if offset is not None and positive, compute only for last 'offset' days
    """
    now = datetime.utcnow()
    delta = timedelta(days=offset) if offset else None
    mindate = now-delta if delta else datetime.min
    logging.debug('Considering all logs from %s', mindate)
    size = 0
    for log in self.myLogbook:
      logdate = datetime.strptime( log['date'], self.__DATE_FORMAT )
      if logdate >= mindate: size += log['size']
    return size
  
  def print_logbook ( self ):
    if self.myLogbook:
        for log in self.myLogbook:
            sys.stdout.write ( '{0}\t{1}\t{2}\t{3}\t{4}\t{5:.3f}\n'.format(
                log['transactionID'], log['date'], log['node'],
                log['datatype'], log['directory'], 
                log['size']) )
    else: sys.stderr.write('Logbook is empty.\n')
    
  def send_data ( self ):
    """ runs the SEND_DATA operation """
    # calculate dir size
    mycommandline = '%s %s %s' % (
      self.__CONFIG['system']['disk usage command full path'][1],
      self.__CONFIG['system']['disk usage command arguments'][1], 
      self.myDirectoryName )
    args = shlex.split ( mycommandline )
    logging.info('Calculating size of %s ' % self.myDirectoryName) 
    logging.debug('Calling external process : %s ' % mycommandline ) 
    proc = subprocess.Popen ( args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    logging.debug('Reading stdout from external process') 
    (stdoutdata, stderrdata) = proc.communicate()
    if proc.returncode != 0 :
      raise Exception('External process returned non 0 value : %s' % mycommandline)
    sizeGb = float ( stdoutdata.split()[0] ) / 1024**3
    logging.info('Directory size is %.2fGb' % sizeGb)
    # check limits (logbook)
    if ( self.myLogbook and not self.ignoreLimits):
      logging.info('Checking size limits : must be under %.2fGb per week.' % self.__CONFIG['limits']['weekly max size'][1]) 
      totalsize = self.logbook_compute_size(offset=7)
      logging.info('Size of data transferred since one week: %.2fGb' % totalsize )
      if (totalsize + sizeGb > self.__CONFIG['limits']['weekly max size'][1]):
	    raise Exception('Transfer size exceeds limit (see log file for details)')
    # compute a transaction ID
    self.myTransactionID = '%s%s' % ( 
        ''.join( [random.choice(string.ascii_uppercase) for x in range(3)]), 
        ''.join( [random.choice(string.digits) for x in range(3)]) )    
    logging.info ( 'Transaction ID is %s' % self.myTransactionID )
    # build xml
    logging.info ('Building XML object')
    tree = Transaction()
    tree.set_transaction_id(self.myTransactionID)
    tree.set_status('1')
    tree.set_resif_node(self.__CONFIG['my resif node']['my node name'][1])
    tree.set_data_type(self.myDataType)
    now = time.strftime(self.__DATE_FORMAT,time.gmtime())
    tree.set_last_updated(now)
    tree.set_client_size( str(sizeGb) )
    tree.set_comment('data sent to datacentre and waiting for processing')
    temppath = os.path.join ( self.__CONFIG['system']['working directory'][1], self.myTransactionID )
    logging.info ('Writing XML to temporary file in %s' % temppath)
    os.mkdir ( temppath )
    xmlfile = os.path.join ( temppath, self.TRANSACTION_XML )
    f = open ( xmlfile, 'w' )
    tree.write(f)
    f.close()
    # send data + XML file,
    if not self.myTestOnly:
        logging.info ('Calling rsync to transfer %s and %s' % ( self.myDirectoryName, xmlfile))
        (stdoutdata,stderrdata) = self.myRsync.push ( source = self.myDirectoryName + ' ' + xmlfile, destination = self.myTransactionID )
        logging.debug('rsync stderr follows:')
        logging.debug(stderrdata)
    shutil.rmtree ( temppath )
    # update logbook
    self.myLogbook.append ( { 'date': now,
        'node': self.__CONFIG['my resif node']['my node name'][1],
        'directory':self.myDirectoryName, 
        'transactionID':self.myTransactionID, 
        'size':sizeGb, 
        'datatype':self.myDataType  })
    if not self.myTestOnly:
      logging.info ('Updating transfer loogbook')
      with open ( self.__CONFIG['logging']['logbook'][1], 'w' ) as f: json.dump(self.myLogbook,f,indent=2) 
    # on success, prints transaction ID on stdout and returns 0
    sys.stderr.write ( self.myTransactionID+'\n' )
    return 0

  def retrieve_logs ( self ):
    """ runs the RETRIEVE_LOGS operation"""
    # get remote XML file and print it on stdout,
    tempxml= os.path.join ( self.__CONFIG['system']['working directory'][1], 'tmpxml' + self.myTransactionID )
    if not self.myTestOnly:
        logging.info ("Getting XML file from rsync server for transaction %s" % self.myTransactionID)
        try:
            self.myRsync.pull ( remote = os.path.join ( self.myTransactionID, self.TRANSACTION_XML ), local = tempxml )
        except:
            msg='Could not retrieve XML file for this transaction.'
            logging.error ( msg )
            sys.stderr.write ( msg + '\n' )
            return 1
        # cat temp file on stdout
        with open(tempxml,'r') as f: 
            data = f.read()
            sys.stdout.write(data)
        # remove temp file
        os.remove(tempxml)    
    return 0
    
  if __name__ == "__main__":

    from ResifDataTransfer import ResifDataTransfer
    
    try:            
      # set default return code 
      returncode = 1
      
      # build usage text 
      # see http://ascii-table.com/ansi-escape-sequences.php
      usage = ResifDataTransfer.USAGE.format ( prog = sys.argv[0],
        appname = ResifDataTransfer.APPNAME,
        version = str ( ResifDataTransfer.VERSION[0] ) + '.' + str ( ResifDataTransfer.VERSION[1] ),
        config = ResifDataTransfer.myConfigurationFile,
        contact = ResifDataTransfer.CONTACT,
        vmin = str(ResifDataTransfer.__PYTHON_VERSION_MIN[0]) + "." + str(ResifDataTransfer.__PYTHON_VERSION_MIN[1]),
        vmax = str(ResifDataTransfer.__PYTHON_VERSION_MAX[0]) + "." + str(ResifDataTransfer.__PYTHON_VERSION_MAX[1]),
        bold = '\033[1m', clear = '\033[0m' )
      
      # set some default parameters
      testOnly = False
      ignoreLimits = False
      alternateConfigFile = None
      operationCode = 0
      directory = None
      datatype = None
      transaction = None
      
      # empty command line ?
      if len ( sys.argv[1:] ) == 0  :
        stderr.write ( '-h for usage summary.\n' )
        sys.exit(2)

      # extract command line arguments
      options, args = getopt.gnu_getopt(sys.argv[1:], 'htc:is:d:r:lbv', ['help','test','config=','ignore-limits','send=','data-type=','retrieve-logs=','logbook','debug', 'version'])
      for opt,arg in options:
        if opt in ('-h', '--help'):
          stderr.write ( usage )
          sys.exit ( 2 ) 
        elif opt in ('-t', '--test'):
          testOnly = True
        elif opt in ( '-c', '--config' ):
          alternateConfigFile = arg
        elif opt in ( '-i', '--ignore-limits' ):
          ignoreLimits = True
        elif opt in ('-s', '--send' ):
          operationCode += ResifDataTransfer.OPERATIONS['SEND_DATA']
          directory = arg
        elif opt in ('-d', '--data-type' ):
          datatype = arg
        elif opt in ('-r', '--retrieve-logs'):
          operationCode += ResifDataTransfer.OPERATIONS['RETRIEVE_LOGS']
          transaction = arg
        elif opt in ('-l', '--logbook'):
          operationCode += ResifDataTransfer.OPERATIONS['PRINT_LOGBOOK']
        elif opt in ('-v', '--version'):
            sys.stderr.write('%d.%d\n' % (ResifDataTransfer.VERSION))
            sys.exit(0)    
        elif opt in ('-b', '--debug'): myDebug = True
          
      # initialize class
      myTransfer = ResifDataTransfer ( 
        test = testOnly, 
        configurationFile = alternateConfigFile, 
        operation = operationCode, 
        directoryName = directory,
        dataType = datatype,
        transactionID = transaction,
        ignoreLimits = ignoreLimits
        )
      
      # launch operation
      returncode = myTransfer.start()
      
    # error while parsing command line arguments  
    except getopt.GetoptError, err:
      stderr.write ( str(err) + '. Use -h to display usage.\n' )
      returncode = 2
    except KeyboardInterrupt:
      logging.error ('keyboard interrupt')
      if myDebug: raise
    except Exception, myException:
      returncode = 1
      if myDebug: 
        # print full stack trace
        traceback.print_exc ( file = sys.stdout )
        raise
      # print abbreviated stack trace
      exc_type, exc_value, exc_traceback = sys.exc_info()
      alltraces = traceback.extract_tb ( exc_traceback )
      last = alltraces.pop()
      stderr.write( 'ERROR\n  in file %s\n' % last[0] )
      stderr.write( '  at line %s in %s\n' % ( last[1], last[2] )  )
      stderr.write ( 'DETAILS\n  %s\n' % str(myException) )
    # executed if no exception was raised
    else: pass
    # executed anytime
    finally: sys.exit ( returncode )
  
