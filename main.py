# main.py -- put your code here!

from machine import Pin, ADC, mem32, const
from time import sleep

vectorpines = [12,13,26,25,17,16,27,14]

for i in vectorpines:
    Pin(i, Pin.OUT)

mic = ADC(Pin(35))       # ADC en GPIO35
mic.atten(ADC.ATTN_11DB) # rango 0–3.6V
mic.width(ADC.WIDTH_12BIT) # resolución 12 bits (0-4095)

GPIO=const(0x3FF44004)
semaforo=False

while True:
    value = mic.read()
    print(value)
    sleep(0.1)

    if value > 500: #Situacion 0
        semaforo=True
    if semaforo:
        mem32[GPIO]=0B0110000000000100000000000000 #situacion 1
        sleep(5)
        for i in range(3): #Parpadea situacion 1 verde
            mem32[GPIO]=0B0110000000000100000000000000
            sleep(1)
            mem32[GPIO]=0B0100000000000100000000000000
            sleep(1)
        mem32[GPIO]=0B0100000000100110000000000000#Situacion 2 amarillo prende
        sleep(5)
        mem32[GPIO]=0B1000000000010001000000000000 #Situacion 3
        sleep(5)
        for i in range(3): #Situacion 3 parpadea verde
            mem32[GPIO]=0B1000000000010001000000000000
            sleep(1)
            mem32[GPIO]=0B0000000000010000000000000000
            sleep(1)
        mem32[GPIO]=0B0000000000110110000000000000 #Situacion 4 amarillo prende
        sleep(5)
