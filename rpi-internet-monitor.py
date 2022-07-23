#!/usr/bin/env python3
# sudo python3 rpi-internet-monitor.py -debug -test

import RPi.GPIO as GPIO
import signal
import subprocess
import sys
import time
from datetime import datetime

# Gracefully handle reseting the GPIO state.
def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
  GPIO.cleanup() # cleanup all GPIO
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

lampPin = 16 # The pin connected to the outlet controller.

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme GPIO.setup(lampPin, GPIO.OUT) # Lamp pin set as output
GPIO.setup(lampPin, GPIO.OUT) # LED pin set as output
GPIO.output(lampPin, GPIO.LOW)

try:
    sys.argv[2] == "-test" # force a router reboot
    DELAY_BETWEEN_PINGS = 1    # delay in seconds
    DELAY_BETWEEN_TESTS = 10  # delay in seconds
    LONG_DELAY = 20 # delay in seconds
    SITES = ["google.blah", "github.blah"]
except:
    DELAY_BETWEEN_PINGS = 1    # delay in seconds
    DELAY_BETWEEN_TESTS = 120  # delay in seconds
    LONG_DELAY = 3600 # delay in seconds
    SITES = ["google.com", "github.com"]

# turn off the usb port connected to the power strip for DELAY_BETWEEN_TESTS time
def turn_off_usb(reboot):
    if reboot == 0:
      cmd = "sudo /usr/sbin/uhubctl -l 1-1 -p 2 -a 1" #off"
      #cmd = "GPIO.output(lampPin, GPIO.HIGH)"
      try:
        #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        GPIO.output(lampPin, GPIO.HIGH)
        output = "GPIO.output(lampPin, GPIO.HIGH)"
        debug_message(debug, output)
        time.sleep(DELAY_BETWEEN_TESTS) # wait some time for the router to power down
        cmd = "sudo /usr/sbin/uhubctl -l 1-1 -p 2 -a 0" #on"
        #cmd = "GPIO.output(lampPin, GPIO.LOW)"
        #output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        GPIO.output(lampPin, GPIO.LOW)
        output = "GPIO.output(lampPin, GPIO.LOW)"
        debug_message(debug, output)
        time.sleep(DELAY_BETWEEN_TESTS) # wait for the router to boot back up befoe continuing
        time.sleep(DELAY_BETWEEN_TESTS)
        print("--- Rebooted the router! ---")
        return 0
      except subprocess.CalledProcessError:
        debug_message(debug, cmd + ": error")
        return 0    
    else:
        debug_message(debug, "--- waiting a long time ---")
        print("--- In long wait loop. ---")
        time.sleep(LONG_DELAY)
        return 1

# print messages for debugging when indicator is set
def debug_message(debug_indicator, output_message):
  if debug_indicator:
    print(output_message)

# issue Linux ping command to determine internet connection status
def ping(site):
  cmd = "/bin/ping -c 1 " + site
  try:
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
  except subprocess.CalledProcessError:
    debug_message(debug, site + ": not reachable")
    return 0
  else:
    debug_message(debug, site + ": reachable")
    return 1

# ping the sites in the site list the specified number of times
# and calculate the percentage of successful pings
def ping_sites(site_list, wait_time, times):
  successful_pings = 0
  attempted_pings = times * len(site_list)
  for t in range(0, times):
    for s in site_list:
      successful_pings += ping(s)
      time.sleep(wait_time)
  debug_message(debug, "Percentage successful: " + str(int(100 * (successful_pings / float(attempted_pings)))) + "%")
  return successful_pings / float(attempted_pings)   # return percentage successful 

      
# main program starts here

# check to see if the user wants to print debugging messages
debug = False
if len(sys.argv) > 1:
  if sys.argv[1] == "-debug":
    debug = True
  else:
    print("unknown option specified: " + sys.argv[1])
    sys.exit(1)


# main loop: ping sites, turn appropriate lamp on, wait, repeat
test = 0
reboot = -1
while True:
  test+=1
  debug_message(debug, "----- Test " + str(test) + " -----")
  try:
      sys.argv[2] == "-test" # force a router reboot
      success = 0
  except:
      success = ping_sites(SITES, DELAY_BETWEEN_PINGS, 2)
  if success == 0:
      debug_message(debug, "---- No internet - restarting router ----")
      reboot+=1
      ret_reboot = turn_off_usb(reboot)
      if ret_reboot == 0:
          with open('reboot_flg.txt', 'w') as f: 
              f.write(datetime.now().strftime('%B %d, %Y %I:%M:%S %p')) 
          print(datetime.now().strftime('%B %d, %Y %I:%M:%S %p')) 
  else:
      debug_message(debug, "---- Internet is working fine ----")
      reboot = -1
  debug_message(debug, "Waiting " + str(DELAY_BETWEEN_TESTS) + " seconds until next test.")
  time.sleep(DELAY_BETWEEN_TESTS)

