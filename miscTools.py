"""
Miscellaneous utilities tools
"""

import os
import sys
import stat
import string
import platform
import ConfigParser

def size_format(num):
    """
    returns bytes value (num) to human readable size 
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')
    
def bit_count ( myInteger ) :
  """
  returns the number of bits set to 1
  http://stackoverflow.com/questions/9829578/fast-way-of-counting-bits-in-python
  """
  return ( bin(myInteger).count("1") )

def is_exe ( fpath ):
  """returns True if fpath is an executable file, else False"""
  return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def which ( command ):
  """
  'which' Unix command equivalent
  returns None if command not found
  http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
  """
  try:
    fpath, fname = os.path.split(command)
    if fpath:
      if is_exe(command): return command
    else:
      # exception raised if PATH does not exist
      for path in os.environ["PATH"].split(os.pathsep):
	path = path.strip('"')
	exe_file = os.path.join(path, command)
	if is_exe(exe_file): return exe_file
  except: pass
  return None

def check_python ( min, max ):
  """
  returns True if running Python version is between
  min and max version, else returns False
  """
  myversion = sys.version_info
  return ( min < myversion < max )
    
def check_platform( validatedPlatforms ):
  """
  returns True if current running system is in validatedPlatforms, else False
  """
  return ( platform.system() in validatedPlatforms )

def running_under_root():
  """
  returns True if it can be determined that we'running 
  under root. False otherwise.
  """
  if getattr( os, "geteuid" ):
    return ( os.geteuid() == 0 ) 
  return False

def load_registry ( myConfigurationFile, CONFIG, paranoid = False, ghost = True ):
    """
    load parameters from configuration file
    and put it in a registry-like object.
    paranoid : set True to ensure config file not readable by others
    ghost : don't raise exception if missing parameters in file   
    """
    myParser = ConfigParser.SafeConfigParser()
    if not myParser.read ( myConfigurationFile ):
      raise Exception ('Cannot read ' + myConfigurationFile )
    # check file permissions
    if paranoid:
        mode = os.stat(myConfigurationFile)[stat.ST_MODE]
        if bool(mode & stat.S_IROTH):
            raise Exception ('Configuration file is readable by other users. Tip for Unix systems : chmod 600 ' + self.myConfigurationFile)
    # for every sections and options,
    for section in CONFIG:
      for option in CONFIG[section].keys():
        # if the option is found in the config file,
        if myParser.has_option(section,option): 
            fieldtype = CONFIG[section][option][0]
            # get the option value according to field type
            try:
                if fieldtype == str: 
                    value = myParser.get(section,option,raw=True)
                    if value=='': value = None
                elif fieldtype == int: value = myParser.getint(section,option)
                elif fieldtype == float: value = myParser.getfloat(section,option)
                elif fieldtype == bool: value = myParser.getboolean(section,option)
                else: raise Exception('Unknown type declared in registry.')
                # if the value is not blank, update the registry
                if value is not None: CONFIG[section][option][1] = value
            # FIXME if the field is not well formatted, just ignore : use default value instead
            except ValueError, err: pass
        # if the option was not found in the config file,
        else: 
            if not ghost: raise Exception('Configuration file : parameter \'%s\' missing in section [%s]' % (option, section))

def split_key_value ( mystring, key, sep='=' ):
    """
    split a "key=value" string, returns: 
    (key,value) if ok
    (key,None) if key exist but no value
    (None,None) if key does not exist or problem while splitting 
    """
    try: 
        array = mystring.split (sep , 1 )
        if len(array)==2:
            if array[0]==key: 
                value = array[1]
                if value: return key,value
                else: return key,None
    except: pass
    return None,None
	
if __name__ == '__main__': pass
