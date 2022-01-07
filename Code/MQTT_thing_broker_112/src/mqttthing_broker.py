#!/usr/bin/env python3

'''

    Broker:         112
'''

import sys
import signal
import threading
from TempHumActuatorResource2 import TempHumActuatorResource2

import log
from tools import get_ip_address_by_if_name
import mqttconfig

from Sensor import Sensor
from Actuator import Actuator
from Actuator2 import Actuator2

from ButtonResource import ButtonResource
from LedResource import LedResource
from TimeResource import TimeResource
from TempHumActuatorResource import TempHumActuatorResource

from grove_pi_interface import GrovePiInteractor


# connected hardware
NETWORK_INTERFACE = "eth0"

PI94 = "172.16.32.94"
PI143 = "172.16.32.143"

DISPLAY2_PIN           = int( 4 )
LED_PIN           = int( 3)
WATER_PIN           = int( 2 )

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
  """ 
  resources[ 'button0' ] = ButtonResource( connector = BUTTON0_PIN, \
                                           lock = lock, \
                                           mqtt_client = mqtt_client, \
                                           running = True, \
                                           pub_topic = LOCAL_IP + "/sensors/button0", \
                                           polling_interval = float( 0.15 ), \
                                           sampling_resolution = int( 2 ) ) 

  resources[ 'led94' ] = LedResource( connector = LED94_PIN, \
                                     mqtt_client = mqtt_client, \
                                     sub_topic = PI94 + "/sensors/button0", \
                                     nuances_resolution = int( 2 ) )

  resources[ 'led143' ] = LedResource( connector = LED143_PIN, \
                                      mqtt_client = mqtt_client, \
                                      sub_topic = PI143 + "/sensors/button0", \
                                      nuances_resolution = int( 2 ) )


  resources[ 'temphum94' ] = TempHumActuatorResource( connector = 0, \
                                                    mqtt_client = mqtt_client, \
                                                    sub_topic = PI94 + '/sensors/temphum94', \
                                                    nuances_resolution = int( 0 ) )

  resources[ 'temphum143' ] = TempHumActuatorResource ( connector = 0, \
                                                    mqtt_client = mqtt_client, \
                                                    sub_topic = PI143 + '/sensors/temphum143', \
                                                    nuances_resolution = int( 0 ) )
"""                                                    
  resources[ 'temphumBoth' ] = TempHumActuatorResource2 ( connector1 = WATER_PIN, \
                                                    connector2 = LED_PIN, \
                                                    mqtt_client = mqtt_client, \
                                                    sub_topic1 = PI94 + '/sensors/temphum94', \
                                                    sub_topic2 = PI143 + '/sensors/temphum143', \
                                                    nuances_resolution = int( 0 ) )

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

