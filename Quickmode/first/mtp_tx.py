try:

    import RPi.GPIO as GPIO
    from libraries.lib_nrf24 import NRF24
    import time
    import spidev

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    #GPIO.setup(16, GPIO.OUT)#LED 1
    #GPIO.setup(20, GPIO.OUT)#LED 2
    #GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#TXRX
    #GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#ONOFF
    GPIO.output(23,1)
    GPIO.output(24,1)
    GPIO.output(16,0)
    GPIO.output(20,0)

    TX_RX=True

    #while True:
    #    input_onoff= GPIO.input(15)
    #    input_txrx= GPIO.input(14)
    #    if(input_onoff==True):
    #        time.sleep(1)
    #        print("waiting")
    #    else:
    #        TX_RX=input_txrx
    #        break

    if(TX_RX):
        print("Transmitter")
        pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

        radio = NRF24(GPIO, spidev.SpiDev())
        radio2 = NRF24(GPIO, spidev.SpiDev())
        radio.begin(0, 17)
        radio2.begin(1, 17)
        radio.setPayloadSize(32)
        radio.setChannel(0x60)  # this is the lower channel
        radio2.setPayloadSize(32)
        radio2.setChannel(0x65)

        radio.setDataRate(NRF24.BR_250KBPS)#2MBPS)
        radio.setPALevel(NRF24.PA_HIGH)#MIN)
        radio.setAutoAck(False)
        radio.enableDynamicPayloads()
        radio2.setDataRate(NRF24.BR_250KBPS)#2MBPS)
        radio2.setPALevel(NRF24.PA_HIGH)#MIN)
        radio2.setAutoAck(False)
        radio2.enableDynamicPayloads()

        radio.openWritingPipe(pipes[1])
        radio.printDetails()
        print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
        radio2.openReadingPipe(0, pipes[0])
        radio2.printDetails()

        ack  =  []
        str_ack=""
        sizepayload=31
        packets = []
        actual_flag=0
        previous_flag=0
        infile= open("file_to_send", "rb" )
        data= infile.read()
        j=0
        infile.close()
        message_aux=[]



        # radio.startListening()
        # message = list(input("Enter a message to send: "))
        for i in range (0, len(data),sizepayload):
            if(i+sizepayload)>len(data):
                packets.append(data[i:])
            else:
                packets.append(data[i:i+sizepayload])



        inicio=time.time()
        for message in packets:
           # message = list("Hello World is awesome ")
            message_aux=message
            radio.write(chr(actual_flag)+ message_aux)
            print("We sent the message of {}".format(message))
            previous_flag = actual_flag
            actual_flag=(actual_flag+1)%10

            timeout = time.time() + 0.5
            time.sleep(0.05)
            while(1):
                radio2.openReadingPipe(0,pipes[0])
                radio2.startListening()
                if radio2.available(0):
                    radio2.read(ack, radio2.getDynamicPayloadSize())
                    str_ack=""
                    for x in range(0, len(ack)):
                        str_ack=str_ack + chr(ack[x])
                    if (str_ack[0] == 'A') 
                        print(str_ack)
                        print("Arriba Ack recibidoQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
                        if(list(str_ack) != (list("ACK")+list(actual_flag))):
                            print(list("ACK")+list(actual_flag))
                            radio.write(chr(previous_flag) + message_aux)
                            timeout=time.time() + 0.5
                            print("mistaken")
                        else:
                            break
                if((time.time()+0.2) > timeout):
                    print("reenvio tramax")
                    j=j+1
                    print(j)
                    radio.openWritingPipe(pipes[1])
                    radio.write(chr(previous_flag) + message_aux)
                    timeout=time.time() + 0.5
    #        time.sleep(1)


        final=time.time()
        tiempo=final-inicio
        print(tiempo)
        GPIO.output(23,0)
        GPIO.output(24,0)
        GPIO.output(16,0)

    else:
        print("Receiver")
        pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

        radio =NRF24(GPIO, spidev.SpiDev())
        radio.begin(0,17)
        radio.setPayloadSize(32)
        radio.setChannel(0x60)#lower
        radio.setDataRate(NRF24.BR_250KBPS)#BR_2MBPS)
        radio.setPALevel(NRF24.PA_HIGH)#LOW)#HIGH)#PA_MIN)
        radio.setAutoAck(False)
        radio.enableDynamicPayloads()

        radio2 =NRF24(GPIO, spidev.SpiDev())
        radio2.begin(1,17)
        radio2.setPayloadSize(32)
        radio2.setChannel(0x65)#higher
        radio2.setDataRate(NRF24.BR_250KBPS)#BR_2MBPS)
        radio2.setPALevel(NRF24.PA_HIGH)#LOW)#HIGH)#PA_MIN)
        radio2.setAutoAck(False)
        radio2.enableDynamicPayloads()

        radio.openReadingPipe(0, pipes[1])
        radio2.openWritingPipe(pipes[0])

        radio.printDetails()
        print("///////////////////////////////////////////////////////////")
        radio2.printDetails()

        frame = []
        str_frame=""
        flag=0
        outputfile = open("revived_file", "wb")
        while(1):
            str_frame=""
            timeout=time.time() +0.5
            radio.openReadingPipe(0, pipes[1])
            while(1):#time.time() < timeout):

                ##radio.startListening()
                if radio.available(0):
                    radio.read(frame, radio.getDynamicPayloadSize())
                    print(frame)
                    print(flag)
                    if(chr(frame[0])==chr(flag)):
                        for x in range(1, len(frame)):
                            str_frame=str_frame + chr(frame[x])
                        outputfile.write(str_frame)
                        print(frame)
                        print(str_frame)
                        flag=(flag+1)%10
                        radio2.write(list("ACK")+list(chr(flag)))
                        break
                    else:
                        radio2.write(list("ACK")+list(flag))
                        timeout=time.time() + 0.5
                if((time.time()+0.3) > timeout):
                    radio.openReadingPipe(0, pipes[1])
                    radio.startListening()
                    radio2.write(list("ACK")+list(flag))
                    timeout=time.time() + 0.5

except KeyboardInterrupt:
    GPIO.output(23,0)
    GPIO.output(24,0)
    GPIO.cleanup()
