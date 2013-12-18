#!/usr/bin/python

#Google.
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom
import getopt
import sys
import string
import time
from time import sleep

#Rele.
import RPi.GPIO as GPIO
errores_rele=0


RELE1 = 18
RELE2 = 7
STATUSLED=16

#espera entre busqueda y  busqueda. seg
WAIT_TIME=400

text_event=""

def Start_Google():
       global cal_client
       
       print "Start  Google...."
       cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python_Sample-1.0')
       cal_client.ClientLogin("mail",  "passs", cal_client.source)
       print "Start  Google  [OK]"
      
       
def googleCa():
       global cal_client
       global text_event
       
       rc=GPIO.LOW

       query = gdata.calendar.client.CalendarEventQuery()
       query.start_min = time.strftime("%Y-%m-%dT%H:%M:%S.000+01:00", time.gmtime())
       query.start_max = time.strftime("%Y-%m-%dT%H:%M:%S.000+01:00", time.localtime(time.time()+300))
       # los siguientes 300 seg.
       
       feed = cal_client.GetCalendarEventFeed(q=query)
       
       #print 'Events on Primary Calendar: %s' % (feed.title.text,)
       for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
        for a_when in an_event.when:
			text_event = "Event: '" + an_event.title.text +"' Entre " + a_when.start + " y " + a_when.end
			rc=GPIO.HIGH
        
       return rc

def empezar_rele():     
     print "empezar_rele...."
     GPIO.setmode(GPIO.BCM)
     GPIO.setup(RELE1, GPIO.OUT)
     GPIO.setup(RELE2, GPIO.OUT)
     GPIO.setup(STATUSLED, GPIO.OUT)
     
     GPIO.output(RELE1, GPIO.HIGH)
     GPIO.output(RELE2, GPIO.HIGH)
     GPIO.output(STATUSLED, GPIO.LOW)
     print "empezar_rele %d y %d [OK]" %(RELE1, RELE2)
     print "Estado incial All GPIO.LOW" 

     

def cambiarRele(Estado):
     global errores_rele
     try:
        GPIO.output(RELE2, Estado)
        GPIO.output(STATUSLED, Estado)
        errores_rele=0
     except:
        print"ERRROR!!! No se puede.num_Rele"
        errores_rele+=1
        sleep (33)
        if (errores_rele> 3):
          print "ERROR: Max numero de erorres reiniciamos:! "
          os.system("reboot")

def main():
     global text_event
     global WAIT_TIME
     
     old_estado = GPIO.LOW
     old_time= 0
     
     #int
     empezar_rele()
     Start_Google()
     
     while (1):

          estado= googleCa()
          cambiarRele(estado)

          if (estado != old_estado):
               print "IMP: cambiio de estado: antes: %d ahora: %d" %(old_estado, estado)
               old_estado = estado 
               old_time =  time.time()
               print text_event
               
          #control del led status.
          for x in range(0, WAIT_TIME):
               GPIO.output(STATUSLED, GPIO.HIGH)
               GPIO.output(STATUSLED, GPIO.LOW)
               sleep((0.5-(estado*0.3)))
               GPIO.output(STATUSLED, GPIO.LOW)
               GPIO.output(STATUSLED, GPIO.HIGH)
               sleep((0.5-(estado*0.3)))

          if (estado==GPIO.HIGH) and (time.time()-old_time>1800):
               print "Mucho tiempo encendido: apagamos 30 seg."
               cambiarRele(GPIO.LOW)
               sleep (30)
               cambiarRele(estado)
               old_time= time.time()
               
if __name__ == '__main__':
  main()
