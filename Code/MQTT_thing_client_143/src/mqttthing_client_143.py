#!/usr/bin/env python3

'''
    Client:         143
'''

import sys
import signal
import threading

import log
from tools import get_ip_address_by_if_name
import mqttconfig

from Sensor import Sensor
from Actuator import Actuator

from TimeResource import TimeResource
from TempHumidityResource import TempHumidityResource

from grove_pi_interface import GrovePiInteractor


# connected hardware
NETWORK_INTERFACE = "eth0"

TEMPHUM143_PIN           = int( 4 )

LOCAL_IP = get_ip_address_by_if_name( NETWORK_INTERFACE )

# globals

# logging setup
logger = log.setup_custom_logger( "mqtt_thing_main" )

lock = threading.Lock()
resources = { }
mqtt_client = mqttconfig.setup_mqtt_client( LOCAL_IP )

# Create a single instance of the GrovePi interactor
gpi = GrovePiInteractor()



# signal handler to perform a proper shutdown of the application.
def signal_handler( *args ):
  logger.debug( "\n\n\n\n\n" + \
                "+--------------------------------------------------------------------+\n" + \
                "| Thing was interrupted by key stroke. Thats all, folks! Exiting ... |\n" + \
                "+--------------------------------------------------------------------+" )
  
  # clean up sensors and actuators. 
  # set their output to low
  for key, value in resources.items():
    if isinstance( value, Sensor ):
      lock.acquire()
      value.running = False 
      lock.release()
    
    if isinstance( value, Actuator ):
      value.tear_down()
      mqtt_client.unsubscribe( value.sub_topic )

  # Stop the GrovePi interactor
  gpi.stop_interactor()


  # stop the clock resource
  lock.acquire()
  ( resources[ 'clock0' ] ).running = False
  lock.release()

  mqtt_client.loop_stop()
  mqtt_client.disconnect()


def main():

  signal.signal( signal.SIGINT, signal_handler )


  # add all resources to the application
  resources[ 'temphum0' ] = TempHumidityResource( connector = TEMPHUM143_PIN, \
                                                  lock = lock, \
                                                  mqtt_client = mqtt_client, \
                                                  running = True, \
                                                  pub_topic = LOCAL_IP + '/sensors/temphum143', \
                                                  polling_interval = float( 1.0 ), \
                                                  sampling_resolution = int( 0 ) )                                   

  resources[ 'clock0' ] = TimeResource( lock = lock, \
                                        mqtt_client = mqtt_client, \
                                        running = True, \
                                        pub_topic = LOCAL_IP + "/stuff/clock0", \
                                        pub_interval = float( 2.0 ) )

  # Start the GrovePi interactor thread to be able
  # to send/receive to/from the GrovePi board.
  gpi.start()


  # start the sensor threads ...
  for key, value in resources.items():
    if isinstance( value, Sensor ):
      value.start()

  # start time resource
  ( resources[ 'clock0' ] ).start()


  '''
  if not called here running threads
  are not affected by Ctrl + C
  because the main thread finishes
  here and its child threads
  become orphans ...
  '''
  signal.pause() 


if __name__ == "__main__": 
  main()

