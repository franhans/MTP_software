try:
    import RPi.GPIO as GPIO
    from lib_nrf24 import NRF24
    import time
    import spidev

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23,1)
    GPIO.output(24,1)

    pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

    radio =NRF24(GPIO, spidev.SpiDev())
    radio.begin(0,17)
    radio.setPayloadSize(32)
    radio.setChannel(0x65)
    radio.setDataRate(NRF24.BR_2MBPS)
    radio.setPALevel(NRF24.PA_MIN)
    radio.setAutoAck(False)
    radio.enableDynamicPayloads()

    radio2 =NRF24(GPIO, spidev.SpiDev())
    radio2.begin(1,17)
    radio2.setPayloadSize(32)
    radio2.setChannel(0x60)
    radio2.setDataRate(NRF24.BR_2MBPS)
    radio2.setPALevel(NRF24.PA_MIN)
    radio2.setAutoAck(False)
    radio2.enableDynamicPayloads()

    radio.openReadingPipe(0, pipes[1])
    radio2.openWritingPipe(pipes[0])

    radio.printDetails()
    print("///////////////////////////////////////////////////////////")
    radio2.printDetails()

    frame = []
    str_frame=""
    flag="A"
    outputfile = open("hola1.txt", "wb")
    

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
                if(chr(frame[0])==flag):
                    for x in range(1, len(frame)):
                        str_frame=str_frame + chr(frame[x])
                    outputfile.write(str_frame)
                    print(frame)
                    print(str_frame)
                    if(flag=="A"):
                        flag="B"
                    else:
                        if(flag=="B"):
                            flag="C"
                        else:
                            if(flag=="C"):
                                flag="A"
                    radio2.write(list("ACK")+list(flag))
                    break
                else:
                    radio2.write(list("ACK")+list(flag))
                    timeout=time.time() + 0.5
            if((time.time()+0.3) > timeout):
                radio.openReadingPipe(0, pipes[1])
                radio.startListening()
                radio2.write(list("ACK")+list(flag))
                timeout=time.time() + 0.5
                
                
        #time.sleep(1)

except KeyboardInterrupt:
    GPIO.output(23,0)
    GPIO.output(24,0)
    GPIO.cleanup()























    
