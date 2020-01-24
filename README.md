# rf2mqtt
AppDaemon script to convert tasmota sonoff rf bridge input to mqtt and home assistant sensors.  It uses mqtt discovery to automatically create sensors for everything.

Edit the rf2mqtt.py script to replace/add each sensor entry:
```
     { "name":"button_01", "on_code":"ABCDEF", "off_code": None, "device_class": None },
```
 - "name" is your chosen name for the sensor.  It will appear as a binary_sensor with this name in home assistant automatically.
 - "on_code" is the code received to turn on the binary_sensor.  You will see these in your Tasmota console when you activate your button/sensor.  It's what is listed under "Data" as seen here :
```
   00:42:33 MQT: tele/tasmota_rf_bridge/RESULT = {"Time":"2020-01-24T00:42:33","RfReceived":{"Sync":8830,"Low":290,"High":920,"Data":"ABCDEF","RfKey":"None"}}
```
 - "off_code" is the code received to turn off the sensor.  If it is set to None, the sensor will act as a momentary button and reset to "off" automatically after 1 second. 
 - "device_class" isn't required, but can be set to "motion", "door", etc. as per https://www.home-assistant.io/integrations/binary_sensor/  otherwise, leave it as None.

Further, you can replace each of these with your desired MQTT topics :

    self.mqtt_topic_prefix = "rf2mqtt/sensor/"
    self.mqtt_topic_attributes = "/attributes"
    self.mqtt_bridge_topic = "tele/tasmota_rf_bridge"
    
Finally, the Sonoff RF Bridge will be refered to as this in its sensor in Home Assitant :
```
    self.bridge_name = "rf_bridge" 
```
