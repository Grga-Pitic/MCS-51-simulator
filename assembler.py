#coding:utf-8

# считывает код на языке ассемблера из файла и возвращает его
def read_source(file_='listing.asm'):
    command_list = []
    f = open(file_, 'r')
    for line in f:
        line = ''.join(line.split('\n'))
        command_list.append(line.upper())
    f.close()
    
    return command_list
    
def save_hex_code(hex_code, file_='listing.hex'):
    f = open(file_, 'w')
    for line in hex_code:
        f.write(line + '\n')
    f.close()

def get_bit_address(op):
    bitname = op
    address = 0
    if bitname == 'C':
        address = 0xD0 + 7
    elif bitname == 'AC':
        address = 0xD0 + 6
    elif bitname == 'F0':
        address = 0xD0 + 5
    elif bitname == 'RS1':
        address = 0xD0 + 4
    elif bitname == 'RS0':
        address = 0xD0 + 3
    elif bitname == 'OV':
        address = 0xD0 + 2
#    elif bitname == '':
#        address = 0xD0 + 1
    elif bitname == 'P':
        address = 0xD0 + 0
    if address != 0:
        return str(hex(address))[2:]
    
    byte, bit = op.split('.')
    
    if byte == 'BIT':
        bit = int(bit, 16) % 0x80
    else:
        bit = int(bit) % 0x8
  #  print byte, bit
    if byte == 'ACC':
        address = 0xE0 + bit
    elif byte == 'B':
        address = 0xF0 + bit
    elif byte == 'PSW':
        address = 0xD0 + bit
    elif byte == 'IP':
        if bit >= 5:
            return -1
        address = 0xB8 + bit
    elif byte == 'P3':
        address = 0xB0 + bit
    elif byte == 'IE':
        if bit == 5 or bit == 6:
            return -1
        address = 0xA8 + bit
    elif byte == 'P2':
        address = 0xA0 + bit
    elif byte == 'SCON':
        address = 0x98 + bit
    elif byte == 'P1':
        address = 0x90 + bit
    elif byte == 'TCON':
        address = 0x88 + bit
    elif byte == 'P0':
        address = 0x80 + bit
    elif (byte[0] == '[') & (byte[-1] == ']'):
        byte = int(byte[1:-1], 16) - 0x20
        address = byte * 0x8 + bit
    elif byte == 'BIT':
        address = bit
        
    

        
    if address < 0x10:
        address = '0' + str(hex(address))[2:]
    else:
        address = str(hex(address))[2:]
    return address

def translate_comand_to_hex(comand, list_hex_comands,
                            list_len_comands, list_jumps):
    # убираем из команды запятую (для гибкости синтаксиса, да) и разбиваем
    # строчку на мнемонику и операнды
    comand = ''.join(comand.split(','))
    comand = comand.split(' ')

    
    
    if comand[0] == 'NOP':
        list_hex_comands.append('00')
        list_len_comands.append(1)
# ================КОМАНДЫ ПЕРЕСЫЛКИ ДАННЫХ==================
    elif comand[0] == 'MOV':                        # mov
        if comand[1] == 'A':                        # mov a
            if list(comand[2])[0] == 'R':           # mov a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0xE8 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
                                                    # mov a, []
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                                                    # mov a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('e5 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # mov a, [R0]
                    list_hex_comands.append('e6')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # mov a, [R1]
                    list_hex_comands.append('e7')
                    list_len_comands.append(1)
            elif comand[2][0:2] == '0X':        # mov a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('74 ' + operand)
                list_len_comands.append(2)
                
        elif comand[1][:1] == 'R':              # mov Rn
            n = int(comand[1][1:2]) % 8
         #   print comand
            if comand[2] == 'A':                # mov Rn, A
                code = str(hex(0xF8 + n))[2:4]
                list_hex_comands.append(code)
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                if comand[2][1:3] == '0X':        # mov Rn, [ad] с префиксом 0x
                    code = str(hex(0xA8 + n))[2:4]
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append(code + ' ' + operand)
                    list_len_comands.append(2)

            elif comand[2][0:2] == '0X':        # mov Rn, const с префиксом 0x
                code = str(hex(0x78 + n))[2:4]
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append(code + ' ' + operand)
                list_len_comands.append(2)

        elif comand[1] == '[R0]':        # mov [R0]
            if comand[2] == 'A':         # mov [R0], a
                list_hex_comands.append('f6')
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                if comand[2][1:3] == '0X':        # mov [R0], [ad] с префиксом 0x
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('a6 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][0:2] == '0X':        # mov [R0], const с префиксом 0x
                    code = str(hex(0x78 + n))[2:4]
                    operand = int(comand[2][2:], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('76 ' + operand)
                    list_len_comands.append(2)
                 
        elif comand[1] == '[R1]':        # mov [R1]
            if comand[2] == 'A':                # mov [R1], a
                list_hex_comands.append('f7')
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                if comand[2][1:3] == '0X':        # mov [R1], [ad] с префиксом 0x
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('a7 ' + operand)
                    list_len_comands.append(2)

                elif comand[2][0:2] == '0X':        # mov [R1], const с префиксом 0x
                    operand = int(comand[2][2:], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('77 ' + operand)
                    list_len_comands.append(2)
                
                                                # mov []
        elif (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            if comand[1][1:3] == '0X':        # mov [ad] с 0x
                ad = int(comand[1][1:-1], 16) % 0x100
                ad = str(hex(ad))[2:4]
            else:
                pass

            if len(ad) < 2:
                ad = '0' + ad

            if comand[2] == 'A':                # mov [ad], a
                list_hex_comands.append('f5 ' + ad)
                list_len_comands.append(2)
            elif list(comand[2])[0] == 'R':           # mov [ad], Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x88 + n
                code = str(hex(code))[2:4]
                list_hex_comands.append(code + ' ' + ad)
                list_len_comands.append(2)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                
                                                    # mov [add], [ads] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('85 '+ ad + ' ' + operand)
                    list_len_comands.append(3)

                elif comand[2][1:-1] == '[R0]':        # mov [ad], [[R0]]
                    list_hex_comands.append('86 ' + ad)
                    list_len_comands.append(2)
                    
                elif comand[2][1:-1] == '[R1]':        # mov [ad], [[R1]]
                    list_hex_comands.append('87 ' + ad)
                    list_len_comands.append(2)

            elif comand[2][0:2] == '0X':        # mov [ad], const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('75 ' + ad + ' ' + operand)
                list_len_comands.append(3) 

        elif comand[1] == 'DPTR':                   # mov DPTR, const
            if comand[2][0:2] == '0X':        # mov DPTR, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x10000
                operand = str(hex(operand))[2:]
                for i in range(len(operand), 4):
                    operand = '0' + operand
                list_hex_comands.append('90 ' + operand[0:2] + ' ' + operand[2:4])
                list_len_comands.append(3)
# ======================================================================
        elif comand[1] == 'C':          
                                               # mov c, bit
                ad = get_bit_address(comand[2])
                list_hex_comands.append('A2 ' + ad)
                list_len_comands.append(2)
        else:
            if comand[2] == 'C':
                ad = get_bit_address(comand[1])
                list_hex_comands.append('92 ' + ad)
                list_len_comands.append(2)
# ======================================================================
    elif comand[0] == 'MOVC':
        if comand[1] == 'A':                        # movc a
            if (comand[2] == '[[DPTR]+A]') | (comand[2] == '[A+[DPTR]]'):
                list_hex_comands.append('93')
                list_len_comands.append(1)
            if (comand[2] == '[PC+A]') | (comand[2] == '[A+PC]'):
                list_hex_comands.append('83')
                list_len_comands.append(1)  
    elif comand[0] == 'MOVX':
        if comand[1] == 'A':                        # movx a
            if comand[2] == '[R0]':                 # movx a, [R0]
                list_hex_comands.append('e2')
                list_len_comands.append(1)
            elif comand[2] == '[R1]':                 # movx a, [R1]
                list_hex_comands.append('e3')
                list_len_comands.append(1)
            elif comand[2] == '[DPTR]':                 # movx a, [DPTR]
                list_hex_comands.append('e0')
                list_len_comands.append(1)
        elif comand[1] == '[DPTR]':                 # movx [DPTR], a
            if comand[2] == 'A':
                list_hex_comands.append('f0')
                list_len_comands.append(1)

        elif comand[1] == '[R0]':                   # movx [R0], a
            if comand[2] == 'A':
                list_hex_comands.append('f2')
                list_len_comands.append(1)

        elif comand[1] == '[R1]':                   # movx [R1], a
            if comand[2] == 'A':
                list_hex_comands.append('f3')
                list_len_comands.append(1)
            
    elif comand[0] == 'PUSH':
        if (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            if comand[1][1:3] == '0X':        # PUSH [ad], const с префиксом 0x
                operand = int(comand[1][3:-1], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('c0 ' + operand)
                list_len_comands.append(2)
    elif comand[0] == 'POP':
        if (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            if comand[1][1:3] == '0X':        # pop [ad], const с префиксом 0x
                operand = int(comand[1][3:-1], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('d0 ' + operand)
                list_len_comands.append(2)
    elif comand[0] == 'XCH':
        if comand[1] == 'A':                        # xch a
            if list(comand[2])[0] == 'R':           # xch a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0xC8 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
                
            elif comand[2] == '[R0]':               # xch a, [R0]
                list_hex_comands.append('c6')
                list_len_comands.append(1)
            elif comand[2] == '[R1]':
                list_hex_comands.append('c7')
                list_len_comands.append(1)
                
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                                                    # xch a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('c5 ' + operand)
                    list_len_comands.append(2)
                
    elif comand[0] == 'XCHD':
        if comand[1] == 'A':
            if comand[2] == '[R0]':               # xchd a, [R0]
                list_hex_comands.append('d6')
                list_len_comands.append(1)
            elif comand[2] == '[R1]':
                list_hex_comands.append('d7')
                list_len_comands.append(1)
                
# ======================АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ===============================
    elif comand[0] == 'ADD':
        if comand[1] == 'A':                        # add a
            if list(comand[2])[0] == 'R':           # add a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x28 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # add a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('25 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # add a, [R0]
                    list_hex_comands.append('26')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # add a, [R1]
                    list_hex_comands.append('27')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # add a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('24 ' + operand)
                list_len_comands.append(2)
    elif comand[0] == 'ADDC':
        if comand[1] == 'A':                        # ADDC a
            if list(comand[2])[0] == 'R':           # ADDC a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x38 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # ADDC a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('35 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # ADDC a, [R0]
                    list_hex_comands.append('36')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # ADDC a, [R1]
                    list_hex_comands.append('37')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # ADDC a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('34 ' + operand)
                list_len_comands.append(2)
                                                # DA a
    elif comand[0] == 'DA':
        if comand[1] == 'A':
            list_hex_comands.append('d4')
            list_len_comands.append(1)
    elif comand[0] == 'SUBB':
        if comand[1] == 'A':                        # subb a
            if list(comand[2])[0] == 'R':           # subb a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x98 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # subb a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('95 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # subb a, [R0]
                    list_hex_comands.append('96')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # subb a, [R1]
                    list_hex_comands.append('97')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # subb a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('94 ' + operand)
                list_len_comands.append(2)
    elif comand[0] == 'INC':
                                                # inc a
        if comand[1] == 'A':
            list_hex_comands.append('04')
            list_len_comands.append(1)
                                                # inc Rn
        if comand[1] == 'R':
            n = int(list(comand[1])[1]) % 8
            code = 0x08 + n
            list_hex_comands.append(str(hex(code))[2:4])
            list_len_comands.append(1)
                                                # inc ad с префиксом 0x
        if (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            if comand[1][1:3] == '0X':
                    operand = int(comand[1][1:-1], 16) % 0x100   # чекнуть надо бы
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('05 ' + operand)
                    list_len_comands.append(2)
                                                # inc DPTR
        if comand[1] == 'DPTR':
            list_hex_comands.append('A3')
            list_len_comands.append(1)
                                                # inc [[R1]]
        if comand[1] == '[[R0]]':
            list_hex_comands.append('06')
            list_len_comands.append(1)
        if comand[1] == '[[R1]]':               # inc [[R1]]
            list_hex_comands.append('07')
            list_len_comands.append(1)
    elif comand[0] == 'DEC':
                                                # dec a
        if comand[1] == 'A':
            list_hex_comands.append('14')
            list_len_comands.append(1)
                                                # dec Rn
        if comand[1] == 'R':
            n = int(list(comand[1])[1]) % 8
            code = 0x18 + n
            list_hex_comands.append(str(hex(code))[2:4])
            list_len_comands.append(1)
                                                # dec ad с префиксом 0x
        if (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            if comand[1][1:3] == '0X':
                    operand = int(comand[1][1:-1], 16) % 0x100   # чекнуть надо бы
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('15 ' + operand)
                    list_len_comands.append(2)
                                                # dec [[R0]]
        if comand[1] == '[[R0]]':
            list_hex_comands.append('16')
            list_len_comands.append(1)
        if comand[1] == '[[R1]]':               # dec [[R1]]
            list_hex_comands.append('17')
            list_len_comands.append(1)
            
    elif comand[0] == 'MUL':
        if comand[1] == 'AB':
            list_hex_comands.append('A4')
            list_len_comands.append(1)
    elif comand[0] == 'DIV':
        if comand[1] == 'AB':
            list_hex_comands.append('84')
            list_len_comands.append(1)
# ======================ЛОГИЧЕСКИЕ ОПЕРАЦИИ========================
    elif comand[0] == 'ANL':
        if comand[1] == 'A':                        # anl a
            if list(comand[2])[0] == 'R':           # anl a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x58 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # anl a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('55 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # anl a, [R0]
                    list_hex_comands.append('56')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # anl a, [R1]
                    list_hex_comands.append('57')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # anl a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('54 ' + operand)
                list_len_comands.append(2)
        elif (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
                                                # anl [ad], a
            if comand[1][1:3] == '0X':
                if comand[2] == 'A':
                    operand = int(comand[1][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('52 ' + operand)
                    list_len_comands.append(2)
                                                # anl [ad], const
                if comand[2][0:2] == '0X':
                    operand1 = int(comand[1][1:-1], 16) % 0x100
                    operand1 = str(hex(operand1))[2:4]
                    operand2 = int(comand[2], 16) % 0x100
                    operand2 = str(hex(operand2))[2:4]
                    if len(operand1) < 2:
                        operand1 = '0' + operand1
                    if len(operand2) < 2:
                        operand2 = '0' + operand2
                    list_hex_comands.append('53 ' + operand1 + ' ' + operand2)
                    list_len_comands.append(3)
# ========================================================================
        elif comand[1] == 'C':                  # anl c, /bit
            if comand[2][0] == '/':
                ad = get_bit_address(comand[2][1:])
                list_hex_comands.append('B0 ' + ad)
                list_len_comands.append(2)
            else:                               # anl c, bit
                ad = get_bit_address(comand[2])
                list_hex_comands.append('82 ' + ad)
                list_len_comands.append(2)
# ========================================================================
            
            
                    
    elif comand[0] == 'ORL':
        if comand[1] == 'A':                        # orl a
            if list(comand[2])[0] == 'R':           # orl a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x48 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # orl a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('45 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # orl a, [R0]
                    list_hex_comands.append('46')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # orl a, [R1]
                    list_hex_comands.append('47')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # orl a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('44 ' + operand)
                list_len_comands.append(2)
        elif (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
                                                # orl [ad], a
            if comand[1][1:3] == '0X':
                if comand[2] == 'A':
                    operand = int(comand[1][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('42 ' + operand)
                    list_len_comands.append(2)
                                                # orl [ad], const
                if comand[2][0:2] == '0X':
                    operand1 = int(comand[1][1:-1], 16) % 0x100
                    operand1 = str(hex(operand1))[2:4]
                    operand2 = int(comand[2], 16) % 0x100
                    operand2 = str(hex(operand2))[2:4]
                    if len(operand1) < 2:
                        operand1 = '0' + operand1
                    if len(operand2) < 2:
                        operand2 = '0' + operand2
                    list_hex_comands.append('43 ' + operand1 + ' ' + operand2)
                    list_len_comands.append(3)
# ========================================================================
        elif comand[1] == 'C':                  # orl c, /bit
            if comand[2][0] == '/':
                ad = get_bit_address(comand[2][1:])
                list_hex_comands.append('A0 ' + ad)
                list_len_comands.append(2)
            else:                               # orl c, bit
                ad = get_bit_address(comand[2])
                list_hex_comands.append('72 ' + ad)
                list_len_comands.append(2)
# ========================================================================
    elif comand[0] == 'XRL':
        if comand[1] == 'A':                        # xrl a
            if list(comand[2])[0] == 'R':           # xrl a, Rn
                n = int(list(comand[2])[1]) % 8
                code = 0x68 + n
                list_hex_comands.append(str(hex(code))[2:4])
                list_len_comands.append(1)
            elif (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):

                                                    # xrl a, [ad] с префиксом 0x
                if comand[2][1:3] == '0X':
                    operand = int(comand[2][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('65 ' + operand)
                    list_len_comands.append(2)
                elif comand[2][1:-1] == 'R0':        # xrl a, [R0]
                    list_hex_comands.append('66')
                    list_len_comands.append(1)
                    
                elif comand[2][1:-1] == 'R1':        # xrl a, [R1]
                    list_hex_comands.append('67')
                    list_len_comands.append(1)
                    
            elif comand[2][0:2] == '0X':        # xrl a, const с префиксом 0x
                operand = int(comand[2][2:], 16) % 0x100
                operand = str(hex(operand))[2:4]
                if len(operand) < 2:
                    operand = '0' + operand
                list_hex_comands.append('64 ' + operand)
                list_len_comands.append(2)
        elif (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
                                                # xrl [ad], a
            if comand[1][1:3] == '0X':
                if comand[2] == 'A':
                    operand = int(comand[1][1:-1], 16) % 0x100
                    operand = str(hex(operand))[2:4]
                    if len(operand) < 2:
                        operand = '0' + operand
                    list_hex_comands.append('62 ' + operand)
                    list_len_comands.append(2)
                                                # xrl [ad], const
                if comand[2][0:2] == '0X':
                    operand1 = int(comand[1][1:-1], 16) % 0x100
                    operand1 = str(hex(operand1))[2:4]
                    operand2 = int(comand[2], 16) % 0x100
                    operand2 = str(hex(operand2))[2:4]
                    if len(operand1) < 2:
                        operand1 = '0' + operand1
                    if len(operand2) < 2:
                        operand2 = '0' + operand2
                    list_hex_comands.append('63 ' + operand1 + ' ' + operand2)
                    list_len_comands.append(3)
    elif comand[0] == 'CLR':                    # clr a
        if comand[1] == 'A':
            list_hex_comands.append('E4')
            list_len_comands.append(1)
# ========================================================================
        elif comand[1] == 'C':                  # clr c
            list_hex_comands.append('C3')
            list_len_comands.append(1)
                                                # clr bit
        else:
            ad = get_bit_address(comand[1])
            list_hex_comands.append('C2 ' + ad)
            list_len_comands.append(2)
# ========================================================================
    elif comand[0] == 'CPL':                    # cpl a
        if comand[1] == 'A':   
            list_hex_comands.append('F4')
            list_len_comands.append(1)
# ========================================================================
        elif comand[1] == 'C':                  # clr c
            list_hex_comands.append('B3')
            list_len_comands.append(1)
                                                # clr bit
        else:
            ad = get_bit_address(comand[1])
            list_hex_comands.append('B2 ' + ad)
            list_len_comands.append(2)
# ========================================================================
    elif comand[0] == 'RL':                    # rl a
        if comand[1] == 'A':
            list_hex_comands.append('23')
            list_len_comands.append(1)
    elif comand[0] == 'RLC':                    # rlc a
        if comand[1] == 'A':   
            list_hex_comands.append('33')
            list_len_comands.append(1)
    elif comand[0] == 'RR':                    # rr a
        if comand[1] == 'A':
            list_hex_comands.append('03')
            list_len_comands.append(1)
    elif comand[0] == 'RRC':                    # rrc a
        if comand[1] == 'A':   
            list_hex_comands.append('13')
            list_len_comands.append(1)
    elif comand[0] == 'SWAP':                    # rrc a
        if comand[1] == 'A':   
            list_hex_comands.append('C4')
            list_len_comands.append(1)
# ======================ОПЕРАЦИИ НАД БИТАМИ========================
    
    elif comand[0] == 'SETB':                    # CLR c
        if comand[1] == 'C':   
            list_hex_comands.append('D3')
            list_len_comands.append(1)
        else:
            
            ad = get_bit_address(comand[1])
            list_hex_comands.append('D2 ' + ad)
            list_len_comands.append(2)

# ======================КОМАНДЫ ПЕРЕДАЧИ УПРАВЛЕНИЯ========================

    elif comand[0] == 'LJMP':                    # LJMP ad16
        operand = str(int(comand[1], 16) % 0x10000)
        list_hex_comands.append('02 ' + operand)
        list_len_comands.append(3)
        list_jumps.append(len(list_hex_comands))

    elif comand[0] == 'AJMP':                    # AJMP ad11 TODO
        operand = str(int(comand[1], 16) % 0x800)
        list_hex_comands.append('01 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'SJMP':                    # SJMP rel 
        operand = str(int(comand[1], 16) % 0x100)
        list_hex_comands.append('80 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JMP':                    # JMP [A+DPTR]
        if comand[1] == '[A+DPTR]':
            list_hex_comands.append('73')
            list_len_comands.append(1)
    elif comand[0] == 'JZ':                    # JZ rel 
        operand = str(int(comand[1], 16) % 0x100)
        list_hex_comands.append('60 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JNZ':                    # JNZ rel 
        operand = str(int(comand[1], 16) % 0x100)
        list_hex_comands.append('70 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JC':                    # JC rel 
        operand = str(int(comand[1], 16) % 0x100)
        list_hex_comands.append('40 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JNC':                   # JNC rel 
        operand = str(int(comand[1], 16) % 0x100)
        list_hex_comands.append('50 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JB':                    # JB bit, rel 
        operand = str(int(comand[2], 16) % 0x100)
        ad = get_bit_address(comand[1])
        list_hex_comands.append('20 ' + ad + ' ' + operand)
        list_len_comands.append(3)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JNB':                    # JNB bit, rel 
        operand = str(int(comand[2], 16) % 0x100)
        ad = get_bit_address(comand[1])
        list_hex_comands.append('30 ' + ad + ' ' + operand)
        list_len_comands.append(3)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'JBC':                    # JBC rel
        operand = str(int(comand[1], 16) % 0x100)
        ad = get_bit_address(comand[1])
        list_hex_comands.append('10 ' + ad + ' ' + operand)
        list_len_comands.append(3)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'DJNZ':                    # DJNZ Rn rel
        operand = str(int(comand[2], 16) % 0x100)
        if list(comand[1])[0] == 'R':           
            n = int(list(comand[1])[1]) % 8
            code = 0xD8 + n
            list_hex_comands.append(str(hex(code))[2:4] + ' ' + operand)
            list_len_comands.append(2)
            list_jumps.append(len(list_hex_comands))
                                                # DJNZ [ad] rel
        elif (list(comand[1])[0] == '[') & (list(comand[1])[-1] == ']'):
            ad = int(comand[1][1:-1], 16) % 0x100
            ad = str(hex(ad))[2:4]
            if len(ad) < 2:
                ad = '0' + ad
            list_hex_comands.append('D5 ' + ad + ' ' + operand)
            list_len_comands.append(3)
            list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'CJNE':                   # CJNE
        operand = str(int(comand[3], 16) % 0x100)
                                                # CJNE A
        if comand[1] == 'A':
            
                                                # CJNE A, ad, rel
            if (list(comand[2])[0] == '[') & (list(comand[2])[-1] == ']'):
                ad = int(comand[2][1:-1], 16) % 0x100
                ad = str(hex(ad))[2:4]
                if len(ad) < 2:
                    ad = '0' + ad
                list_hex_comands.append('B5 ' + ad + ' ' + operand)
                list_len_comands.append(3)
                list_jumps.append(len(list_hex_comands))
                                                # CJNE A, const, rel
            elif comand[2][0:2] == '0X':
                operand1 = int(comand[2][2:], 16) % 0x100
                operand1 = str(hex(operand1))[2:4]
                if len(operand1) < 2:
                    operand1 = '0' + operand1
                list_hex_comands.append('B4 ' + operand1 + ' ' + operand)
                list_len_comands.append(3)
                list_jumps.append(len(list_hex_comands))
                                                # CJNE Rn, const, rel
        elif list(comand[1])[0] == 'R':
            n = int(list(comand[1])[1]) % 8
            code = 0xB8 + n
            if comand[2][0:2] == '0X':
                operand1 = int(comand[2][2:], 16) % 0x100
                operand1 = str(hex(operand1))[2:4]
                if len(operand1) < 2:
                    operand1 = '0' + operand1
                
                list_hex_comands.append(str(hex(code))[2:4] + ' ' +
                                        operand1 + ' ' + operand)
                list_len_comands.append(2)
                list_jumps.append(len(list_hex_comands))
                                                # CJNE [R0], const, rel
        elif comand[1] == '[R0]':
            operand1 = int(comand[2][2:], 16) % 0x100
            operand1 = str(hex(operand1))[2:4]
            if len(operand1) < 2:
                operand1 = '0' + operand1
            list_hex_comands.append('B6 ' + operand1 + ' ' + operand)
            list_len_comands.append(3)
            list_jumps.append(len(list_hex_comands))
                                                # CJNE [R1], const, rel
        elif comand[1] == '[R1]':
            operand1 = int(comand[2][2:], 16) % 0x100
            operand1 = str(hex(operand1))[2:4]
            if len(operand1) < 2:
                operand1 = '0' + operand1
            list_hex_comands.append('B7 ' + operand1 + ' ' + operand)
            list_len_comands.append(3)
            list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'LCALL':                   # lcall ad16
        operand = str(int(comand[1], 16) % 0x10000)
        list_hex_comands.append('12 ' + operand)
        list_len_comands.append(3)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'ACALL':                   # acall ad11 TODO
        operand = str(int(comand[1], 16) % 0x800)
        list_hex_comands.append('11 ' + operand)
        list_len_comands.append(2)
        list_jumps.append(len(list_hex_comands))
    elif comand[0] == 'RET':
        list_hex_comands.append('22')
        list_len_comands.append(1)
    elif comand[0] == 'RETI':
        list_hex_comands.append('32')
        list_len_comands.append(1)
    
        

 #   print list_hex_comands
    return comand

def translate_jumps(list_len_comands, list_hex_comands, list_jumps):
    ad16 = ['02', '12']
    ad11 = ['11', '01']
    ad8 = ['80', '60', '70', '40', '50', '20', '30', '10', 'D5', 'B5', 'B6',
           'B7', 'B4', 'B8', 'B9', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF']  # TODO

    for j in list_jumps:
        good_comand = list_hex_comands[j - 1].split(' ')
        ad = int(good_comand[-1])               # адрес команды (не байта)
        good_comand[-1] = hex(list_len_comands[ad])[2:]
  #      print good_comand
        if good_comand[0] in ad16:
            while len(good_comand[-1]) < 4:
                good_comand[-1] = '0' + good_comand[-1]
            good_comand[-1] = good_comand[-1][:2] + ' ' + good_comand[-1][2:]
            
        elif good_comand[0] in ad11:          # TODO переполнение 11 бит
            good_comand[0] = int(good_comand[0], 16)
            good_comand[-1] = int(good_comand[-1])
            a10 = (good_comand[-1] & 0x400)
            a9 = (good_comand[-1] & 0x200)
            a8 = (good_comand[-1] & 0x100)
            good_comand[-1] = hex(good_comand[-1] & 0xff)[2:]
            good_comand[0] = hex(good_comand[0] | a10 | a9 | a8)[2:]
            if len(good_comand[-1]) < 2:
                good_comand[-1] = '0' + good_comand[-1]
            if len(good_comand[0]) < 2:
                good_comand[0] = '0' + good_comand[0]
        if good_comand[0] in ad8:
            while len(good_comand[-1]) < 2:
                code = list_len_comands[ad] - list_len_comands[j]
                code = code % 256
                if code < 0:
                    code += 256
                code = hex(code)[2:]
                if len(code) < 2:
                    code = '0' + code
                good_comand[-1] = code
                
        good_comand = ' '.join(good_comand)
        list_hex_comands[j - 1] = good_comand
      #  print good_comand
    return list_hex_comands

def comand_address(list_len_comands):
    for i in range(len(list_len_comands) - 1):
        list_len_comands[i + 1] = list_len_comands[i + 1] + list_len_comands[i]
    return [0] + list_len_comands                       # костыль
    
def run(list_asm_comands):
 #   list_asm_comands = read_source()

    # длина команды в байтах
    list_len_comands = []
    # шестнадцатеричный код команды
    list_hex_comands = []
    # список переходов
    list_jumps = []
    for cmd in list_asm_comands:
     #   print cmd
        translate_comand_to_hex(cmd, list_hex_comands,
                                list_len_comands, list_jumps)
    list_len_comands = comand_address(list_len_comands)
    list_hex_comands = translate_jumps(list_len_comands, list_hex_comands,
                                       list_jumps)
    list_hex_comands = ' '.join(list_hex_comands).lower().split(' ')
 #   print list_hex_comands
    if list_hex_comands == ['']:
        return [0]
    for i in range(len(list_hex_comands)):
        list_hex_comands[i] = int(list_hex_comands[i], 16)
  #      print list_hex_comands[i]
 #   print list_hex_comands
    return list_hex_comands
 #   save_hex_code(list_hex_comands)
 

#test()
