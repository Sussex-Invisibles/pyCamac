##############################################
# Functions to operate camac - gpib interface
#
# Author: Ed Leming
# Date:   09/02/15
##############################################
try:
    #from pyvisa.vpp43 import visa_library, visa_exceptions
    #visa_library.load_library("/Library/Frameworks/Visa.framework/VISA")
                                                                                                            
    import visa
except ImportError:
    print "No VISA/pyVISA software installed, cannot use VisaUSB"
import sys
import struct
import numpy as np
import time
import pyvisa

class GPIB(object):

    def __init__(self):
        """ Try the default connection."""
        try:
            rm = visa.ResourceManager()
            for instrument in rm.list_resources():
                if instrument[0:4] == "GPIB":
                    self._connection = rm.open_resource(instrument)
                    print "Connecting to", instrument
        except visa.VisaIOError:
            print "Cannot connect to any instrument."
            raise

    def send(self, command):
        """ Send a command, doesn't expect a returned result."""
        self._connection.write(command)

    def ask(self, command):
        """ Send a command and expect an answer."""
        try:
            self._connection.write(command)
            return self._connection.read_raw()
        except visa.VisaIOError:
            # No answer given
            return None

    def read(self):
        """ Send a command and expect an answer."""
        try:
            return self._connection.read_raw()
        except visa.VisaIOError:
            # No answer given
            return None

    def initialize(self):
        """ Send initialize command"""
        self.send(chr(33))

    def clear(self):
        """ Send clear command"""
        self.send(chr(34))

    def clear_and_initialize(self):
        """ Send clear and initialize command"""
        self.send(chr(35))

    def inhibit(self):
        """ Send inhibit command"""
        self.send(chr(72))

    def deassert_inhibit(self):
        """ Send deassert_inhibit command"""
        self.send(chr(64))


class Scalar(GPIB):
    
    def reset_values(self, n=18, slots=[0,1,2,3], output=False):
        """ Reset the count on a scalar
        
        :param n (int): The address slot of the module being acted on (defaults to 18)
        :param slots (list): List containing the scalar slots to be re-set.  
        :param output (bool): If true, will print results (defaults to false)
        """
        for i in slots:
            # 9 is the clear command
            write_str = "%s%s%s" % (chr(9), chr(i), chr(n))
            read_str = self.ask(write_str)
            read_array = [ ord(x) for x in read_str ]
            if output is True:
                print read_array

    def read_single(self, a=2, n=18, output=False):
         """ Read current scalar count
         
         :param a (int 0-3): Scalar input to be measured (defaults to 2)
         :param n (int): The address slot of the module being acted on (defaults to 18)
         :param output (bool): If true, will print results (defaults to false)
         """
         write_str = "%s%s%s" % (chr(0), chr(a), chr(n))
         print "Write string:", write_str
         read_str = self.ask(write_str)
         read_array = [ ord(x) for x in read_str ]
         v_U = np.uint16(struct.unpack( "H", read_str[0:-2:1] )[0])
         if output is True:
             print read_array
             print "First chars = %s\tint cast = %i" % ( read_array[:-2:1], np.uint16(v_U))
         return v_U

    def read_continuous(self, run_time, a=2, n=18, output=False):
         """ Read continuous, compensating for overloading of 16bit integer

         :param run_time (int): Time for which the scalar should run given in mins
         :param a (int 0-3): Scalar input to be measured (defaults to 2)
         :param n (int): The address slot of the module being acted on (defaults to 18)
         :param output (bool): If true, will print results (defaults to false)
         """
         time_str = time.strftime("%H:%M %x", time.gmtime())
         print "Will count scalar for %1.1f mins, starting at %s...." % (run_time, time_str)
         val_1, val_2, total, count = 0, 0, 0, 0
         self.reset_values()
         start = time.time()
         while time.time()-start < run_time*60:
             try:
                 val_1 = self.read_single(a=a, n=n, output=output)
                 time.sleep(5)
                 val_2 = self.read_single(a=a, n=n, output=output)
                 if val_2 < val_1:
                     count = count + 1
                 total = count*65536 + (val_2 - 1)
             except (KeyboardInterrupt, SystemExit):
                 print "KEYBOARD INTERUPT!!"
                 print "\nTotal counts at interupt (after %1.2f mins) = %i\n" % ( (time.time()-start)/60, total)
                 raise
             if round(time.time()-start, -1) % 10 == 0:
                 print "#######################"
                 print "Time = %1.1f mins\nCounts = %i\nRate = %1.2e Hz" % ((time.time()-start)/60, total, total/(time.time()-start))
                 #print "rate = %1.1e Hz\ncounts = %i\ntime = %1.1f s" % (total/(time.time()-start), total, time.time()-start)
         
         print "#######################"
         print "FINAL"
         print "Time = %1.1f mins\nCounts = %i\nMean Rate = %1.2e Hz" % ((time.time()-start)/60, total, \
total/(time.time()-start))

         return total
