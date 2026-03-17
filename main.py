# main.py -- put your code here!
from machine import Pin, ADC, mem32, const, Timer
from time import sleep

def Peaton(pin):
    global BotonPeaton
    print("Activo el semaforo peatonal")
    BotonPeaton=1

vectorpines = [12,13,26,25,17,16,27,14]

for i in vectorpines:
    Pin(i, Pin.OUT)

mic = ADC(Pin(35))       # ADC en GPIO35
mic.atten(ADC.ATTN_11DB) # rango 0–3.6V
mic.width(ADC.WIDTH_12BIT) # resolución 12 bits (0-4095)

GPIO=const(0x3FF44004)
semaforo=False

pulsador=Pin(18,Pin.IN,Pin.PULL_DOWN)
pulsador.irq(trigger=Pin.IRQ_RISING,handler=Peaton)

BotonPeaton=0

pinesdisplay=[5,23,22,21,0,2,4]

for i in pinesdisplay:
    Pin(i,Pin.OUT)

pinmux=[18,19]
mux=[Pin(i,Pin.OUT) for i in pinmux]

display= [[1,1,1,1,1,1,0],
          [0,1,1,0,0,0,0],
          [1,1,0,1,1,0,1],
          [1,1,1,1,0,0,1],
          [0,1,1,0,0,1,1],
          [1,0,1,1,0,1,1],
          [1,0,1,1,1,1,1],
          [1,1,1,0,0,0,0],
          [1,1,1,1,1,1,1],
          [1,1,1,0,0,1,1]]

contador = 10
muxContador = 0
contadorActivo = False

def conteo(Timer):

    global contador
    global muxContador
    muxContador += 1
    if muxContador == 100:

        if contadorActivo and contador > 0:
            contador -= 1
            print(contador)

        muxContador = 0
temporizador = Timer(0)
temporizador.init(period=10, mode=Timer.PERIODIC, callback=conteo)

def actualizar_display():

    if contadorActivo and contador > 0:

        mux[0].value(1)
        mux[1].value(1)

        if muxContador % 2 == 0:

            for i in range(7):
                Pin(pinesdisplay[i], value=display[contador % 10][i])

            mux[1].value(0)

        else:

            decena = contador // 10

            for i in range(7):
                Pin(pinesdisplay[i], value=display[decena][i])

            mux[0].value(0)

while True:
    actualizar_display()
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
        contador = 10
        contadorActivo = True

        while contador > 0:
            actualizar_display()
            sleep(0.01)
        contadorActivo=False
        mem32[GPIO]=0B0000000000110110000000000000 #Situacion 4 amarillo prende
        sleep(5)
        if BotonPeaton:
            print("inicia el ciclo peatonal")
            mem32[GPIO]=0B0000000000100110000000000000 #Situacion 5 peatonal verde
            sleep(3)
            mem32[GPIO]=0B1100000000010000000000000000
            sleep(5)
            for i in range(3): #Situacion 5 parpadea verde
                mem32[GPIO]=0B1100000000010000000000000000
                sleep(1)
                mem32[GPIO]=0B0100000000010000000000000000
                sleep(1)
            BotonPeaton=0
        print("Termina el ciclo semaforo")
