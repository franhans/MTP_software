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

    radio = NRF24(GPIO, spidev.SpiDev())
    radio2 = NRF24(GPIO, spidev.SpiDev())
    radio.begin(0, 17)
    radio2.begin(1, 17)
    radio.setPayloadSize(32)
    radio.setChannel(0x65)
    radio2.setPayloadSize(32)
    radio2.setChannel(0x60)

    radio.setDataRate(NRF24.BR_2MBPS)
    radio.setPALevel(NRF24.PA_MIN)
    radio.setAutoAck(False)
    radio.enableDynamicPayloads()
    radio2.setDataRate(NRF24.BR_2MBPS)
    radio2.setPALevel(NRF24.PA_MIN)
    radio2.setAutoAck(False)
    radio2.enableDynamicPayloads()
##    radio.enableAckPayload()

    # radio.openReadingPipe(1, pipes[1])
    radio.openWritingPipe(pipes[1])
    radio.printDetails()
    print("///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
    radio2.openReadingPipe(0, pipes[0])
    radio2.printDetails()

    ack  =  []
    str_ack=""
    sizepayload=31
    packets = []
    actual_flag="A"
    previous_flag="A"
    infile= open("hola2.txt", "rb" )
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
	



    for message in packets:
       # message = list("Hello World is awesome ")
	message_aux=message
        radio.write(actual_flag+ message_aux)
        print("We sent the message of {}".format(message))
	previous_flag = actual_flag
	if (actual_flag=="A"):
	    actual_flag="B"
        else:
	    if(actual_flag=="B"):
		actual_flag="C"
	    else:
		if(actual_flag=="C"):
		    actual_flag="A"
        # Check if it returned ackPL
####        if radio.isAckPayloadAvailable():
##            returnedPL = []
##            radio.read(returnedPL, radio.getDynamicPayloadSize())
##            print("Our returned payload was {}".format(returnedPL))
##        else:
##            print("No payload received")
##        radio2.startListening()
        timeout = time.time() + 0.5
        while(1):
	    radio2.openReadingPipe(0,pipes[0])
	    radio2.startListening()
            if radio2.available(0):
                radio2.read(ack, radio2.getDynamicPayloadSize())
		str_ack=""
		for x in range(0, len(ack)):
		    str_ack=str_ack + chr(ack[x])
		print(str_ack)
		print("Arriba Ack recibidoQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
		if(list(str_ack) != (list("ACK")+list(actual_flag))):
		    print(list("ACK")+list(actual_flag))
		    radio.write(previous_flag + message_aux)
		    timeout=time.time() + 0.5
		    print("mistaken")
		else:
		    break
	    if((time.time()+0.2) > timeout):
		print("reenvio tramax")
		j=j+1
		print(j)
		radio.openWritingPipe(pipes[1])
		radio.write(previous_flag + message_aux)
		timeout=time.time() + 0.5
#        time.sleep(1)
        
except KeyboardInterrupt:
    GPIO.output(23,0)
    GPIO.output(24,0)
    GPIO.cleanup()
