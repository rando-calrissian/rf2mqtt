import appdaemon.plugins.hass.hassapi as hass
import json

# Basic Tasmota Sonoff RF Bridge sensor converter.  Takes RF Codes in over MQTT and outputs individual sensor over MQTT with Home Assistant AutoDiscovery of each sensor
# Momentary buttons will automatically toggle back off after one second in Home Assistant

# USAGE :  Replace the names and on/off codes, pluse the bridge and MQTT topic names if desired.

class rf2mqtt(hass.Hass):

  def initialize(self):
    # If the off_code is None, will be treated as a momentary button that is pressed for 1 second
    self.sensors = [
     { "name":"button_01", "on_code":"ABCDEF", "off_code": None, "device_class": None },
     { "name":"button_02", "on_code":"QWERTY", "off_code": None, "device_class": None },
     { "name":"button_03", "on_code":"ASDFGH", "off_code": None, "device_class": None },
     { "name":"button_04", "on_code":"123456", "off_code": None, "device_class": None },
     { "name":"motionsensor_01", "on_code":"ZXCVBN", "off_code": "POIUYT", "device_class": "motion" }
     ]
    
    self.mqtt_topic_prefix = "rf2mqtt/sensor/"
    self.mqtt_topic_attributes = "/attributes"
    self.mqtt_bridge_topic = "tele/tasmota_rf_bridge"
    self.bridge_name = "rf_bridge" 
    
    
    # create discovery topic for tasmota sonoff rf bridge
    self.call_service("mqtt/publish", topic='homeassistant/sensor/' + self.bridge_name + '/config', payload='{"name": "' + self.bridge_name + '", "state_topic": "' + self.mqtt_bridge_topic + '/LWT", "json_attributes_topic": "' + self.mqtt_bridge_topic + '/RESULT"}', retain=True)
    # Listen for this Sensor
    self.listen_state(self.on_code_received, "sensor." + self.bridge_name, attribute="all" )    
    self.create_sensors()
  
  def create_sensors( self ):
    for sensor in self.sensors:
      discovery_topic = {}
      discovery_topic["state_topic"] = self.mqtt_topic_prefix + sensor["name"]
      if sensor["off_code"] is None :
        discovery_topic["off_delay"] = 1
      else:
        discovery_topic["payload_off"] = "off"
      if sensor["device_class"] is not None:
        discovery_topic["device_class"] = sensor["device_class"]
      discovery_topic["payload_on"] = "on"
      discovery_topic["json_attributes_topic"]= self.mqtt_topic_prefix + sensor["name"] + "/attributes"
      discovery_topic["name"] = sensor["name"]
      discovery_topic["unique_id"] = "rf2mqtt_sensor_" + sensor["name"]
      topic = "homeassistant/binary_sensor/rf2mqtt/" + discovery_topic["unique_id"] + "/config"
      self.call_service("mqtt/publish", topic = topic, payload= json.dumps(discovery_topic), retain = True)
      self.log( "Creating Discovery Topic : {} - {}".format( topic, json.dumps(discovery_topic) ) )
    
  def on_code_received(self, entity, attribute, old, new, kwargs):
    RfReceived = new["attributes"]["RfReceived"]
    rf_code = RfReceived["Data"]
    attributes = json.dumps({ "last_update": new["attributes"]["Time"], "RfReceived": new["attributes"]["RfReceived"] })
    
    #self.log("Received New Result for {} : {}".format(rf_code, new))

    sensor_list = list( filter(lambda sensor: sensor['on_code'] == rf_code, self.sensors) ) + list( filter(lambda sensor: sensor['off_code'] == rf_code, self.sensors) )

    if sensor_list:
      for sensor in sensor_list:
        #self.log("Sensor Found : {}".format( sensor ))
        topic = self.mqtt_topic_prefix + sensor["name"]
        if sensor["on_code"] == rf_code:
          payload = "on"
        else:
          payload = "off"
        self.call_service( "mqtt/publish", topic = topic, payload= payload, retain = False )
        self.call_service( "mqtt/publish", topic = topic + "/attributes", payload= attributes, retain = True )
        self.log("Sensor State Changed: {} {}".format(topic, payload))
    else:
      self.log("Unrecognized RF Code : {}".format( rf_code ) )

