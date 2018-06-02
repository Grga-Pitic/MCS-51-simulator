#-*- coding: utf-8 -*-
from Tkinter import *
import tkFileDialog
import simulator
import preprocessor
import assembler

root = Tk()
win_reg = Toplevel(root)
win_prog_mem = Toplevel(root)
win_data_mem = Toplevel(root)
win_proc = Toplevel(root)

list_v = []

def LoadFile():
    global list_v
    
    source = list_v[5]
    fn = tkFileDialog.Open(root, filetypes = [('*.asm files', '.asm')]).show()
    if fn == '':
        return
    source.delete('1.0', 'end') 
    source.insert('1.0', open(fn, 'rt').read())
    
def SaveFile():
    global list_v
    
    source = list_v[5]
    fn = tkFileDialog.SaveAs(root, filetypes = [('*.asm files', '.asm')]).show()
    if fn == '':
        return
    if not fn.endswith(".asm"):
        fn+=".asm"
    open(fn, 'wt').write(source.get('1.0', 'end'))

def NewFile():
    global list_v
    source = list_v[5]
    source.delete('1.0', 'end')
    simulator.init_8051()
    update_data()

def show_hint_reg():
    if win_reg.state() == 'withdrawn':
        win_reg.deiconify()
    else:
        win_reg.withdraw()
def show_hint_prog_mem():
    if win_prog_mem.state() == 'withdrawn':
        win_prog_mem.deiconify()
    else:
        win_prog_mem.withdraw()
def show_hint_data_mem():
    if win_data_mem.state() == 'withdrawn':
        win_data_mem.deiconify()
    else:
        win_data_mem.withdraw()
def show_hint_proc():
    if win_proc.state() == 'withdrawn':
        win_proc.deiconify()
        win_proc.overrideredirect()
    else:
        win_proc.withdraw()

def Run(event=0):
    print ('sad')

def Step(event=0):
    simulator.step()
    update_data()

def Assembly(event=0):
    global list_v
    
    source = list_v[5].get('1.0', END)
    source = preprocessor.run(source)
    source = assembler.run(source)
    simulator.init_8051()
    simulator.load_hex_to_pm(source)
    update_data()

def About():
    About = Toplevel(root)
    About.title('О программе')
    About.minsize(320, 80)
    txt = u"Курсовой проект\nТема: Симулятор микроконтроллера семейства 8051\n"
    txt += u"Руководитель: Куликов В.С.\nСтудент группы 3-09-П Константинов И.Э."
    lbl = Label(About, text=txt, justify='left')
    lbl.pack()

def Quit():
    root.destroy()

def init_root(root):
    root.title('Симулятор 8051')
    root.minsize(637, 480)
    root.resizable(width=True, height=True)
    
    m = Menu(root) #создается объект Меню на главном окне
    root.config(menu=m) #окно конфигурируется с указанием меню для него
     
    fm = Menu(m) #создается пункт меню с размещением на основном меню (m)
    m.add_cascade(label=u"Файл",menu=fm) #пункту располагается на основном меню (m)
    fm.add_command(label=u"Новый", command=NewFile)
    fm.add_command(label=u"Открыть...", command=LoadFile) #формируется список команд пункта меню
    fm.add_command(label=u"Сохранить...", command=SaveFile)
    fm.add_command(label=u"Выход", command=Quit)

    vm = Menu(m)
    m.add_cascade(label=u"Просмотр", menu=vm)
    vm.add_command(label=u"Процессор", command=show_hint_proc)
    vm.add_command(label=u"Память программ", command=show_hint_prog_mem)
    vm.add_command(label=u"Память данных", command=show_hint_data_mem)
    vm.add_command(label=u"Регистры общего назначения", command=show_hint_reg)
    
    rm = Menu(m)
    m.add_cascade(label=u"Запуск", menu=rm)
    rm.add_command(label=u"Ассемблирование (F4)", command=Assembly)
    rm.add_command(label=u"Запуск (F5)", command=Run)
    rm.add_command(label=u"Шаг (F6)", command=Step)
    
    hm = Menu(m) #второй пункт меню
    m.add_cascade(label=u"Помощь",menu=hm)
    hm.add_command(label=u"О программе", command=About)
    
    text_source = Text(root, width=77, height=27, state=DISABLED)
    text_source.pack(side='left', expand=True , fill="both")

    s_sb = Scrollbar(root)
    s_sb.pack(side='right', fill="y")

    text_source['yscrollcommand'] = s_sb.set
    text_source.config(state='normal')    
    s_sb.configure(command=text_source.yview)
    return text_source

# окно дампа памяти программ

def output_prog_mem(text_dump):
    k = 0
    text_dump.config(state='normal')
    text_dump.delete('1.0', END)
    for i in range(256):
        for j in range(16):
            hex_ = hex(simulator.program_memory[k])[2:]
            if len(hex_) < 2:
                hex_ = '0' + hex_
            text_dump.insert(INSERT, hex_.upper()+' ')
            k += 1

        text_dump.insert(INSERT, '\n')
        
    text_dump.config(state='disabled')

def on_closing_prog_mem():
    win_prog_mem.withdraw()

def init_win_prog_mem(win_prog_mem):
    win_prog_mem.title(u'Дамп памяти программ')
    win_prog_mem.minsize(430, 280)
    win_prog_mem.resizable(width=False, height=False)
    win_prog_mem.withdraw()
    win_prog_mem.protocol("WM_DELETE_WINDOW", on_closing_prog_mem)
  
    s_sb = Scrollbar(win_prog_mem)
    s_sb.place(x=398, y=10, height=260)
    
    text_dump = Text(win_prog_mem, width=48, height=16, state=DISABLED)
    text_dump.place(x=10, y=10)
    text_dump.configure(yscrollcommand=s_sb.set)
    s_sb.configure(command=text_dump.yview)
    
    output_prog_mem(text_dump)
    return text_dump

# окно дампа памяти данных

def output_data_mem(text_dump):
    k = 0
    text_dump.config(state='normal')
    text_dump.delete('1.0', END)
    for i in range(8):
        for j in range(16):
            hex_ = hex(simulator.RAM[k])[2:]
            if len(hex_) < 2:
                hex_ = '0' + hex_
            text_dump.insert(INSERT, hex_.upper()+' ')
            k += 1

        text_dump.insert(INSERT, '\n')
        
    text_dump.config(state='disabled')

def on_closing_data_mem():
    win_data_mem.withdraw()

def init_win_data_mem(win_data_mem):
    win_data_mem.title(u'Дамп памяти данных')
    win_data_mem.minsize(410, 100)
    win_data_mem.geometry('410x150+40+60')
    win_data_mem.resizable(width=False, height=False)
    win_data_mem.withdraw()
    win_data_mem.protocol("WM_DELETE_WINDOW", on_closing_data_mem)
    

    text_dump = Text(win_data_mem, width=48, height=8, state=DISABLED)
    text_dump.place(x=10, y=10, height=130)
    output_data_mem(text_dump)
    return text_dump

def output_POH(list_entry_val):
    for i in range(4):
        for j in range(8):
            list_entry_val[i][j].config(state=NORMAL)
            txt =hex(simulator.RAM[simulator.POH[i][j]])[2:]
            if len(txt) < 2:
                txt = '0' + txt
            list_entry_val[i][j].delete(0, END)
            list_entry_val[i][j].insert(INSERT, txt.upper())
            list_entry_val[i][j].config(state=DISABLED)


def on_closing_reg():
    win_reg.withdraw()

def init_win_reg(win_reg):
    win_reg.title(u'Регистры')
    win_reg.minsize(160, 200)
    win_reg.resizable(width=False, height=False)
    win_reg.withdraw()
    win_reg.protocol("WM_DELETE_WINDOW", on_closing_reg)
    
    list_entry_val = []
    for i in range(4):
        lbl = Label(win_reg, text=u'Банк'+str(i))
        lbl.grid(row=0, column=i*2, columnspan=2)
        l = []
        for j in range(8):
            etr = Entry(win_reg, state=DISABLED, width=2)
            lbl = Label(win_reg, text='R'+str(j))
            lbl.grid(row=j+1, column=i*2)
            etr.grid(row=j+1, column=i*2+1)
            l.append(etr)
        list_entry_val.append(l)
    output_POH(list_entry_val)
    return list_entry_val

def get_reg_data():
    reg_data = []
    
    reg_data.append(simulator.PC)
    reg_data.append(simulator.RAM[simulator.DPTR])
    reg_data.append(simulator.RAM[simulator.SP])
    reg_data.append(simulator.RAM[simulator.ACC])
    reg_data.append(simulator.RAM[simulator.B])
    reg_data.append(simulator.RAM[simulator.SCON])
    reg_data.append(simulator.RAM[simulator.SBUF])
    reg_data.append(simulator.RAM[simulator.IP])
    reg_data.append(simulator.RAM[simulator.IE])
    reg_data.append(simulator.RAM[simulator.P0])
    reg_data.append(simulator.RAM[simulator.P1])
    reg_data.append(simulator.RAM[simulator.P2])
    reg_data.append(simulator.RAM[simulator.P3])
    reg_data.append(simulator.RAM[simulator.TMOD])
    reg_data.append(simulator.RAM[simulator.TCON])
    THL0 = (simulator.RAM[simulator.TH0] << 8) + simulator.RAM[simulator.TL0]
    THL1 = (simulator.RAM[simulator.TH1] << 8) + simulator.RAM[simulator.TL1]
    reg_data.append(THL0)
    reg_data.append(THL1)
    reg_data.append(simulator.RAM[simulator.PCON])
    reg_data.append(simulator.RAM[simulator.PSW])
    return reg_data

def output_proc(list_entry_val, list_entry_flags):
    reg_data = get_reg_data()
    for i in range(19):
        len_output = 2
        if (i == 0) or (i == 1) or (i == 15) or (i == 16):
            len_output = 4
        
        list_entry_val[i].config(state=NORMAL)
        list_entry_val[i].delete(0, END)

        txt = hex(reg_data[i])[2:]
        while len(txt) < len_output:
            txt = '0' + txt
        
        list_entry_val[i].insert(INSERT, txt.upper())
        list_entry_val[i].config(state=DISABLED)

    flags = bin(reg_data[18])[2:]
    while len(flags) < 8:
        flags = '0' + flags
    flags = list(flags)
    for i in range(8):
        list_entry_flags[i].config(state=NORMAL)
        list_entry_flags[i].delete(0, END)
        list_entry_flags[i].insert(INSERT, flags[i].upper())
        list_entry_flags[i].config(state=DISABLED)
    
    
def on_closing_proc():
    win_proc.withdraw()

def init_win_proc(win_proc):
    win_proc.title(u'Процессор')
    win_proc.minsize(190, 180)
    win_proc.resizable(width=False, height=False)
    win_proc.protocol("WM_DELETE_WINDOW", on_closing_proc)
    win_proc.withdraw()

    label_text = "PC DPTR SP ACC B SCON SBUF IP IE".split(' ')
    label_text_psw = "PSW C AC F0 RS1 RS0 OV - P".split(' ')
    label_text += "P0 P1 P2 P3 TMOD TCON THL0 THL1 PCON".split(' ')
    list_entry_val = []
    k = 0
    for i in range(2):
        for j in range(9):
            lbl = Label(win_proc, text=label_text[k])
            lbl.grid(row=j+1, column=i*2, sticky="w")
            etr = Entry(win_proc, state=DISABLED, width=2)
            etr.grid(row=j+1, column=i*2+1, sticky="w")
            k += 1
            list_entry_val.append(etr)
    list_entry_val[0].config(width=4)
    list_entry_val[1].config(width=4)
    list_entry_val[15].config(width=4)
    list_entry_val[16].config(width=4)
    
    lbl = Label(win_proc, text=label_text_psw[0])
    lbl.grid(row=1, column=5)
    etr = Entry(win_proc, state=DISABLED, width=2)
    etr.grid(row=1, column=6)
    list_entry_val.append(etr)

    list_entry_flags = []
    
    for i in range(8):
        lbl = Label(win_proc, text=label_text_psw[i+1])
        lbl.grid(row=i+2, column=5, sticky="w")
        etr = Entry(win_proc, state=DISABLED, width=1)
        etr.grid(row=i+2, column=6, sticky="w")
        list_entry_flags.append(etr)
    output_proc(list_entry_val, list_entry_flags)
    return list_entry_val, list_entry_flags

def update_data():
    global list_v
    output_prog_mem(list_v[0])
    output_data_mem(list_v[1])
    output_POH(list_v[2])
    output_proc(list_v[3], list_v[4])


def main():


    simulator.init_8051()
    list_entry = []
    
    root_text_source = init_root(root)
    prog_mem_text = init_win_prog_mem(win_prog_mem)
    data_mem_text = init_win_data_mem(win_data_mem)
    POH_data_entry_list = init_win_reg(win_reg)
    RS_data_entry_list, flags_entry_list = init_win_proc(win_proc)
    global list_v
    list_v.append(prog_mem_text)
    list_v.append(data_mem_text)
    list_v.append(POH_data_entry_list)
    list_v.append(RS_data_entry_list)
    list_v.append(flags_entry_list)
    list_v.append(root_text_source)

    root.bind('<F4>', Assembly)
    root.bind('<F5>', Run)
    root.bind('<F6>', Step)
    
    
    root.mainloop()

main()
