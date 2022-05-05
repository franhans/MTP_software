import RPi.GPIO as GPIO
from lib_nrf24.lib_nrf24 import NRF24
import time
import spidev
import math
import sys
import os
import shutil
import gzip
import RPi.GPIO as GPIO


def progressBar(count, total):
    bar_len = 60
    filled_len = int(round(bar_len*count/float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s\r" % (bar, percents, '%'))
    sys.stdout.flush()

def transmit():

    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    # SPI initialization
    radio = NRF24(GPIO, spidev.SpiDev()) #SPI configuration
    radio.begin(0, 17)
    time.sleep(0.5)
    radio.setRetries(15,15)
    radio.setPayloadSize(32)
    radio.setChannel(0x60)

    radio.setPALevel(NRF24.PA_HIGH)
    radio.setDataRate(NRF24.BR_2MBPS)
    radio.setAutoAck(False)
    radio.enableAckPayload()
    radio.enableDynamicPayloads()

    radio.openWritingPipe(pipes[1])
    radio.openReadingPipe(1, pipes[0])
    radio.printDetails()

    print("Transceiver initialized")

    print(radio.getCRCLength())

    # Start opening the file
    # Gets input file, if no fie has been specified, default file "test.txt" is used
    if len(sys.argv) > 1:
        filename = str(sys.argv[1])
    else:
        filename = "test.txt"

    print("Name of the text file: ", filename)

    with open(filename, 'rb') as f_in:
        with gzip.open('transmit.txt.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    # Loads input file as an array of bytes
    file = open('transmit.txt.gz', mode='rb', buffering=0)
    data = bytearray()
    while(True):
        d = file.read(32)
        if(d == b''):
            break
        data += d
    file.close()

    size = len(data)
    #print("Size in bytes---->>>>>> ", size)

    start_time = time.time()

    payload_length = 29
    num_packets = math.ceil(size/payload_length)
    currentPacket = 0
    counter=0
    timeout=0.1

    # Data transmission
    while counter < num_packets:

        dataSize = min(payload_length, size-counter*payload_length)

        # Check if the packet is the last one
        #packet = [int(0x00)] if (counter == (num_packets - 1)) else packet = [int(0xFF)]
        if counter == (num_packets - 1):
            packet = [int(0x00)] #we are sending the last packet
            #print("Las packet sent")
        else:
            packet = [int(0xFF)] #the packet is not the last one

        packet.append(int(0xFF & (currentPacket))) # Add the id of the packet

        packet.append(int(dataSize)) # Add the payload length

        for i in range(payload_length): # Add the data in the payload
            # If data size is less than payload size, fill with 0
            if i < dataSize:
                packet.append(int(data[counter*payload_length+i]))
            else:
                packet.append(int(0))

        # transmission of the packet and wait for the ACK
        retransmit = True
        #print("Packet ---->>>>>> ", packet)
        while retransmit:
            #print("Retransmitting...", packet)

            radio.write(packet) # Send the packet

            t0 = time.time()
            radio.startListening()
            while((time.time()-t0)<timeout):
                if radio.available(pipes[0]):
                    ack=[]
                    ack_size = radio.getDynamicPayloadSize() #obtain the ACK length
                    if ack_size > 0:
                        #print("ack_size: ", ack_size)
                        radio.read(ack, 1) #the ACK are always 32 bytes
                        #print("ACK_value: ", ack)
                        ack_id = (0xFF & ack[0]) 
                        if ack_id == currentPacket:
                            retransmit = False
                            break
                            #print('---------------Received = Type')
                time.sleep(0.00001)
            radio.stopListening()
	    

        currentPacket = (currentPacket + 1)%250
        counter = counter + 1
        progressBar(counter, num_packets)

        #if counter == num_packets:
        #    break

    transfer_time = time.time() - start_time
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
    radio2.setDataRate(NRF24.BR_2MBPS)
    radio2.setPALevel(NRF24.PA_HIGH)

    radio2.setAutoAck(False)
    radio2.enableAckPayload()

    radio2.openWritingPipe(pipes[0])
    radio2.openReadingPipe(1, pipes[1])

    radio2.startListening()
    radio2.stopListening()
    radio2.printDetails()

    payload_length = 29
    id_expected=0
    counter=0 #number of received packets
    last_packet = False
    data = [] # Array to store the whole data


    radio2.startListening()
    try:
        while (not last_packet):
            #pipe = [0]
            while not radio2.available():
                time.sleep(0.00001)

            #print('packet recived')
            packet = []
            radio2.read(packet, 32)

            packet_id = packet[1]
            #print("packet_id: ", packet_id)

            #Generate the ACK
            ack = bytearray(1)
            ack[0] = int(0xFF & packet_id)
            radio2.stopListening()
            radio2.write(ack)
            time.sleep(0.00001)
            radio2.startListening()

            if packet_id == id_expected : #check if tha packet is the one expected

                size = packet[2] # Get the size of the data in the payload
                #print("Size:", size)
		
                l = len(data)

                # Check if current data buffer is large enough to store the received data
                if l < counter*payload_length + size:
                    # If not, append 0 until it's large enough to store the received data
                    for i in range(counter*payload_length + size - l):
                        data.append(0)

                # Get the received data and store it in the data buffer
                #print("packet:", packet)
                for i in range(size):
                    data[counter*payload_length + i] = packet[i + 3]

                # If the received packet is the last one, write the buffer to a file and exit
                if GPIO.input(16) or (packet[0] == 0x00):
                    file = open("received_compressed.txt", mode="wb")
                    file.write(bytearray(data))
                    file.close()
                    #Decompress
                    with gzip.open('received_compressed.txt', 'rb') as f:
                        uncompressed_sentences = f.read()

                    uncompressedFile = open('received.txt', 'wb') 
                    uncompressedFile.write(uncompressed_sentences)

                    last_packet = True

                id_expected = (id_expected+1)%250
                counter = counter+1

    except KeyboardInterrupt:
        # If the program is interrupted, write received data into file and exit
        file = open("received.txt", mode="wb")
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
    time.sleep(0.1)

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
