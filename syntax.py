#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from Tkinter import *
from tkFont import *
from FileDialog import *
from ScrolledText import ScrolledText
from lexer import lexer_analysis

grammar = {}#存储grammar.ds中读取的语法，例grammar['Lambda'] = [';', 'program']
terminal = []#终结符表
nonterminal = []#非终结符表
first = {}#字典形式储存first集，字典value为一个列表，例first[a] = {'b', '+'}
follow = {}#字典形式储存follow集，字典value为一个列表，例follow[a] = {'b', '+'}
parsing_table = {}#转换表
token = []
token_attr = []
leaf_tab = {}#用来记录语法生成树中，每个符号缩进的长度

def fileloader():#窗口打开文件载入代码
	global root
	code.delete(1.0, END)#清空code输入框
	fd = LoadFileDialog(root)#打开文件
	filename = fd.go()
	fin = open(filename, "r")
	input_file = fin.read()
	fin.close()
	code.insert(1.0, input_file)#插入到界面

def grammar_scanner():#读取grammar.ds语法文件
	grammarIn = open('grammar.ds', 'r')
	grammar_lines = grammarIn.readlines()
	grammarIn.close()

	for line in grammar_lines:#每一行作为一条语法规则
		line_terminal = []
		line_nonterminal = []
		grammar_sequence = []
		temp = ""

		line = line.strip()
		tags = line.split("\t->\t")#分割语法中左项和右项
		if tags[0] is not None:
			tags[0] = tags[0][1:len(tags[0])-1]#除去左项两端的<>
			line_nonterminal.append(tags[0])#左项默认加到非终结符
			grammar_sequence.append(tags[0])#记录当前行出现过的语法token
		i = 0#处理右项的循环变量
		while i < len(tags[1]):
			if tags[1][i] == '<':#如果出现<164>形式的非终结符，可以将其根据第164条语法进行拓展
				i += 1
				while tags[1][i] != '>':#提取语法序号（temp = 164）
					temp += tags[1][i]
					i = i +1
				line_nonterminal.append(temp)#加到非终结符
				grammar_sequence.append(temp)#记录当前行出现过的语法token
				temp = ""
			elif tags[1][i] == '[':#如果出现[double]，[%]等形式的终结符
				i = i + 1
				while tags[1][i] != ']':#提取终结符（temp = double）
					temp += tags[1][i]
					i += 1

				if i != len(tags[1]) - 1 and  tags[1][i+1] == ']':#处理类似于[[]<normal expr>[]]情况下，]符号嵌套（即语法项中存在]符号）
					temp += tags[1][i]
					i += 1
				line_terminal.append(temp)#加到终结符
				grammar_sequence.append(temp)#记录当前行出现过的语法token
				temp = ""
			i += 1
		if grammar_sequence[0] not in grammar:
			grammar[grammar_sequence[0]] = []#在grammar的字典中创建以左项为key的list，例如grammar['Lambda'] = []
		grammar[grammar_sequence[0]].append(grammar_sequence[1:len(grammar_sequence)])#将右项加入到左项作为key的list中，例[['Lambda'], [';', 'program']]
		for each in line_nonterminal:#将在每行出现过的非终结符，加入到全局的非终结符表。leaf_tab先置为0，等待后续处理
			if each not in nonterminal:
				nonterminal.append(each)
				leaf_tab[each] = 0
		for each in line_terminal:#将在每行出现过的终结符，加入到全局的终结符表。
			if each not in terminal:
				terminal.append(each)
	terminal.append('$')#将$加入到终结符表，语法中未出现，但是分析中需要

def getFirst():#求first集
	global grammar
	global terminal
	global nonterminal
	global first

	for ter in terminal:
		first[ter] = [ter]#终结符的first集设置为其本身
	for nonter in nonterminal:
		first[nonter] = []#非终结符first集先置空，建立每个first[nonter]列表
		for sequence in grammar[nonter]:
			if sequence == ['null']:#能推导出空的非终结符，先将列表的第一位设置成null，
				first[nonter] = ['null']

	stopFlag = False#设置一个标识循环添加终结符过程结束的flag
	while(not stopFlag):
		stopFlag = True#假定没有新添加的非终结符（即该过程将结束）
		for nonter in nonterminal:
			for sequence in grammar.get(nonter, []):#非终结符nonter根据语法能推导出的每一个符号序列e
				counter = 0#统计nonter能推倒出的项中包含多少的null
				for tag in sequence:#循环处理sequence中每一个符号tag
					for tagFirst in first[tag]:#tag的first中每一项都有可能成为被添加到first[nonter]
						if tagFirst != 'null' and tagFirst not in first[nonter]:#如果该项不是null且未出现，就添加到first[nonter]
							first[nonter].append(tagFirst)
							stopFlag = False#有新添加的符号，可能依据这项推导出新的符号，应再次进行循环
					if 'null' not in first[tag]:
						break
					else:#如果能tag推到出null，counter++
						counter += 1
				if counter == len(sequence) and 'null' not in first[nonter]:#如果sequence包含的每一项，能能推倒出null，那么nonter应能推导出null，如果不存在则添加
					first[nonter].append('null')
					stopFlag = False#新添加null，可能依据这项推导出新的符号，应再次进行循环

	#print first

def getFollow():#求follow集
	global grammar
	global terminal
	global nonterminal
	global first
	global follow

	follow['program'] = ['$']
	for ter in terminal:#初始化终结符的follow集为空列表
		follow[ter] = []
	for nonter in nonterminal::#初始化非终结符的follow集为空列表
		follow[nonter] = []

	for nonter in nonterminal:
		for sequence in grammar[nonter]:#sequence为nonter能推倒出的每一项序列构成的列表
			for i in xrange(0,len(sequence)-1):
				for next_first in first[sequence[i+1]]:#从sequence中第二项开始，枚举sequence中每一项的first中的符号next_first
					if next_first != 'null' and next_first not in follow[sequence[i]]:#当第i + 1项的first不是空符号，就将其添加到第i项的follow集中
						follow[sequence[i]].append(next_first)

	stopFlag = False#设置一个标识循环添加终结符过程结束的flag
	while(not stopFlag):
		stopFlag = True#假定没有新添加的非终结符（即该过程将结束）
		for nonter in nonterminal:
			for sequence in grammar[nonter]:#sequence为nonter能推倒出的每一项序列构成的列表
				for i in xrange(0,len(sequence)-1):
					for each_follow in follow[nonter]:#枚举nonter的follow集中的每一项
						if each_follow not in follow[sequence[i]]:#nonter的follow集中的内容，应该存在于nonter能推导出的每一项的follow中
							follow[sequence[i]].append(each_follow)
							stopFlag = False#有新添加的符号，可能依据这项推导出新的follow集中的内容，应再次进行循环
					if 'null' not in first[sequence[i]]:#如果第i不能推导出null，那么follow集中的内容不能被第i + 1项包含，应停止循环
						break

	#print follow

def get_parsing_table():
	global first
	global follow
	global parsing_table
	for nonter in nonterminal:
		parsing_table[nonter] = {}
		for ter in terminal:
			parsing_table[nonter][ter] = -2#状态转换表每一位初始成-2（拿一个负数标记，-1有其他意义）

	for nonter in nonterminal:
		for i in xrange(0,len(grammar[nonter])):#枚举处理nonter推倒的第i条语法
			counter = 0#统计nonter能推倒出的项中包含多少的null
			for tag in grammar[nonter][i]:#tag为第i条语法中的每一个符号
				for each_first in first[tag]:
					if parsing_table[nonter][each_first] < 0:
						parsing_table[nonter][each_first] = i#将转换表赋值成第i条语法序号的i
				if 'null' not in first[tag]:
					break
				else:#若能推导出null，counter++
					count += 1
			if counter == len(grammar[nonter][i]):#如果nonter第i条语法的每一项都能推出null
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
	global token_attr
	global code
	stack = range(1000)
	stack[0] = 'program'
	tab = range(1000)
	tab[0] = 0
	leaf_tab['program'] = 0
	stack_top = 0
	token_pointer = 0

	analysis.delete(1.0, END)
	syntax_result = []
	token = []
	token_attr = []

	input_raw = code.get(1.0, END)
	input_str = input_raw.split("\n")
	input_lines = lexer_analysis(input_str)
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


root = Tk()#主窗口
code = ScrolledText(root, width=50, height=30, font=15)#代码显示窗口
analysis = ScrolledText(root, width=200, height=30, font=10)#语法分析树窗口

def interface():
	global root
	global code
	global analysis
	t = StringVar()
	t.set('Syntax by LiTianbao')
	label = Label(root, textvariable = t, font=15)
	Analysis = Button(root, text = 'Syntax  Analysis', command = syntax_analysis, font=15)
	load = Button(root, text = '    Load   code    ', command = fileloader, font=15)
	root.title("Syntax")
	#root.geometry('1500x800')
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
