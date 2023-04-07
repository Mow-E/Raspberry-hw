import serial #use serial module

ser = serial.Serial('/dev/ttyS0', 9600)  # Change this to the appropriate serial port and baud rate
ser.flushInput() # wait until all data is written

# try:
#     ser = serial.Serial(
#         port='COM3',
#         baudrate=921600,
#         timeout  = 0.1,
#         parity=serial.PARITY_NONE,
#         stopbits=serial.STOPBITS_ONE,
#         bytesize=serial.EIGHTBITS
#         )
#     ser.isOpen() # try to open port, if possible print message and proceed with 'while True:'
#     print ("port is opened!")

# except IOError: # if port is already opened, close it and open it again and print message
#   ser.close()
#   ser.open()
#   print ("port was already open, was closed and opened again!")

while True:
    message = input("Enter command to send: ") #user input received from mobile phone '1', '2', '3', '4', '5', 'd'
    if (message == '1'):
        ser.write(message.encode())
        print("Sent: ", message)
        response = ser.readline().decode()
        print("Received: ", response.strip())
    
    