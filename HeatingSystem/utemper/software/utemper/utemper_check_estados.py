#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, time
import xml.etree.ElementTree as ET
import socket
import os, os.path, subprocess
import utemper_ipAddress
from uuid import getnode as get_mac
from utemper_public import *

class cCheck_estados:
    flie_config_wifi = "/tmp/wifi.var"
    file_watchdog =  "/tmp/file_watchdog.txt"
    lastTimeNoche=0
    
    lastTimeCheckInternet=0    
    lastTimeReadWifiStatus =0
    lastTimeModifyWifiStatus =0
    lastTimePerroGuardian = 0

    def __init__(self):
        default_timeout = 5
        socket.setdefaulttimeout(default_timeout)
        gv.number_equipo = int(("0x"+ getserial()), 0)
        if (gv.number_equipo<=0):
            log(5, "Error al leer number_equipo: "+ gv.number_equipo )
            log(5, "Numero de equipo por defecto: 00000000000000" )
        # Check with configuration.
        if(gv.number_equipo != int(cread_config().read_config("serial"))):
            cread_config().update_config_file("serial",str(gv.number_equipo))
		#Wifi Status.
        self.read_wifi_estado()
         
    def suceso (self):
        # check noche:
        if (time.time()-self.lastTimeNoche>900):
            self.checkNoche()
            self.lastTimeNoche = time.time()
            
        if (time.time()-self.lastTimeCheckInternet>180):
            # enviar estado del equipo.
            log(0, "suceso check estados: leemos el estado del Internet" )
            self.check_intenernet()
            self.lastTimeCheckInternet = time.time()
            if (gv.internet == 1):
               gv.wifi_ip = utemper_ipAddress.get_lan_ip()
            
        if (time.time()-self.lastTimeReadWifiStatus>15):
            self.read_wifi_estado()
            self.lastTimeReadWifiStatus = time.time()

        if (time.time()-self.lastTimePerroGuardian>60):
            self.ActualizaWatchdog()
            self.lastTimePerroGuardian = time.time()
            
    def reset(self):
        self.checkNoche()
        self.read_wifi_estado()

    def checkNoche(self):
        ahora= time.strptime( time.strftime("%I:%M %p", time.localtime()), "%I:%M %p")
        if (gv.hora_init_dia < ahora < gv.hora_init_noche):
            if gv.noche!=0:
                gv.noche=0 # dia
                gv.reset_class = 2
                log(2, "Cambiamos a dia. Reseteamos.")
        else:
            if gv.noche!=1:
                gv.noche=1 # noche
                gv.reset_class = 2
                log(2, "Cambiamos a noche. Reseteamos.")

    def check_intenernet(self):
        # check internet.
        ip_ping = "8.8.8.8"
        result = os.system("ping -c 1 -w 1 %s >/dev/null" %ip_ping)
        if (result== 0):
            gv.internet=1
        else:
            gv.internet=0
         
    def read_wifi_estado(self):
        # read
        try:
            if (os.path.getmtime(self.flie_config_wifi) != self.lastTimeModifyWifiStatus):
                log(1, "suceso check estados: leemos el estado Wifi" )
                f = open(self.flie_config_wifi)
                lines = f.readlines()
                f.close()
                if int(lines[2]) == 1:
                    gv.internet = 1
                gv.wifi_estado=int(lines[0]) + int(lines[1]) + int(lines[2])
                gv.wifi_ip=lines[3].replace("\n", "")
                self.lastTimeModifyWifiStatus = os.path.getmtime(self.flie_config_wifi)
                return 1
            else:
                return 0

        except:
            log(4, "Imposible poder leer el estado del wifi del fichero wifi.var" )
            gv.wifi_estado = 0
            gv.wifi_ip = ""
            return 0

    def ActualizaWatchdog(self):
        try:
            log(0, "Actualizamos perro guardian: " + self.file_watchdog)
            f = open(self.file_watchdog,'w')
            lines = f.write("1")
            f.close()
        except:
            log(5, "Imposible actulizar perro guardian: reboot!!" )
            subprocess.call("reboot")
            exit()


def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
	
  except:
    cpuserial = "00000000000000"
  return cpuserial
