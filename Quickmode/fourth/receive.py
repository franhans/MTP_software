#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Program to receive packets from the radio link
#

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev
import os


pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio2 = NRF24(GPIO, spidev.SpiDev())
radio2.begin(0, 25)

radio2.setRetries(15,15)

radio2.setPayloadSize(32)
radio2.setChannel(0x60)
radio2.setDataRate(NRF24.BR_250KBPS)
radio2.setPALevel(NRF24.PA_MIN)

radio2.setAutoAck(True)
radio2.enableAckPayload()

radio2.openWritingPipe(pipes[0])
radio2.openReadingPipe(1, pipes[1])

radio2.startListening()
radio2.stopListening()

radio2.printDetails()

radio2.startListening()

# Packet is 32 bytes
#   byte 0: indicates if the received packet is the last one
#   byte 1-4: id of the packet
#   byte 5: size of the data
#   byte 6-31: data
# Payload is 26 bytes
payloadSize = 26

# Buffer to store received data
data = []
try:
    while True:
        pipe = [0]
        while not radio2.available(pipe):
            time.sleep(10000/1000000.0)

        recv_buffer = []
        radio2.read(recv_buffer, 32)

        # Get the id of the packed, which corresponds to bytes 1 to 4
        packet_id = [recv_buffer[1], recv_buffer[2], recv_buffer[3], recv_buffer[4]]
        # return the id of the received packet as ack
        radio2.writeAckPayload(1, packet_id, 4)

        # Obtain the value of the id by weighting and adding the differt bytes
        n = packet_id[0] << 24 | packet_id[1] << 16 | packet_id[2] << 8 | packet_id[3]

        # Get the size of the data in the payload
        size = recv_buffer[5]

        # If first byte is 0x55 it means it's the last packet
        last = True if (recv_buffer[0] == 0x55) else False

        # Get current length of data array
        l = len(data)

        # Check if current data buffer is large enough to store the received data
        if l < n*payloadSize + size:
            # If not, append 0 until it's large enough to store the received data
            for i in range(n*payloadSize + size - l):
                data.append(0)

        # Get the received data and store it in the data buffer
        for i in range(size):
            r = recv_buffer[i + 6]
            data[n*payloadSize + i] = r

        # If the received packet is the last one, write the buffer to a file and exit
        if last:
            file = open("received.txt", mode="wb")
            file.write(bytearray(data))
            file.close()
            break
except KeyboardInterrupt:
    # If the program is interrupted, write received data into file and exit
    file = open("partial_received.txt", mode="wb")
    file.write(bytearray(data))
    file.close()

GPIO.cleanup()
