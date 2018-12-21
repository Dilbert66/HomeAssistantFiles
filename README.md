# Alexa - Broadlink/OpenMQTTGateway - Home Assistant Media Player/TV controller including channel selection.

This customization uses a modified broadlink.py file from from Vassilis Panos's project at  
https://github.com/vpnmaster/homeassistant-custom-components as well as a modified version of the 
default Home Assistant Alexa component module.

**Update**: added Openmqtt media player module. Tested and working.

## Background
I was using the Broadlink Alexa skill and found it had a tendency to keep
 adding extra digits when responding to a change channel command on my TV.  Since I am also using Home Assistant  (with Haaska) at home, I felt I would 
 rather be able to control all aspects of the broadlink from my own system instead of depending on a third party buggy tool which I have no control of.
After looking around, I could not find anything that was accomplishing all I wanted to do without ugly hacks.   I decided to use 
Vassilis Broadlink.py component as as base since it had most functions setup.  I would then add the rest of the functions I needed as well as using this as an opportunity to get 
more familiar with HA and Python.  

## The missing functions that were added:

-  Ability to enter a TV  channel using direct number keypad entry using digits or a TV Callsign or use 
an Alexa phrase such as Alexa, change channel to 123 on TV or Alexa, change channel to PBS on TV
- Play/Pause a TV broadcast (I have a PVR)
- Volume stepped control via Alexa . For example say Alexa, increase volume by 10 on TV.

## Code changes
**Alexa component** <br/>
- added ChannelController capability that adds voice control of all channel changing activities.<br/>
- added stepped voice control. <br/>
I've called this component smarter_home.py so not to conflict with the existing HA alexa component.  
You can't use both at the same time as they both use the same /alexa/smart_home endpoint.


**broadlink.py** <br/>
- added channel tuning function as well as play/pause capability.  Also converted the code to use inline configuration options within the configuration.yaml file  instead of using external ini files for code configuration.  All configs are setup with the broadlink option in the configuraiton.yaml file. I used the media_player.play_media function for channel control. <br/>

- added input_text config option in configuration.yaml to allow changing channel from the HA console just by entering the channel number or callsign.

**openmqtt.py** <br/>
- same functions as the broadlink module except uses a diy openmqttgateway module.  I built mine from a very inexpensive Sonoff RF bridge by adding an IR transmitter to it. 
- for more info about building one or getting ir codes visit: https://github.com/1technophile/OpenMQTTGateway/wiki/User-guide-IR


## Installation
## NOTE: You must be using Haaska or the HA cloud integration for the Alexa component to work. If not you will need to create your own Alexa intents. 

1. create a "custom_components" directory in your HA configuration directory and copy the alexa and media_player subdirectories into it.
2. add the config options in your configuration.yaml and automations.yaml.  Of course you'll need to use your own IR codes for the functions.

## configuration.yaml

```
api: #enable api

alexa:
  smarter_home:  #enable custom Alexa component

media_player:
  - platform:  broadlink  #enable broadlink component. options: broadlink / openmqtt
  
  #broadlink only options
    host: 192.168.1.11    #ip address of broadlink device - not needed for openmqtt
    mac: '77:FF:77:55:CC:66'  # mac address of broadlink device - not needed for openmqtt
  ## end broadlink only options
  
  ## openmqtt only options
    command_topics:
       - topic: "home/OpenMQTTGateway/commands/IR_GC"
         type: ir   # used to send IR codes - First topic in the list is the default
       - topic: "home/OpenMQTTGateway/commands/MQTTto433"
         type: rf  # use to send RF codes. Choose rf type in the codes by prepending rf: to the code ie: "rf:<code>"
  ## end openmqtt only options
  
    name: tv                  # friendly name used by Alexa or HA console
    ping_host: 192.168.1.12  # ip adress of smart tv to detect it's state  - optional
    channels:     # used with alexa or input text box for finding channels by name - optional
        - name: city  # channel name
          channel: 7  # actual channel number
        - name: pulse24
          channel: 24
        - name: amc
          channel: 31
    codes:   # list of functions and associated broadlink ir codes. customize to your own learned devices.  Include digits 0 - 9
        turn_on: JgBQAAABKZEVERQRFBEUERUQFRAVNRUQFTYUNhU1FTUVNRU2FBEVNRUQFTUVEBURFDYVEBUQFRAVNRUQFTYUNhUQFTUVNRU2FAAFFQABKEkTAA0FAAAAAAAAAAA= | JgBkAG5vG1QbVBscG1QbVBtUG1QcUxwbHBwbHBscGxwcUxwcGxwbHBscHBwbVBtUG1QbAATXbm8bVBtUGxwbVBtUG1QbVBtUGxwcGxwcGxwbHBxTHBscHBscGxwcGxxTHFMcUxwADQUAAAAA
        turn_off: JgBQAAABKZEVERQRFBEUERUQFRAVNRUQFTYUNhU1FTUVNRU2FBEVNRUQFTUVEBURFDYVEBUQFRAVNRUQFTYUNhUQFTUVNRU2FAAFFQABKEkTAA0FAAAAAAAAAAA= | JgBkAG5vG1QbVBscG1QbVBtUG1QcUxwbHBwbHBscGxwcUxwcGxwbHBscHBwbVBtUG1QbAATXbm8bVBtUGxwbVBtUG1QbVBtUGxwcGxwcGxwbHBxTHBscHBscGxwcGxxTHFMcUxwADQUAAAAA
        volume_up: JgBYAAABJ5QTEhMSExITEhMSExMSOBITEzcTNxM4EjgSOBM3ExITOBITEjgTEhM3EzcTExITEhMSOBMSEzcTEhMTEjgSOBM3EwAFFQABJ0oSAAxWAAEmShMADQU=
        volume_down: JgBYAAABJ5QSExITExITEhMSExITOBITEjgTNxM3EzgSOBI4ExITNxMSEzgSOBM3EzcTEhMTEhMSOBITExITEhMSEzcTOBI4EwAFFgABJ0oTAAxWAAEnShIADQU=
        next_channel: JgBkAG9uHFMcUxwcG1QbVBtUGxwbVBtUG1QbHBwcGxwbVBscGxwcGxxUGxwbHBscHFMcAATWbm8cUxxTHBscVBtUG1QbHBtUG1QbVBscHBscHBtUGxwbHBwbHFMcHBscGxwcUxwADQUAAAAA
        previous_channel: JgAyAG5vG1QbVBscHFMcUxwbHFQbVBtUG1QbHBscHBscUxwcGxwbVBscHBscHBscG1QbAA0FAAAAAAAA
        mute: JgBYAAABJ5QTEhMSExITEhMTEhMSOBMSEzcTNxM4EjgTNxM3ExITOBITEhMSExMSEzcTEhMSExMSOBI4EzcTNxMTEjgSOBM3EwAFFwABJ0kTAAxUAAEnShMADQU=
        enter: gBkAG5vG1QcUxwbHFMcUxwcGxwbVBtUGxwcGxwcGxwbVBscHBscUxxTHBwbHBtUG1QbAATWbm4cVBtUGxwbVBtUGxwcGxxTHFMcHBscGxwcGxxTHBwbHBtUG1QbHBwbHFMcVBsADQUAAAAA
         play: JgCWAG5vG1QbVBscG1QcUxxTHFMcGxwcG1QbVBscGxwcUxwcGxwbHBscHFMcUxwcGxwbAATVb24cUxxTHRsbVBtUHFMbVBscGxwcUxxTHBwbHBtUGxwbHBwcGxwbVBtUGxwbHBwABNVubxtUHFMcGxxTHFMcUxxUGxwbHBtUG1QbHBwcG1QbHBscGxwcGxxUG1QbHBscGwANBQAA
        pause: JgBkAG5vG1QbVBscHFMcUxxTHBscUxwcGxwbHBwbHBwbVBscGxwcGxxTHBwbVBtUG1QbAATXbm8bVBtUGxwbVBtUG1QcGxxTHBwbHBscGxwcHBtUGxwbHBscHFMcHBtUG1QbVBsADQUAAAAA
        stop: JgCWAG5vG1QbVBscHFMcUxwbHBwbVBscG1QbVBscHBscVBscGxwbVBtUGxwcUxwcGxwbAATVb24cUxxTHBwbVBtUGxwbHBxTHBscUxxUGxwbHBtUGxwcGxxTHFQbHBtUGxwbHBwABNZubxtUHVIbHBtUG1QbHBwbHFMcHBtUG1QbHBscHFMcGxwcG1QbVBscG1QcGxwcGwANBQAA
        key_0: JgBkAG9uHFMcUxwcG1QbVBtUGxwbHBxTHFMcGxwcGxwbVBscHBscHBtUG1QbHBscHFMcAATXbm8bVBtUGxwbVBtUG1QbHBwbHFQbVBscGxwbHBxTHBwbHBscG1QbVBscHBwbVBsADQUAAAAA
        key_1: JgBkAG9uHFMcUxwcG1QbVBscGxwbHBwcG1QbHBscGxwcUxwcGxwbVBtUG1QbVBscHFMcAATWbm8cUxxTHBscUxxTHBwbHBscHBscUxwcGxwbHBxTHBscHBtUG1QbVBtUGxwbVBwADQUAAAAA
        key_2: JgBkAG9uHFMcUxwcG1QbVBtUGxwbHBwbHFQbHBscGxwcUxwbHBwbHBtUG1QbVBscHFMcAATWbm8cUxxTHBscVBtUG1QbHBscGxwcUxwcGxwbHBtUGxwcHBscG1QbVBtUGxwcUxwADQUAAAAA
        key_3: JgBkAG5vG1QbVBscHFMcUxwcG1QbHBscHFMcGxwcGxwbVBscHBscUxwcG1QbVBscG1QbAATWbm4cVBtUGxwbVBtUGxwcUxwbHBwbVBscGxwcGxxTHBwbHBtUGxwcUxxTHBscUxwADQUAAAAA
        key_4: JgBkAG5vG1QbVBscHFMcUxxTHFMcHBscG1QbHBwbHBwbVBscGxwbHBwbHFMcVBscG1QbAATXbm8bVBtUGxwbVBtUHFMcUxwbHBwbVBscGxwcGxxTHBwbHBscHBscUxxTHBwbVBsADQUAAAAA
        key_5: JgBkAG5vG1QbVBscHFMcUxwcGxwbVBscG1QbHBwcGxwbVBscGxwcUxxTHBwbVBscG1QbAATVb24cUxxTHBwbVBtUGxwbHBxTHBwbVBscGxwbHBxTHBwbHBtUG1QbHBxTHBscUxwADQUAAAAA
        key_6: JgBkAG5vG1QbVBscHFMcUxxTHBwbVBwbG1QbHBscHBwbVBscGxwbHBxTHBwbVBscG1QbAATVb24cUxxTHBwbVBtUG1QbHBtUGxwcUxwbHBwbHBxTGxwcGxwcG1QbHBtUGxwcUxwADQUAAAAA
        key_7: JgBkAG5vHFMcUxwbHFMcVBscG1QbVBscHFMcGxwcGxwbVBscGxwcUxwcGxwbVBscG1QcAATUbm8bVBtUGxwcUxxTHBwbVBtUGxwbVBscHBscHBtUGxwbHBxTHBscHBtUGxwbVBsADQUAAAAA
        key_8: JgBkAG5vG1QbVBscHFMcUxxTHFMcUxwcG1QbHBscHBscUxwcGxwbHBwbHBwbVBscG1QbAATVbm8bVBtUGxwcUxxTHFMcUxxTHBwbVBscGxwbHBxTHBwbHBscGxwcGxxTHBwbVBsADQUAAAAA
        key_9: JgBkAG5vG1QbVBscG1QcUxwbHBwbHBtUG1QbHBwbHBwbVBscGxwcUxxTHFMcHBscG1QbAATXb24cUxxTHBwbVBtUGxwbHBwbHFMcUxwcGxwbHBxTHBscHBtUG1QbVBscGxwcUxwADQUAAAAA
    sources:  # video sources 
      - name: "Cable" 
        code: JgBWAAABJpITERMSExITEhMRExITNxMSEzcTNxM3EzcTNxM3ExITNxM3ExITEhMRExITNxMSExETEhM3EzcTNxM3ExITNxM3EwAFNgABJkkTAAxiAAEmSROSDQU=

      - name: "Chromecast"
        code: JgBWAAABJpITERMSExITEhMRExITNxMSEzcTNxM3EzcTNxM3ExITNxMSExITNxMRExITNxMSExETNxM3ExITNxM3ExITNxM3EwAFNgABJkkTAAxiAAEmSROSDQU=


input_text:   # HA input text box used to enter a channel number or channel name for channel switching 
    tv_channel:
        name: TV Channel
        min: 0 
        max: 5 
        pattern: 'a-z|A-Z|0-9]*'
        initial: '' 
 
```

## automations.yaml
```
#waits for input from the input_text function above and sends it to the media_player.play_media service of the broadlink component
- alias: Send Channel
  trigger:
    - platform: state
      entity_id: input_text.tv_channel
  action:
    - service: media_player.play_media
      data_template: 
         entity_id: media_player.tv
         media_content_id: '{{ states.input_text.tv_channel.state }}'
         media_content_type: 'channel'

```


## Supported Alexa phrases:
```
### Power control
Alexa, turn on TV
Alexa, turn off TV
Alexa, power on TV
Alexa, power on TV

### Volume control
Alexa, turn up volume by 5 on TV
Alexa, volume up on TV
Alexa, volume down on TV
Alexa, turn up the volume on TV
Alexa, turn down the volume on TV
Alexa, mute on TV
Alexa, unmute on TV

### Channel control
Alexa, channel up on TV
Alexa, channel down on TV
Alexa, change channel to 30 on TV
Alexa, change channel to FOX on TV 


### Media control
Alexa, play on TV
Alexa, stop/pause on TV
Alexa, resume on TV

### Input control
Alexa, change input to HDMI 1 on TV
```






