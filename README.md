# ALEXA - Broadlink - Home Assistant TV controller including channel selection.

This customization uses a modified broadlink.py file from from Vassilis Panos's project at 
https://github.com/vpnmaster/homeassistant-custom-components as well as a modified version of the 
default Home Assistant Alexa component module.

## Background
I was using the Broadlink Alexa skill and found it had a tendency to keep
 adding extra digits when responding to a change channel command on my TV.  Since I am also using Home Assistant  (with Haaska) at home, I felt I would 
 rather be able to control all aspects of the broadlink from my own system instead of depending on a third party buggy tool which I have no control of.
After looking around, I could not find anything that was accomplishing all I wanted to do without ugly hacks.   I decided to use 
Vassilis Broadlink.py component as as base since it had most functions setup.  I would then add the rest of the functions I needed as well as using this as an opportunity to get 
more familiar with HA and Python.  

## The missing functions:

-  Ability to enter a TV  channel using direct number keypad entry using digits or a TV Callsign or use 
an Alexa phrase such as Alexa, change channel to 123 on TV or Alexa, change channel to PBS on TV
- Play/Pause a TV broadcast (I have a PVR)
- Volume stepped control via Alexa . For example say Alexa, increase volume by 10 on TV.

## Code changes
Alexa component - added ChannelController capability that adds voice control of all channel changing activities.
- added stepped voice control.  I've called the component smarter_home.py so not to conflic with the existing 
HA alexa component.  You can't use both at the same time as they both use the same /alexa/smart_home endpoint.


broadlink.py - added channel tuning function as well as play/pause.  Also converted the code to use the default 
configuration.yaml format instead of using external *.ini files for code configuration.  All configs are setup with the broadlink 
option in the configuraiton.yaml file.  Since HA does not by default have channel changing capability, i had to use the
Play Media function to accomplish this (as used in the samsungtv component) 

Added input_text config option in configuration.yaml to allow changing channel from the HA console just by entering the channel number or callsign.

## Installation
# NOTE: You MUST use Haaska or the HA cloud integration for the Alexa component to work. If not you will need to create your own Alexa intents.

1. Create a "custom_components" directory in your HA configuration directory and copy the alexa and media_player subdirectories into it.
2. add the config options in your configuration.yaml and automations.yaml.  Of course you'll need to use your own IR codes for the functions.

## configuration.yaml

api:  # activate web api

alexa:
  smarter_home:  # activate Alexa component

media_player:
   - platform:  broadlink
    host: 192.168.1.11  # ip address of your broadlink device - required
    mac: '77:FF:77:55:CC:66' # mac address of your broadlink device  - required
    name: tv   # display name of this device - required (used by Alexa)
    ping_host: 192.168.1.12  # optional - smart tv ip address -  if you have a smart tv on the network, this will detect it's state. 
    channels:   # used when you enter or say a channel name instead of entering a channel numerically
        city: 7
        pulse: 24
        amc: 31
    codes:  # this is the list of your IR codes.  The function names are constants. 
	sources:  # your input sources. 
      - name: "Cable" 
        code: 
      - name: "Chromecast"
        code: 
```
api:

alexa:
  smarter_home:

media_player:
  - platform:  broadlink
    host: 192.168.1.11
    mac: '77:FF:77:55:CC:66'
    name: tv 
    ping_host: 192.168.1.12
    channels:
        city: 7
        pulse: 24
        amc: 31
    codes:
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
    sources:
      - name: "Cable" 
        code: JgBWAAABJpITERMSExITEhMRExITNxMSEzcTNxM3EzcTNxM3ExITNxM3ExITEhMRExITNxMSExETEhM3EzcTNxM3ExITNxM3EwAFNgABJkkTAAxiAAEmSROSDQU=

      - name: "Chromecast"
        code: JgBWAAABJpITERMSExITEhMRExITNxMSEzcTNxM3EzcTNxM3ExITNxMSExITNxMRExITNxMSExETNxM3ExITNxM3ExITNxM3EwAFNgABJkkTAAxiAAEmSROSDQU=


input_text:
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
`
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
Alexa, resume on TV``

```





