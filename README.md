# RPi-GPIO-Router-Reboot

Program to monitor internet connection and reboot the router by turning a power strip off and on.

*This fork differs by use of GPIO rather than USB to control power strip. The reason for this is that the 
power level of the USB is affected by events such as reboot of the Pi, leading to possibly disruptive results.*

## Highlights:

  1. Configurable time delays
  2. debug and test modes

## Installation:

  1. Set up hardware: IoT Power Relay for Arduino, Raspberry Pi connected to the USB port of the Raspberry Pi.
  2. Install uhubctl (see https://github.com/mvp/uhubctl).
  3. Download / clone this software.
  4. Set up and register internet-monitor.service if you want to run this as a service when the Raspberry Pi starts up.
  5. Optionally set up node-red and use the flows.json file.
  
