
import os
import socket
import shlex
import subprocess
import logging

class Rsync():
  """
  a basic wrapper class for the rsync command line
  """
  myServer = None
  myPort = None
  myTimeout = None
  myModule = None
  myLogin = None
  myPassword = None
  myCompress = None
  myDryRun = None
  myCommand = None
  myBandwitdhLimit = None
  myExtraArgs = None
  
  def check_rsync_server_socket ( self ):
    """
    check if remote rsync server is online.
    raise an exception if not.
    """
    try:
      mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      mysocket.settimeout ( self.myTimeout )
      mysocket.connect ( (self.myServer, self.myPort) )
      # send a protocol-compatible string, 
      # so we do not generate an error log on the server side
      mysocket.send ('@RSYNCD: 30.0\n')
      mysocket.send ('#list\n')  
      mysocket.shutdown(socket.SHUT_RDWR)
      mysocket.close()
    except Exception, err : raise Exception ( "Problem while checking rsync server : %s " % err )

  def build_base_command_line ( self ):
    """returns skeleton for rsync command line (without source nor destination)"""
    # setup rsync parameters
    # about --out-format : it is important that %n comes last :
    # makes parsing the line with special chars in filenames easier
    mycommandline = [ self.myCommand,
        '-rtx', 
        '--exclude=lost+found/',
        '--out-format=%i %l %n',
        ]
    if self.myDryRun: mycommandline.append ('-n')
    if self.myCompress: mycommandline.append ('-z')
    if self.myBandwitdhLimit: mycommandline.append ('--bwlimit=%i' % self.myBandwitdhLimit)
    if self.myExtraArgs: 
      eargs = shlex.split( self.myExtraArgs )
      for arg in eargs: mycommandline.append ( arg )
    return mycommandline
    
  def push ( self, source, destination = None ) :
    """
    push 'source' (directory(s), file(s)) to remote module.
    (multiples sources must separated by spaces)
    'destination' is appended to module.
    Returns a string with all files transferred, line by line,
    with format '%i %l %n' (see rsyncd.conf manpage, section 'log format').
    Warning : %n may contains special characters depending on filenames.
    """
    # setup rsync command line
    mycommandline = self.build_base_command_line()
    # setup source & destination
    if (self.myLogin != "" ): at = '@' 
    else: at=''
    remote = 'rsync://' + self.myLogin + at + self.myServer + '/' + self.myModule
    if ( destination ): remote = remote + '/' + destination
    sources = shlex.split ( source ) 
    for s in sources: mycommandline.append ( s )
    mycommandline.append ( remote )
    (stdoutdata, stderrdata) = self.launch_rsync ( mycommandline )
    return ( stdoutdata,stderrdata )  

  def pull ( self, remote, local ) :
    """
    pull 'remote' (directory or file) from module to 'local' (local directory or file).
    Returns a string with all files transferred, line by line,
    with format '%i %l %n' (see rsyncd.conf manpage, section 'log format').
    Warning : %n may contains special characters depending on filenames.
    """
    # setup rsync command line
    mycommandline = self.build_base_command_line()
    # setup source & destination
    if (self.myLogin != "" ): at = '@' 
    else: at=''
    source = 'rsync://' + self.myLogin + at + self.myServer + '/' + self.myModule + '/' + remote
    mycommandline.append ( source )
    mycommandline.append ( local )
    (stdoutdata, stderrdata) = self.launch_rsync(mycommandline)
    return ( stdoutdata,stderrdata )  
  
  def launch_rsync ( self, mycommandline ):
    """launch rsync command"""
    # setup environnement
    myenv = os.environ
    myenv['RSYNC_PASSWORD'] = self.myPassword
    # make a human readable string
    cmdstring = str()
    for token in mycommandline: cmdstring += token + ' '
    logging.debug (cmdstring)
    # launch rsync
    proc = subprocess.Popen ( mycommandline, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    logging.info('Rsync running...') 
    (stdoutdata, stderrdata) = proc.communicate()
    logging.info ( 'Rsync return code is %i' % proc.returncode )
    if proc.returncode != 0 :
      logging.debug ( 'rsync stderr : %s ' % stderrdata )
      raise Exception('Rsync returned an error. Transfer aborted.')
    # return file list
    return ( stdoutdata, stderrdata )  
    
  def __init__ ( self, 
    server, 
    module, 
    port = 873, 
    timeout = 5, 
    login = None, 
    password = None,
    compress = False, 
    dryrun = False,
    command = '/usr/bin/rsync',
    bwlimit = None,
    extraargs = None ):
    
    self.myServer = server
    self.myPort = port
    self.myTimeout = timeout
    self.myModule = module
    self.myLogin = login
    self.myPassword = password
    self.myCompress = compress
    self.myDryRun = dryrun
    self.myCommand = command
    self.myExtraArgs = extraargs
    self.myBandwitdhLimit = bwlimit
    self.check_rsync_server_socket()
  
  if __name__ == "__main__":
    pass
