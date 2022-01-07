#!/usr/bin/env python3

import log
import mqttconfig

from Actuator import Actuator

from grove_pi_interface import InteractorMember, \
                               DIGITAL_WRITE

# logging setup
logger = log.setup_custom_logger( "mqtt_thing_temp_hum_resource" )


class TempHumActuatorResource( Actuator ):

  def __init__( self, connector, \
                mqtt_client, \
                sub_topic, \
                nuances_resolution ):
    
    super( TempHumActuatorResource, self ).__init__( connector, \
                                         mqtt_client, \
                                         sub_topic, nuances_resolution )
    """
    self.grovepi_interactor_member = InteractorMember( connector, \
                                                       'OUTPUT', \
                                                       DIGITAL_WRITE )

    self.value = False

    self.grovepi_interactor_member.tx_queue.put( \
        ( self.grovepi_interactor_member, int( self.value ) ) )
  """
  def on_mqtt_message( self, client, userdata, message ):
    payload = str( "" )
    logger.debug( "Got message on topic: " + str( message.topic ) + " --> " + str(message.payload) )
    payload = self.decode_payload_ascii_str( message.payload )
    self.value = payload
    self.set_actuator( self.value )

  def getPayload(message):
    return message.playload

  def set_actuator( self, value ):
    pass
    """
    self.grovepi_interactor_member.tx_queue.put( \
        ( self.grovepi_interactor_member, int( self.value ) ) )
    """
      

  def tear_down( self ):
    logger.debug( "tearing things down ..." )
    self.set_actuator( int( 0 ) )


  def decode_payload_ascii_str( self, payload ):
    ascii_str = str( "" )

    if( isinstance( payload, bytes ) ):
      try:
        ascii_str = str( payload.decode( 'ascii' ) )
      except ValueError:
        logger.debug( "received payload does not contain anything convertible to bool" )
      except Exception:
        logger.debug( "Exception occurred while converting payload to bool" )
    else:
      logger.debug( "To decode message payload you have to use an array of bytes as input." )
      
    return ascii_str
  

  def str_to_bool( self, bool_as_str ):
    # Precondition: bool_as_str is either "True" or "False" nothing else
    return bool_as_str == "True" 

