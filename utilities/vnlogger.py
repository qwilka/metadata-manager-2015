"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import logging
import os
import sys


# http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())


def setup_logger(logfile="messages_log.txt", lvl=logging.INFO, 
                redir_STOUT=False, redir_STDERR=False,
                frmt = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'):
    if redir_STOUT:
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
     
    if redir_STDERR:
        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl 
    
    logger = logging.getLogger("")
    logger.setLevel(lvl)
    fh = logging.FileHandler(logfile, mode='w')
    formatter = logging.Formatter(frmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if not redir_STOUT and logger.level <= logging.WARN:
        print("Logging application messages to file {}," 
               " if problems check this file.".format( os.path.abspath(logfile)) )
    return logger


if __name__ == "__main__":
    pass

