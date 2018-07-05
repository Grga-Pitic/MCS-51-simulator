#coding:utf-8

import Tkinter
import tkMessageBox

mnemonics = ['MOV', 'MOVC', 'MOVX', 'PUSH', 'POP', 'XCH', 'XCHD', 'ADD', 'NOP',
             'ADDC', 'DA', 'SUBB', 'INC', 'DEC', 'MUL', 'DIV', 'ANL', 'ORL',
             'XRL', 'CLR', 'CPL', 'RL', 'RLC', 'RR', 'RRC', 'SWAP', 'SETB',
             'LJMP', 'AJMP', 'SJMP', 'JMP', 'JZ', 'JNZ', 'JC', 'JNC', 'JB',
             'JNB', 'JBC', 'DJNZ', 'CJNE', 'LCALL', 'ACALL', 'RET', 'RETI']

# считывает код на языке ассемблера из файла и возвращает его
def read_source(file_='listing.asm'):
    command_list = []
    f = open(file_, 'r')
    for line in f:
        line = ''.join(line.split('\n'))
        command_list.append(line.upper())
    f.close()
    
    return command_list

def save_code(code, file_='listing2.asm'):
    f = open(file_, 'w')
    for line in code:
        f.write(line + '\n')
    f.close()

def checking_for_mistakes(line):
    if line[0] == ':':
        return 0
    
    line = ''.join(line.split(','))
    line = line.split(' ')
    if line[-1] == '':
        line.pop()
    err = True  # err = True, если мнемоника неизвестна
    for m in mnemonics:
        if m == line[0]:
            err = False

    # если мнемоника неизвестна
    if err:
        return 1
    # если в первом операнде только одна скобка
    if len(line) == 3:
        if (line[1][0] == '[') ^ (line[1][-1] == ']'): # исключающее или
            return 2
    # если во втором операнде только одна скобка
    if len(line) == 3:
        if (line[2][0] == '[') ^ (line[2][-1] == ']'): # исключающее или
            return 3
    # ошибок нет
    return 0
        

def translate_const():
    pass

def run(source):
    source = source.upper().split('\n')
    good_source = []
    line_number = 0
    for line in range(len(source)):
        if source[line] != '':
            if (source[line][0] != ';'):
                source[line] = source[line].split(';')[0] # удаляет комментарий
                err = checking_for_mistakes(source[line])
                if err == 0:
                    print u"Строка №", line_number, u"готово"
                    good_source.append(source[line])
                elif err == 1:
                    tkMessageBox.showinfo("Ошибка ассемблирования",
                                          u"Строка №"+str(line_number)+u" неизвестная команда")
                    break
                elif err == 2:
                    tkMessageBox.showinfo("Ошибка ассемблирования",
                                          u"Строка №"+line_number+u" ошибка в первом операнде")
                    print 
                    break
                elif err == 3:
                    tkMessageBox.showinfo("Ошибка ассемблирования",
                                          u"Строка №"+line_number+u" ошибка во втором операнде")
                    break
                line_number += 1
    return good_source
        

#run('hui')
    
