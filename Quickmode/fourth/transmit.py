#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Program to send packets to the radio link
#


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import file_to_bytes
import time
import spidev
import math
import sys

def progressBar(count, total):
    bar_len = 60
    filled_len = int(round(bar_len*count/float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s\r" % (bar, percents, '%'))
    sys.stdout.flush()

##########################################################################
# Chip configuration
pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

# SPI initialization
radio = NRF24(GPIO, spidev.SpiDev())
# Initialization SPI chip select of pin 25
radio.begin(0, 25)
time.sleep(1)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(NRF24.BR_250KBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
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
data = file_to_bytes.file_to_bytearray(filename)

size = len(data)

initial_time = time.time()

payloadSize = 26
num_packets = math.ceil(len(data)/payloadSize)
currentPacket = 0

# Packet transfer start
while currentPacket < num_packets:
    # Gets the size of the data to be sent
    dataSize = min(payloadSize, size-currentPacket*payloadSize)

    # If it's the last packet, send a different header
    if currentPacket == (num_packets - 1):
        buf = [int(0x55)]
    else:
        buf = [int(0xFF)]

    # Append the current packet number to the packet
    buf.append(int(0xFF & (currentPacket >> 24)))
    buf.append(int(0xFF & (currentPacket >> 16)))
    buf.append(int(0xFF & (currentPacket >> 8)))
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
        if radio.isAckPayloadAvailable():
            pl_buffer=[]
            # Read ack data
            radio.read(pl_buffer, 4)
            # Convert the received ack bytes into an integer corresponding to the id of the packet
            ack_id = ((0xFF & pl_buffer[0]) << 24) | ((0xFF & pl_buffer[1]) << 16) | ((0xFF &pl_buffer[2]) << 8) | (0xFF & pl_buffer[3])

            #print("ACK id:")
            #print(ack_id)
            # If the received ack corresponds to the sent packet, pass to next one
            if ack_id == currentPacket:
                retransmit = False
        time.sleep(0.05)

    currentPacket = currentPacket + 1

    progressBar(currentPacket, num_packets)

    if currentPacket == num_packets:
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
