#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from Tkinter import *
from tkFont import *
from FileDialog import *
from ScrolledText import ScrolledText

grammar = {}
terminal = []
nonterminal = []
first = {}
follow = {}
parsing_table = {}
token = []
token_attr = []
leaf_tab = {}

def fileloader():
	global root
	global token
	code.delete(1.0, END)
	fd = LoadFileDialog(root)
	filename = fd.go()
	fin = open(filename, "r")
	input_file = fin.read()
	code.insert(1.0, input_file)
	input_lines = input_file.split('\n')
	for lines in input_lines:
		tags = lines.split('\t')
		while tags.count('') > 0:
			tags.remove('')
		if(len(tags) != 0):
			if(tags[0] == 'SEP' or tags[0] == 'OP'):
				token.append(tags[1])
			else:
				token.append(tags[0])
			token_attr.append(tags[1])

	fin.close()

def grammar_scanner():
	grammarIn = open('grammar.ds', 'r')
	grammar_lines = grammarIn.readlines()
	grammarIn.close()

	for line in grammar_lines:
		line_terminal = []
		line_nonterminal = []
		grammar_sequence = []
		temp = ""

		line = line.strip()
		tags = line.split("\t->\t")
		if tags[0] is not None:
			tags[0] = tags[0][1:len(tags[0])-1]
			line_nonterminal.append(tags[0])
			grammar_sequence.append(tags[0])
		i = 0
		while i < len(tags[1]):
			if tags[1][i] == '<':
				i += 1
				while tags[1][i] != '>':
					temp += tags[1][i]
					i = i +1
				line_nonterminal.append(temp)
				grammar_sequence.append(temp)
				temp = ""
			elif tags[1][i] == '[':
				i = i + 1
				while tags[1][i] != ']':
					temp += tags[1][i]
					i += 1
				
				if i != len(tags[1]) - 1 and  tags[1][i+1] == ']':
					temp += tags[1][i]
					i += 1
				line_terminal.append(temp)
				grammar_sequence.append(temp)
				temp = ""
			i += 1
		if grammar_sequence[0] not in grammar:
			grammar[grammar_sequence[0]] = []
		grammar[grammar_sequence[0]].append(grammar_sequence[1:len(grammar_sequence)])
		for each in line_nonterminal:
			if each not in nonterminal:
				nonterminal.append(each)
				leaf_tab[each] = 0
		for each in line_terminal:
			if each not in terminal:
				terminal.append(each)
	terminal.append('$')

def getFirst():
	global grammar
	global terminal
	global nonterminal
	global first

	for ter in terminal:
		first[ter] = [ter]
	for nonter in nonterminal:
		first[nonter] = []
		for sequence in grammar[nonter]:
			if sequence == ['null']:
				first[nonter] = ['null']

	stopFlag = False
	while(not stopFlag):
		stopFlag = True
		for nonter in nonterminal:
			for sequence in grammar.get(nonter, []):
				counter = 0
				for tag in sequence:
					for tagFirst in first[tag]:
						if tagFirst != 'null' and tagFirst not in first[nonter]:
							first[nonter].append(tagFirst)
							stopFlag = False
					if 'null' not in first[tag]:
						break
					else:
						counter += 1
				if counter == len(sequence) and 'null' not in first[nonter]:
					first[nonter].append('null')
					stopFlag = False

	#print first

def getFollow():
	global grammar
	global terminal
	global nonterminal
	global first
	global follow

	follow['program'] = ['$']
	for ter in terminal:
		follow[ter] = []
	for nonter in nonterminal:
		follow[nonter] = []

	for nonter in nonterminal:
		for sequence in grammar[nonter]:
			for i in xrange(0,len(sequence)-1):
				for next_first in first[sequence[i+1]]:
					if next_first != 'null' and next_first not in follow[sequence[i]]:
						follow[sequence[i]].append(next_first)

	stopFlag = False
	while(not stopFlag):
		stopFlag = True
		for nonter in nonterminal:
			for sequence in grammar[nonter]:
				for i in xrange(0,len(sequence)-1):
					for each_follow in follow[nonter]:
						if each_follow not in follow[sequence[i]]:
							follow[sequence[i]].append(each_follow)
							stopFlag = False
					if 'null' not in first[sequence[i]]:
						break

	#print follow

def get_parsing_table():
	global first
	global follow
	global parsing_table
	for nonter in nonterminal:
		parsing_table[nonter] = {}
		for ter in terminal:
			parsing_table[nonter][ter] = -2
	
	for nonter in nonterminal:
		for i in xrange(0,len(grammar[nonter])):
			counter = 0
			for tag in grammar[nonter][i]:
				for each_first in first[tag]:
					if parsing_table[nonter][each_first] < 0:
						parsing_table[nonter][each_first] = i
				if 'null' not in first[tag]:
					break
				else:
					count += 1
			if counter == len(grammar[nonter][i]):
				for each_follow in follow[nonter]:
					if each_follow in terminal:
						if parsing_table[nonter][each_follow] < 0:
							parsing_table[nonter][each_follow] = i
	# 同步集合位为-1
	for nonter in nonterminal:
		for each_follow in follow[nonter]:
			if parsing_table[nonter][each_follow] < 0:
				parsing_table[nonter][each_follow] = -1
	#print parsing_table

syntax_result = []

def syntax_analysis():
	global parsing_table
	global syntax_result
	global token
	stack = range(1000)
	stack[0] = 'program'
	tab = range(1000)
	tab[0] = 0
	leaf_tab['program'] = 0
	stack_top = 0
	token_pointer = 0

	while(stack_top >= 0):
		if(token_pointer >= len(token)):
			syntax_result.append('error:程序结构不完整,编译失败')
			break
		if(stack[stack_top] in terminal):

			if stack[stack_top] == token[token_pointer]:
				if token[token_pointer] not in ("IDN", "INUM", "FNUM"):
					syntax_result.append('    ' * tab[stack_top] + 'leaf:[' + token[token_pointer] + ']')
				else:
					syntax_result.append('    ' * tab[stack_top] + 'leaf:[' + token[token_pointer] + ":" + token_attr[token_pointer] + ']')

				#print 'leaf:[' + token[token_pointer] + ']'
			else:
				syntax_result.append('    ' * tab[stack_top] + 'error:不可接受的终结符：[' + token[token_pointer] + ']')		
			stack_top -= 1
			token_pointer += 1
		else:
			if parsing_table[stack[stack_top]][token[token_pointer]] < 0:
				if ['Lambda'] in grammar[stack[stack_top]]:
					#syntax_result.append('success: [' + stack[stack_top] + ']\t->\t[Lambda]')
					stack_top -= 1
				else:
					if parsing_table[stack[stack_top]][token[token_pointer]] == -1:
						syntax_result.append('    ' * tab[stack_top] + 'error: [' + token[token_pointer] + ']不可接受,进入同步恢复状态,栈顶元素为:'+stack[stack_top])
						stack_top -= 1
					else:
						syntax_result.append('    ' * tab[stack_top] + 'error: [' + token[token_pointer] + ']不可接受,忽略该符号以恢复错误')
						token_pointer += 1
			else:
				tmp_sequence = grammar[stack[stack_top]][parsing_table[stack[stack_top]][token[token_pointer]]]
				
				tmp_str = '    ' * tab[stack_top] + 'success: [' + stack[stack_top] + ']\t->\t'
				tab_temp = tab[stack_top]
				stack_top -= 1
				for x in xrange(0,len(tmp_sequence)):
					tmp_str = tmp_str + '[' + tmp_sequence[x] +']'
					stack_top += 1
					stack[stack_top] = tmp_sequence[len(tmp_sequence) - 1 - x]
					tab[stack_top] = tab_temp + 1
				syntax_result.append(tmp_str)
					
		if token_pointer == len(token):
			break	
	for each in syntax_result:
		analysis.insert(END,each + '\n')


root = Tk()
code = ScrolledText(root, width=50, height=30, font=15)
analysis = ScrolledText(root, width=200, height=30, font=10)

def interface():
	global root
	global code
	global analysis
	t = StringVar()
	t.set('Syntax by LiTianbao')
	label = Label(root, textvariable = t, font=15)
	Analysis = Button(root, text = 'Syntax  Analysis', command = syntax_analysis, font=15)
	load = Button(root, text = '    Load  token    ', command = fileloader, font=15)
	root.title("Syntax")
	root.geometry('1600x800')
	label.pack(side = TOP)
	Analysis.pack(side = BOTTOM)
	load.pack(side = BOTTOM)
	code.pack(side = LEFT)
	analysis.pack(side = RIGHT)
	root.mainloop()

def main():
	global token
	#read token from lexer
	grammar_scanner()
	getFirst()
	getFollow()
	get_parsing_table()
	interface()
	#syntax_analysis()
	
if __name__ == '__main__':
	main()