from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from functions_cia_finder import *
from os import startfile
from PIL import ImageTk

import datetime


def first():
    label3.pack_forget()
    button_devicesort.pack_forget()
    device_entry.pack_forget()
    button_searchbysid.pack_forget()
    label1.pack(side=TOP, padx=10, pady=50)
    button_chose_dir.pack(side=TOP, padx=40, pady=10, ipadx=5, ipady=5)
    button_chose_dir.bind('<Return>', lambda _: browse_button())
    button_chose_dir.focus_set()


def open_info():
    startfile("info.txt")


def browse_button():
    global folder_path
    global path
    global sfile
    path = filedialog.askdirectory() + '/'
    folder_path.set(path)
    sfile = path + "out.log"
    r = combine_files(path, sfile)
    if r == 0:
        messagebox.showerror('Ошибка', 'В директории нет *.log файлов.')
        return
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Объединение и сортировка файлов завершены.' + sfile)
        label1.pack_forget()
        button_chose_dir.pack_forget()
        label2.pack(side=TOP, padx=10, pady=50)
        data_entry.pack(side=TOP, padx=10, pady=10)
        button_datasort.pack(side=TOP, padx=10, pady=10)
        button_datasort.bind('<Return>', lambda _: d_sort())
        button_datasort.focus_set()


def d_sort():
    global data
    data = data_entry.get()
    r = sort_by_data(path, sfile, data)
    if r == 0:
        messagebox.showerror('Ошибка', 'Нет записи по указанной дате ' + data + '.')
    else:
        if r == 2:
            messagebox.showinfo('Уведомление', 'Файл уже существует ' + path + data + '/' + data + '.txt' + '.')
        else:
            messagebox.showinfo('Уведомление', 'Сортировка по дате ' + data + " завершена.")

        label2.pack_forget()
        data_entry.pack_forget()
        button_datasort.pack_forget()
        label3.pack(side=TOP, padx=10, pady=50)
        device_entry.pack(side=TOP, padx=10, pady=5)
        button_devicesort.pack(side=TOP, padx=10, pady=10)
        button_devicesort.bind('<Return>', lambda _: device_sort())
        button_devicesort.focus_set()
        button_searchbysid.pack(side=TOP, padx=10, pady=10)


def device_sort():
    device = device_entry.get()
    path_f = path + data + '/' + device.replace("*", "").replace("|", "") + '.txt'
    dfile = path + data + '/' + data + '.txt'
    r = sort_by_device_name(dfile, device, path_f)
    if os.stat(path_f).st_size == 0:
        messagebox.showinfo('Уведомление', 'Нет записи по этому устройству')
        os.remove(path_f)
        os.remove(path_f[:-4] + '_mini.txt')
    elif r == 0:
        messagebox.showinfo('Уведомление', 'Введите названия устройства')
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Сортировка по устройству ' + path_f + " завершена.")
        first()
        startfile(path_f)
    else:
        messagebox.showerror('Ошибка', 'Произошла ошибка. Повторите попытку')


def sort_sid():
    sid = device_entry.get()
    path_f = path + data + '/' + sid.replace("*", "").replace("|", "") + '.txt'
    dfile = path + data + '/' + data + '.txt'
    r = search_by_session_id(dfile, sid, path_f)
    if os.stat(path_f).st_size == 0:
        messagebox.showinfo('Уведомление', 'Нет записи по этой сессии')
        os.remove(path_f)
    elif r == 0:
        messagebox.showinfo('Уведомление', 'Введите ID сессии')
    elif r == 1:
        messagebox.showinfo('Уведомление', 'Сортировка сессии ' + path_f + " завершена.")
        first()
        startfile(path_f)
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

info_button = Button(master=window, text="?", width=5, height=1, background="yellow", command=open_info, font="16")
info_button.pack(fill=X)

label1 = Label(text="Выберите папку где хранятся логи CashInsight", font="Arial 12")

button_chose_dir = Button(master=window, text="Выбрать папку", background="#534", foreground="#ccc",
                          font="16", command=browse_button)

label2 = Label(master=window, text="Сортировать файл по дате: ", font="Arial 12")

data_entry = Entry(master=window, width=10, font="Arial 12")

now = datetime.datetime.now()

data_entry.insert(END, now.strftime("%Y-%m-%d"))

button_datasort = Button(master=window, text="Cортировать", background="#534", foreground="#ccc",
                         font="16", width=14, command=d_sort)

label3 = Label(master=window, text="Введите название устройства или ID сессии", font="Arial 12")

device_entry = Entry(master=window, width=20, font="Arial 12")

button_devicesort = Button(master=window, text="Поиск по устройству", background="#534", foreground="#ccc",
                           font="16", width=30, command=device_sort)

button_searchbysid = Button(master=window, text="Поиск по сессии", background="#534", foreground="#ccc",
                            font="16", width=30, command=sort_sid)

label_version = Label(master=window, text="logAn version 1.0", font="Arial 8")
label_version.pack(side=BOTTOM, padx=20, pady=5)

first()
window.mainloop()
