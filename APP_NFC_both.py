"""
py3tinker by David Gomez
-----------------

Python 3 tk GUI for NFC Reader
"""

import datetime
import gettext
import sys
import time
from collections import namedtuple
#from AESCipher import AESCipher as aesci

try: # Python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    from tkinter.filedialog import askopenfilename
except ImportError: # Python 2
    import Tkinter as Tk
    import ttk
    import tkFont as font

try: # Raspberry Pi
    import RPi.GPIO as GPIO
    Blue = True
except ImportError: # Other system
    GPIO = None
    Blue = False
#RPi.GPIO is not None else raise ValueError(f'RPi.GPIO module not imported. Please pip install.')

import SimpleMFRC522
import signal

#import mifareauth 
import logging
import ctypes
import string
#import nfc

# wiegan
import hwiegand

# All translations provided for illustrative purposes only.
 # english
_ = lambda s: s

#reader_white = mifareauth.NFCReader()

Block = namedtuple("Block", ["block_value", "block_n"])

class PopupDialog(ttk.Frame):
    "Sample popup dialog implemented to provide feedback."

    def __init__(self, parent, title, body):
        ttk.Frame.__init__(self, parent)
        self.top = tk.Toplevel(parent)
        _label = ttk.Label(self.top, text=body, justify=tk.LEFT)
        _label.pack(padx=10, pady=10)
        _button = ttk.Button(self.top, text=_("OK"), command=self.ok_button)
        _button.pack(pady=5)
        self.top.title(title)

    def ok_button(self):
        "OK button feedback."

        self.top.destroy()



class NavigationBar(ttk.Frame):
    "Sample navigation"

    _advertisement = 'NFC Reader:'+ '\n\n' +' Python Project For Mifare Classic 1K Cards'
    _product = _('Name') + ': NFCPy'
    _boilerplate = _advertisement + '\n\n' + _product + '\n\n'

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.config(border=1, relief=tk.GROOVE)

        #self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        #self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=1)

        self.cardinfo = tk.Label(self)
        self.cardinfo.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.cardinfo.config(text=self._boilerplate)
        self.pack()

    def onselect(self, event):
        """Sample function provided to show how navigation commands may be \
        received."""

        widget = event.widget
        _index = int(widget.curselection()[0])
        _value = widget.get(_index)
        print(_('List item'), ' %d / %s' % (_index, _value))




class StatusBar(ttk.Frame):
    "Sample status bar"
    _status_bars = 4

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.labels = []
        self.config(border=1, relief=tk.GROOVE)
        for i in range(self._status_bars):
            _label_text = _('Unset status ') + str(i + 1)
            self.labels.append(ttk.Label(self, text=_label_text))
            self.labels[i].config(relief=tk.GROOVE)
            self.labels[i].pack(side=tk.LEFT, fill=tk.X)
        self.pack()

    def set_text(self, status_index, new_text):
        self.labels[status_index].config(text=new_text)




class ToolBar(ttk.Frame):
    "Sample toolbar"

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.buttons = []
        self.config(border=1, relief=tk.GROOVE)
        for i in range(1, 5):
            _button_text = _('Operacion ') + str(i)
            self.buttons.append(ttk.Button(self, text=_button_text,
                                           command=lambda i=i:
                                           self.run_tool(i)))
            self.buttons[i - 1].pack(side=tk.LEFT, fill=tk.X)
        self.pack()

    def run_tool(self, number):
        "Sample function provided to show how a toolbar command may be used."
        if (number == 1):
            self.master.mainframe_destroy(MainFrame)
        elif(number == 2):
            self.master.mainframe_destroy(DynaFrame)
        elif(number == 3):
            self.master.mainframe_destroy(Dyna_writeFrame)
        #print(_('Toolbar button'), number, _('pressed'))



class SecoundWindow(tk.Toplevel):
    def __init__(self, parent, block, number):
        super().__init__(parent)
        self.frame = BlockForm(self, block, number)

    def change(self, frame, block, number):
        self.frame = frame(self, block, number)



class BlockForm(ttk.Frame):
    def __init__(self, parent, block, number):
        ttk.Frame.__init__(self, parent)
        
        self.block_value = tk.StringVar(parent, block[0])
        self.block_n = block[1]
        self.number = number

        if (number == 16):
            label = tk.Label(parent, text="Editar El Bloque " + str(block[1]))
            entry_block_value = tk.Entry(parent, textvariable=self.block_value, width=number)
            btn = tk.Button(parent, text="Guardar", command=self.open)
        else:
            label = tk.Label(parent, text="Editar El Sector " + str(block[1]))
            entry_block_value = tk.Entry(parent, textvariable=self.block_value, width=number)
            btn = tk.Button(parent, text="Guardar", command=self.open)
        label.grid(row=0, columnspan=2)
        entry_block_value.grid(row=1, column=1)
        btn.grid(row=2, columnspan=2)

    def open(self):
        self.grab_set()
        block_1 = self.block_value.get()
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.change(SaveFrame, Block(block_1, self.block_n), self.number)



class SaveFrame(ttk.Frame):

    _advertisement = 'Ponga La Tarjeta'

    def __init__(self, parent, block, number):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(parent, anchor=tk.CENTER, foreground='green')
        label.pack(fill=tk.BOTH, expand=1)
        label.config(text=self._advertisement)
        btn = tk.Button(parent, text="Cancelar", command=self.master.destroy)
        btn.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=0)

        print(block)

        data = [False, True]
        if (number == 16):
            #data = reader.write(block[1], block[0])
            pass
        else:
            pass
            #data = reader.write(block[1], block[0])
        if data[1]:
            self.master.destroy()



class SaveWindow(tk.Toplevel):
    def __init__(self, parent, block, number):
        super().__init__(parent)
        self.frame = SaveFrame(self, block, number)



class MainFrame(ttk.Frame):
    "Main area of user interface content."

    past_time = datetime.datetime.now()
    _advertisement = 'Ponga La Tarjeta'
    _time = 'leido en: '
    _id = 'NFC Card ID: '
    _boilerplate = _advertisement + '\n\n' + _time + '\n\n'

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.var = tk.IntVar()
        self.var.set(1)
        self.display = tk.Label(self,
                                 foreground='green')

        self.frame = tk.Frame(self)
        self.block = tk.Radiobutton(
            self.frame, text="Por Bloque",
            variable=self.var, value=1)
        self.block.grid(row=0, column=0, sticky=tk.W)
        self.sector = tk.Radiobutton(
            self.frame, text="Por Sector",
            variable=self.var, value=2)
        self.sector.grid(row=0, column=1, sticky=tk.W)
        self.btn = tk.Button(self.frame, text="Leer", command=self.reader)
        self.btn.grid(row=0, column=3, sticky=tk.W)
        self.frame.pack(side=tk.TOP, fill=tk.Y)

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.group_1 = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        #self.canvas.configure(yscrollcommand= self.scrollbar.set)
        #self.data = [True, False]

        #self.reader()

    def ocultar(self):
        self.canvas.destroy()
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.group_1.destroy()
        self.group_1 = tk.Frame(self.canvas)
        self.scrollbar.destroy()
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand= self.scrollbar.set)
        self.display.config(text=self._advertisement)
        self.display.pack(fill=tk.BOTH, expand=1)
        #self.data[0] = True
        #self.display.after(1000, self.reader)

    def open_window_1(self, block):
        window = SecoundWindow(self, block, 16)

    def open_window_2(self, block):
        window = SecoundWindow(self, block, 48)
    
    def onConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width = (canvas_width - 10))

    def reader(self):
        self.ocultar()

        self.display.config(text=self._advertisement)
        self.display.pack(fill=tk.BOTH, expand=1)

        #id = reader.read_id()
        data = [True, True]
        #data = reader.read_Dump()
        data_2 = []
        #if self.data[0]:
        if data[1]:
            """
            for i in range(64):
                if data[1][i] not []
                    text_read = ''.join(chr(j) for j in data[1][i])
                    data_2.append(text_read)
                    #print(text_read)
            """
            if (self.var.get() == 1):
                """
                for i in range(64):
                    if data[1][i] not []
                        text_read = ''.join(chr(j) for j in data[1][i])
                        data_2.append(text_read)
                        #print(text_read)
                """
                for i in range(64):
                    data_2.append(Block('1234567891234567', i))
            else:
                """
                text_read = ''
                for i in range(64):
                    if data[1][i] not []
                        text_read +=''.join(chr(j) for j in data[1][i])
                    if ((i+1)%4 == 0):
                        data_2.append(text_read)
                        text_read = ''
                    #print(text_read)
                """
                for i in range(16):
                    data_2.append(Block('123456789123456712345678912345671234567891234567', i))
        #    catch_index_error(i, data[1])
            #self.btn.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=0)
            self.display.config(text=self._id + str(data[0]) + '\n\n' + self._time)
            self.display.pack(fill=tk.Y, expand=0)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=0)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            self.group_1.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
 
            self.canvas_frame = self.canvas.create_window((4,4), window= self.group_1, anchor=tk.NW)

            self.canvas.itemconfig(self.canvas_frame, width = (self.canvas.winfo_width() - 10))
            self.group_1.bind("<Configure>", self.onConfigure)
            self.canvas.bind("<Configure>", self.FrameWidth)

            if (self.var.get() == 1):
                for i in range(16):
                    self.create_block(self.group_1, data_2, i)
            else:
                for i in range(16):
                    self.create_sector(self.group_1, data_2, i)
        else:
            self.display.after(1000, self.reader)

    def create_block(self, group, data, i):
        group_2 = tk.LabelFrame(group, padx=15, pady=10, text="Sector "+str(i))
        group_2.pack(fill=tk.BOTH, expand=1)

        j = i * 4
        ttk.Label(group_2, text="Bloque "+str(j)).grid(row=j)
        ttk.Label(group_2, text="Bloque "+str(j+1)).grid(row=j + 1)
        ttk.Label(group_2, text="Bloque "+str(j+2)).grid(row=j + 2)
        ttk.Label(group_2, text=data[j][0], width=16).grid(row=j, column=1, sticky=tk.W)
        ttk.Label(group_2, text=data[j + 1][0], width=16).grid(row=j + 1, column=1, sticky=tk.W)
        ttk.Label(group_2, text=data[j + 2][0], width=16).grid(row=j + 2, column=1, sticky=tk.W)
        ttk.Button(group_2, text="Editar", command=lambda j=data[j]: self.open_window_1(j)).grid(row=j, column= 2)
        ttk.Button(group_2, text="Editar", command=lambda j=data[j+1]: self.open_window_1(j)).grid(row=j + 1, column= 2)
        ttk.Button(group_2, text="Editar", command=lambda j=data[j+2]: self.open_window_1(j)).grid(row=j + 2, column= 2)
        #Grid.columnconfigure(frame, x, weight=1)
        #Grid.rowconfigure(frame, y, weight=1)
        #self.master.grid_rowconfigure(0, weight=1)
        #self.master.grid_columnconfigure(0, weight=1)

    def create_sector(self, group, data, i):
        group_2 = tk.LabelFrame(group, padx=15, pady=10, text="Sector "+str(i))
        group_2.pack(fill=tk.BOTH, expand=1)

        #ttk.Label(group_2, text="Bloke "+str(i)).grid(row=i)
        #ttk.Label(group_2, text="Bloke "+str(j+1)).grid(row=j + 1)
        #ttk.Label(group_2, text="Bloke "+str(j+2)).grid(row=j + 2)
        ttk.Label(group_2, text=data[i][0], width=48).grid(row=i, column=1, sticky=tk.W)
        #ttk.Label(group_2, text=data[j + 1][0], width=16).grid(row=j + 1, column=1, sticky=tk.W)
        #ttk.Label(group_2, text=data[j + 2][0], width=16).grid(row=j + 2, column=1, sticky=tk.W)
        ttk.Button(group_2, text="Editar", command=lambda i=data[i]: self.open_window_2(i)).grid(row=i, column= 2)
        #ttk.Button(group_2, text="Editar", command=lambda j=data[j+1]: self.open_window(j)).grid(row=j + 1, column= 2)
        #ttk.Button(group_2, text="Editar", command=lambda j=data[j+2]: self.open_window(j)).grid(row=j + 2, column= 2)
        #Grid.columnconfigure(frame, x, weight=1)
        #Grid.rowconfigure(frame, y, weight=1)
        #self.master.grid_rowconfigure(0, weight=1)
        #self.master.grid_columnconfigure(0, weight=1)

class Dyna_writeFrame(ttk.Frame):
    "Main area of user interface content."

    past_time = datetime.datetime.now()
    _advertisement = 'Ponga La Tarjeta'
    _time = 'leido en: '
    _id = 'NFC Card ID: '
    _help = 'Selencione el sector a modificar'
    _boilerplate = _advertisement + '\n\n' + _time + '\n\n'

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        
        self.var_s = []
        for i in range(16):
            self.var_s.append(tk.IntVar())

        self.var_all = tk.IntVar()
        self.var_n = []
        self.block_value = []
        for i in range(64):
            self.var_n.append(tk.IntVar())
        
        self.check_b = []
        self.check_s = []
        self.entry_block = [] 
        """
        self.var = tk.IntVar()
        self.var.set(1)

        self.display = tk.Label(self,
                                 foreground='green')

        self.frame = tk.Frame(self)
        self.sector_n = []
        for i in range(16):
            self.sector_n.append(tk.Checkbutton(
                self.frame, text="Sector "+str(i),
                variable=self.var_n[i]))
            self.sector_n[i].grid(row=int(i/4), column=i%4, sticky=tk.W)
        self.block = tk.Radiobutton(
            self.frame, text="Por Bloque",
            variable=self.var, value=1)
        self.block.grid(row=4, column=0, sticky=tk.W)
        self.sector = tk.Radiobutton(
            self.frame, text="Por Sector",
            variable=self.var, value=2)
        self.sector.grid(row=4, column=1, sticky=tk.W)
        self.btn = tk.Button(self.frame, text="Leer", command=self.reader)
        self.btn.grid(row=4, column=3, sticky=tk.W)
        self.frame.pack(side=tk.TOP, fill=tk.Y)

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.group_1 = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        """
        self.frame = []
        self.var_code = tk.StringVar()

        helv25 = MyFont = font.Font(size='25')
        self.helv16 = MyFont = font.Font(size='10')
        self.helv18 = MyFont = font.Font(size='13')
        self.check_frame = tk.Frame(self)
        self.display_weigand_fa = tk.Label(self.check_frame, text="Facility code: ", foreground='green', font=self.helv18)
        self.display_weigand_fa.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.display_weigand_ca = tk.Label(self.check_frame, text="Card code: ", foreground='green', font=self.helv18)
        self.display_weigand_ca.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.display_hex_id = tk.Label(self.check_frame, text="UID Hex: ", foreground='green', font=self.helv18)
        self.display_hex_id.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.check_all = tk.Checkbutton(self.check_frame, variable=self.var_all, text="Selecciona todo", command= self.cb_all_s).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.button_clear = tk.Button(self.check_frame, text="Vaciar", command=self.cb_clear_all).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        #self.entry_code = tk.Entry(self.check_frame, textvariable=self.var_code, width=16).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        #self.var_code.trace("w", lambda name, index, mode, str_var=self.var_code: self.character_limit(str_var))
        #self.butto_encry = tk.Button(self.check_frame, text="Encriptar", command=self.cb_encry).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        #self.butto_decry = tk.Button(self.check_frame, text="Desencriptar", command=self.cb_decry).pack(side=tk.LEFT, fill=tk.BOTH, expand=0)
        self.check_frame.pack(side=tk.TOP, fill=tk.Y, expand=0)

        for i in range(4):
            self.frame.append(tk.Frame(self))

        self.btn_frame = tk.Frame(self)
        self.btn = []
        self.btn.append(tk.Button(self.btn_frame, text="Leer", command=self.read, font=helv25))
        self.btn.append(tk.Button(self.btn_frame, text="Editar", command=self.edit, font=helv25))
        self.btn.append(tk.Button(self.btn_frame, text="Escribir", command=self.write, font=helv25))
        self.display = tk.Label(self, foreground='green', font=helv25)
        #self.display_weigand_id = tk.Label(self.check_frame, text="Wiegand: ", foreground='green', font=self.helv16)
        #self.display_weigand_id.pack(side=tk.RIGHT, fill=tk.Y, expand=0)
        self.reader()

    def hide(self):
        self.canvas.destroy()
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.group_1.destroy()
        self.group_1 = tk.Frame(self.canvas)
        self.scrollbar.destroy()
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand= self.scrollbar.set)
        self.display.config(text=self._help)
        self.display.pack(fill=tk.BOTH, expand=1)

    def cb_encry(self):
        cipher = aesci(self.var_code.get())

        if(self.var_n[1].get()):
                self.block_value[1].set(cipher.encrypt(self.block_value[1].get()))
        if(self.var_n[2].get()):
                self.block_value[2].set(cipher.encrypt(self.block_value[2].get()))

        for i in range(1,16):
            j = i * 4
            if(self.var_n[j].get()):
                self.block_value[j].set(cipher.encrypt(self.block_value[j].get()))
            if(self.var_n[j+1].get()):
                self.block_value[j+1].set(cipher.encrypt(self.block_value[j+1].get()))
            if(self.var_n[j+2].get()):
                self.block_value[j+2].set(cipher.encrypt(self.block_value[j+2].get()))

    def cb_decry(self):
        cipher = aesci(self.var_code.get())

        if(self.var_n[1].get()):
                self.block_value[1].set(cipher.decrypt(self.block_value[1].get()))
        if(self.var_n[2].get()):
                self.block_value[2].set(cipher.decrypt(self.block_value[2].get()))

        for i in range(1,16):
            j = i * 4
            if(self.var_n[j].get()):
                self.block_value[j].set(cipher.decrypt(self.block_value[j].get()))
            if(self.var_n[j+1].get()):
                self.block_value[j+1].set(cipher.decrypt(self.block_value[j+1].get()))
            if(self.var_n[j+2].get()):
                self.block_value[j+2].set(cipher.decrypt(self.block_value[j+2].get()))

    def cb_clear_all(self):
        for i in range(16):
            j = i * 4
            if(self.var_n[j].get()):
                self.block_value[j].set('')
            if(self.var_n[j+1].get()):
                self.block_value[j+1].set('')
            if(self.var_n[j+2].get()):
                self.block_value[j+2].set('')


    def cb_all_s(self):
        if(self.var_all.get()):
            for i in range(16):
                j = i * 4
                self.check_b[j].select()
                self.check_b[j+1].select()
                self.check_b[j+2].select()
                self.check_s[i].select()
        else:
            for i in range(16):
                j = i * 4
                self.check_b[j].deselect()
                self.check_b[j+1].deselect()
                self.check_b[j+2].deselect()
                self.check_s[i].deselect()
        
    def cb_s(self, number):

        j = number * 4

        if(self.var_s[number].get()):
            for i in range(3):
                self.check_b[j+i].select()
        else:
            for i in range(3):
                self.check_b[j+i].deselect()

    def cb_b(self, number):

        count = 0
        j = int(number/4)
        k = j * 4

        if(self.var_n[number].get()):
            for i in range(3):
                if(self.var_n[k+i].get()):
                    count += 1
            if(count == 3):
                self.check_s[j].select()
        else:
            self.check_s[j].deselect()

    def read_blue(self, number):
        reader = SimpleMFRC522.SimpleMFRC522()
        data = reader.read_block(number)
        self.block_value[number].set(data[1])
        reader.Close_MFRC522()
        #time.sleep(0.1)
        return data

    def read2(self):

        time_exc=time.clock()
        self.display.config(text='', foreground='green')
        flag = False
        
        self.disable()
        if(Blue):

            if(self.var_n[0].get()):
                flag = True
                reader = SimpleMFRC522.SimpleMFRC522()
                data = reader.read_block(number)
                self.block_value[number].set(data[0])
                reader.Close_MFRC522()
            else:
                self.block_value[0].set('')
            if(self.var_n[1].get()):
                flag = True
                data = read_blue(1)
            else:
                self.block_value[1].set('')
            if(self.var_n[2].get()):
                flag = True
                data = read_blue(2)
            else:
                self.block_value[2].set('')

            for i in range(1,16):
                j = i * 4

                if(self.var_n[j].get()):
                    flag = True
                    data = read_blue(j)
                else:
                    self.block_value[j].set('')

                if(self.var_n[j+1].get()):
                    flag = True
                    data = read_blue(j+1)
                else:
                    self.block_value[j+1].set('')

                if(self.var_n[j+2].get()):
                    flag = True
                    data = read_blue(j+2)
                else:
                    self.block_value[j+2].set('')
        else:
            pass

        if (flag == False):
            self.display.config(text='Seleccione al menos un sector', foreground='green')
        else:
            if (data[1] is not None):
                if(data[1] is not ''):
                    self.display.config(text='Leido en : %.1f segundos.' % (time.clock() - time_exc), foreground='green')
                else:
                    self.display.config(text='Error al leer la tarjeta', foreground='red')
            else:
                self.display.config(text='Ponga la tarjeta por favor', foreground='red')

        self.display.pack(fill=tk.BOTH, expand=1)

    def read(self):

        time_exc=time.clock()

        self.display.config(text='', foreground='green')
        global Blue
        
        if(Blue):
            reader = SimpleMFRC522.SimpleMFRC522()
            uid = reader.read_id_no_block()
            reader.Close_MFRC522()
            
            if(uid is not None):
                
                reader = SimpleMFRC522.SimpleMFRC522()
                uid = reader.num_to_hex(uid)[1:9]
                reader.Close_MFRC522()
                self.display_hex_id.config(text='UID Hex: '+ uid + ' ', foreground='blue')
                self.display_weigand_fa.config(text='Facility code: '+ hwiegand.facility_c(hwiegand.h_w(uid))+ '    ', foreground='green')
                self.display_weigand_ca.config(text='Card code: '+ hwiegand.n_card(hwiegand.h_w(uid)) + '    ', foreground='green')
                #self.display_weigand_id.config(text='Weigand: '+ hwiegand.h_w(uid) + ' ', foreground='black')
                reader = SimpleMFRC522.SimpleMFRC522()
                data = reader.read_Dump()
                reader.Close_MFRC522()
            else:
                data = []
                data.append(None)
                data.append(None)
        else:
            data = []
            data.append(None)
            data.append(None)
            uid = reader_white.select_card_especial()
            if(uid):
                print("balla")
                data = []
                data.append(uid)
                data.append(reader_white.read_card_f())
                reader_white.closed_device()
                reader_white.closed_context()
        flag = False
        
        self.disable()
        if(data[0] is not None):

            if (data[1] is not None):

                """
                if(Blue):

                    if(self.var_n[0].get()):
                        flag  = True
                        #self.read_blue(i)
                        self.block_value[0].set(data[0])
                    else:
                        self.block_value[0].set('')

                    for i in range(1,64):
                        if(self.var_n[i].get()):
                            flag  = True
                            #self.read_blue(i)
                            self.block_value[i].set(data[1][i])
                    else:
                            self.block_value[i].set('')
                else:
                    pass
                """

                if(self.var_n[0].get()):
                    flag  = True
                    #self.read_blue(i)
                    self.block_value[0].set(data[0])
                else:
                    self.block_value[0].set('')

                for i in range(1,64):
                    if(self.var_n[i].get()):
                        flag  = True
                        #self.read_blue(i)
                        self.block_value[i].set(data[1][i])
                    else:
                        self.block_value[i].set('')

                if (flag == False):
                    self.display.config(text='Seleccione al menos un sector', foreground='green')
                else:
                    self.display.config(text='Leido en : %.1f segundos.' % (time.clock() - time_exc), foreground='green')
            else:
                self.display.config(text='Error al leer la tarjeta', foreground='red')
                self.display_hex_id.config(text='UID Hex: '+ uid + ' ', foreground='blue')
                self.display_weigand_fa.config(text='Facility code: ', foreground='green')
                self.display_weigand_ca.config(text='Card code: ', foreground='green')

        else:
            self.display.config(text='Ponga la tarjeta por favor', foreground='red')
            self.display_hex_id.config(text='UID Hex: '+ uid + ' ', foreground='blue')
            self.display_weigand_fa.config(text='Facility code: ', foreground='green')
            self.display_weigand_ca.config(text='Card code: ', foreground='green')


        #time.sleep(0.1)
        self.display.pack(fill=tk.BOTH, expand=1)

    def disable(self):
        self.check_b[0].configure(state='normal')
        for i in range(1,64):
            self.entry_block[i].configure(state='disabled')

    def edit(self):
        self.display.config(text='', foreground='green')
        self.check_b[0].configure(state='disabled')
        for i in range(1,64):
            self.entry_block[i].configure(state='normal')

    def write_blue(self, number):
        reader = SimpleMFRC522.SimpleMFRC522()
        data = reader.write_block(number, self.block_value[number].get())
        reader.Close_MFRC522()
        #time.sleep(0.1)
        return data

    def write(self):
        flag = False
        data = [] 
        data.append(None)
        data.append(None)
        
        time_exc=time.clock()
        self.display.config(text='', foreground='green')

        """
        if(Blue):
            #sector 0
            if(self.var_n[1].get()):
                data = write_blue(1)
            if(self.var_n[2].get()):
                data = write_blue(2)

            #all other sectors
            for i in range(1,16):
                j = i * 4
                if(self.var_n[j].get()):
                    flag = True
                    data = write_blue(j)
                if(self.var_n[j+1].get()):
                    flag = True
                    data = write_blue(j+1)
                if(self.var_n[j+2].get()):
                    flag = True
                    data = write_blue(j+2)
        else:
            pass
        """
        global Blue
        
        if(Blue):
            reader = SimpleMFRC522.SimpleMFRC522()
            uid = reader.read_id_no_block()
            reader.Close_MFRC522()

            if(uid is not None):
                
                reader = SimpleMFRC522.SimpleMFRC522()
                uid = reader.num_to_hex(uid)[1:9]
                reader.Close_MFRC522()
                self.display_hex_id.config(text='UID Hex: '+ uid + ' ', foreground='blue')
                self.display_weigand_fa.config(text='Facility code: '+ hwiegand.facility_c(hwiegand.h_w(uid))+ '    ', foreground='green')
                self.display_weigand_ca.config(text='Card code: '+ hwiegand.n_card(hwiegand.h_w(uid)) + '    ', foreground='green')
                

            for i in range(1,64):
                if(self.var_n[i].get()):
                    flag = True
                    #self.write_blue(i)
                    reader = SimpleMFRC522.SimpleMFRC522()
                    data = reader.write_block(i, self.block_value[i].get())
                    reader.Close_MFRC522()
                    #time.sleep(0.1)
        else:
            uid = reader_white.select_card_especial()
            if (uid):
                #reader_white.read_card_f()
                reader_white.select_card_especial()
                reader_white.closed_device() #ojo
                reader_white.closed_context() #ojo
            #time.sleep(3.01)
            for i in range(1,15):
                if(self.var_n[i].get()):
                    flag = True
                    if(uid):
                        #print(uid)
                        data = []
                        data.append(uid)
                        
                        reader_white.select_card_especial()
                        print("escribiendo")
                        data.append(reader_white.auth_and_write(i, uid, self.block_value[i].get()))
                        reader_white.closed_device() #ojo
                        reader_white.closed_context() #ojo
                        
                        

                    else:
                        print("no hay tarjeta al escribir")
                        
                        #reader_white.closed_device() #ojo
                        #reader_white.closed_context() #ojo
                        break # hay q romper el ciclo

        if (flag == False):
            self.display.config(text='Seleccione al menos un sector', foreground='green')
            self.display_weigand_fa.config(text='Facility code: ', foreground='green')
            self.display_weigand_ca.config(text='Card code: ', foreground='green')

        else:
            if (data[0] is not None):
                if(data[1] is not ''): #error aqui
                    self.display.config(text='Escrito en: %.1f segundos.' % (time.clock() - time_exc), foreground='green')
                else:
                    self.display.config(text='Error al leer la tarjeta', foreground='red')
                    self.display_weigand_fa.config(text='Facility code: ', foreground='green')
                    self.display_weigand_ca.config(text='Card code: ', foreground='green')

            else:
                self.display.config(text='Ponga la tarjeta por favor', foreground='red')
                self.display_weigand_fa.config(text='Facility code: ', foreground='green')
                self.display_weigand_ca.config(text='Card code: ', foreground='green')
        
        self.display.pack(fill=tk.BOTH, expand=1)

    def open_window_1(self, block):
        window = SaveWindow(self, block, 16)

    def open_window_2(self, block):
        window = SaveWindow(self, block, 48)

    def onConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width = (canvas_width - 10))

    def reader(self):

        frame = []
        number = 0
        for i in range(16):
            frame.append(tk.Frame(self.frame[number]))
            self.create_block(frame[i], i)
            if ((i+1) < 16):
                number = int((i+1)/4)

            frame[i].pack(side=tk.LEFT, fill=tk.Y, expand=0)

        for i in range(4):
            self.frame[i].pack(side=tk.TOP, fill=tk.Y, expand=0)

        self.btn[0].pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.btn[1].pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.btn[2].pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=0)

    def character_limit(self, entry_text):
        #print("aqui", entry_text.get())
        if len(entry_text.get()) > 16:
            entry_text.set(entry_text.get()[:16])

    def create_block(self, group, i):
        group_2 = tk.LabelFrame(group, padx=15, pady=10, text="Sector "+str(i))
        group_2.pack(fill=tk.BOTH, expand=1)

        j = i * 4
        self.check_s.append(tk.Checkbutton(group_2, variable=self.var_s[i], command=lambda i=i: self.cb_s(i)))
        for k in range(4):
            self.block_value.append(tk.StringVar(group_2, ''))
            self.block_value[j+k].trace("w", lambda name, index, mode, str_var=self.block_value[j+k]: self.character_limit(str_var))
            #self.block_value[j+k].trace("w", lambda *args: self.character_limit())
            self.check_b.append(tk.Checkbutton(group_2, variable=self.var_n[j+k], command=lambda j=j+k: self.cb_b(j)))
            self.entry_block.append(tk.Entry(group_2, textvariable=self.block_value[j+k], width=10, state='disable'))

        ttk.Label(group_2, width=9, text="Bloque "+str(j)).grid(row=j, column=1)
        ttk.Label(group_2, text="Bloque "+str(j+1)).grid(row=j + 1, column=1)
        ttk.Label(group_2, text="Bloque "+str(j+2)).grid(row=j + 2, column=1)

        self.check_s[i].grid(row=j+1, column=0)

        #tk.Entry(group_2, textvariable=self.block_value[j], width=10).grid(row=j, column=2, sticky=tk.W)
        #tk.Entry(group_2, textvariable=self.block_value[j+1], width=10).grid(row=j+1, column=2, sticky=tk.W)
        #tk.Entry(group_2, textvariable=self.block_value[j+2], width=10).grid(row=j+2, column=2, sticky=tk.W)

        for k in range(3):
            self.check_b[j+k].grid(row=j+k, column=3)
            self.entry_block[j+k].grid(row=j+k, column=2, sticky=tk.W)
        """
        for i in range(3):
            group_2.columnconfigure((0,1), weight=1)
            group_2.rowconfigure((0,2), weight=1)
        """
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_columnconfigure(0, weight=1)
    """
    def create_sector(self, group, data, i):
        group_2 = tk.LabelFrame(group, padx=15, pady=10, text="Sector "+str(i))
        group_2.pack(fill=tk.BOTH, expand=1)

        block_value = tk.StringVar(group_2, data[i])

        #ttk.Label(group_2, text="Bloke "+str(i)).grid(row=i)
        #ttk.Label(group_2, text="Bloke "+str(j+1)).grid(row=j + 1)
        #ttk.Label(group_2, text="Bloke "+str(j+2)).grid(row=j + 2)
        tk.Entry(group_2, textvariable=block_value, width=48).grid(row=i, column=1, sticky=tk.W)
        #ttk.Label(group_2, text=data[i][0], width=48).grid(row=i, column=1, sticky=tk.W)
        #ttk.Label(group_2, text=data[j + 1][0], width=16).grid(row=j + 1, column=1, sticky=tk.W)
        #ttk.Label(group_2, text=data[j + 2][0], width=16).grid(row=j + 2, column=1, sticky=tk.W)
        ttk.Button(group_2, text="Guardar", command=lambda i=data[i]: self.open_window_2(i)).grid(row=i, column= 2)
        #ttk.Button(group_2, text="Editar", command=lambda j=data[j+1]: self.open_window(j)).grid(row=j + 1, column= 2)
        #ttk.Button(group_2, text="Editar", command=lambda j=data[j+2]: self.open_window(j)).grid(row=j + 2, column= 2)
        #Grid.columnconfigure(frame, x, weight=1)
        #Grid.rowconfigure(frame, y, weight=1)
        #self.master.grid_rowconfigure(0, weight=1)
        #self.master.grid_columnconfigure(0, weight=1)
    """


class MenuBar(tk.Menu):
    "Menu bar appearing with expected components."

    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.optionVar = tk.IntVar()
        self.optionVar.set(1)

        filemenu = tk.Menu(self, tearoff=False)
        filemenu.add_command(label=_('New'), command=self.new_dialog)
        filemenu.add_separator()
        filemenu.add_command(label=_('Exit'), underline=1, command=self.quit)

        lectormenu = tk.Menu(self, tearoff=False)
        if(GPIO is not None):
            lectormenu.add_radiobutton(label="Lector Azul", value=1, variable=self.optionVar, command=self.blue_reader)
        else:
            self.optionVar.set(0)
            lectormenu.add_radiobutton(label="Lector Azul", value=1, variable=self.optionVar, command=self.blue_reader, state='disable')
        lectormenu.add_radiobutton(label="Lector Blanco", value=0, variable=self.optionVar, command=self.white_reader)

        helpmenu = tk.Menu(self, tearoff=False)
        helpmenu.add_command(label=_('Help'), command=lambda:
                             self.help_dialog(None), accelerator="F1")
        helpmenu.add_command(label=_('About'), command=self.about_dialog)
        self.bind_all('<F1>', self.help_dialog)

        self.add_cascade(label=_('Inicio'), underline=0, menu=filemenu)
        self.add_cascade(label=_('Lector'), underline=0, menu=lectormenu)
        self.add_cascade(label=_('Help'), underline=0, menu=helpmenu)

    def blue_reader(self):
        if(GPIO is not None):
            global Blue
            Blue = True 
        else:
            pass
            #raise ValueError(f'RPi.GPIO module not imported. Please pip install.')

    def white_reader(self):
        global Blue
        Blue = False

    def quit(self):
        "Ends toplevel execution."

        sys.exit(0)

    def help_dialog(self, event):
        "Dialog cataloging results achievable, and provided means available."

        _description = _('Help not yet created.')
        PopupDialog(self, 'Py3 tk', _description)

    def about_dialog(self):
        "Dialog for program."

        _description = 'Python 3 tk GUI'
        if _description == '':
            _description = _('No description available')
        _description += '\n'
        _description += '\n' + _('Author') + ': David Gomez'
        _description += '\n' + _('Email') + ': agiledesign2.0@gmail.com'
        _description += '\n' + _('Version') + ': 2.0.0'
        _description += '\n' + _('GitHub Package') + \
                        ': App_NFC'
        PopupDialog(self, _('About') + ' Python3 tk',
                    _description)

    def new_dialog(self):
        "Non-functional dialog indicating successful navigation."

        PopupDialog(self, _('New button pressed'), _('Not yet implemented'))
    """
    def open_dialog(self):
        "Standard askopenfilename() invocation and result handling."

        _name = tk.filedialog.askopenfilename()
        if isinstance(_name, str):
            print(_('File selected for open: ') + _name)
        else:
            print(_('No file selected'))
    """



class Application(tk.Tk):
    "Create top-level tk widget containing all other widgets."

    def __init__(self):
        tk.Tk.__init__(self)
        menubar = MenuBar(self)
        self.config(menu=menubar)
        self.wm_title('APP_NFC')
        self.wm_geometry('640x480')
        pad=0
        self._geom='200x200+0+0'
        self.geometry("{0}x{1}+0+0".format(
            self.winfo_screenwidth()-pad, self.winfo_screenheight()-100))
        self.bind('<Escape>',self.toggle_geom) 

# Status bar selection == 'y'
        self.statusbar = StatusBar(self)
        self.statusbar.pack(side='bottom', fill='x')
        self.bind_all('<Enter>', lambda e: self.statusbar.set_text(0,
                      'Mouse: 1'))
        self.bind_all('<Leave>', lambda e: self.statusbar.set_text(0,
                      'Mouse: 0'))
        self.bind_all('<Button-1>', lambda e: self.statusbar.set_text(1,
                      'Clicked at x = ' + str(e.x) + ' y = ' + str(e.y)))
        self.start_time = datetime.datetime.now()
        self.uptime()

        self.mainframe = Dyna_writeFrame(self)
        self.mainframe.pack(fill=tk.BOTH, expand=1)

# Status bar selection == 'y'

    def mainframe_destroy(self, frame):
        self.mainframe.destroy()
        self.mainframe = frame(self)
        self.mainframe.pack(fill=tk.BOTH, expand=1)

    def uptime(self):
        _upseconds = str(int(round((datetime.datetime.now() - self.start_time).total_seconds())))
        self.statusbar.set_text(2, _('Uptime') + ': ' + _upseconds)
        self.after(1000, self.uptime)

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom



if __name__ == '__main__':
    APPLICATION_GUI = Application()
    APPLICATION_GUI.mainloop()
