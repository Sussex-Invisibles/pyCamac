###########################################
# Test GPIB-USB connections with LeCroy
# 8901A interface
#
# Author: Ed Leming
# Date:   09/02/15
##########################################
import camac
import time


if __name__ == "__main__":

    # Initialize Scalar class
    scalar = camac.Scalar()

    # Clear all old commands
    scalar.clear_and_initialize()

    # Reset scalar values and take single readings
    #scalar.reset_values()
    #first = scalar.read_single()
    #print first
    #time.sleep(5)
    #second = scalar.read_single()
    #print first, second, second-first

    # Reset and take continuous reading
    scalar.reset_values()
    print scalar.read_continuous(2)
