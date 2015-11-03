#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from Tkinter import *
from tkFont import *
from FileDialog import *
from ScrolledText import ScrolledText

def fileloader():
	global root
	code.delete(1.0, END)
	fd = LoadFileDialog(root)
	filename = fd.go()
	fin = open(filename, "r")
	input_file = fin.read()
	input_lines = input_file[0].split("\n")
	code.insert(1.0, input_file)
	fin.close()

def syntax():
	print 1

root = Tk()
code = ScrolledText(root, width=50, height=30, font=15)
analysis = ScrolledText(root, width=50, height=30, font=15)

def pre_interface():
	global root
	global code
	global analysis
	t = StringVar()
	t.set('Syntax by LiTianbao')
	label = Label(root, textvariable = t, font=15)
	Analysis = Button(root, text = 'Syntax Analysis', command = syntax, font=15)
	load = Button(root, text = '    Lode  code    ', command = fileloader, font=15)
	root.title("Syntax")
	label.pack(side = TOP)
	Analysis.pack(side = BOTTOM)
	load.pack(side = BOTTOM)
	code.pack(side = LEFT)
	analysis.pack(side = RIGHT) 
	root.mainloop()

def main():
	pre_interface()
	lexer()

if __name__ == '__main__':
	main()