#!/usr/bin/env python3

'''

'''

import threading
import mqttconfig


class Actuator2( threading.Thread ):

  def __init__( self, 
                connector1, \
                connector2, \
                mqtt_client, \
                sub_topic1, \
                sub_topic2, \
                nuances_resolution = int( 2 ) ):

    self.connector = connector1
    self.connector = connector2
    self.mqtt_client = mqtt_client
    self.sub_topic1 = sub_topic1
    self.sub_topic2 = sub_topic2
    self.nuances_resolution = nuances_resolution
    self.grovepi_interactor_member = None

    self.mqtt_client.subscribe( self.sub_topic1, mqttconfig.QUALITY_OF_SERVICE )
    self.mqtt_client.message_callback_add( self.sub_topic1, self.on_mqtt_message )
    self.mqtt_client.subscribe( self.sub_topic2, mqttconfig.QUALITY_OF_SERVICE )
    self.mqtt_client.message_callback_add( self.sub_topic2, self.on_mqtt_message )


  # Function has to be overridden in derived class.
  def on_mqtt_message( self, client, userdata, message ):
    pass  


  # Function has to be overridden in derived class.
  def set_actuator( self, value ):
    pass

  
  # Function has to be overridden in derived class.
  def input_valid( self, input ):
    pass
		
  
  # Function has to be overridden in derived class.
  def is_equal( self, a, b ):
    pass


  # Function has to be overridden in derived class.
  def tear_down( self ):
    pass

