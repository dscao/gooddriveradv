# gooddriveradv 优驾高级版或胎压S版

配置方法：

device_tracker:  
# 优驾胎压S版
  - platform: gddradv
    name: '优驾胎压S版'
    gddrtype: 'taiyas'
    uv_id: '654321'
    u_id: '123456'
    sdf: '6928FAA6-B970-F5A5-85F0-XXXXXXXXXXXX'
    cookie: 'connect.sid=s%3AbFmlUsQbHXXXXXXXXXXXXXXXXXXXXXXXXn.mXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    token: '9509bfa92dbXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
 #优驾高级版   
  - platform: gddradv
    name: '优驾高级版 '
    gddrtype: 'advanced'
    uv_id: '987654'
    u_id: '123456'
    sdf: '6928FAA6-B970-F5A5-85F0-XXXXXXXXXXXX'
    cookie: 'connect.sid=s%3AbFmlUsQbHXXXXXXXXXXXXXXXXXXXXXXXXn.mXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    token: '9509bfa92dbXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    
    
sensor:
  - platform: template
    sensors:
      since_last_carstop1:
        friendly_name: 小汽车胎压S版停车时长
        value_template: >-
          {% set stop_time = as_timestamp(now()) - as_timestamp(state_attr('device_tracker.gddr_gooddriver1', 'statustime')) %}
          {% set days = (stop_time // (60 * 60 * 24)) %}
          {% set weeks = (days// 7) %}
          {% set hours = (stop_time// (60 * 60)) - days * 24 %}
          {% set minutes = (stop_time // 60) - (days * 24 * 60) %}
          {% set days = ((stop_time // (60 * 60 * 24))) - (weeks * 7) %}
          {% set minutes = (minutes) - (hours * 60) %}
          {% macro phrase(value, name) %}
            {%- set value = value | int %}
            {{-'{}{}{}'.format(value,name,end) if value | int > 0 else''}}
          {%- endmacro %}
          {% set text = [ phrase(weeks,'周'),phrase(days,'天'), phrase(hours,'小时'), phrase(minutes,'分钟') ] | select('!=','') | list | join('') %}
          {% if state_attr('device_tracker.gddr_gooddriver1', 'status') == "车辆熄火" %}
            {{ text }}
          {% else %}
            运行中
          {% endif %}
  - platform: template
    sensors:
      since_last_carstop2:
        friendly_name: 小汽车高级版停车时长
        value_template: >-
          {% set stop_time = as_timestamp(now()) - as_timestamp(state_attr('device_tracker.gddr_gooddriver2', 'statustime')) %}
          {% set days = (stop_time // (60 * 60 * 24)) %}
          {% set weeks = (days// 7) %}
          {% set hours = (stop_time// (60 * 60)) - days * 24 %}
          {% set minutes = (stop_time // 60) - (days * 24 * 60) %}
          {% set days = ((stop_time // (60 * 60 * 24))) - (weeks * 7) %}
          {% set minutes = (minutes) - (hours * 60) %}
          {% macro phrase(value, name) %}
            {%- set value = value | int %}
            {{-'{}{}{}'.format(value,name,end) if value | int > 0 else''}}
          {%- endmacro %}
          {% set text = [ phrase(weeks,'周'),phrase(days,'天'), phrase(hours,'小时'), phrase(minutes,'分钟') ] | select('!=','') | list | join('') %}
          {% if state_attr('device_tracker.gddr_gooddriver2', 'status') == "车辆熄火" %}
            {{ text }}
          {% else %}
            运行中
          {% endif %}
