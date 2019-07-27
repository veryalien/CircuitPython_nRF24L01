'''
    Templated example of using the library to transmit
    and retrieve custom automatic acknowledgment payloads.

    Master transmits a dummy payload every second and prints the ACK payload.
    Slave prints the received value and sends a dummy ACK payload.
'''

import time, board, digitalio as dio
from circuitpython_nrf24l01.rf24 import RF24

addresses = (b'1Node', b'2Node')
# these addresses should be compatible with the GettingStarted.ino sketch included in TRMh20's arduino library

ce = dio.DigitalInOut(board.D7)
csn = dio.DigitalInOut(board.D5)

spi = board.SPI()
# we'll be sending a dynamic payload of size 5 bytes (a 5 character string)
nrf = RF24(spi, csn, ce)

def master():
    nrf.open_tx_pipe(addresses[0]) # set address of RX node into a TX pipe
    # set address of TX node into an RX pipe. NOTE you MUST specify
    # which pipe number to use for RX, we'll be using pipe 1
    # pipe number options range [0,5]
    nrf.open_rx_pipe(1, addresses[1])
    nrf.stop_listening() # put radio in TX mode and power down

    while True:
        try:
            # payloads needs to be in a buffer protocol object (bytearray). Just like the addressess.
            temp = b'Hello'
            print("Sending (raw): {}".format(repr(temp)))
            # to read the ACK payload during TX mode we
            # pass the parameter read_ack as True.
            result = nrf.send(temp, read_ack=True)
            if result == 0:
                print('send() timed out')
            elif result == 1:
                # print the received ACK that was automatically fetched and saved to nrf's ack attribute
                print('raw ACK: {}'.format(repr(nrf.ack)))
                # the ACk payload should also include the default
                # response data that the nRF24L01 uses despite
                # a custom set ACK payload.
            elif result == 2:
                print('send() failed')
        except KeyboardInterrupt:
            break
        time.sleep(1)

def slave():
    # we must use a tuple to set the ACK payload
    # data and corresponding pipe number
    # pipe number options range [0,5]
    # NOTE ACK payloads need to be in a buffer
    # protocol object (bytearray)
    ACK = (b'World', 1)
    # set address of RX node into a TX pipe
    nrf.open_tx_pipe(addresses[1])
    # set address of TX node into an RX pipe. NOTE you MUST specify
    # which pipe number to use for RX, we'll be using pipe 1
    nrf.open_rx_pipe(1, addresses[0])
    # put radio into RX mode, power it up, and set the first
    # transmission's ACK payload and pipe number
    nrf.start_listening(ACK)

    while True:
        try:
            nrf.ack = ACK
            if nrf.any():
                rx = nrf.recv()
                print("Received (raw): {}".format(repr(rx)))
        except KeyboardInterrupt:
            break

print("""\
    nRF24L01 ACK test.\
    Run slave() on receiver\
    Run master() on transmitter.""")
