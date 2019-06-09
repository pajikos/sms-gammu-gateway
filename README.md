# REST API SMS Gateway using gammu
Simple SMS REST API gateway for sending SMS from gammu supported devices. Gammu supports standard AT commands, which are using most of USB GSM modems.

![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/pajikos/sms-gammu-gateway.svg)
![Docker Automated build](https://img.shields.io/docker/automated/pajikos/sms-gammu-gateway.svg)
![GitHub](https://img.shields.io/github/license/pajikos/sms-gammu-gateway.svg)

When you run this application, you can simply send SMS using REST API:
```
POST http://xxx.xxx.xxx.xxx:5000/sms
Content-Type: application/json
Authorization: Basic admin password
{
  "text": "Hello, how are you?",
  "number": "+420xxxxxxxxx"
}
```
of you can simply get the current signal strength:
```
GET http://xxx.xxx.xxx.xxx:5000/signal
```
and the response:
```
{
  "SignalStrength": -83, 
  "SignalPercent": 45, 
  "BitErrorRate": -1
}
```
There are two options how to run this REST API SMS Gateway:
* Standalone installation
* Running in Docker

## Prerequisites
Either you are using Docker or standalone installation, your GSM modem must be visible in the system. 
When you put a USB stick to your system, you have to see a new USB device:
```
dmesg | grep ttyUSB
```
or typing command:
```
lsusb
```
```
...
Bus 001 Device 009: ID 12d1:1406 Huawei Technologies Co., Ltd. E1750
...
```
If only cdrom device appeared, install [usb-modeswitch](http://www.draisberghof.de/usb_modeswitch) to see a modem as well:
```
apt-get install usb-modeswitch
```

## Standalone installation
This guide does not cover Python 3.x installation process (including pip), but it is required as well.
#### Install system dependencies (using apt):
```
apt-get update && apt-get install -y pkg-config gammu libgammu-dev libffi-dev
```
#### Clone repository
```
git clone https://github.com/pajikos/sms-gammu-gateway
cd sms-gammu-gateway
```
3. Install python dependencies
```
pip install -r requirements.txt
```
#### Edit gammu configuration 
You usually need to edit device property in file [gammu.config](https://wammu.eu/docs/manual/config/index.html) only, e.g.:
```
[gammu]
device = /dev/ttyUSB1
connection = at
```
#### Run application (it will start to listen on port 5000):
```
python run.py
``` 

## Running in Docker
In a case of using any GSM supporting AT commands, you can simply run the container:
```
docker run -d -p 5000:5000 --device=/dev/ttyUSB0:/dev/mobile pajikos/sms-gammu-gateway
```
#### Docker compose:
```
version: '3'
services:
  sms-gammu-gateway:
    container_name: sms-gammu-gateway
    restart: always
    image: pajikos/sms-gammu-gateway
    environment:
      - PIN="1234"
    ports:
      - "5000:5000"
    devices:
      - /dev/ttyUSB1:/dev/mobile
```

## FAQ
#### PIN configuration
Pin to unblock SIM card could be set using environment variable PIN, e.g. PIN=1234.
#### Authentication
Out of the box, there is needed an HTTP Basic authentication to send any SMS, username and password can be configured in `credentials.txt`
#### How to use HTTPS?
Using environment variable SSL=True, the program expects RSA private key and certificate to provide content via HTTPS.
Expected file paths (you can edit it in run.py or mount your own key/cert in Docker):

```
/ssl/key.pem
/ssl/cert.pem
```
#### It does not work...
Try to check [gammu configuration file site](https://wammu.eu/docs/manual/config/index.html)

## Integration with Home Assistant
#### Signal Strength sensor
```
- platform: rest
  resource: http://172.16.100.10:5070/signal
  name: GSM Signal
  scan_interval: 30
  value_template: '{{ value_json.SignalPercent }}'
  unit_of_measurement: '%'
```

#### SMS notification
```
notify:    
  - name: SMS GW
    platform: rest
    resource: http://xxx.xxx.xxx.xxx:5000/sms
    method: POST_JSON
    authentication: basic
    username: admin
    password: password
    target_param_name: number
    message_param_name: text
```

#### Using in Automation
```
- alias: Alarm Entry Alert - Garage Door
  trigger:
    platform: state
    entity_id: binary_sensor.garage_door
    state: 'on'
  condition:
    - platform: state
      entity_id: alarm_control_panel.alarm
      state: 'armed_home'
  action:
    service: notify.sms_gw
    data:
      message: 'alert, entry detected at garage door'
      target: '+xxxxxxxxxxxx'
```