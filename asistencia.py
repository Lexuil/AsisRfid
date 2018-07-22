import rfid
import machine
import utime
from machine import RTC

boton = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# RTC
rtc = RTC()

def showdate():
	date = rtc.datetime()
	dates = []

	for x in range(7):
		if date[x] < 10:
			dates += ["0"+str(date[x])]
		else:
			dates += [str(date[x])]

	return [["Fecha: "+dates[2]+"/"+dates[1]+"/"+dates[0]],["Hora: "+dates[4]+":"+dates[5]+":"+dates[6]]]

def ingreso():

	date = showdate()

	f = open('www/registro.csv','a')
	name = rfid.read_name()
	f.write(str(date[0][0][7:17]+';'+date[1][0][6:14]+';'+name+';ingreso;\n'))
	f.close()
	print('ok')

	return name


def salida():

	date = showdate()

	f = open('www/registro.csv','a')
	name = rfid.read_name()
	f.write(str(date[0][0][7:17]+';'+date[1][0][6:14]+';'+name+';salida;\n'))
	f.close()
	print('ok')

	return name