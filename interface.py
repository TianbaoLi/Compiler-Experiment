# -*- coding: utf-8 -*-
from Tkinter import *
from tkFont import *
def lexer():
	text = code.get(1.0, END)
	analysis.insert(1.0, text)

root = Tk()
code = Text(root, width=50, height=30)
analysis = Text(root, width=50, height=30)
t = StringVar()
t.set('Lexer by LiTianbao')
label = Label(root, textvariable = t)
button = Button(root, text = 'Lexical Analysis', command = lexer)
label.pack(side = TOP)
button.pack(side = BOTTOM)
code.pack(side = LEFT)
analysis.pack(side = RIGHT) 
root.mainloop()