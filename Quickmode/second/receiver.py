#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to receive packets from the radio link
#

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from libraries.lib_nrf24 import NRF24
import time
import spidev



pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)

radio.setRetries(15,15)

radio.setPayloadSize(32)
radio.setChannel(0x60)
radio.setDataRate(NRF24.BR_2MBPS)
radio.setPALevel(NRF24.PA_MAX)
#radio.setAutoAck(False)
radio.enableDynamicPayloads()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()

last=False
file=[]
filename = 'text_rcv.txt'
text = open(filename, 'wb')

id_expected=8
id_last=0

while not last:
    while not radio.available():
        time.sleep(0.01)

    recv_buffer = []
    radio.read(recv_buffer, radio.getDynamicPayloadSize())
    print(recv_buffer)
    header = recv_buffer[0]

    id_received = header & 0x08
    print('ID Expexted', id_expected)
    print('ID Received', id_received)
    if id_received == id_expected:
        sentence=(recv_buffer[1:radio.getDynamicPayloadSize()]) #todo
        print(file)
        aux = id_expected
        id_expected = id_last
        id_last = aux

        # Send ACK
        radio.stopListening()
        ack=bytearray(1)
        ack[0]=(0xFF)
        time.sleep(0.1)
        print(radio.write(ack))
        time.sleep(0.1)
        radio.startListening()
        print(len(recv_buffer))
        if len(recv_buffer) == 32:
            last=True
            print(last)
            text.close()
        else:
            text.write(bytearray(sentence))
    elif len(recv_buffer) ==32:
        last=True
        text.close()
