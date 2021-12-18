"""
Support for gooddriver.cn 优驾胎压S和高级版
# Author:
    dscao
# Created:
    2021/3/8
    
https://ssl.gooddriver.cn/UserServices/GetUserIOTDevice

device_tracker:  
  - platform: gddradv
    name: 'gooddriver'
    uv_id: '654321'
    u_id: '123456'
    sdf: '6928FAA6-B970-F5A5-85F0-XXXXXXXXXXXX'
    cookie: 'connect.sid=s%3AbFmlUsQbH0XhfoXs-w3m4toLN6rXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    token: '9509bfa92db1XXXXXXXXXXXXXXXXXXXX'
"""
import logging
import asyncio
import json
import time, datetime
import requests
import re
from dateutil.relativedelta import relativedelta 
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from datetime import timedelta
from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout
import homeassistant.util.dt as dt_util
from homeassistant.components import zone
from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.device_tracker.const import CONF_SCAN_INTERVAL
from homeassistant.components.device_tracker.legacy import DeviceScanner
from homeassistant.const import (
    CONF_NAME,
    ATTR_GPS_ACCURACY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    STATE_HOME,
    STATE_NOT_HOME,
)
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import slugify
from homeassistant.helpers.event import track_utc_time_change
from homeassistant.util import slugify
from homeassistant.util.location import distance


TYPE_GEOFENCE = "Geofence"

__version__ = '0.1.1'
_Log=logging.getLogger(__name__)

COMPONENT_REPO = 'https://github.com/dscao/gooddriveradv/'
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
ICON = 'mdi:car'

DEFAULT_NAME = 'gooddriver'
GDDRTYPE = 'gddrtype'
UV_ID = 'uv_id'
U_ID = 'u_id'
SDF = 'sdf'
COOKIE = 'cookie'
TOKEN = 'token'

API_URL = "http://restcore.gooddriver.cn/API/Values/HudDeviceDetail/"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(GDDRTYPE): cv.string,
    vol.Required(UV_ID): cv.string,
    vol.Required(U_ID): cv.string,
    vol.Required(SDF): cv.string,
    vol.Required(COOKIE): cv.string,
    vol.Required(TOKEN): cv.string,
    vol.Optional(CONF_NAME, default= DEFAULT_NAME): cv.string,
})





async def async_setup_scanner(hass, config, async_see, discovery_info=None):
    interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    sensor_name = config.get(CONF_NAME)
    gddrtype = config.get(GDDRTYPE)
    uv_id = config.get(UV_ID)
    u_id = config.get(U_ID)
    sdf = config.get(SDF)
    cookie = config.get(COOKIE)
    token = config.get(TOKEN)
    
    if gddrtype == "taiyas" :
        API_URL = "https://ssl.gooddriver.cn/UserServices/GetUserIOTDevice"
    elif gddrtype == "advanced" :
        API_URL = "https://ssl.gooddriver.cn/UserServices/getLastCarStopInfo"
        
    url = API_URL
    _Log.info("url:" + url + " ; SDF:" + sdf )
    scanner = GddradvDeviceScanner(hass, async_see, sensor_name, url, uv_id, u_id, sdf, cookie, token, gddrtype)
    await scanner.async_start(hass, interval)
    return True


class GddradvDeviceScanner(DeviceScanner):
    def __init__(self, hass, async_see, sensor_name: str, url: str, uv_id: str, u_id: str, sdf: str, cookie: str, token: str, gddrtype: str):
        """Initialize the scanner."""
        self.hass = hass
        self.async_see = async_see
        self._name = sensor_name
        self._url = url
        self._uvid = uv_id
        self._uid = u_id
        self._sdf = sdf
        self._cookie = cookie
        self._token = token
        self._gddrtype = gddrtype
        self._state = None
        self.attributes = {}
    
    def post_data(self, url, headerstr, datastr):
        json_text = requests.post(url, verify=False, headers=headerstr, data = datastr).content
        json_text = json_text.decode('utf-8')
        json_text = re.sub(r'\\','',json_text)
        json_text = re.sub(r'"{','{',json_text)
        json_text = re.sub(r'}"','}',json_text)
        resdata = json.loads(json_text)
        return resdata
        
        
    def time_diff (timestamp):
                result = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
                hours = int(result.seconds / 3600)
                minutes = int(result.seconds % 3600 / 60)
                seconds = result.seconds%3600%60
                if result.days > 0:
                    return("{0}天{1}小时{2}分钟".format(result.days,hours,minutes))
                elif hours > 0:
                    return("{0}小时{1}分钟".format(hours,minutes))
                elif minutes > 0:
                    return("{0}分钟{1}秒".format(minutes,seconds))
                else:
                    return("{0}秒".format(seconds))
                    
                    
    async def async_start(self, hass, interval):
        """Perform a first update and start polling at the given interval."""
        await self.async_update_info()
        interval = max(interval, DEFAULT_SCAN_INTERVAL)
        async_track_time_interval(hass, self.async_update_info, interval)             
            
    
    async def async_update_info(self, now=None):
        """Get the gps info."""
        
        HEADERS = {
            'Host': 'ssl.gooddriver.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self._cookie,
            'Content-Length': '49',
            'Connection': 'keep-alive',
            'SDF': self._sdf,
            'token': self._token,
            'Accept': '\*/\*',            
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'gooddriver/.7.1 CFNetwork/1209 Darwin/20.2.0'
            }

        Data = '{\"UV_ID\":' + self._uvid + ',\"U_ID\":' + self._uid + ',\"QUERY_USAGE\":true}'
        
        def time_diff (timestamp):
            result = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
            hours = int(result.seconds / 3600)
            minutes = int(result.seconds % 3600 / 60)
            seconds = result.seconds%3600%60
            if result.days > 0:
                return("{0}天{1}小时{2}分钟".format(result.days,hours,minutes))
            elif hours > 0:
                return("{0}小时{1}分钟".format(hours,minutes))
            elif minutes > 0:
                return("{0}分钟{1}秒".format(minutes,seconds))
            else:
                return("{0}秒".format(seconds))
                

        try:
            async with timeout(10):                
                ret =  await self.hass.async_add_executor_job(self.post_data, self._url, HEADERS, Data)
                _Log.debug("请求结果: %s", ret)
        except (
            ClientConnectorError
        ) as error:
            raise UpdateFailed(error)
        _Log.debug("Requests remaining: %s", self._url)
        
        if self._gddrtype == "taiyas" :
            if ret['ERROR_CODE'] == 0:
                _Log.info("请求服务器信息成功.....") 
                
                if ret['MESSAGE']['UID_STATE'] == 1:
                    status = "车辆点火"
                elif ret['MESSAGE']['UID_STATE'] == 2:
                    status = "车辆熄火"
                elif ret['MESSAGE']['UID_STATE'] == 3:
                    status = "车辆离线"
                else:
                    status = "未知"
                                   
                kwargs = {
                    "dev_id": slugify("gddr_{}".format(self._name)),
                    "host_name": self._name,                
                    "attributes": {
                        "icon": ICON,
                        "status": status,
                        "querytime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "statustime": re.sub(r'\/','-',ret['MESSAGE']['UID_UPLOAD_TIME']), 
                        "time": ret['MESSAGE']['UID_RECENT_PLACE']['Time'],
                        "speed": ret['MESSAGE']['UID_RECENT_PLACE']['Speed'],
                        "course": ret['MESSAGE']['UID_RECENT_PLACE']['Course'],
                        "Parking_time": time_diff (int(time.mktime(time.strptime(ret['MESSAGE']['UID_RECENT_PLACE']['Time'], "%Y-%m-%d %H:%M:%S")))),
                        },
                    }
                kwargs["gps"] = [
                        ret['MESSAGE']['UID_RECENT_PLACE']['Lat'] - 0.00101,
                        ret['MESSAGE']['UID_RECENT_PLACE']['Lng'] - 0.00600,
                    ]
           
            else:
                _Log.error("send request error....")
        elif self._gddrtype == "advanced" :    
            if ret['UV_LAST_STATION'] != "":
                _Log.info("请求服务器信息成功.....") 
                
                strlist = ret['UV_LAST_STATION'].split(',')
                if float(strlist[2]) == 0:
                    status = "车辆熄火"
                else:
                    status = "车辆点火"
                
                kwargs = {
                    "dev_id": slugify("gddr_{}".format(self._name)),
                    "host_name": self._name,                
                    "attributes": {
                        "icon": ICON,
                        "status": status,
                        "querytime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "statustime": re.sub(r'\/','-',ret['UV_LAST_STAYTIME']), 
                        "Parking_time": time_diff (int(time.mktime(time.strptime(re.sub(r'\/','-',ret['UV_LAST_STAYTIME']), "%Y-%m-%d %H:%M:%S")))),
                        },
                    }
                kwargs["gps"] = [
                        float(strlist[1]) - 0.00751,
                        float(strlist[0]) - 0.01230,
                    ]
           
            else:
                _Log.error("send request error....")
        result = await self.async_see(**kwargs)
        return result
