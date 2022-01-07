#!/usr/bin/env python3

import log
import mqttconfig
import math

from grove_rgb_lcd import *

from Actuator2 import Actuator2

from grove_pi_interface import InteractorMember, \
                               DIGITAL_WRITE

# logging setup
logger = log.setup_custom_logger( "mqtt_thing_temp_hum_resource" )

Topic94 = "172.16.32.94/sensors/temphum94"
Topic143 = "172.16.32.143/sensors/temphum143"


hum94 = 80.0
temp94 = 20.0
hum143 = 80.0
temp143 = 20.0

tempHumDic = { 15 : 100, 16 : 95, 17 : 89, 18 : 84, 19 : 79, 20 : 75, 21 : 70, 22 : 66, 23 : 63, 24 : 59, 25 : 56, 26 : 53, 27 : 50, 28 : 47, 29 : 45 }

class TempHumActuatorResource2( Actuator2 ):
  @staticmethod
  def parseHum(messagePayload):
    return float(messagePayload.split(",")[1])

  @staticmethod
  def parseTemp(messagePayload):
    return float(messagePayload.split(",")[0])

  @staticmethod
  def getHumDic(temperatur):
    return tempHumDic.get(temperatur)

  @staticmethod
  def setTempHumOnDisplay(temp1, hum1, temp2, hum2):
    setText("Humidor: "+ str(temp1) + "/" + str(hum1) + " (" + str(temp2) + "/" + str(hum2) + ")")
    setRGB(0,128,64)

  @staticmethod
  def setErrorOnDisplay(message):
    setText(message)
    setRGB(255,0,0)


  def __init__( self, 
                connector1, \
                connector2, \
                mqtt_client, \
                sub_topic1, \
                sub_topic2, \
                nuances_resolution ):
    
    super( TempHumActuatorResource2, self ).__init__( connector1, \
                                         connector2, \
                                         mqtt_client, \
                                         sub_topic1, sub_topic2, nuances_resolution )
    
    self.grovepi_interactor_member1 = InteractorMember( connector1, \
                                                       'OUTPUT', \
                                                       DIGITAL_WRITE )

    self.grovepi_interactor_member2 = InteractorMember( connector2, \
                                                       'OUTPUT', \
                                                       DIGITAL_WRITE )

    self.value1 = False
    self.value2 = False

    self.grovepi_interactor_member1.tx_queue.put( \
        ( self.grovepi_interactor_member1, int( self.value1 ) ) )
    
    self.grovepi_interactor_member2.tx_queue.put( \
        ( self.grovepi_interactor_member2, int( self.value2 ) ) )
  
  def on_mqtt_message( self, client, userdata, message ):

    global temp94
    global hum94
    global temp143
    global hum143

    payload = str( "" )

    messagePayload = str(message.payload).split("'")[1]

    if(message.topic == Topic94):
        temp94 = TempHumActuatorResource2.parseTemp(messagePayload)
        hum94 = TempHumActuatorResource2.parseHum(messagePayload)

        logger.debug( "Values on: " + str( message.topic ) + " --> " + str(temp94) + "/" + str(hum94) )

    if(message.topic == Topic143):
        temp143 = TempHumActuatorResource2.parseTemp(messagePayload)
        hum143 = TempHumActuatorResource2.parseHum(messagePayload)
        logger.debug( "Values on: " + str( message.topic ) + " --> " + str(temp143) + "/" + str(hum143) )

    if(not math.isnan(temp94)):
      if(((temp94 < 29.5) & (temp94 >= 14.5)) & (hum94 < TempHumActuatorResource2.getHumDic(round(temp94)))):
        self.value1 = True
      else:
        self.value1 = False

    logger.debug("self Value: " + str(self.value1))

    if(not math.isnan(temp94)):
      if((temp94 < 15.0) | (temp94 > 29.0) | (abs(temp94 -temp143) > 3.0)):
        TempHumActuatorResource2.setErrorOnDisplay("TEMPERATURE CRITICAL: Open Me!")
        self.value2 = True
      else:
        TempHumActuatorResource2.setTempHumOnDisplay(temp94, hum94, temp143, hum143)
        self.value2 = False

    
    #payload = self.decode_payload_ascii_str( message.payload )
    #self.value = payload
    self.set_actuator1( self.value1 )
    self.set_actuator2( self.value2 )

  def set_actuator1( self, value1 ):
    self.grovepi_interactor_member1.tx_queue.put( \
        ( self.grovepi_interactor_member1, int( self.value1 ) ) )

  def set_actuator2( self, value2 ):
    self.grovepi_interactor_member2.tx_queue.put( \
        ( self.grovepi_interactor_member2, int( self.value2 ) ) )

  def tear_down( self ):
    logger.debug( "tearing things down ..." )
    self.set_actuator( int( 0 ) )
    self.value1 = False
    self.value2 = False


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

