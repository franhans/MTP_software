#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Program to send packets to the radio link
#


import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import math
import sys

##########################################################################
# Chip configuration
GPIO.setmode(GPIO.BCM)
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

# SPI initialization
radio = NRF24(GPIO, spidev.SpiDev())
# Initialization SPI chip select of pin 25
radio.begin(0, 17)
time.sleep(1)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(False)
radio.enableAckPayload()

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])
radio.printDetails()
##########################################################################

print("\n\n\n\n")

# Gets input file, if no fie has been specified, default file "test.txt" is used
if len(sys.argv) > 1:
    filename = str(sys.argv[1])
else:
    filename = "test.txt"

print("File to send: ", filename)

# Loads input file as an array of bytes
file = open(filename, mode='rb', buffering=0)
data = bytearray()
while(True):
    d = file.read(32)
    if(d == b''):
        break
    data += d
file.close()

size = len(data)

initial_time = time.time()

payloadSize = 29
num_packets = math.ceil(size/payloadSize)
currentPacket = 0
counter=0

# Packet transfer start
while counter < num_packets:
    # Gets the size of the data to be sent
    dataSize = min(payloadSize, size-currentPacket*payloadSize)

    # If it's the last packet, send a different header
    if counter == (num_packets - 1):
        buf = [int(0x55)]
    else:
        buf = [int(0xFF)]

    # Append the current packet number to the packet
    buf.append(int(0xFF & (currentPacket)))

    # Append the size of the payload to the packet
    buf.append(int(dataSize))

    # Append actual payload to the packet
    for i in range(payloadSize):
        # If data size is less than payload size, fill with 0
        if i < dataSize:
            buf.append(int(data[currentPacket*payloadSize+i]))
        else:
            buf.append(int(0))

    retransmit = True
    # send a packet to receiver until ack is received
    while retransmit:
        # Send packet
        radio.write(buf)
        # did it return with a payload?
        radio.startListening() # Escuchamos para recibir ACK
        t0 = time.time()
        while(((time.time()-t0)<0.2):
            if radio.available(pipe):
                pl_buffer=[]
                ack_size = radio.getDynamicPayloadSize()
                if ack_size > 0: # Si lo que recibimos no es NULL -> es ACK
                    pl_buffer = radio.read(ack_size)
                    #print(pl_buffer)
                    # Convert the received ack bytes into an integer corresponding to the id of the packet
                    ack_id = (0xFF & pl_buffer[0])
                    if ack_id == currentPacket:
                        retransmit = False
                        radio.stopListening()
                        #print('---------------Received = Type')
                    print('------------------------ACK Received')
                time.sleep(0.005)

    currentPacket = (currentPacket + 1)%250
    counter = counter + 1

    if counter == num_packets:
        break

transfer_time = time.time() - initial_time
if transfer_time > 60:
    print("Total time:"),
    print(transfer_time/60),
    print("min")
else:
    print("Total time:"),
    print(transfer_time),
    print("seconds")
