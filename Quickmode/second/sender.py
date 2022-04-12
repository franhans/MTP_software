import RPi.GPIO as GPIO
from libraries.lib_nrf24 import *
import time
import spidev
import struct
import math

GPIO.setmode(GPIO.BCM)

pipes = [[0xe7,0xe7,0xe7,0xe7,0xe7], [0xc2,0xc2,0xc2,0xc2,0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0,17)
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MAX)
#radio.setAutoAck(False)
radio.enableDynamicPayloads()
#radio.enableAckPayload()
radio.stopListening()
radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1,pipes[0])
radio.printDetails()

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

filename = "text.txt"

file = open(filename, "rb")
strF = file.read()
file.close()
buf=list(chunkstring(strF,30))
print(len(buf))

Timeout=500e-3
id_current=0
id_last=8

for k,p in enumerate(buf):
    packet=bytearray(len(p)+1)
    aux = id_current
    id_current = id_last  #00010000 # esto se calculará a partir del for i su contador y luego haremos mod2 para tenere solo 1 bit
    id_last = aux
    header = (0xFF & id_current)
    ack_received = False
    packet[0]=header
    packet[1:] = bytearray(p)
    while not ack_received:
        timer = time.time()
        sent = radio.write(packet)
#        print(bytearray(p).decode('utf8'))
        if sent:
            print(sent)
            while (ack_received == False) and ((time.time()-timer) < Timeout):
                radio.startListening()
                time.sleep(0.05)
                if radio.available():
                    ack_buf=[]
                    radio.read(ack_buf, radio.getDynamicPayloadSize())
                    if (ack_buf[0] & 0xFF)==0xFF: # Si lo que recibimos no es NULL -> es ACK
                        ack_received = True
                        print('ACK Received')
        time.sleep(0.25)
        radio.stopListening()
radio.write([1 for _ in range(32)])
print("Done")

