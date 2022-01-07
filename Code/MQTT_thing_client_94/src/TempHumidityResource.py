#!/usr/bin/env python3

'''
                    ___           ___           ___     
        ___        /\__\         /\  \         /\  \    
       /\  \      /::|  |       /::\  \       /::\  \   
       \:\  \    /:|:|  |      /:/\:\  \     /:/\ \  \  
       /::\__\  /:/|:|  |__   /::\~\:\  \   _\:\~\ \  \ 
    __/:/\/__/ /:/ |:| /\__\ /:/\:\ \:\__\ /\ \:\ \ \__\
   /\/:/  /    \/__|:|/:/  / \:\~\:\ \/__/ \:\ \:\ \/__/
   \::/__/         |:/:/  /   \:\ \:\__\    \:\ \:\__\  
    \:\__\         |::/  /     \:\ \/__/     \:\/:/  /  
     \/__/         /:/  /       \:\__\        \::/  /   
                   \/__/         \/__/         \/__/    


    File:          TempHumidityResource.py


    Purpose:       Derived class from the
                   sensor class that
                   implements the concrete
                   behaviour of a GrovePi
                   temperatture and humidity
                   sensor.

                   Class is based on
                   the abstract sensor
                   class.


    Remarks:       - The GrovePi module has
                     to be installed to 
                     interact with the GrovePi
                     hardware.

                   - This class holds the value
                     of a rotary angle sensor 
                     ([temp,humidity]) and publishes 
                     it to a MQTT topic if 
                     it changes its state.


    Author:        P. Leibundgut <leiu@zhaw.ch>


    Date:          12/2019

'''

import log
import mqttconfig

from Sensor import Sensor
from grove_pi_interface import InteractorMember, \
                               DHT_READ, \
                               flush_queue

BLUE_COLORED_SENSOR  = 0
WHITE_COLORED_SENSOR = 1

# logging setup
logger = log.setup_custom_logger( 'mqtt_thing_temperature_humidity_resource' )

class TempHumidityResource( Sensor ):

  def __init__( self, connector, lock, \
                mqtt_client, running, \
                pub_topic, \
                polling_interval, \
                sampling_resolution ):

    super( TempHumidityResource, self ).__init__( connector, lock, \
                                                  mqtt_client, running, \
                                                  pub_topic, \
                                                  polling_interval, \
                                                  sampling_resolution )

    self.grovepi_interactor_member = InteractorMember( connector, \
                                                       'INPUT', \
                                                       DHT_READ, \
                                                       WHITE_COLORED_SENSOR )

    self.temp_value = float( 0 )
    self.hum_value  = float( 0 )


  def read_sensor( self ):
    new_temp_value = float( 0 )
    new_hum_value  = float( 0 )

    self.grovepi_interactor_member.tx_queue.put( ( self.grovepi_interactor_member, ) )
    [ new_temp_value, new_hum_value ] = \
        self.grovepi_interactor_member.rx_queue.get()
    self.grovepi_interactor_member.rx_queue.task_done()

    # flush the rx queue if more than one value was present
    flush_queue( self.grovepi_interactor_member.rx_queue )

    # ... or True is just because the temp humidity should be
    # published every time, not only if the value has changed.
    if not self.is_equal( [ self.temp_value, self.hum_value ], 
                          [ new_temp_value, new_hum_value ] ) \
       or True:
      self.temp_value = float( new_temp_value )
      self.hum_value  = float( new_hum_value )
      self.lock.acquire()
      self.mqtt_client.publish( self.pub_topic,
          ( str( self.temp_value ) + ',' + str( self.hum_value ) ), \
          mqttconfig.QUALITY_OF_SERVICE, False )
      self.lock.release()
      logger.debug( '---temp humidity sensor published its value: Temp: ' + \
                    str( self.temp_value ) + \
                    ', Humidity: ' + str( self.hum_value ) )


  def is_equal( self, a, b ):
    return a == b

