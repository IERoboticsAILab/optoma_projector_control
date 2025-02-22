import paho.mqtt.client as mqtt
import serial
import json
import glob

TOPIC_PREFIX = "home/projectors"

# Commands for the projector
commands_dict_ascii = {
    # Static commands (no parameters) 
    "HDMI1": "~00305 1\r", # HDMI1 
    "HDMI2": "~0012 15\r", # HDMI2
    "OFF": "~0000 0\r", # OFF
    "ON": "~0000 1\r", # ON

    "4:3": "~0060 1\r", # 4:3 aspect ratio
    "16:9": "~0060 2\r", # 16:9 aspect ratio

    "UP": "~00140 10\r",   # Remote Mouse Up
    "LEFT": "~00140 11\r", # Remote Mouse Left
    "ENTER": "~00140 12\r", # Remote Mouse Enter
    "RIGHT": "~00140 13\r", # Remote Mouse Right
    "DOWN": "~00140 14\r",  # Remote Mouse Down

    "MENU": "~00140 20\r", # Menu
    "BACK": "~00140 74\r", # Back

    # Dynamic commands (require parameters n)
    "H-IMAGE-SHIFT": "~0063 n\r", # horizontal image shift (-100 <= n <= 100)
    "V-IMAGE-SHIFT": "~0064 n\r", # vertical image shift (-100 <= n <= 100)

    "H-KEYSTONE": "~0065 n\r", # horizontal keystone (-40 <= n <= 40)
    "V-KEYSTONE": "~0066 n\r", # vertical keystone (-40 <= n <= 40)
}

# Find the USB serial device
def find_usb_serial_device():
    usb_devices = glob.glob('/dev/ttyUSB*')
    if not usb_devices:
        raise RuntimeError("No USB serial device found")
    return usb_devices[0]  # Return first available USB device

# Subscribe to the topic
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscription successful with QoS: {granted_qos}")

# Unsubscribe from the topic
def on_unsubscribe(client, userdata, mid):
    print("Successfully unsubscribed.")
    client.disconnect()

# Message received from the topic
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    received_message = json.loads(payload)

    print(f"Received message: {received_message} on topic: {msg.topic}")

    target = received_message['target']
    command = received_message['command']
    value = received_message.get('value')

    if command in commands_dict_ascii:
        ascii_command = commands_dict_ascii[command]
        if "n" in ascii_command and value is not None:
            ascii_command = ascii_command.replace("n", value)
        if target == 'NORTH':
            ser.write(ascii_command.encode('utf-8'))
            print(f"Sent {received_message} command: {ascii_command}")
            client.publish(f"{TOPIC_PREFIX}/status", json.dumps({"status": "OK", "command": command}))
            print(f"Command {command} executed successfully")
    else:
        print(f"No command found for message: {command}")
        client.publish(f"{TOPIC_PREFIX}/status", json.dumps({"status": "ERROR", "command": command}))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
        client.subscribe(f"{TOPIC_PREFIX}/#")
    else:
        print(f"Failed to connect, error code: {rc}")

# Find the USB serial device
print(find_usb_serial_device())
ser = serial.Serial(find_usb_serial_device(), 9600)  

# Initialize the MQTT client
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.username_pw_set("mqtt", "123456789") 
mqttc.connect("10.205.10.7", 1883, 60)  
mqttc.loop_forever()