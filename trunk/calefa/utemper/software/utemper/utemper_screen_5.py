#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import os
from pygame.locals import *
from utemper_public import *
import utemper_screen_image
import socket
import psutil
import datetime

import utemper_ipAddress

class cScreen_5:
    carpeta_img = "img/dia/"
    letra_color = (0,0,0)
    cUtemperSceenImagen=None
    screen = None
    letra= None
    
    def __init__(self, screen):
        self.screen = screen
        try:
            self.cUtemperSceenImagen = utemper_screen_image.cScreenImeges()
            self.letra= pygame.font.Font("font/stag-sans-light-webfont.ttf", 20)
        except:
            log(4,"Imposible iniciar la pantalla 5 ")
            self.pantalla=0

    def refrescar_screen(self):
        if (gv.noche==1):
            self.carpeta_img="img/noche/"
            self.letra_color=(255,255,255)
        else:
            self.carpeta_img="img/dia/"
            self.letra_color=(0,0,0)
            
        # cargamos el fondo
        fichero_fondo = self.carpeta_img+"fondo/config_fondo.jpg"
        fondo = self.cUtemperSceenImagen.getImagen(fichero_fondo)
        self.screen.blit(fondo, (0, 0))
		
        #text.
        try:
            string="IP: " + utemper_ipAddress.get_lan_ip()
        except:
            string="IP: Error!"
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 30))
        
        string = "Num Equipo: \n" + str(gv.number_equipo)
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 60))

        string = "%Uso CPU: " + str(psutil.cpu_percent(interval=1))
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 100))
        
        ''' string = "%Memoria: " + str(psutil.virtual_memory().percent)
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 130))'''
        
        string = "%Disco Usado: " + str(psutil.disk_usage('/').percent)
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 160))
        
        '''string = "Encendido desde: " + datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%d-%m %H:%M:%S")
        mytext = self.letra.render(string, False, self.letra_color).convert_alpha()
        self.screen.blit(mytext, (20, 200))'''
        
        
        # se muestran lo cambios en pantalla
        pygame.display.flip()
        log(1,"Refrescar screen 5 OK")

    def boton_screen (self, pos):
        # Entrar menu
        self.screen_number = 1
        