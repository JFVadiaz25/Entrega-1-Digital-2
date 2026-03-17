# main.py -- put your code here!
from machine import Pin, ADC, mem32, const, Timer
from time import sleep

#Pines Semaforo
vectorpines = [12,13,3,25,17,16,27,14]
for i in vectorpines:
    Pin(i, Pin.OUT)

mic = ADC(Pin(35))       # ADC en GPIO35
mic.atten(ADC.ATTN_11DB) # rango 0–3.6V
mic.width(ADC.WIDTH_12BIT) # resolución 12 bits (0-4095)


#Boton Peatonal
def Peaton(pin):
    global BotonPeaton
    print("Activo el semaforo peatonal")
    BotonPeaton=1

pulsador=Pin(32,Pin.IN,Pin.PULL_DOWN)
pulsador.irq(trigger=Pin.IRQ_RISING,handler=Peaton)

#Pines Display Y Mux
pinesdisplay=[5,23,22,21,0,2,4] #a,b,c,d,e,f,g

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

def conteo(Timer):
    global contador
    global muxContador
    global contadorTiempo
    muxContador += 1
    contadorTiempo += 1
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


#Valores iniciales
contador = 10
muxContador = 0
contadorActivo = False
BotonPeaton=0
GPIO=const(0x3FF44004)
semaforo=False

estado=1
contadorTiempo=0 
parpadeo=0
value = 0

while True:
    actualizar_display()
    if muxContador % 20 == 0:
        value = mic.read()
        

    if value > 500: #Situacion 0
        semaforo=True
    if semaforo:
        if estado == 1:
            mem32[GPIO]=0B0010000000000100000000001000 #situacion 1
            if contadorTiempo >= 500:   # 5 segundos
                contadorTiempo = 0
                estado = 2
            
        elif estado == 2: #Parpadea verde situacion 1
            if contadorTiempo >= 50:
                contadorTiempo=0
                parpadeo+=1
                if parpadeo %2:
                    mem32[GPIO]=0B0010000000000100000000001000
                else:
                    mem32[GPIO]=0B0000000000000100000000001000
                if parpadeo >=6:
                    estado=3
                    parpadeo=0

        elif estado == 3:
            mem32[GPIO]=0B0000000000100110000000001000 #Situacion 2 amarillo prende
            if contadorTiempo >= 500:
                contadorTiempo=0
                estado=4

        elif estado == 4:
            mem32[GPIO]=0B0000000000010101000000000000
            if contadorTiempo == 1:
                contador = 10
                contadorActivo = True

            if contadorTiempo >= 1000:
                contadorTiempo = 0
                contadorActivo = False
                estado = 5
        elif estado == 5:
            mem32[GPIO]=0B0000000000110110000000000000 #Situacion 4 amarillo prende
            if contadorTiempo >= 500:
                contadorTiempo=0
                if BotonPeaton:
                    print("inicia el ciclo peatonal")   
                    estado=6
                else:
                    estado=1 
        elif estado == 6:
            mem32[GPIO]=0B0000000000100110000000000000 #Situacion 5 peatonal verde
            if contadorTiempo >= 300:
                contadorTiempo=0
                estado=7
        elif estado ==7:
            mem32[GPIO]=0B1100000000010000000000001000
            if contadorTiempo >=500:
                    contadorTiempo=0
                    estado=8
        elif estado==8: #Situacion 5 parpadea verde
            if contadorTiempo >= 50:
                contadorTiempo=0
                parpadeo+=1
                if parpadeo %2:
                    mem32[GPIO]=0B1100000000010000000000001000
                else:
                    mem32[GPIO]=0B0100000000010000000000001000
                if parpadeo >=6:
                    parpadeo=0
                    BotonPeaton=0
                    estado=1
                print("Termina el ciclo semaforo")