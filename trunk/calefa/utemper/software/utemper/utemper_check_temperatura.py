#!/usr/bin/env python

import sys
import time, datetime, os
from utemper_public import *

class cCheck_temperatura:
    lastTimeCheckCalefa=0
    RELE_FILE="/tmp/rele.var"
    FOLER_PROGRA = "programacion/"
    tiempo_rele = 0
    horarios=[]
    def __init__(self):
        # read config value:
        gv.temperatura_max = float (cread_config().read_config("temperatura"))
        gv.estadoCalefa = int (cread_config().read_config("estado_caldera"))
        self.leer_temperatura()
        self.checkEstadoCheckCalefacion()
        self.actualiza_rele(gv.rele)

    def suceso(self):
        # check  programacion del la calefacion:
        if (time.time()-self.lastTimeCheckCalefa>6):
            self.checkEstadoCheckCalefacion()
            self.lastTimeCheckCalefa = time.time()
            
    def reset(self):
        self.__init__()
        
    def checkEstadoCheckCalefacion(self):
        if(gv.estadoCalefa == 0):
            # estado Apagado.
            if (gv.rele !=0):
                self.actualiza_rele(0)

        elif(gv.estadoCalefa == 1):
            #estado  Encendido.
            self.check_temperatura()

        elif (gv.estadoCalefa == 2):
            # estado programado
            hora=time.localtime()
            index = (hora.tm_hour*4) + (hora.tm_min/15)
            if 0 < index >=len(self.horarios):
                clog().log(3, "checkEstadoCheckCalefacion: mal estado de index en leer estado %d " %(index) )
                index = 0
            if (self.horarios[index]!="0"):
                self.check_temperatura()
            else:
                if (gv.rele !=0):
                   self.actualiza_rele(0)
                
    def check_temperatura(self):
        clog().log(0, "Temperatura: %.2f Temperatura_Max %.2f " %(gv.temperatura , gv.temperatura_max ))
        if ((gv.temperatura + 0.2) < gv.temperatura_max) and (gv.rele==0):
                # temperatura menor y rele apagado.
                self.actualiza_rele(1)

        elif ((gv.temperatura - 0.2) > gv.temperatura_max) and (gv.rele==1):
                # temperatura mayor y rele encendido.
                self.actualiza_rele(0)
                
    def actualiza_rele(self, valor):
        iFile = file(self.RELE_FILE, 'w')
        iFile.write(str(valor))
        iFile.close()
        gv.rele = valor
        clog().log(2, "Actulizado valor del rele a -%d- " %(valor) )
        
    def leer_temperatura(self):
        fichero = str(time.localtime().tm_wday +1) + ".txt"
        clog().log(1, "Leer la temperatura del fichero %s..." %(self.FOLER_PROGRA +fichero) )
        iFile = file(self.FOLER_PROGRA +fichero, 'r')
        line = iFile.readline()
        line = line.replace("\n", "")
        iFile.close()        
        self.horarios = line.split(';')
