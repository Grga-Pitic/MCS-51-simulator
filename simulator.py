# -*- coding: utf-8 -*-
from string import zfill

RAM = []
program_memory = []

ACC = 0xE0
B = 0xF0
PSW = 0xD0
SP = 0x81
DPTR = 0x83
DPH = 0x83
DPL = 0x82
P0 = 0x80
P1 = 0x90
P2 = 0xA0
P3 = 0xB0
IP = 0xB8
IE = 0xA8
TMOD = 0x89
TCON = 0x88
TH0 = 0x8C
TL0 = 0x8A
TH1 = 0x8D
TL1 = 0x8B
SCON = 0x98
SBUF = 0x99
PCON = 0x87


POH = []


PC = 0
cycle = 0

reg_bank = 0

def init_8051():
    init_POH()
    init_RAM()
    init_program_memory()
    global reg_bank
    global PC
    global cycle
    PC = 0
    cycle = 0
    reg_bank = 0
    
def init_POH():
    global POH
    p = []
    R0 = []
    R1 = []
    R2 = []
    R3 = []
    for i in range(0, 8):
        R0.append(i)
        R1.append(i + 8)
        R2.append(i + 16)
        R3.append(i + 24)
    p.append(R0)
    p.append(R1)
    p.append(R2)
    p.append(R3)
    POH = p
        

def init_RAM():
    global RAM
    r = []
    for i in range(256):
        r.append(0)
    RAM = r
    RAM[SP] = 0x7
    RAM[P0] = 0xFF
    RAM[P1] = 0xFF
    RAM[P2] = 0xFF
    RAM[P3] = 0xFF

def init_program_memory():
    global program_memory
    p = []
    for i in range(4096):
        p.append(0)
    program_memory = p

# Загрузка кодов команд в память программ
def load_hex_to_pm(hex_listing):
    global program_memory
    global PC
    PC = 0
    program_memory = []
    init_program_memory()
    i = 0
    while i < len(hex_listing):
        program_memory[i] = hex_listing[i]
        i += 1

def get_bit_address(bit_address):
    bit = bit_address % 8
    if bit_address < 0x80:
        byte = 0x20 + bit_address // 8
        
    elif (bit_address >= 0x80) & (bit_address < 0x88):
        byte = P0
    elif (bit_address >= 0x88) & (bit_address < 0x90):
        byte = TCON
    elif (bit_address >= 0x90) & (bit_address < 0x97):
        byte = P1
    elif (bit_address >= 0x97) & (bit_address < 0xA0):
        byte = SCON
    elif (bit_address >= 0xA0) & (bit_address < 0xA8):
        byte = P2
    elif (bit_address >= 0xA8) & (bit_address < 0xB0):
        if (bit == 0x5) | (bit == 0x6):
            return 0
        byte = IE
    elif (bit_address >= 0xB0) & (bit_address < 0xB8):
        byte = P3
    elif (bit_address >= 0xB8) & (bit_address < 0xBD):
        byte = IP
    elif (bit_address >= 0xD0) & (bit_address < 0xD8):
        byte = PSW
    elif (bit_address >= 0xE0) & (bit_address < 0xE8):
        byte = ACC
    elif (bit_address >= 0xF0) & (bit_address < 0xF8):
        byte = B
    else:
        return 0
        
    return byte, bit
        
    pass

# возвращает n-й бит принятого байта
def get_bit(byte, n=0):
    return (byte >> n) & 1

def reverse_byte(byte):
    new_byte = 0
    for i in range(8):
        new_bit = get_bit(byte, i)
        if new_bit:
            new_bit = 0
        else:
            new_bit = 1
        new_byte += new_bit << i
    return new_byte


def set_bit(byte, n=0, bit=0):
    new_byte = 1
    if bit:
        new_byte = new_byte << n
        return new_byte | byte
    else:
        new_byte = new_byte << n
        new_byte = reverse_byte(new_byte)
        return new_byte & byte

# считывает машинный код из файла и возвращает его
def read_hex(file_='listing.hex'):
    hex_simbols = list('0123456789abcdef')
    f = open(file_, 'r')
    lines = list(f.read().lower())
    f.close()

    # извлекаем из шестнадцатеричных кодов только цифры 16-ричной
    # системы счисления (типа шоб можно было там писать в свободном стиле)
    lines_clr = []
    for i in range(len(lines)):
        if lines[i] in hex_simbols:
            lines_clr.append(lines[i])
    
    if (len(lines_clr) % 2) == 1:
        lines_clr.append('0')

    list_bytes = []
    for i in range(0, len(lines_clr), 2): 
        i = lines_clr[i]+lines_clr[i + 1]
        list_bytes.append(int(i, 16))
    return list_bytes


# инкрементирует счетчик команд
# нужно для фиксирования времени выполнения кода
# и для организации работы таймеров (в дальнейшем)
def inc_PC():
    global PC
    PC += 1

def inc_cycle():
    global cycle
    cycle += 1

def read_listing(file_='listing.asm'):
    f = open(file_, 'r')
    lines = f.read()
    f.close()
    return lines

def print_program_memory():
    print "===PROGRAM MEMORY==="
    for i in range(0, 4096, 16):
        print program_memory[i:i+16]

def print_RAM():
    global RAM
    print "===RAM===="
    for i in range(0, 128, 16):
        print RAM[i:i+16]

def print_SFR():
    print 'ACC =', hex(RAM[ACC])
    print 'B =', hex(RAM[B])
    print 'PSW =', hex(RAM[PSW]), bin(RAM[PSW])
    print 'SP =', hex(RAM[SP])
    print 'DPTR =', hex(RAM[DPTR])
    print 'P0 =', hex(RAM[P0])
    print 'P1 =', hex(RAM[P1])
    print 'P2 =', hex(RAM[P2])
    print 'P3 =', hex(RAM[P3])
    print 'IP =', hex(RAM[IP])
    print 'IE =', hex(RAM[IE])
    print 'TMOD =', hex(RAM[TMOD])
    print 'TCON =', hex(RAM[TCON])
    print 'TH0 =', hex(RAM[TH0])
    print 'TL0 =', hex(RAM[TL0])
    print 'TH1 =', hex(RAM[TH1])
    print 'TL1 =', hex(RAM[TL1])
    print 'SCON =', hex(RAM[SCON])
    print 'SBUF =', hex(RAM[SBUF])
    print 'PCON =', hex(RAM[PCON])

def step():
    global RAM
    global program_memory
    global PC
    global SP
    global POH

    if PC >= 0x1000:
        return

    
    reg_bank = 0
    if program_memory[PC] == 0x0:               # nop
        inc_cycle()
        PC += 1
    # ==============КОМАНДЫ ПЕРЕСЫЛКИ ДАННЫХ =================
    elif (program_memory[PC] & 0xf8) == 0xE8:   # (A) <- (Rn) 
        n = program_memory[PC] & 0x7
        RAM[ACC] = RAM[POH[reg_bank][n]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xE5:            # (A) <- (ad)
        RAM[ACC] = RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xE6:            # (A) <- ((@R0))
        RAM[ACC] = RAM[RAM[POH[reg_bank][0]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xE7:            # (A) <- ((@R1))
        RAM[ACC] = RAM[RAM[POH[reg_bank][1]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x74:            # (A) <- #d
        RAM[ACC] = program_memory[PC + 1]
        inc_cycle()
        PC += 2
    elif (program_memory[PC]&0xF8) == 0xF8:     # (Rn) <- (A)
        n = program_memory[PC] & 0x7
        RAM[POH[reg_bank][n]] = RAM[ACC]
        inc_cycle()
        PC += 1
    elif (program_memory[PC]&0xF8) == 0xA8:     # (Rn) <- (ad)
        n = program_memory[PC] & 0x7
        RAM[POH[reg_bank][n]] = RAM[program_memory[PC + 1]]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif (program_memory[PC]&0xF8) == 0x78:     # (Rn) <- #d
        n = program_memory[PC] & 0x7
        RAM[POH[reg_bank][n]] = program_memory[PC + 1]
        inc_cycle()
        PC += 2
    elif (program_memory[PC]&0xF8) == 0x88:     # (ad) <- (Rn)
        n = program_memory[PC] & 0x7
        RAM[program_memory[PC + 1]] = RAM[POH[reg_bank][n]]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xF5:            # (ad) <- (A)
        RAM[program_memory[PC + 1]] = RAM[ACC]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x85:            # (add) <- (ads)
        RAM[program_memory[PC + 1]] = RAM[program_memory[PC + 2]]
        inc_cycle()
        inc_cycle()
        PC += 3
    elif program_memory[PC] == 0x86:            # (ad) <- ((R0))
        RAM[program_memory[PC + 1]] = RAM[RAM[POH[reg_bank][0]]] 
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x87:            # (ad) <- ((R1))
        RAM[program_memory[PC + 1]] = RAM[RAM[POH[reg_bank][1]]] 
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x75:            # (ad) <- #d
        RAM[program_memory[PC + 1]] = program_memory[PC + 2]
        inc_cycle()
        inc_cycle()
        PC += 3
    elif program_memory[PC] == 0xF6:            # ((R0)) <- (A)
        RAM[RAM[POH[reg_bank][0]]] = RAM[ACC]   
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xF7:            # ((R1)) <- (A)
        RAM[RAM[POH[reg_bank][1]]] = RAM[ACC]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x66:            # ((R0)) <- (ad)
        RAM[RAM[POH[reg_bank][0]]] = RAM[program_memory[PC + 1]]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x67:            # ((R1)) <- (ad)
        RAM[RAM[POH[reg_bank][1]]] = RAM[program_memory[PC + 1]]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x76:            # ((R0)) <- #d
        RAM[RAM[POH[reg_bank][0]]] = program_memory[PC + 1]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x77:            # ((R1)) <- #d
        RAM[RAM[POH[reg_bank][1]]] = program_memory[PC + 1]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x90:            # (DPTR) <- #d16
        d = program_memory[PC + 1] << 4
        d += program_memory[PC + 2]
        RAM[DPTR] = d
        inc_cycle()
        inc_cycle()
        PC += 3
    elif program_memory[PC] == 0x93:            # (A) <- ((A)+(DPTR))
       # print RAM[ACC], RAM[DPTR]
        RAM[ACC] = program_memory[RAM[DPTR] + RAM[ACC]]
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x83:            # (PC) <- (PC)+1
                                                # (A) <- ((A)+(PC))
        RAM[ACC] = program_memory[PC + RAM[ACC]]
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xE2:            # (A) <- ((R0))
                                                # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xE3:            # (A) <- ((R1))
                                                # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xE0:            # (A) <- ((DPTR))
                                                # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xF2:            # ((R0)) <- (A) 
        #RAM[RAM[POH[reg_bank][0]]]             # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xF3:            # ((R1)) <- (A)
                                                # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xF0:            # (((DPTR)) <- (A)
                                                # ВПД пока не реализовано
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xC0:            # (SP) <- (SP)+1
                                                # ((SP)) <- (ad)
        RAM[SP] += 1
        RAM[RAM[SP]] = RAM[program_memory[PC + 1]]
        inc_cycle()
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xD0:            # (ad) <- ((SP))
                                                # (SP) <- (SP)-1
        RAM[program_memory[PC + 1]] = RAM[RAM[SP]]
        RAM[SP] -= 1
        inc_cycle()
        inc_cycle()
        PC += 2
    elif (program_memory[PC]&0xF8) == 0xC8:     # (A) <-> (Rn)
        n = program_memory[PC] & 0x7
        RAM[ACC], RAM[POH[reg_bank][n]] = RAM[POH[reg_bank][n]], RAM[ACC]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xC5:            # (A) <-> (ad)
        RAM[ACC], RAM[program_memory[PC + 1]] = RAM[program_memory[PC + 1]], RAM[ACC]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xC6:            # (A) <-> (R0)
        RAM[ACC], RAM[RAM[POH[reg_bank][0]]] = RAM[RAM[POH[reg_bank][0]]], RAM[ACC]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xC7:            # (A) <-> (R1)
        RAM[ACC], RAM[RAM[POH[reg_bank][1]]] = RAM[RAM[POH[reg_bank][1]]], RAM[ACC]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xD6:            # (A0..3) <->((R0)0..3)
        ACC_lower_tetrad = RAM[ACC] & 0xF
        RAM[ACC] = RAM[ACC] & 0xF0
        reg_lower_tetrad = RAM[RAM[POH[reg_bank][0]]] & 0xF
        RAM[RAM[POH[reg_bank][0]]] = RAM[RAM[POH[reg_bank][0]]] & 0xF0
        RAM[ACC] += reg_lower_tetrad
        RAM[RAM[POH[reg_bank][0]]] += ACC_lower_tetrad
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xD7:            # (A0..3) <->((R1)0..3)
        ACC_lower_tetrad = RAM[ACC] & 0xF
        RAM[ACC] = RAM[ACC] & 0xF0
        reg_lower_tetrad = RAM[RAM[POH[reg_bank][1]]] & 0xF
        RAM[RAM[POH[reg_bank][1]]] = RAM[RAM[POH[reg_bank][1]]] & 0xF0
        RAM[ACC] += reg_lower_tetrad
        RAM[RAM[POH[reg_bank][1]]] += ACC_lower_tetrad
        inc_cycle()
        PC += 1
    #===============КОМАНДЫ АРИФМЕТИЧЕСКИХ ОПЕРАЦИЙ==============
    elif (program_memory[PC] & 0xf8) == 0x28:    # (A) < (A)+(Rn)
        n = program_memory[PC] & 0x7
        RAM[ACC] += RAM[POH[reg_bank][n]]
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x25:            # (A) <- (A)+(ad)
        RAM[ACC] += RAM[program_memory[PC + 1]]
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x26:            # (A) <- (A)+((R0))
        RAM[ACC] += RAM[RAM[POH[reg_bank][0]]]
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x27:            # (A) <- (A)+((R1))
        RAM[ACC] += RAM[RAM[POH[reg_bank][1]]]
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x24:            # (A) <- (A)+#d
        RAM[ACC] += program_memory[PC + 1]
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif (program_memory[PC] & 0xf8) == 0x38:   # (A) <- (A)+(Rn)+(C)
        previous_ACC = RAM[ACC]
        n = program_memory[PC] & 0x7
        RAM[ACC] += RAM[POH[reg_bank][n]] + get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x35:            # (A) <- (A)+(ad)+(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] += RAM[program_memory[PC + 1]] + get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x36:            # (A) <- (A)+((R0))+(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] += RAM[RAM[POH[reg_bank][0]]] + get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x37:            # (A) <- (A)+((R1))+(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] += RAM[RAM[POH[reg_bank][1]]] + get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x34:            # (A) <- (A)+#d+(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] += program_memory[PC + 1] + get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xD4:            # десятичная коррекция аккума
                                                # потом доделаю
        C = 0
        A03 = RAM[ACC] & 0xF
        A47 = (RAM[ACC] & 0xF0) >> 4
        if (A03 > 9) | (get_bit(RAM[PSW], 6) == 1):
            if (A03 + 6) > 16:
                C = 1
                A03 -= 10
        if (A47 > 9) | (get_bit(RAM[PSW], 7) == 1):
            if (A47 + 6) > 16:
                A47 -= 10 - C
                RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        RAM[ACC] = (A47 << 4) + A03
        inc_cycle()
        PC += 1
    elif (program_memory[PC] & 0xf8) == 0x98:   # (A) <- (A)-(Rn)-(C)
        previous_ACC = RAM[ACC]
        n = program_memory[PC] & 0x7
        RAM[ACC] -= RAM[POH[reg_bank][n]] - get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x95:            # (A) <- (A)-(ad)-(C)
        previous_ACC = RAM[ACC]
  #      print RAM[ACC], RAM[program_memory[PC + 1]], get_bit(RAM[PSW], 8)
        RAM[ACC] -= RAM[program_memory[PC + 1]] - get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x96:            # (A) <- (A)-((R0))-(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] -= RAM[RAM[POH[reg_bank][0]]] - get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x97:            # (A) <- (A)-((R1))-(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] -= RAM[RAM[POH[reg_bank][1]]] - get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x94:            # (A) <- (A)-#d-(C)
        previous_ACC = RAM[ACC]
        RAM[ACC] -= program_memory[PC + 1] - get_bit(RAM[PSW], 8)
        if (previous_ACC // 0x10) != (RAM[ACC] // 0x10):
            RAM[PSW] = set_bit(RAM[PSW], 6, 1)
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x04:            # (A) <- (A)+1
        RAM[ACC] += 1
        if RAM[ACC] > 0xff:
            RAM[ACC] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif (program_memory[PC] & 0xf8) == 0x08:   # (Rn) <- (Rn)+1
        n = program_memory[PC] & 0x7
        RAM[POH[reg_bank][n]] += 1
        if RAM[POH[reg_bank][n]] > 0xff:
            RAM[POH[reg_bank][n]] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x05:            # (ad) <- (ad)+1
        RAM[program_memory[PC + 1]] += 1
        if RAM[program_memory[PC + 1]] > 0xff:
            RAM[program_memory[PC + 1]] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x06:            # ((R0)) <- ((R0))+1
        RAM[RAM[POH[reg_bank][0]]] += 1
        if RAM[RAM[POH[reg_bank][0]]] + 1 > 0xff:
            RAM[RAM[POH[reg_bank][0]]] -= 0x1
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x07:            # ((R0)) <- ((R0))+1
        RAM[RAM[POH[reg_bank][1]]] += 1
        if RAM[RAM[POH[reg_bank][1]]] > 0xff:
            RAM[RAM[POH[reg_bank][1]]] -= 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xA3:            # (DPTR) <- (DPTR)+1
        RAM[DPTR] += 1
        if RAM[DPTR] > 0xFFFF:
            RAM[DPTR] -= 0x10000
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x14:            # (A) <- (A)-1
        RAM[ACC] -= 1
        if RAM[ACC] < 0:
            RAM[ACC] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif (program_memory[PC] & 0xf8) == 0x18:   # (Rn) <- (Rn)-1
        n = program_memory[PC] & 0x7
        RAM[POH[reg_bank][n]] -= 1
        if RAM[POH[reg_bank][n]] < 0:
            RAM[POH[reg_bank][n]] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x15:            # (ad) <- (ad)-1
        RAM[program_memory[PC] + 1] -= 1
        if RAM[POH[reg_bank][n]] < 0:
            RAM[POH[reg_bank][n]] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x16:            # ((R0)) <- ((R0))-1
        RAM[RAM[POH[reg_bank][0]]] -= 1
        if RAM[RAM[POH[reg_bank][0]]] < 0:
            RAM[RAM[POH[reg_bank][0]]] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x17:            # ((R1)) <- ((R1))-1
        RAM[RAM[POH[reg_bank][1]]] -= 1
        if RAM[RAM[POH[reg_bank][1]]] < 0:
            RAM[RAM[POH[reg_bank][1]]] += 0x100
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xA4:            # (A)(B) <- (A)*(B)
        mul = RAM[ACC]*RAM[B]
        RAM[ACC] = mul & 0xFF
        RAM[B] = (mul & 0xFF00) >> 8
        inc_cycle()
        inc_cycle()
        inc_cycle()
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x84:            # (B) <- (A) mod (B)
                                                # (A) <- (A) div (B)
        mod = RAM[ACC] % RAM[B]
        div = RAM[ACC] // RAM[B]
        RAM[ACC] = div
        RAM[B] = mod
        inc_cycle()
        inc_cycle()
        inc_cycle()
        inc_cycle()
        PC += 1
    # ============КОМАНДЫ ЛОГИЧЕСКИХ ОПЕРАЦИЙ===================
    elif (program_memory[PC] & 0xf8) == 0x58:   # (A) <- (A) AND (Rn)
        n = program_memory[PC] & 0x7
        RAM[ACC] = RAM[ACC] & RAM[POH[reg_bank][n]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x55:            # (A) <- (A) AND (ad)
        RAM[ACC] = RAM[ACC] & RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x56:            # (A) <- (A) AND ((R0))
        RAM[ACC] = RAM[ACC] & RAM[RAM[POH[reg_bank][0]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x57:            # (A) <- (A) AND ((R1))
        RAM[ACC] = RAM[ACC] & RAM[RAM[POH[reg_bank][1]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x54:            # (A) <- (A) AND #d 
        RAM[ACC] = RAM[ACC] & program_memory[PC + 1]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x52:            # (ad) <- (A) AND (ad)
        RAM[program_memory[PC + 1]] = RAM[ACC] & RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x53:            # (ad) <- #d AND (ad)
        RAM[program_memory[PC + 1]] = program_memory[PC + 2] & RAM[program_memory[PC + 1]]
        inc_cycle()
        inc_cycle()
        PC += 3
    elif (program_memory[PC] & 0xf8) == 0x48:   # (A) <- (A) OR (Rn)
        n = program_memory[PC] & 0x7
        RAM[ACC] = RAM[ACC] | RAM[POH[reg_bank][n]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x45:            # (A) <- (A) OR (ad)
        RAM[ACC] = RAM[ACC] | RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x46:            # (A) <- (A) OR ((R0))   
        RAM[ACC] = RAM[ACC] | RAM[RAM[POH[reg_bank][0]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x47:            # (A) <- (A) OR ((R1))   
        RAM[ACC] = RAM[ACC] | RAM[RAM[POH[reg_bank][1]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x44:            # (A) <- (A) OR #d 
        RAM[ACC] = RAM[ACC] | program_memory[PC + 1]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x42:            # (ad) <- (ad) OR (A)
        RAM[program_memory[PC + 1]] = RAM[ACC] | RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif (program_memory[PC] & 0xf8) == 0x68:   # (A) <- (A) XOR (Rn)
        n = program_memory[PC] & 0x7
        RAM[ACC] = RAM[ACC] ^ RAM[RAM[POH[reg_bank][n]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x65:            # (A) <- (A) XOR (ad)
        RAM[ACC] = RAM[ACC] ^ RAM[program_memory[PC + 1]]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0x66:            # (A) <- (A) XOR ((R0))
        RAM[ACC] = RAM[ACC] ^ RAM[RAM[POH[reg_bank][0]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x67:            # (A) <- (A) XOR ((R1))
        RAM[ACC] = RAM[ACC] ^ RAM[RAM[POH[reg_bank][1]]]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x64:            # (A) <- (A) XOR #d
        RAM[ACC] = RAM[ACC] ^ program_memory[PC + 1]
        inc_cycle()
        PC += 2
    elif program_memory[PC] == 0xE4:            # (A) <- 0
        RAM[ACC] = 0
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0xF4:            # (A) <- NOT(A)
        RAM[ACC] = ~RAM[ACC]
        inc_cycle()
        PC += 1
    elif program_memory[PC] == 0x23:              
        RAM[ACC] = RAM[ACC] << 1
        c = RAM[ACC] & 0x100
        RAM[ACC] = RAM[ACC] | (c >> 8)
        inc_cycle()
        PC += 1

    elif program_memory[PC] == 0x03:
        c = RAM[ACC] & 0x1
        RAM[ACC] = RAM[ACC] >> 1
        RAM[ACC] = RAM[ACC] | (c << 7)
        inc_cycle()
        PC += 1

    elif program_memory[PC] == 0xC4:            # (A0..3) <-> (A4..7)
        A03 = (RAM[ACC] & 0x0F) << 4
        A47 = (RAM[ACC] & 0xF0) >> 4
        RAM[ACC] = A03 + A47
        inc_cycle()
        PC += 1
    
    # ===========КОМАНДЫ ПЕРЕДАЧИ УПРАВЛЕНИЯ============
    elif program_memory[PC] == 0x02:            # (PC) <- ad16 # 
        ad16 = (program_memory[PC + 1] << 8) + program_memory[PC + 2]
        PC = ad16

    # AJMP 
    elif (program_memory[PC] & 0x1F) == 0x01:
        ad11 = ((program_memory[PC] & 0xE0) << 3) + program_memory[PC + 1]
    #    print bin((program_memory[PC] & 0xE0) << 3)
        PC = ad11
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x80:            # (PC) <- (PC) + rel
                                                # (PC) <- (PC) + 2
        rel = program_memory[PC + 1]
    #    PC += 2
        
        if rel < 0x80:
            PC += rel
        else:
            PC -= 0x100 - rel
            print PC
                                                     
        inc_cycle()
        inc_cycle()                                            
    elif program_memory[PC] == 0x73:            # (PC) <- (A) + (DPTR)
        PC = RAM[ACC] + RAM[DPTR]
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x60:            # (PC) <- (PC) + 2
                                                # if (A) = 0 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 1]
   #     PC += 2
        if RAM[ACC] == 0:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x70:            # (PC) <- (PC) + 2
                                                # if (A) <> 0 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 1]
    #    PC += 2
        if RAM[ACC] != 0:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x40:            # (PC) <- (PC) + 2
                                                # if (C) = 1 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 1]
    #    PC += 2
        if get_bit(RAM[PSW], 8) == 1:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x50:            # (PC) <- (PC) + 2
                                                # if (C) = 0 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 1]
    #    PC += 2
        if get_bit(RAM[PSW], 8) == 0:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    # JN bit, rel
    elif program_memory[PC] == 0x20:            # (PC) <- (PC) + 3
                                                # if (bit) = 1 then
                                                # (PC) <- (PC) + (rel)
        byte, bit = get_bit_address(program_memory[PC + 1])
        rel = program_memory[PC + 2]
     #   PC += 3
        if get_bit(byte, bit):
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    # JNB bit, rel
    elif program_memory[PC] == 0x30:            # (PC) <- (PC) + 3
                                                # if (bit) = 0 then
                                                # (PC) <- (PC) + (rel)
        byte, bit = get_bit_address(program_memory[PC + 1])
        rel = program_memory[PC + 2]
     #   PC += 3
        if get_bit(byte, bit):
            if not (rel < 0x80):
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    # JBC bit, rel
    elif program_memory[PC] == 0x10:            # (PC) <- (PC) + 3
                                                # if (bit) = 1 then
                                                # (PC) <- (PC) + (rel)
                                                # (bit) <- 0
        byte, bit = get_bit_address(program_memory[PC + 1])
        rel = program_memory[PC + 2]
    #    PC += 3
        if get_bit(byte, bit):
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
            RAM[byte] = set_bit(RAM[byte], bit, 0)
        inc_cycle()
        inc_cycle()
    elif (program_memory[PC] & 0xf8) == 0xD8:   # (PC) <- (PC) + 2
                                                # (Rn) <- (Rn) - 1
                                                # if (Rn) <> 0 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 1]
        n = program_memory[PC] & 0x7
     #   PC += 2
        
        RAM[POH[reg_bank][n]] -= 1
        if RAM[POH[reg_bank][n]] != 0:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
        
    elif program_memory[PC] == 0xD5:            # (PC) <- (PC) + 2
                                                # (ad) <- (ad) - 1
                                                # if (ad) <> 0 then
                                                # (PC) <- (PC) + (rel)
        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
     #   PC += 2
        
        RAM[program_memory[ad]] -= 1
        if RAM[ad] != 0:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xB5:            # (PC) <- (PC) + 3
                                                # if (A) <> (ad) then
                                                # (PC) <- (PC) + (rel)
                                                # if (A) < (ad) then
                                                # (C) <- 1 else (C) <- 0
        
        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
    #    PC += 3
        if RAM[ACC] <> RAM[ad]:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        if RAM[ACC] < RAM[ad]:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 8, 0)
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xB4:            # (PC) <- (PC) + 3
                                                # if (A) <> #d then
                                                # (PC) <- (PC) + rel
                                                # if (A) < #d then
                                                # (C) <- 1 else (C) <- 0
        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
     #   PC += 3
        if RAM[ACC] <> ad:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        if RAM[ACC] < ad:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 8, 0)
        inc_cycle()
        inc_cycle()
    elif (program_memory[PC] & 0xf8) == 0xB8:   # (PC) <- (PC) + 3
                                                # if (Rn) <> #d then
                                                # (PC) <- (PC) + rel
                                                # if (Rn) < #d then
                                                # (C) <- 1 else (C) <- 0
        n = program_memory[PC] & 0x7
        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
     #   PC += 3
        
        if RAM[POH[reg_bank][n]] <> ad:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        if RAM[POH[reg_bank][n]] < ad:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 8, 0)
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xB6:            # (PC) <- (PC) + 3
                                                # if ((R0)) <> #d then
                                                # (PC) <- (PC) + rel
                                                # if ((R0)) < #d then
                                                # (C) <- 1 else (C) <- 0
        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
   #     PC += 3
        if RAM[RAM[POH[reg_bank][0]]] <> ad:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        if RAM[RAM[POH[reg_bank][0]]] < ad:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 8, 0)
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xB7:            # (PC) <- (PC) + 3
                                                # if ((R1)) <> #d then
                                                # (PC) <- (PC) + (rel)
                                                # if ((R1)) < #d then
                                                # (C) <- 1 else (C) <- 0

        rel = program_memory[PC + 2]
        ad = program_memory[PC + 1]
   #     PC += 3
        if RAM[RAM[POH[reg_bank][1]]] <> ad:
            if rel < 0x80:
                PC += rel
            else:
                PC -= 0x100 - rel
        if RAM[RAM[POH[reg_bank][1]]] < ad:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 8, 0)
        inc_cycle()
        inc_cycle()

    # LCALL
    elif program_memory[PC] == 0x12:            # (PC) <- (PC) + 3
                                                # (SP) <- (SP) + 1
                                                # ((SP)) <- (PC0..7)
                                                # (SP) <- (SP) + 1
                                                # ((SP)) <- (PC8..15)
                                                # (PC) <- ad16                               
        ad16 = (program_memory[PC + 1] << 8) + program_memory[PC + 2]
      #  PC += 3
        
        RAM[SP] += 1
        RAM[RAM[SP]] = PC & 0xFF
        RAM[SP] += 1
        RAM[RAM[SP]] = (PC & 0xFF00) >> 8
        PC = ad16
        
        inc_cycle()
        inc_cycle()
    # ACALL
    elif (program_memory[PC] & 0x1F) == 0x11:
      #  PC += 2
        ad11 = ((program_memory[PC] & 0xE0) << 3) + program_memory[PC + 1]
        
        RAM[SP] += 1
        RAM[RAM[SP]] = PC & 0xFF
        RAM[SP] += 1
        RAM[RAM[SP]] = (PC & 0xFF00) >> 8
        PC = ad11
        inc_cycle()
        inc_cycle()
    # RET
    elif program_memory[PC] == 0x22:            # 
        PC = (RAM[RAM[SP]] << 8) + RAM[RAM[SP - 1]]
        RAM[SP] -= 2
        inc_cycle()
        inc_cycle()
    # RETI
    elif program_memory[PC] == 0x32:
        PC = (RAM[RAM[SP]] << 8) + RAM[RAM[SP - 1]]
        RAM[SP] -= 2
        inc_cycle()
        inc_cycle()
#==========Команды операций над битами==================
    
    elif program_memory[PC] == 0xC3:        # (C) <- 0
        RAM[PSW] = set_bit(RAM[PSW], 7, 0)
        PC += 1
        inc_cycle()
    elif program_memory[PC] == 0xC2:        # (b) <- 0
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[byte] = set_bit(RAM[byte], bit, 0)
        PC += 2
        inc_cycle()
    elif program_memory[PC] == 0xD3:        # (C) <- 1  
        RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        PC += 1
        inc_cycle()
    elif program_memory[PC] == 0xD2:        # (b) <- 1
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[byte] = set_bit(RAM[byte], bit, 1)
        PC += 2
    elif program_memory[PC] == 0xB3:        # (C) <- NOT(C)
        if get_bit(RAM[PSW], 7):
            RAM[PSW] = set_bit(RAM[PSW], 7, 0)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 7, 1)
        PC += 1
        inc_cycle()
    elif program_memory[PC] == 0xB2:        # (b) <- NOT(b)
        byte, bit = get_bit_address(program_memory[PC + 1])
        if get_bit(RAM[byte], bit):
            RAM[byte] = set_bit(RAM[byte], bit, 0)
        else:
            RAM[byte] = set_bit(RAM[byte], bit, 1)
        PC += 2
        inc_cycle()
    elif program_memory[PC] == 0x82:        # (C) <— (C) AND (b)
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[PSW] = RAM[PSW] & bit
        PC += 2
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xB0:        # (C) <— (C) AND (NOT(b))
        byte, bit = get_bit_address(program_memory[PC + 1])
        if get_bit(RAM[byte], bit):
            RAM[PSW] = set_bit(RAM[PSW], 7, get_bit(RAM[PSW], 7) & 0)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 7, get_bit(RAM[PSW], 7) & 1)
        PC += 2
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0x72:        # (C) <— (C) OR (b)
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[PSW] = RAM[PSW] | bit
        PC += 2
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xA0:        # (C) <— (C) OR (NOT(b))
        byte, bit = get_bit_address(program_memory[PC + 1])
        if get_bit(RAM[byte], bit):
            RAM[PSW] = set_bit(RAM[PSW], 7, get_bit(RAM[PSW], 7) | 0)
        else:
            RAM[PSW] = set_bit(RAM[PSW], 7, get_bit(RAM[PSW], 7) | 1)
        PC += 2
        inc_cycle()
        inc_cycle()
    elif program_memory[PC] == 0xA2:
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[PSW] = set_bit(RAM[PSW], 7, get_bit(RAM[byte], bit))
        PC += 2
        inc_cycle()
    elif program_memory[PC] == 0x92:
        byte, bit = get_bit_address(program_memory[PC + 1])
        RAM[byte] = set_bit(RAM[byte], bit, get_bit(RAM[PSW], 7))
        PC += 2
        inc_cycle()
        inc_cycle()


def run_8051():
    while PC < 4096:
        step()

def reset_8051():
    global RAM
    global PC
    global cycle
    global reg_bank

def clear_pm():
    global program_memory
    for i in range(4096):
        program_memory[i] = 0
    
    for i in range(256):
        RAM[i] = 0
    PC = 0
    cycle = 0
    reg_bank = 0

def test():
    init_8051()
    hex_ = read_hex()
    print hex_
    load_hex_to_pm(hex_)

