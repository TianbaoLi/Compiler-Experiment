#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from Tkinter import *
from tkFont import *

KEYWORD_LIST = ['if', 'else', 'while', 'break', 'continue', 'for', 'double', 'int', 'float', 'long', 'short', 'bool', 
				'switch', 'case', 'return', 'void']

SEPARATOR_LIST = ['{', '}', '[', ']', '(', ')', '~', ',', ';', '.', '?', ':', ' ']

OPERATOR_LIST = ['+', '++', '-', '--', '+=', '-=', '*', '*=', '%', '%=', '->', '|', '||', '|=',
				 '/', '/=', '>', '<', '>=', '<=', '=', '==', '!=', '!', '&']

CATEGORY_DICT = {
	#KEYWORD
	"far": 257,
	"near": 258,
	"pascal": 259,
	"register": 260,
	"asm": 261,
	"cdecl": 262,
	"huge": 263,
	"auto": 264,
	"double": 265,
	"int": 266,
	"struct": 267,
	"break": 268,
	"else": 269,
	"long": 270,
	"switch": 271,
	"case": 272,
	"enum": 273,
	"register": 274,
	"typedef": 275,
	"char": 276,
	"extern": 277,
	"return": 278,
	"union": 279,
	"const": 280,
	"float": 281,
	"short": 282,
	"unsigned": 283,
	"continue": 284,
	"for": 285,
	"signed": 286,
	"void": 287,
	"default": 288,
	"goto": 289,
	"sizeof": 290,
	"volatile": 291,
	"do": 292,
	"if": 293,
	"while": 294,
	"static": 295,
	"interrupt": 296,
	"sizeof": 297,
	"NULL": 298,
	#SEPARATOR
	"{": 299,
	"}": 300,
	"[": 301,
	"]": 302,
	"(": 303,
	")": 304,
	"~": 305,
	",": 306,
	";": 307,
	".": 308,
	"#": 309,
	"?": 310,
	":": 311,
	#OPERATOR
	"<<": 312,
	">>": 313,
	"<": 314,
	"<=": 315,
	">": 316,
	">=": 317,
	"=": 318,
	"==": 319,
	"|": 320,
	"||": 321,
	"|=": 322,
	"^": 323,
	"^=": 324,
	"&": 325,
	"&&": 326,
	"&=": 327,
	"%": 328,
	"%=": 329,
	"+": 330,
	"++": 331,
	"+=": 332,
	"-": 333,
	"--": 334,
	"-=": 335,
	"->": 336,
	"/": 337,
	"/=": 338,
	"*": 339,
	"*=": 340,
	"!": 341,
	"!=": 342,
	"sizeof": 343,
	"<<=": 344,
	">>=": 345,
	"int10": 346,
	"int16": 347,
	"int8": 348,
	"char": 350,
	"string": 351,
	"bool": 352,
	"float_const": 353,
	"ID": 354
}

current_row = -1
current_line = 0
input_str = []
out_line = 1

def getchar():
	global current_row
	global current_line
	current_row += 1

	if current_row == len(input_str[current_line]):
		current_line += 1
		current_row = 0

	if current_line == len(input_str) - 1:
		return 'SCANEOF'

	return input_str[current_line][current_row]


def ungetchar():
	global current_row
	global current_line
	current_row = current_row - 1
	if current_row < 0:
		current_line = current_line - 1
		current_row = len(input_str[current_row]) - 1
	return input_str[current_line][current_row]

def error(msg, line=None, row=None):
	global out_line
	if line is None:
		line = current_line + 1
	if row is None:
		row = current_row + 1
	analysis.insert(str(out_line) + '.0', str(line) + ':' + str(row) + 'Error: ' + msg)
	analysis.insert(str(out_line) + '.end', "\n")
	out_line = out_line + 1

def scanner():
	global current_line
	global current_row
	current_char = getchar()
	if current_char == 'SCANEOF':
		return ('SCANEOF', '', '')
	if current_char.strip() == '':
		return
	if current_char.isdigit():
		int_value = 0
		while current_char.isdigit():
			int_value = int_value * 10 + int(current_char)
			current_char = getchar()
		if current_char not in OPERATOR_LIST and current_char not in SEPARATOR_LIST and current_char != 'e':
			line = current_line + 1
			row = current_row + 1
			ungetchar()
			error('illigal identifier', line, row)
			return ('SCANEOF', '', '')
		if current_char != '.' and current_char != 'e':
			ungetchar()
			return ('INT10', int_value, CATEGORY_DICT['int10'])
		if current_char == 'e':
			power_value = str(int_value) + 'e'
			current_char = getchar()
			while current_char.isdigit():
				power_value += current_char
				current_char = getchar()
			if current_char not in OPERATOR_LIST and current_char not in SEPARATOR_LIST:
				line = current_line + 1
				row = current_row + 1
				ungetchar()
				error('illigal const int value in power', line, row)
				return ('SCANEOF', '', '')
			ungetchar()
			return ('INT10', power_value, CATEGORY_DICT['int10'])
		if current_char == '.':
			float_value = str(int_value) + '.'
			current_char = getchar()
			while current_char.isdigit():
				float_value += current_char
				current_char = getchar()
			if current_char not in OPERATOR_LIST and current_char not in SEPARATOR_LIST or current_char == '.':
				line = current_line + 1
				row = current_row + 1
				ungetchar()
				error('illigal const float value', line, row)
				return ('SCANEOF', '', '')
			ungetchar()
			return ('FLOAT_CONST', float_value, CATEGORY_DICT['float_const'])
	if current_char.isalpha() or current_char == '_':
		string = ''
		while current_char.isalpha() or current_char.isdigit() or current_char == '_' and current_char != ' ':
			string += current_char
			current_char = getchar()
			if current_char == 'SCANEOF':
				break
		ungetchar()
		if string in KEYWORD_LIST:
			return (string, '', CATEGORY_DICT[string])
		else:
			return ('ID', string, CATEGORY_DICT['ID'])

	if current_char == '\"':
		str_literal = ''
		line = current_line + 1
		row = current_row + 1

		current_char = getchar()
		while current_char != '\"':
			str_literal += current_char
			current_char = getchar()
			if current_char == 'SCANEOF':
				error('missing terminating \"', line, row)

				current_line = line
				current_row = row
				return ('SCANEOF', '', '')
		return('STRING_LITERAL', str_literal, CATEGORY_DICT['string'])

	if current_char == '/':
		next_char = getchar()
		line = int(current_line) + 1
		row = int(current_row) + 1
		if next_char == '*':
			comment = ''
			next_char = getchar()
			while True:
				if next_char == 'SCANEOF':
					error('unteminated /* comment', line, row)
					return ('SCANEOF', '', '')
				if next_char == '*':
					end_char = getchar()
					if end_char == '/':
						return None
					if end_char == 'SCANEOF':
						error('unteminated /* comment', line, row)
						return ('SCANEOF', '', '')
				comment += next_char
				next_char = getchar()
		else:
			ungetchar()
			op = current_char
			current_char = getchar()
			if current_char in OPERATOR_LIST:
				op += current_char
			else:
				ungetchar()
			return ('OP', op, CATEGORY_DICT[op])

	if current_char in SEPARATOR_LIST:
		return ('SEP', current_char, CATEGORY_DICT[current_char])

	if current_char in OPERATOR_LIST:
		op = current_char
		current_char = getchar()
		if current_char in OPERATOR_LIST:
			op += current_char
		else:
			ungetchar()
		return ('OP', op, CATEGORY_DICT[op])
	else:
		error('unknown character: ' + current_char)

root = Tk()
code = Text(root, width=50, height=30, font=15)
analysis = Text(root, width=50, height=30, font=15)

def lexer():
	global current_row
	global current_line
	global input_str
	global out_line
	analysis.delete(1.0, END)
	input_raw = code.get(1.0, END)
	input_str = input_raw.split("\n")
	current_row = -1
	current_line = 0
	out_line = 1
	
	while True:
		r = scanner()
		if r is not None:
			if r[0] == 'SCANEOF':
				break
			analysis.insert(str(out_line) + '.0', str(r[0]) + "\t\t" + str(r[1]) + "\t\t" + str(r[2]))
			analysis.insert(str(out_line) + '.end', "\n")
			out_line = out_line + 1

def pre_interface():
	global root
	global code
	global analysis
	t = StringVar()
	t.set('Lexer by LiTianbao')
	label = Label(root, textvariable = t, font=15)
	button = Button(root, text = 'Lexical Analysis', command = lexer, font=15)
	root.title("LEXER")
	label.pack(side = TOP)
	button.pack(side = BOTTOM)
	code.pack(side = LEFT)
	analysis.pack(side = RIGHT) 
	root.mainloop()

def main():
	pre_interface()
	lexer()

if __name__ == '__main__':
	main()
