import asyncio
import logging
import binascii
import socket
import os.path
import platform
import subprocess as sp
import time
import voluptuous as vol
import homeassistant.util as util
import homeassistant.helpers.config_validation as cv
import re
from homeassistant.components import mqtt
from homeassistant.components.media_player import (
    SUPPORT_TURN_ON, SUPPORT_TURN_OFF, SUPPORT_VOLUME_MUTE,SUPPORT_PAUSE, 
    SUPPORT_VOLUME_STEP, SUPPORT_SELECT_SOURCE, SUPPORT_PREVIOUS_TRACK,
    SUPPORT_NEXT_TRACK, MediaPlayerDevice, PLATFORM_SCHEMA, MEDIA_TYPE_CHANNEL, SUPPORT_PLAY,  SUPPORT_PLAY_MEDIA,SUPPORT_STOP)
from homeassistant.components.mqtt import (
    CONF_COMMAND_TOPIC,
    CONF_QOS, CONF_RETAIN
    
    )
from homeassistant.const import (
    CONF_HOST, CONF_MAC, CONF_TIMEOUT, STATE_OFF, STATE_ON,STATE_IDLE,
    STATE_PLAYING, STATE_PAUSED, STATE_UNKNOWN, CONF_NAME, CONF_FILENAME)
from homeassistant.helpers.event import (async_track_state_change)
from homeassistant.core import callback
from base64 import b64encode, b64decode


_LOGGER = logging.getLogger(__name__)

CONF_PING_HOST = 'ping_host'
CONF_POWER_CONS_SENSOR = 'power_consumption_entity'
CONF_POWER_CONS_THRESHOLD = 'power_consumption_threshold'

DEFAULT_NAME = 'IR Media Player'
DEFAULT_PING_TIMEOUT = 1
KEY_PRESS_TIMEOUT=0.5
VOLUME_STEPS=1

SUPPORT_IR_TV = SUPPORT_TURN_OFF | SUPPORT_TURN_ON | \
    SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_STEP | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_PLAY | SUPPORT_PLAY_MEDIA | SUPPORT_STOP | SUPPORT_PAUSE 

CONF_CODES='codes'
CONF_INPUTS='sources'	
CONF_CHANNELS='channels'
CONF_COMMAND_TOPICS='command_topics'
CONF_COMMAND_TOPIC='command_topic'

CODES_SCHEMA = vol.Schema({cv.slug: cv.string})
INPUTS_SCHEMA = vol.Schema({'name':cv.string,'code':cv.string})
CHANNELS_SCHEMA = vol.Schema({'name':cv.string,'channel':cv.string})
TOPICS_SCHEMA = vol.Schema({'topic':cv.string,'type':cv.string})

	
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#    vol.Required(CONF_COMMAND_TOPICS): TOPICS_SCHEMA,
    vol.Required(CONF_COMMAND_TOPICS, default={}):
        vol.Or(cv.ensure_list(TOPICS_SCHEMA), TOPICS_SCHEMA),
    vol.Optional(CONF_PING_HOST): cv.string,
    vol.Optional(CONF_POWER_CONS_SENSOR): cv.entity_id,
    vol.Optional(CONF_POWER_CONS_THRESHOLD, default=10): cv.positive_int,
    vol.Optional(CONF_CODES, default={}):
        vol.Or(cv.ensure_list(CODES_SCHEMA), CODES_SCHEMA),
    vol.Optional(CONF_INPUTS, default={}):
        vol.Or(cv.ensure_list(INPUTS_SCHEMA), INPUTS_SCHEMA),
    vol.Optional(CONF_CHANNELS, default={}):
        vol.Or(cv.ensure_list(CHANNELS_SCHEMA), CHANNELS_SCHEMA),
})

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):    
    """Set up the IR Media Player platform."""
    name = config.get(CONF_NAME)
    #ip_addr = config.get(CONF_HOST)
    #mac_addr = binascii.unhexlify(config.get(CONF_MAC).encode().replace(b':', b''))
    ir_codes={}
    ir_codes[CONF_COMMAND_TOPICS]={}
    ir_codes[CONF_CODES]={}
    ir_codes[CONF_INPUTS]={}
    ir_codes[CONF_CHANNELS]={}
    ir_codes[CONF_CODES]=config.get(CONF_CODES)
    
    for channel in config.get(CONF_CHANNELS):
        key=channel['name'].lower().strip()
        ir_codes[CONF_CHANNELS][key]=channel['channel']

    
    for topic in config.get(CONF_COMMAND_TOPICS):
        ir_codes[CONF_COMMAND_TOPICS][topic['type']]=topic['topic']
        if CONF_COMMAND_TOPIC not in ir_codes.keys():
            ir_codes[CONF_COMMAND_TOPIC]=topic['topic']

        

    for input in config.get(CONF_INPUTS):
        ir_codes[CONF_INPUTS][input['name']]=input['code']
	
    ping_host = config.get(CONF_PING_HOST)
    power_cons_entity_id = config.get(CONF_POWER_CONS_SENSOR)
    power_cons_threshold = config.get(CONF_POWER_CONS_THRESHOLD)
    
    async_add_devices([MQTTIRMediaPlayer(hass, name, mqtt, ir_codes, ping_host, power_cons_entity_id, power_cons_threshold)], True)
    
    
class MQTTIRMediaPlayer(MediaPlayerDevice):

    def __init__(self, hass, name, ir_device, ir_codes, ping_host, power_cons_entity_id, power_cons_threshold):
        self._name = name
        self._state = STATE_OFF 
        self._muted = False
        self._volume = 0
        self._sources_list = []
        self._qos=1
        self._retain=0
        self._ir_device = ir_device
        self._commands = ir_codes
        self._ping_host = ping_host
        self._current_power_cons = 0
        self._power_cons_entity_id = power_cons_entity_id
        self._power_cons_threshold = power_cons_threshold
        
        self._source = None
        
        self._first_pop_up = True
        
        sources_list = []
        for (key, value) in self._commands[CONF_INPUTS].items():
            sources_list.append(key)
                
        self._sources_list = sources_list
            
        if power_cons_entity_id:
            async_track_state_change(
                hass, power_cons_entity_id, self._async_power_cons_sensor_changed)
                
            sensor_state = hass.states.get(power_cons_entity_id)    
                
            if sensor_state:
                self._async_update_power_cons(sensor_state)
                
    async def _async_power_cons_sensor_changed(self, entity_id, old_state, new_state):
        """Handle temperature changes."""
        if new_state is None:
            return

        self._async_update_power_cons(new_state)
        await self.async_update_ha_state()
        
    @callback
    def _async_update_power_cons(self, state):
        try:
            _state = state.state
            if self.represents_float(_state):
                self._current_power_cons = float(state.state)
            else:
                self._current_power_cons = 0
        except ValueError as ex:
            _LOGGER.error('Unable to update from sensor: %s', ex)
            
    def represents_float(self, s):
        try: 
            float(s)
            return True
        except ValueError:
            return False 
                        

    def send_ir(self, section, value):
        if value not in self._commands[section].keys():
            return
        ircode=self._commands[section][value]
        commands = ircode.split("|")
       
        for command in commands: 
            topic=self._commands[CONF_COMMAND_TOPIC]
            r=re.search('^\s*((.+?):)(.+)',command)
            payload=command                 

            if r:
                ty=r.group(2).strip()
                if ty in self._commands[CONF_COMMAND_TOPICS].keys():
                    payload=r.group(3)
                    topic=self._commands[CONF_COMMAND_TOPICS][ty]

            self._ir_device.async_publish(
             self.hass,topic,payload ,self._qos 
               ,self._retain)
            _LOGGER.debug('in openmqtt sent command %s, %s', topic,payload)
                
            if len(commands) > 1:
                time.sleep(.500)
        
    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
    
    @property
    def is_volume_muted(self):
        return False

    @property
    def volume_level(self):
        return self._volume
    
    @property
    def source_list(self):
        return self._sources_list
        
    @property
    def source(self):
        return self._source
        
    @property
    def media_title(self):
        return None
    
    @property
    def supported_features(self):
        if self._sources_list:
            return SUPPORT_IR_TV | SUPPORT_SELECT_SOURCE
        return SUPPORT_IR_TV
        
    def turn_off(self):
        self.send_ir(CONF_CODES, 'turn_off')
        self._state = STATE_OFF
        self.schedule_update_ha_state()
        
    def turn_on(self):
        self.send_ir(CONF_CODES,'turn_on')
        self._state = STATE_PLAYING
        self._source = None
        self.schedule_update_ha_state()
    
    def media_play(self):
        self.send_ir(CONF_CODES, 'play')
        self._state=STATE_PLAYING
        self.schedule_update_ha_state()
        return

    def media_pause(self):
        self.send_ir(CONF_CODES, 'pause')
        self._state=STATE_PAUSED
        self.schedule_update_ha_state()
        return
        
    def media_stop(self):
        self.send_ir(CONF_CODES, 'stop')
        self._state=STATE_IDLE
        self.schedule_update_ha_state()
        return
        
    def media_previous_track(self):
        if self._state == STATE_OFF:
            self._state = STATE_IDLE
        self.send_ir(CONF_CODES, 'previous_channel')
        self.schedule_update_ha_state()

    def media_next_track(self):
        if self._state == STATE_OFF:
            self._state = STATE_IDLE
        self.send_ir(CONF_CODES, 'next_channel')
        self.schedule_update_ha_state()

    def volume_down(self):
        for step in range(VOLUME_STEPS):
            self.send_ir(CONF_CODES, 'volume_down')
        self.schedule_update_ha_state()
     
    def volume_up(self):
        for step in range(VOLUME_STEPS):
            self.send_ir(CONF_CODES, 'volume_up')
        self.schedule_update_ha_state()

    def set_volume_level(self, volume):
        volume=int(volume * 100) 
        isUp=False
        if volume > 50:
            isUp=True
            volume=volume-50

        _LOGGER.debug('in change set volume: %s,%s', volume,isUp)

        for step in range(volume):
            if isUp:
                self.send_ir(CONF_CODES, 'volume_up')
            else:
                self.send_ir(CONF_CODES, 'volume_down')
            
        self.schedule_update_ha_state()

        return

    def mute_volume(self, mute):
        self.send_ir(CONF_CODES, 'mute')
        self._muted = mute
        self.schedule_update_ha_state()
        
    def select_source(self, source):
#        if self._first_pop_up == True:
 #           self._source = None
 #           self._first_pop_up = False
 #       else:
        self.send_ir(CONF_INPUTS, source)
        self._source = source
        self.schedule_update_ha_state()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support changing a channel."""
        if media_type != MEDIA_TYPE_CHANNEL:
            _LOGGER.error('Unsupported media type')
            return
        media_id=media_id.lower().strip()

        if not media_id.isdigit():
            #we have a channel name instead so fetch channel
            if media_id in self._commands[CONF_CHANNELS].keys():
                media_id=self._commands[CONF_CHANNELS][media_id]
                _LOGGER.debug('found channel lookup: %s', media_id)
            else:
                return

        # media_id should only be a channel number
        try:
            cv.positive_int(media_id)
        except vol.Invalid:
            _LOGGER.error('Media ID must be positive integer')
            return
        _LOGGER.debug('in change channel to channel: %s', media_id)

        for digit in media_id:
            await self.hass.async_add_job(self.send_ir, CONF_CODES,'key_' + digit)
            await asyncio.sleep(KEY_PRESS_TIMEOUT, self.hass.loop)
        await self.hass.async_add_job(self.send_ir, CONF_CODES,'enter')

 



    def update(self):
        if self._ping_host:
            if platform.system().lower() == 'windows':
                ping_cmd = ['ping', '-n', '1', '-w',
                            str(DEFAULT_PING_TIMEOUT * 1000), str(self._ping_host)]
            else:
                ping_cmd = ['ping', '-c', '1', '-W',
                            str(DEFAULT_PING_TIMEOUT), str(self._ping_host)]

            status = sp.call(ping_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            if bool(status):
                self._state=STATE_OFF
            else:
                if self._state==STATE_OFF:
                    self._state=STATE_IDLE

        elif self._power_cons_entity_id:
            if self._current_power_cons <= self._power_cons_threshold:
                self._state=STATE_OFF
            else:
                if self._state==STATE_OFF:
                    self._state=STATE_IDLE
                

