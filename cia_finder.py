from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from functions_cia_finder import *
import datetime


def select_log_dir():
    global folder_path
    global path
    global sourcefile
    path = filedialog.askdirectory() + '/'
    folder_path.set(path)
    sourcefile = path + "out.log"
    r = combine_files(path, sourcefile)
    if r == 0:
        messagebox.showerror('Ошибка', 'В директории нет *.log файлов.')
        return
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Объединение и сортировка файлов завершены.' + sourcefile)
        l1.pack_forget()
        button2.pack_forget()
        lbl2.pack(side=TOP, padx=20, pady=0)
        data_entry.pack(side=TOP, padx=10, pady=0)
        button.pack(side=TOP, padx=10, pady=10)
        button.bind('<Return>', lambda _: sort_by_data())
        button.focus_set()


def sorting_by_data():
    global data
    data = data_entry.get()
    r = sort_by_data(path, sourcefile, data)
    if r == 0:
        messagebox.showerror('Ошибка', 'Нет записи по указанной дате ' + data + '.')
    else:
        if r == 2:
            messagebox.showinfo('Уведомление', 'Файл уже существует ' + path + data + '/' + data + '.txt' + '.')
        else:
            messagebox.showinfo('Уведомление', 'Сортировка по дате ' + data + " завершена.")
        lbl3.pack()
        device_entry.pack()
        button3.pack()
        button3.bind('<Return>', lambda _: sorting_by_device())
        button4.pack()
        button3.focus_set()
        lbl2.pack_forget()
        data_entry.pack_forget()
        button.pack_forget()


def sorting_by_device():
    device = device_entry.get()
    path_f = path + data + '/' + device + '.txt'
    datafile = path + data + '/' + data + '.txt'
    r = sort_by_device_name(datafile, device, path_f)
    if r == 0:
        messagebox.showinfo('Уведомление', 'Введите названия устройства')
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Формирование по устройству ' + path_f + " завершено.")
    else:
        messagebox.showerror('Ошибка', 'Произошла ошибка. Повторите попытку')


def sorting_by_sid():
    sid = device_entry.get()
    path_f = path + data + '/' + sid[4:] + '.txt'
    dfile = path + data + '/' + data + '.txt'
    r = search_by_session_id(dfile, sid, path_f)
    if r == 0:
        messagebox.showinfo('Уведомление', 'Введите ID сессии')
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Формирование по сессии ' + path_f + " завершено.")
    else:
        messagebox.showerror('Ошибка', 'Произошла ошибка. Повторите попытку')


window = Tk()


folder_path = StringVar()
window.title("Разбор логов CashIsight")
window.geometry('600x400+200+100')
window.update_idletasks()

w, h, sx, sy = map(int, re.split('[x+]', window.winfo_geometry()))
sw = (window.winfo_rootx() - sx) * 2 + w
sh = (window.winfo_rooty() - sy) + (window.winfo_rootx() - sx) + h
sx = (window.winfo_screenwidth() - sw) // 2
sy = (window.winfo_screenheight() - sh) // 2
window.wm_geometry('+%d+%d' % (sx, sy))
comf = Frame(window)
comf.pack(fill=X)

l1 = Label(text="Выберите папку где хранятся логи CashInsight", font="Arial 12")
l1.pack(side=TOP, padx=20, pady=50)

button2 = Button(master=window, text="Выбрать папку", background="#534", foreground="#ccc",
                 font="16", command=select_log_dir)

button2.pack(side=TOP, padx=20, pady=0, ipadx=5, ipady=5)

button2.bind('<Return>', lambda _: select_log_dir())
button2.focus_set()

lbl2 = Label(master=window, text="Сортировать файл по дате: ", padx=125, pady=100, font="Arial 12")
data_entry = Entry(master=window, width=10)
now = datetime.datetime.now()
data_entry.insert(END, now.strftime("%Y-%m-%d"))

button = Button(master=window, text="ОК", background="#534", foreground="#ccc",
                font="16", command=sorting_by_data)
lbl3 = Label(master=window, text="Введите название устройства", font="Arial 12")
device_entry = Entry(master=window, width=20)
button3 = Button(master=window, text="ОК", background="#534", foreground="#ccc",
                 font="16", command=sorting_by_device)
lbl4 = Label(master=window, text="Введите название устройства", font="Arial 12")

button4 = Button(master=window, text="Поиск по сессии", background="#534", foreground="#ccc",
                 font="16", command=sorting_by_sid)

window.mainloop()
