import RPi.GPIO as GPIO
from lib_nrf24.lib_nrf24 import NRF24
import time
import spidev
import math
import sys
import os
import RPi.GPIO as GPIO
import os


def transmit():
    ##########################################################################
    # Chip configuration
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
    print("Size ---->>>>>> ", size)

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
        print("Buffer ---->>>>>> ", buf)
        while retransmit:
            print("Retransmitting...", buf)
            # Send packet
            radio.write(buf)
            # did it return with a payload?
            radio.startListening() # Escuchamos para recibir ACK
            t0 = time.time()
            while((time.time()-t0)<0.2):
                if radio.available(pipes[0]):
                    pl_buffer=[]
                    ack_size = radio.getDynamicPayloadSize()
                    if ack_size > 0: # Si lo que recibimos no es NULL -> es ACK
                        print("ack_size: ", ack_size)
                        radio.read(pl_buffer, 32)
                        print("ACK_value: ", pl_buffer)
                        # Convert the received ack bytes into an integer corresponding to the id of the packet
                        ack_id = (0xFF & pl_buffer[0])
                        if ack_id == currentPacket:
                            retransmit = False
                            #print('---------------Received = Type')
                        print('------------------------ACK Received')
                time.sleep(0.005)
            radio.stopListening()

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


def receive():
    
    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    radio2 = NRF24(GPIO, spidev.SpiDev())
    radio2.begin(0, 17)
    radio2.setRetries(15,15)
    radio2.setPayloadSize(32)
    radio2.setChannel(0x60)
    radio2.setDataRate(NRF24.BR_250KBPS)
    radio2.setPALevel(NRF24.PA_MIN)

    radio2.setAutoAck(False)
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
    payloadSize = 29
    last_received=0
    id_expected=0
    counter=0

    # Buffer to store received data
    data = []
    try:
        while True:
            pipe = [0]
            while not radio2.available(pipe):
                time.sleep(10000/1000000.0)

            print('recived')
            recv_buffer = []
            radio2.read(recv_buffer, 32)

            # Get the id of the packed, which corresponds to bytes 1 to 4
            packet_id = recv_buffer[1]
            # return the id of the received packet as ack
            #id_byte = bytearray(32)
            id_byte = [int(0xFF & packet_id)]
            print("packet_id: ", packet_id)
            for i in range(31):
                id_byte.append(int(0xFF & packet_id))
            print("id_byte :", id_byte)
            radio2.stopListening()
            radio2.write(id_byte)
            time.sleep(10000/1000000.0)
            radio2.startListening()

            # Obtain the value of the id by weighting and adding the differt bytes

            if packet_id == id_expected :
                # Get the size of the data in the payload
                size = recv_buffer[2]

                # If first byte is 0x55 it means it's the last packet
                last = True if (recv_buffer[0] == 0x55) else False

                # Get current length of data array
                l = len(data)


                # Check if current data buffer is large enough to store the received data
                if l < counter*payloadSize + size:
                    # If not, append 0 until it's large enough to store the received data
                    for i in range(counter*payloadSize + size - l):
                        data.append(0)

                # Get the received data and store it in the data buffer
                print("Size:", size)
                print("recv_buffer:", recv_buffer)
                for i in range(size):
                    r = recv_buffer[i + 3]
                    data[counter*payloadSize + i] = r

                # If the received packet is the last one, write the buffer to a file and exit
                if last:
                    file = open("received.txt", mode="wb")
                    file.write(bytearray(data))
                    file.close()
                    break

                id_expected = (id_expected+1)%250
                counter = counter+1

    except KeyboardInterrupt:
        # If the program is interrupted, write received data into file and exit
        file = open("partial_received.txt", mode="wb")
        file.write(bytearray(data))
        file.close()

    GPIO.cleanup()


GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.OUT)#LED ON_OFF
GPIO.setup(15, GPIO.OUT)#LED TX
GPIO.setup(18, GPIO.OUT)#LED RX
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#ON_OFF
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#TX_RX

GPIO.output(14,GPIO.LOW)
GPIO.output(15,GPIO.LOW)
GPIO.output(18,GPIO.LOW)

while GPIO.input(16) == True:
    time.sleep(20)

GPIO.output(14,GPIO.HIGH)#system is ON
print("ON")


if GPIO.input(20): # If SW2 'ON' then module is TX
    GPIO.output(18,GPIO.HIGH)#module is RX
    print("RX")
    receive()
    os.system('./write_pen.sh received.txt')

else: # If SW2 'OFF' then module is RX
    GPIO.output(15,GPIO.HIGH)#module is TX
    print("TX")
    os.system('./read_pen.sh test.txt')
    transmit()
 # If SW1 'OFF' system reset

GPIO.output(14,GPIO.LOW)
GPIO.output(15,GPIO.LOW)
GPIO.output(18,GPIO.LOW)

