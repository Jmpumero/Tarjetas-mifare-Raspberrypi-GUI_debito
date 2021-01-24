try: # Raspberry Pi
	import RPi.GPIO as GPIO
except ImportError: # Other system
	GPIO = None

#RPi.GPIO is not None else raise ValueError(f'RPi.GPIO module not imported. Please pip install.')

import SimpleMFRC522
import signal

import time
import logging
import ctypes
import string

from debito_ui import *
from ventana_ayuda_ui import *
"""
Autor:Jose Medina
correo:jmpumero@gmail.com
"""
global flag,flag2,cost,number,uids
global h,av_1
av_1=" SALDO INSUFICIENTE "
t3=" TARJETA INVALIDA "
t1="ERROR T1"
t2="ERROR T2"
t4="ERROR T4"
av_c="Operacion procesada correctamente"
uids=None
h=0
cost=10
number=5


class ventanita(QtWidgets.QDialog,Ui_Dialog):
	def __init__(self, *args, **kwargs):
		QtWidgets.QDialog.__init__(self, *args, **kwargs)
		self.setupUi(self)
		self.setWindowTitle("ventana de prueba")


class MainWindow(QtWidgets.QMainWindow, Ui_APP_debito):

	def __init__(self, *args, **kwargs):
		QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
		self.setupUi(self)
		#self.mainframe = debitar(self)
		self.setWindowTitle("APP DEBITO")
		self.pushButton.clicked.connect(self.detener)
		self.actionDetener.triggered.connect(self.detener)
		self.actionSalir.triggered.connect(self.closed_window)
		self.actionAyuda.triggered.connect(self.ventana_ayuda)
		self.timer1 = QtCore.QTimer(self, interval=300, timeout=self.debitar)
		self.timer1.start()
		self.debitar()


	def closed_window(self):
		self.close()

	def detener(self):
		print("end")
		self.timer1.stop()

	def ventana_ayuda(self):
		self.vent = ventanita()
		self.vent.show()


	def reject(self,a):
		self.aviso_label.setStyleSheet("color: rgb(255, 0, 0);")
		self.aviso_label.setText(a)

	def accept(self,a):
		self.aviso_label.setStyleSheet("color: rgb(0, 170, 0);")
		self.aviso_label.setText(a)

	def cleaning(self):
		self.r_saldo_act_label.setText("")
		self.r_sald_rest_label.setText("")
		self.r_uid_label.setText("")

	def writing(self,uid,v,num):

		reader = SimpleMFRC522.SimpleMFRC522()
		uid_act = reader.read_id_no_block()
		reader.Close_MFRC522()
		if(uid_act is not None):
			reader = SimpleMFRC522.SimpleMFRC522()
			uid_act = reader.num_to_hex(uid_act)[1:9]
			reader.Close_MFRC522()

			if uid_act==uid:
				reader = SimpleMFRC522.SimpleMFRC522()
				vc=str(v)
				data = reader.write_block(num, vc.ljust(16))
				reader.Close_MFRC522()

				reader = SimpleMFRC522.SimpleMFRC522()
				data = reader.read_block(number)
				reader.Close_MFRC522()
				try:
					k=int(data[1])
					self.r_sald_rest_label.setText(str(k))
					if k==v:
						self.accept(av_c)
					else:
						self.reject(t1)
				except TypeError:
					print("")
					#self.reject(t4)
			else:
				print(data[1])
				self.reject(t3)
		else:
			self.reject(t2)


	@QtCore.pyqtSlot()
	def debitar(self):
		global h,number,cost,uids

		#self.cleaning()

		reader = SimpleMFRC522.SimpleMFRC522()
		uid = reader.read_id_no_block()
		reader.Close_MFRC522()


		if(uid is not None):



			reader = SimpleMFRC522.SimpleMFRC522()
			uid = reader.num_to_hex(uid)[1:9]

			reader.Close_MFRC522()
			self.r_uid_label.setText(uid)
			#print(uid)
			reader = SimpleMFRC522.SimpleMFRC522()
			data = reader.read_block(number)
			reader.Close_MFRC522()

			try :
				if int(data[1])==0:
					self.r_saldo_act_label.setText("  "+str(data[1]))
					self.reject(av_1)
				else:
					if int(data[1]):

						credit=int(data[1])
						print(credit)
						v=credit-cost
						#print(v)
						if v>=0:
							print("")
							if uids != uid:
								uids=uid
								self.r_saldo_act_label.setText(str(credit))
								self.writing(uid,v,number)
							else:
								print("")
						else:

							self.reject(av_1)
			except ValueError:
				print(".")
				#self.reject(t3)
			except TypeError:
				print("*")
				#self.reject(t4)
			except IndexError:
				print("error tarjeta fuera de corbetura")
		else:
			uids=None











if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication([])
	window = MainWindow()
	window.show()
	app.exec_()
