#!/usr/bin/env python

import urllib2, time
import json
import glob, os
import xml.etree.ElementTree as ET
import socket
from utemper_public import *
import re

class eltiempo:
   # tiempo
   CONF_FILE= "config/utemper.conf"
   lastTimeTiempo = 0
   
   #temp:
   temp = False


   sensorTemp = None
   
   def __init__(self):
   
      self.lastTimeSendWarnig = 0

      self.lastTimeTemp_OK = time.time()
      self.lastTimeTemp = time.time()
      
      if self.int_tiempo()==1:
         log(1,"init int_tiempo OK")
         
      if self.int_temp()==1:
         self.temp=True
         log(1,"init read temperatura OK")
      else:
         self.temp=False
         log(1,"init read temperatura KO")
      
   def int_tiempo(self):
      self.WOEID = int(cread_config().read_config("WOEID"))
      if self.WOEID ==-1:
         gv.tiempo_OK = False
         log(4,"Error Leer WOEID")
         return 0
      self.leer_tiempo()
      return 1
      
   def int_temp(self):
      # Inciamos Lectura Sensor.
      self.Temper_Port = int(cread_config().read_config("WifiTemp_Port"))
      log(1,"Init Read Temperatura.")
      if (self.Temper_Port >0):
         # Iniciamos el Puerto UDP.
         try:
            self.Sockt.close()
            del(self.Sockt)
         except:
            self.Sockt = None
         self.Sockt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
         self.Sockt.setblocking(0)
         self.Sockt.bind(("", self.Temper_Port ))
         print self.Sockt
         self.regex = ur"Temp=(-?[0-9\.]*);"
         return 1
      else:
         try:
            from w1thermsensor import W1ThermSensor
            time.sleep(0.5)
            self.sensorTemp = W1ThermSensor()
            return 1
         except:
            log(3,("Imposible W1ThermSensor"))
            return 0
         
   def suceso(self):
      #leer tiempo
      tiempoSeg = time.time()
      if (tiempoSeg -self.lastTimeTiempo>1800) and (gv.tiempo_OK):
         self.lastTimeTiempo=time.time()
         self.leer_tiempo()
      elif (tiempoSeg -self.lastTimeTiempo>300) and (gv.tiempo_OK == False):
         self.lastTimeTiempo=time.time()
         if self.int_tiempo()==1:
            log(1,"Read tiempo KO ->  OK Bien ")
            
      #leer temperatura
      if (tiempoSeg -self.lastTimeTemp>10) and (self.temp):

         if (self.Temper_Port > 0):
            result = self.leer_Wifi_temper()
         else:
            result = self.leer_temperatura()
         # Check Result.
         if result==1:#Ok.
            self.lastTimeTemp_OK = tiempoSeg
            self.lastTimeTemp=time.time()
            gv.temperatura_error=0
         else:
            gv.temperatura_error=1
            time.sleep(0.2)
      #fallo leer temp.
      if (tiempoSeg - self.lastTimeTemp_OK>300):
         self.lastTimeTemp_OK=time.time()+(2*3600) # Se reintenta en 2 horas.
         try:
            if (tiempoSeg -self.lastTimeSendWarnig > (12*3600)):# Una vez cada 12 horas.
               urllib2.urlopen('URl???Error_Utemper_Leer_Temperatura.')
               self.lastTimeSendWarnig = time.time()
         except:
            log(4,"Fallo Envio Avisio Caida de lectura de Temp.")
         if self.int_temp()==1:
            self.temp=True
            log(1,"Conseguimos iniciar read temperatura OK")
            
   def reset(self):
      self.__init__()
      
   def leer_tiempo(self):   
      if self.WOEID<=0:
         log(4,("Error al leer tiempo WOEID <0 "))
         gv.tiempo_OK = False
         return 0
      try:
         import urllib2, time
         import json
         import glob, os
         import xml.etree.ElementTree as ET
         log(1,("init leer_tiempo... "))
         f = urllib2.urlopen('https://api.wunderground.com/api//*******/geolookup/conditions/forecast/q/Spain/{Ciudad}.json', timeout = 2)
         json_string = f.read()
         parsed_json = json.loads(json_string)

         gv.tiempo_temp = float(parsed_json['current_observation']['temp_c'])
         gv.tiempo_code = int(3200)
         gv.tiempo_estado = parsed_json['current_observation']['icon']
         gv.tiempo_City = parsed_json['location']['city']
         gv.tiempo_speed = float(parsed_json['current_observation']['wind_kph'])
         f.close()
         
         # dia y noche.
         log(1,("Leemos Hora sale el Sol y Se pone... "))
         f = urllib2.urlopen('https://api.wunderground.com/api/*******/astronomy/q/Spain/{Ciudad}.json', timeout = 2)
         json_string = f.read()
         parsed_json = json.loads(json_string)
         sunrise = parsed_json['sun_phase']['sunrise']['hour'] +":"+ parsed_json['sun_phase']['sunrise']['minute']
         sunset  = parsed_json['sun_phase']['sunset']['hour']  +":"+ parsed_json['sun_phase']['sunset']['minute']
         gv.hora_init_dia = time.strptime(sunrise, "%H:%M")
         gv.hora_init_noche = time.strptime(sunset, "%H:%M")
         f.close()
         log(0," leer_tiempo  [OK] "+ str(gv.tiempo_temp) + " C Code:"+ str(gv.tiempo_code))
         gv.tiempo_OK = True
         return 1
      except:
         log(4,"Imposible poder acceder al tiempo.")
         gv.tiempo_OK = False
         return 0
         
   def leer_temperatura(self):
      log(0,"leer_temperatura...")
      temp_c=0
      count = 0
      try:
         temp_c = self.sensorTemp.get_temperature()
         if (temp_c>2 and temp_c<40):
               gv.temperatura = round(temp_c, 2)
               return 1
         return 0
      except:
         log(3,("Imposible leer temperatura "))
         return 0

   def leer_Wifi_temper(self):
      ## Leemos Temperatura.
      try:
         data = self.Sockt.recv(1024)
         log(1,("Recivido UDP data"))
      except socket.error:
         return 0

      datas= re.match(self.regex, data)
      if(datas):
         Temper = float(datas.group(1))
         if (Temper > 0.0) and (Temper < 50):
            #Ok.
            gv.temperatura =  Temper;
            log(1,("Temperatura Leida OK: ")+ str(gv.temperatura))
            return 1
      return 0 
   
   def read_temp_raw(self):
      f = open(self.device_file, 'r')
      lines = f.readlines()
      f.close()
      return lines
