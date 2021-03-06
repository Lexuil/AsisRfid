import os
import network
import time
import utime
from machine import RTC
from machine import Pin
from machine import TouchPad
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

from lcd import HD44780
import server
import asistencia
import rfid
import keypad

# Fecha
NTP_DELTA = 3155691600  #(colombia)
host = "pool.ntp.org"

# Wifi
#SSIDandPSWD = [["M1","matsuri07"],["Familialexuil97","3202601178"],["ECCI-PROTOTIPADO","123qweasd"]]

# RTC
rtc = RTC()

# LCD
lcd = HD44780()
lcd.PINS = [32, 33, 16, 17, 4, 21]
lcd.init()

# TouchPad
#Touch = [TouchPad(Pin(13)),TouchPad(Pin(12)),TouchPad(Pin(14)),TouchPad(Pin(27))]
led = Pin(5, mode=Pin.OUT)

# Caracteres
Caracteres_min = '12abc3def4ghi5jkl6mno7pqrs8tuv9wxyz0 _:;!"#$%&()*+,-./?@[]^`{|}~'
Caracteres_may = '12ABC3DEF4GHI5JKL6MNO7PQRS8TUV9WXYZ0 _:;!"#$%&()*+,-./?@[]^`{|}~'

def connectWIFI():
	
	f = open("Wifi.txt","r")
	SSIDandPSWD = []
	for line in f:
	    SSIDandPSWD.append(line)

	for x in range(len(SSIDandPSWD)):
		SSIDandPSWD[x] = SSIDandPSWD[x][0:len(SSIDandPSWD[x])-1]

	f.close()

	sel = 0

	while True:
		put_lcd("Seleciona red:",SSIDandPSWD[sel*2])
		time.sleep_ms(500)
		opc = keypad.getkey()

		if opc == "A":
			station = network.WLAN(network.STA_IF)
			station.active(True)

			station.connect(SSIDandPSWD[sel*2],SSIDandPSWD[sel*2+1])
			put_lcd("Conectando a...",SSIDandPSWD[sel*2])

			print("\n\n********conectando a ",SSIDandPSWD[sel*2],"...*********\n\n")
			utime.sleep(5)

			if station.isconnected():
				put_lcd("Conectado"," ")
				time.sleep(3)
				break
		elif opc == "*":
			if sel == 0:
				sel = len(SSIDandPSWD)//2-1
			else:
				sel -= 1
		elif opc == "#":
			if sel == (len(SSIDandPSWD)/2)-1:
				sel = 0
			else:
				sel += 1
		elif opc == "D":
			new_wifi()
			break
			
def new_wifi():
	station = network.WLAN(network.STA_IF)
	station.active(True)
	put_lcd("Buscando..."," ")
	redes = station.scan()

	for x in range(len(redes)):
		redes[x] = redes[x][0].decode('ascii')

	sel1 = 0

	while True:
		put_lcd("Sel. nueva red:",redes[sel1])
		time.sleep_ms(500)
		opc = keypad.getkey()

		if opc == "A":
			Contraseña = put_let("Contasena:")

			station = network.WLAN(network.STA_IF)
			station.active(True)

			station.connect(redes[sel1],Contraseña)
			put_lcd("Conectando a...",redes[sel1])

			print("\n\n********conectando a ",redes[sel1],"...*********\n\n")
			utime.sleep(5)

			if station.isconnected():
				put_lcd("Conectado"," ")

				f = open("Wifi.txt","a")
				f.write(redes[sel1])
				f.write("\n")
				f.write(Contraseña)
				f.write("\n")
				f.close()

				time.sleep(3)
				break

		elif opc == "*":
			if sel1 == 0:
				sel1 = len(redes)-1
			else:
				sel1 -= 1
		elif opc == "#":
			if sel1 == len(redes)-1:
				sel1 = 0
			else:
				sel1 += 1
		elif opc == "D":
			connectWIFI()

def getdate():

	try:
		put_lcd("Obteniendo","Fecha y hora")
		NTP_QUERY = bytearray(48)
		NTP_QUERY[0] = 0x1b
		addr = socket.getaddrinfo(host, 123)[0][-1]
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(2)
		res = s.sendto(NTP_QUERY, addr)
		msg = s.recv(48)
		s.close()
		val = struct.unpack("!I", msg[40:44])[0]
		#print(val - NTP_DELTA)

		tm = utime.localtime(val - NTP_DELTA)
		tm = tm[0:3] + (0,) + tm[3:6] + (0,)
		rtc.datetime(tm)
	except:
		put_lcd("ERROR","Reintentando")
		time.sleep_ms(500)
		getdate()

def showdate():
	date = rtc.datetime()
	dates = []

	for x in range(7):
		if date[x] < 10:
			dates += ["0"+str(date[x])]
		else:
			dates += [str(date[x])]

	return [["Fecha: "+dates[2]+"/"+dates[1]+"/"+dates[0]],["Hora: "+dates[4]+":"+dates[5]+":"+dates[6]]]

def lcd_date():

	time.sleep_ms(200)

	while True:
		date = showdate()
		put_lcd(date[0][0][7:17],date[1][0][6:14])

		key = keypad.getkey_()
		if key == "D":
			break

# def touchpad_read_(timeout = 1000):

# 	timeoutaux = time.ticks_ms()

# 	while True:

# 		if time.ticks_ms() > timeoutaux + timeout:
# 			break
		
# 		y = 0

# 		for x in Touch:
# 			if x.read() < 400:
# 				led.value(1)
# 				time.sleep_ms(50)
# 				led.value(0)
# 				return y

# 			y += 1

# def touchpad_read():

# 	while True:
		
# 		y = 0

# 		for x in Touch:
# 			if x.read() < 400:
# 				led.value(1)
# 				time.sleep_ms(50)
# 				led.value(0)
# 				return y

# 			y += 1

def put_lcd(a,b):
	lcd.set_line(0)
	lcd.set_string(a)
	lcd.set_line(1)
	lcd.set_string(b)

def reg_nombre():
	x = 0
	nombre = ""
	flag = 0

	put_lcd("Nombre:",nombre + Caracteres[x])

	while True:
		opc = keypad.getkey()
		time.sleep_ms(200)

		if opc == "D":
			break
		elif opc == "A":
			if flag == 0:
				if len(nombre) < 14:
					time.sleep_ms(200)
					flag = 1
					nombre += Caracteres[x]
					put_lcd("Nombre:",nombre + Caracteres[x])
				else:
					put_lcd("Error:","Max. caracteres")
			else:
				put_lcd("Ponga la","tarjeta")

				rfid.write_name(nombre)

				put_lcd("Ok",nombre)
				time.sleep(2)
				break

		elif opc == "#":
			flag = 0
			if x == 88:
				x = 0
			else:
				x += 1

			put_lcd("nombre:",nombre + Caracteres[x])

		elif opc == "*":
			flag = 0
			if x == 0:
				x = 88
			else:
				x -= 1

			put_lcd("nombre:",nombre + Caracteres[x])

def conf_manual_time():
	fecha = [2018,7,1]
	hora = [12,30]
	put_lcd("Conf. Fecha:",str(fecha[0])+"/"+str(fecha[1])+"/"+str(fecha[2]))

	aux1 = 0
	aux2 = 0

	while True:
		time.sleep_ms(500)
		opc = keypad.getkey()

		if opc == "A":
			if aux1 < 2:
				aux1 += 1
			else:
				break
		elif opc == "*":
			if fecha[aux1] > 0:
				fecha[aux1] -= 1
			put_lcd("Conf. Fecha:",str(fecha[0])+"/"+str(fecha[1])+"/"+str(fecha[2]))
		elif opc == "#":
			fecha[aux1] += 1
			put_lcd("Conf. Fecha:",str(fecha[0])+"/"+str(fecha[1])+"/"+str(fecha[2]))

	put_lcd("Conf. Hora:",str(hora[0])+":"+str(hora[1]))

	while True:
		time.sleep_ms(500)
		opc = keypad.getkey()

		if opc == "A":
			if aux2 < 1:
				aux2 += 1
			else:
				break
		elif opc == "*":
			if hora[aux2] > 0:
				hora[aux2] -= 1
			put_lcd("Conf. Hora:",str(hora[0])+":"+str(hora[1]))
		elif opc == "#":
			if hora[aux2] < 59:
				hora[aux2] += 1
			put_lcd("Conf. Hora:",str(hora[0])+":"+str(hora[1]))

	date = tuple(fecha) + (0,) + tuple(hora) + (0,0,)
	rtc.datetime(date)

def put_let(a):
	z = 0
	Caracteres = Caracteres_min
	data = ""
	flag = 0

	put_lcd(a,data + Caracteres[z])

	while True:
		time.sleep_ms(200)
		opc = keypad.getkey()

		if opc == "#":
			if flag == 0:
				Caracteres = Caracteres_may
				flag = 1
			else:
				Caracteres = Caracteres_min
				flag = 0
			put_lcd(a,data + Caracteres[z])
		elif opc == "D":
			break
		elif opc == "A":
			put_lcd("Ok",data)
			return data
		elif opc == "B":
			data += Caracteres[z]
			put_lcd(a,data + Caracteres[z])
		elif opc == "C":
			data = data[:len(data)-1]
			put_lcd(a,data + Caracteres[z])
		elif opc == "1":
			z = 0
			put_lcd(a,data + Caracteres[z])
		elif opc == "2":
			if 0 < z < 4:
				z += 1
			else:
				z = 1
			put_lcd(a,data + Caracteres[z])
		elif opc == "3":
			if 4 < z < 8:
				z += 1
			else:
				z = 5
			put_lcd(a,data + Caracteres[z])
		elif opc == "4":
			if 8 < z < 12:
				z += 1
			else:
				z = 9
			put_lcd(a,data + Caracteres[z])
		elif opc == "5":
			if 12 < z < 16:
				z += 1
			else:
				z = 13
			put_lcd(a,data + Caracteres[z])
		elif opc == "6":
			if 16 < z < 20:
				z += 1
			else:
				z = 17
			put_lcd(a,data + Caracteres[z])
		elif opc == "7":
			if 20 < z < 25:
				z += 1
			else:
				z = 21
			put_lcd(a,data + Caracteres[z])
		elif opc == "8":
			if 25 < z < 29:
				z += 1
			else:
				z = 26
			put_lcd(a,data + Caracteres[z])
		elif opc == "9":
			if 29 < z < 34:
				z += 1
			else:
				z = 30
			put_lcd(a,data + Caracteres[z])
		elif opc == "0":
			if 34 < z < 63:
				z += 1
			else:
				z = 35
			put_lcd(a,data + Caracteres[z])


modo = ["Conectado","Desconectado"]
mod = 0

while True:
	put_lcd("Selecione modo:",modo[mod])

	time.sleep_ms(500)
	opc = keypad.getkey()

	if opc == "A" and mod == 0:
		connectWIFI()

		getdate()
		date = showdate()
		print(date[0])
		print(date[1],"\n")

		server.servinit()
		break
	elif opc == "A" and mod == 1:
		conf_manual_time()
		break
	elif opc == "*" or opc == "#":
		if mod == 0:
			mod = 1
		else:
			mod = 0


lcd_date()

while True:

	time.sleep_ms(200)

	put_lcd("B: Ingreso","C: Salida")

	opc = keypad.getkey()
	print(opc)

	if opc == "A":
		pantalla = 0
		time.sleep_ms(200)
		while True:

			if pantalla == 0:
				put_lcd("Leer nombre","de la tarjeta")
				opc = keypad.getkey()
				time.sleep_ms(200)
				if opc == "A":
					put_lcd("Ponga la","tarjeta")
					name = rfid.read_name()
					put_lcd("Nombre:",name)
					time.sleep(2)
				elif opc == "*":
					pantalla = 3
				elif opc == "#":
					pantalla += 1
				elif opc == "D":
					break

			elif pantalla == 1:
				put_lcd("Registrar","Nueva tarjeta")
				opc = keypad.getkey()
				time.sleep_ms(200)
				if opc == "A":
					nombre = put_let("Nombre:")
					put_lcd("Ponga la","tarjeta")
					rfid.write_name(nombre)
					put_lcd("Ok",nombre)
					time.sleep(2)
				elif opc == "*":
					pantalla -= 1
				elif opc == "#":
					pantalla += 1
				elif opc == "#":
					break

			if pantalla == 2:
				put_lcd("Eliminar datos","de asistencia")
				opc = keypad.getkey()
				time.sleep_ms(200)
				if opc == "A":
					put_lcd("Eliminando","espere...")
					os.remove("www/registro.csv")
					f = open('www/registro.csv','a')
					f.close()
					time.sleep_ms(200)
				elif opc == "*":
					pantalla -= 1
				elif opc == "#":
					pantalla += 1
				elif opc == "D":
					break

			if pantalla == 3:
				put_lcd("Ver","IP")
				opc = keypad.getkey()
				time.sleep_ms(200)
				if opc == "A":
					station = network.WLAN(network.STA_IF)
					put_lcd("IP:",str(station.ifconfig()[0]))
					time.sleep(5)
				elif opc == "*":
					pantalla -= 1
				elif opc == "#":
					pantalla = 0
				elif opc == "D":
					break

	elif opc == "B":
		put_lcd("Coloca la","tarjeta")
		name = asistencia.ingreso()
		put_lcd("Hola",name)
		time.sleep_ms(200)

	elif opc == "C":
		put_lcd("Coloca la","tarjeta")
		name = asistencia.salida()
		put_lcd("Chao",name)
		time.sleep_ms(200)

	elif opc == "D":
		lcd_date()


