from __future__ import print_function
import os
import shutil
import glob2


# Функция обядиняет файлы cashinsight*.log, создает на выходе out.log файл
def combine_files(path, sfile):
    stri = []
    filenames = glob2.glob(path + '*.log')  # list of all .log files in the directory
    if len(filenames) == 0:
        return 0
    elif filenames[0].replace("\\", "/") == sfile:
        return 1
    for elem in filenames:
        str_f = elem.split('\\')
        stri.append(str_f[1])
    with open(path + 'output_file.log', 'w+', encoding='utf-8') as wfd:
        for f in stri:
            with open(path + f, 'r+', encoding='utf-8') as fd:
                shutil.copyfileobj(fd, wfd)
    for elem in stri:
        os.remove(path + elem)
    file = path + 'output_file.log'

    with open(file, 'r', encoding='utf-8') as infile, open(sfile, 'w+', encoding='utf-8') as outfile:
        lines = []
        for line in infile:
            if 'Increase the stock of the relevant RSM or reconfigure the' in line:
                prev_line = line
            elif '2020' in line:
                lines.append(line)
            if 'prewarning threshold.' in line:
                line1 = prev_line[:-1] + line
                lines.append(line1)
        lines.sort()
        for elem in lines:
            outfile.write(elem)
    os.remove(file)
    return 1


# Функция сортирует логи по указанной дате, создает папку и файл по дате в папке
def sort_by_data(path, sort_file, x_data):
    with open(sort_file, 'r', encoding='utf-8') as infile:
        r = 0
        for line in infile.readlines():
            if x_data in line:
                if os.path.exists(path + x_data + '/' + x_data + '.txt'):
                    if os.path.getsize(path + x_data + '/' + x_data + '.txt') > 10000:
                        return 2
                elif os.path.exists(path + x_data):
                    path_to_save_data_file = path + x_data
                else:
                    os.mkdir(path + x_data)
                    path_to_save_data_file = path + x_data
                r = 1
        if r == 0:
            return 0
    with open(sort_file, 'r', encoding='utf-8') as infile, open(path_to_save_data_file + '/' + str(x_data) + '.txt',
                                                                'w+',
                                                                encoding='utf-8') as outfile:
        for line in infile.readlines():
            if x_data in line:
                outfile.write(line)
    return r


# Функция формирует файл по устройству, создает файл за операционный день и мини-выписку
def sort_by_device_name(datafile, device_name, path_to_file):
    if device_name == '':
        return 0
    # Список sessionID
    with open(datafile, 'r', encoding='utf-8') as infile:
        str_01 = []
        str_log = []
        for line in infile:
            if device_name in line:
                if 'Glory.ManagerAPI |  | cashIn|' in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6] + '|')
                if 'Glory.ManagerAPI |  | dispense|' in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6] + '|')
                if 'Glory.ManagerAPI |  | emptyDevice|' in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6] + '|')
                if 'Glory.ManagerAPI |  | retrieveInventory|' in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6] + '|')
                if 'Glory.ManagerAPI |  | reset|' in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6] + '|')
        seen = set()
        uniq_session_id = [x for x in str_01 if x not in seen and not seen.add(x)]

    with open(datafile, 'r', encoding='utf-8') as infile, open(path_to_file, 'w+', encoding='utf-8') as outfile, \
            open(path_to_file[0:-4] + '_mini.txt', 'w+', encoding='utf-8') as outfile2:
        cash_end = []
        empty_end = []
        str_err = []
        for line in infile:
            if 'Glory.ManagerAPI |  | logon|null|null|null|entry|' in line:
                prev_line = line
                str_log = line.split('|')
                str_log = str_log[10].split(';')
            if "Glory.DeviceController |  | cashInStart|" + device_name + '|entry' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
                dat = line.split(',')
                if 'R00' in str_log[0].upper():
                    outfile2.write(dat[0] + '. Служебная загрузка\n')
                else:
                    outfile2.write(dat[0] + '. Приходная операция\n')
                outfile2.write('--------------------------------\n')
            if "Glory.DeviceController |  | cashInStart|" + device_name + '|exit' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
            if "Glory.DeviceController |  | cashin|" + device_name + '|entry' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
            if "Glory.DeviceController |  | cashin|" + device_name + '|exit' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                deposit = line.split(';')
                n = int(deposit[1])
                del deposit[0:3]
                if n == 2 or n == 3:
                    outfile.write('Ошибка: ' + deposit[0] + deposit[1] + deposit[2] + deposit[3] + '\n')
                elif n == 1:
                    outfile.write('Предупреждение: ' + deposit[0] + deposit[1] + deposit[2] + deposit[3] + '\n')
                del deposit[0:5]
                c = int(len(deposit) / 5)
                outfile.write('--------------------------------\n')
                k = 1
                for i in range(c):
                    a = int(deposit[k])
                    b = int(deposit[k + 1]) / 100
                    ab1 = a * b
                    if a > 0:
                        outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                        outfile2.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                    i += 1
                    k += 5
                dis_sum = str(deposit[0])
                cash_end.append(dis_sum)
                outfile.write('--------------------------------\n')
                outfile.write(line)
            if "Glory.DeviceController |  | dispense|" + device_name + '|entry' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
                dat = line.split(',')
                outfile2.write(dat[0] + '. Расходная операция\n')
                outfile2.write('--------------------------------\n')
            if "Glory.DeviceController |  | dispense|" + device_name + '|exit' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                dispense = line.split(';')
                n = int(dispense[1])
                del dispense[0:3]
                if n == 2 or n == 3:
                    outfile.write('Ошибка: ' + dispense[0] + dispense[1] + dispense[2] + dispense[4] + '\n')
                elif n == 1:
                    outfile.write('Предупреждение: ' + dispense[0] + dispense[1] + dispense[2] + dispense[4] + '\n')
                del dispense[0:5]
                c = int(len(dispense) / 5)
                if c != 0:
                    outfile.write('--------------------------------\n')
                    k = 1
                    for i in range(c):
                        a = int(dispense[k])
                        b = int(dispense[k + 1]) / 100
                        ab1 = a * b
                        if a > 0:
                            outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                            outfile2.write('aa ' + str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                        i += 1
                        k += 5
                    dis_sum = int(dispense[0]) / 100
                else:
                    dis_sum = 0
                outfile.write('--------------------------------\n')
                outfile.write('Выдано ' + str(dis_sum) + 'KZT\n')
                outfile2.write('--------------------------------\n')
                outfile2.write('ИТОГО ВЫДАНО ' + str(dis_sum) + 'KZT\n')
                outfile2.write('--------------------------------\n\n')
                outfile.write(line)
            if "Glory.DeviceController |  | cashInEnd|" + device_name + '|entry' in line:
                outfile.write(line)
            if "Glory.DeviceController |  | cashInEnd|" + device_name + '|exit' in line:
                outfile.write(line)
            if "Glory.DeviceController |  | cashInRollback|" + device_name + '|entry' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
            if "Glory.DeviceController |  | cashInRollback|" + device_name + '|exit' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                rollback = line.split(';')
                n = int(rollback[1])
                del rollback[0:3]
                if n == 2 or n == 3:
                    outfile.write('Ошибка: ' + rollback[0] + rollback[1] + rollback[2] + rollback[3] + '\n')
                elif n == 1:
                    outfile.write('Предупреждение: ' + rollback[0] + rollback[1] + rollback[2] + rollback[3] + '\n')
                del rollback[0:5]
                c = int(len(rollback) / 5)
                outfile.write('--------------------------------\n')
                k = 1
                for i in range(c):
                    a = int(rollback[k])
                    b = int(rollback[k + 1]) / 100
                    ab1 = a * b
                    if a > 0:
                        outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                    i += 1
                    k += 5
                if c == 0:
                    pass
                else:
                    summa_r = int(rollback[0]) / 100
                    outfile.write('--------------------------------\n')
                    outfile.write('Отменено ' + str(summa_r) + 'KZT\n')
                    outfile2.write('--------------------------------\n')
                    outfile2.write('Отменено.\nИТОГО Принято ' + str(0) + 'KZT\n')
                    outfile2.write('--------------------------------\n\n')
                outfile.write(line)
            if "Glory.DeviceController |  | empty|" + device_name + '|entry' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                outfile.write(line)
            if "Glory.DeviceController |  | empty|" + device_name + '|exit' in line:
                str_line = line.split('|')
                str_err = str_line[1]
                empty = line.split(';')
                n = int(empty[1])
                del empty[0:3]
                if n == 2 or n == 3:
                    outfile.write('Ошибка: ' + empty[0] + empty[1] + empty[2] + empty[3] + '\n')
                elif n == 1:
                    outfile.write('Ошибка: ' + empty[0] + empty[1] + empty[2] + empty[3] + '\n')
                del empty[0:5]
                c = int(len(empty) / 5)
                if c != 0:
                    outfile.write('--------------------------------\n')
                    k = 1
                    for i in range(c):
                        a = int(empty[k])
                        b = int(empty[k + 1]) / 100
                        ab1 = a * b
                        if a > 0:
                            outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                            outfile2.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                        i += 1
                        k += 5
                    empty_sum = str(empty[0])
                    empty_end.append(empty_sum)
                else:
                    empty_sum = 0
                    empty_end.append(empty_sum)
                outfile.write('--------------------------------\n')
                outfile.write(line)
            if "| ERROR | Glory.Assure |  | " in line:
                err = line.split('|')
                if str_err == err:
                    outfile.write("\n" + line)
            if "| ERROR | org.apache.axis2." in line:
                err = line.split('|')
                if str_err == err:
                    outfile.write("\n" + line)
            for elem in uniq_session_id:
                if elem in line:
                    if '|  | logon|' + elem in line:
                        if len(str_log) == 0:
                            print(str_log)
                        else:
                            outfile.write(
                                "\n\n\nПользователь " + str_log[0] + ". Начало сессии " + elem + "\n" + prev_line)
                    if '|  | retrieveInventory|' + elem + 'null|null|exit|' in line:
                        inventory_text = line.split(';')
                        outfile.write('--------------------------------\n')
                        n = inventory_text[1]
                        err = inventory_text[3]
                        k = 0
                        summa_i = 0
                        del inventory_text[0:7]
                        c = int((len(inventory_text) + 1) / 8)
                        if int(n) == 2:
                            outfile.write('Ошибка:' + err + '\n')
                        elif len(inventory_text) > 8:
                            for i in range(c):
                                a = int(inventory_text[k + 4])
                                b = int(inventory_text[k + 5]) / 100
                                ab1 = a * b
                                outfile.write(
                                    inventory_text[k + 1] + ' ' + str(a) + ' x ' + str(b) + ' = ' + str(ab1) +
                                    inventory_text[k + 6] + '\n')
                                i += 1
                                k += 8
                                summa_i += ab1
                            outfile.write('--------------------------------\n')
                            outfile.write("ИТОГО " + str(summa_i) + 'KZT\n')
                    if '| Glory.ManagerAPI |  | startDispenseTransaction|' + elem + 'null|null|entry|' in line:
                        a = line.split("|")
                        b = a[-1].split(';')
                        aa = int(b[0]) / 100
                        outfile.write("\nНачало транзакции. Выдача. Сумма " + str(aa) + ".\n")
                    if 'Glory.ManagerAPI |  | startDepositTransaction|' + elem + 'null|null|entry|' in line:
                        outfile.write("\nНачало транзакции. Прием\n")
                    if 'Glory.ManagerAPI |  | cashInStart|' + elem in line:
                        if device_name in line:
                            outfile.write("\nНачало операции по приему\n")
                    if 'Glory.ManagerAPI |  | cashIn|' + elem in line:
                        if device_name in line:
                            outfile.write("\nПрием\n")
                    if 'Glory.ManagerAPI |  | cashInRollback|' + elem in line:
                        if device_name in line:
                            outfile.write("\nОтмена\n")
                    if 'Glory.ManagerAPI |  | reset|' + elem + "null|" + device_name in line:
                        outfile.write("\nСброс\n")
                    if 'Glory.ManagerAPI |  | reset|' + elem + "null|null|exit" in line:
                        str_line = line.split('|')
                        str_err = str_line[1]
                        reset = line.split(';')
                        n = int(reset[1])
                        del reset[0:3]
                        if n == 2 or n == 3:
                            outfile.write('Ошибка: ' + reset[0] + reset[1] + reset[2] + reset[3])
                        elif n == 1:
                            outfile.write('Ошибка: ' + reset[0] + reset[1] + reset[2] + reset[3])
                    if 'Glory.ManagerAPI |  | cashInEnd|' + elem in line:
                        if device_name in line:
                            outfile.write("\nЗавершение операции по приему\n")
                    if 'Glory.ManagerAPI |  | cashInEnd|' + elem in line:
                        if 'null|exit' in line:
                            summar = 0
                            for csum in cash_end:
                                summar += int(csum)
                            cash_end = []
                            outfile.write('--------------------------------\n')
                            outfile.write('ИТОГО ПРИНЯТО ' + str(summar / 100) + 'KZT\n')
                            outfile.write('--------------------------------\n')
                            outfile2.write('--------------------------------\n')
                            outfile2.write('ИТОГО ПРИНЯТО ' + str(summar / 100) + 'KZT\n')
                            outfile2.write('--------------------------------\n\n')
                    if 'Glory.ManagerAPI |  | endTransaction|' + elem in line:
                        if "|null|entry|" in line:
                            outfile.write("\nЗавершение транзакции\n")
                    if 'Glory.ManagerAPI |  | retrieveInventory|' + elem in line:
                        if 'null|' + device_name in line:
                            outfile.write("\nИнвентаризация\n")
                    if 'Glory.ManagerAPI |  | generateMix|' + elem in line:
                        if device_name + '|entry|' in line:
                            outfile.write("\nСмешивания по номиналам\n")
                    if 'Glory.ManagerAPI |  | generateMix|' + elem in line:
                        if '|null|exit' in line:
                            generate_mix = line.split(';')
                            del generate_mix[0:8]
                            c = int(len(generate_mix) / 5)
                            if c != 0:
                                outfile.write('--------------------------------\n')
                                k = 0
                                for i in range(c):
                                    a = int(generate_mix[k])
                                    b = int(generate_mix[k + 1]) / 100
                                    ab1 = a * b
                                    if a > 0:
                                        outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                                    i += 1
                                    k += 5
                            outfile.write('--------------------------------\n')

                    if 'Glory.ManagerAPI |  | dispense|' + elem in line:
                        if device_name + "|entry" in line:
                            outfile.write("\nВыдача\n")
                    if 'Glory.ManagerAPI |  | logoff|' + elem + 'null|null|entry|' in line:
                        outfile.write("\nЗакрытие сессии " + elem + "\n")
                    if 'Glory.ManagerAPI |  | emptyDevice|' + elem + 'null|' + device_name in line:
                        outfile.write("\nРазгрузка устройства\n")
                    if 'Glory.ManagerAPI |  | emptyDevice|' + elem + 'null|null|exit|' in line:
                        outfile.write(line)
                        sum_ed = 0
                        for esum in empty_end:
                            sum_ed += int(esum)
                        empty_end = []
                        outfile.write('--------------------------------\n')
                        outfile.write('ИТОГО ВЫГРУЖЕНО ' + str(sum_ed / 100) + 'KZT\n')
                        outfile.write('--------------------------------\n')
                        outfile2.write('--------------------------------\n')
                        outfile2.write('ИТОГО ВЫГРУЖЕНО ' + str(sum_ed / 100) + 'KZT\n')
                        outfile2.write('--------------------------------\n\n')
                    if 'Glory.ManagerAPI |  | listDevices|' not in line:
                        if 'Glory.ManagerAPI |  | retrieveDeviceState|' not in line:
                            outfile.write(line)
    with open(path_to_file[0:-4] + '_mini.txt', 'r+', encoding='utf-8') as file:
        str_c = 'ИТОГО ПРИНЯТО'
        str_d = 'ИТОГО ВЫДАНО'
        str_i = 'ИТОГО ВЫГРУЖЕНО'
        c = 0.0
        d = 0.0
        i = 0.0
        for line in file:
            if str_c in line:
                str1 = line.split()
                str2 = str1[2].split('KZT')
                c += float(str2[0])
            if str_d in line:
                str1 = line.split()
                str2 = str1[2].split('KZT')
                d += float(str2[0])
            if str_i in line:
                str1 = line.split()
                str2 = str1[2].split('KZT')
                i += float(str2[0])
            # c += 1
        print("Расходная сумма() ", c, 'KZT')
        print("Приходная сумма ", d + i, 'KZT')
        print("Инкассация", i, 'KZT')
        print("Расхождение", d + i - c, 'KZT')
    return 1


# Функция формирует файл по ID сессии
def search_by_session_id(datafile, session_id, path_to_file):
    if session_id == '':
        return 0
    with open(datafile, 'r', encoding='utf-8') as infile, open(path_to_file, 'w+', encoding='utf-8') as outfile:
        cash_end = []
        empty_end = []
        for line in infile:
            if 'Glory.ManagerAPI |  | logon|null|null|null|entry|' in line:
                prev_line = line
                str_log = line.split('|')
                str_log = str_log[9].split(';')
            if session_id in line:
                if '|  | logon|' + session_id in line:
                    if len(str_log) == 0:
                        print(str_log)
                    else:
                        outfile.write(
                            "\n\n\nПользователь " + str_log[0] + ". Начало сессии " + session_id + "\n" + prev_line)
                if '|  | retrieveInventory|' + session_id + '|null|null|exit|' in line:
                    inventory_text1 = line
                    inventory_text = inventory_text1.split(';')
                    outfile.write('--------------------------------\n')
                    k = 8
                    summa_i = 0
                    if int(inventory_text[1]) == 2:
                        outfile.write('Ошибка:' + inventory_text[3] + '\n')
                    elif len(inventory_text) > 8:
                        for i in range(8):
                            a = int(inventory_text[k + 3])
                            b = int(inventory_text[k + 4]) / 100
                            ab1 = a * b
                            outfile.write(
                                inventory_text[k] + ' ' + str(a) + ' x ' + str(b) + ' = ' + str(ab1) +
                                inventory_text[k + 5] + '\n')
                            i += 1
                            k += 8
                            summa_i += ab1
                        outfile.write('--------------------------------\n')
                        outfile.write("ИТОГО " + str(summa_i) + 'KZT\n')
                if '| Glory.ManagerAPI |  | startDispenseTransaction|' + session_id + '|null|null|entry|' in line:
                    a = line.split("|")
                    b = a[-1].split(';')
                    aa = int(b[0]) / 100
                    outfile.write("\nНачало транзакции. Выдача. Сумма " + str(aa) + ".\n")
                if 'Glory.ManagerAPI |  | startDepositTransaction|' + session_id + '|null|null|entry|' in line:
                    outfile.write("\nНачало транзакции. Прием\n")
                if 'Glory.ManagerAPI |  | cashInStart|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nНачало операции по приему\n")
                if 'Glory.ManagerAPI |  | cashIn|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nПрием\n")
                    elif '|exit' in line:
                        deposit = line.split(';')
                        n = int(deposit[1])
                        del deposit[0:3]
                        if n == 1:
                            outfile.write('Предупреждение: ' + deposit[0] + deposit[1] + deposit[2] + deposit[3] + '\n')
                        elif n == 2 or n == 3:
                            outfile.write('Ошибка: ' + deposit[0] + deposit[1] + deposit[2] + deposit[3] + '\n')
                        del deposit[0:5]
                        c = int(len(deposit) / 5)
                        outfile.write('--------------------------------\n')
                        k = 0
                        for i in range(c):
                            a = int(deposit[k])
                            b = int(deposit[k + 1]) / 100
                            ab1 = a * b
                            if a > 0:
                                outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                            i += 1
                            k += 5
                            cash_end.append(ab1)
                        outfile.write('--------------------------------\n')
                if 'Glory.ManagerAPI |  | cashInRollback|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nОтмена\n")
                    elif '|exit|':
                        rollback = line.split(';')
                        n = int(rollback[1])
                        del rollback[0:3]
                        if n == 2 or n == 3:
                            outfile.write('Ошибка: ' + rollback[0] + rollback[1] + rollback[2] + rollback[3] + '\n')
                        elif n == 1:
                            outfile.write(
                                'Предупреждение: ' + rollback[0] + rollback[1] + rollback[2] + rollback[3] + '\n')
                        del rollback[0:5]
                        c = int(len(rollback) / 5)
                        outfile.write('--------------------------------\n')
                        k = 0
                        for i in range(c):
                            a = int(rollback[k])
                            b = int(rollback[k + 1]) / 100
                            ab1 = a * b
                            if a > 0:
                                outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                            i += 1
                            k += 5
                        if c == 0:
                            pass
                        else:
                            summa_r = int(rollback[0]) / 100
                            outfile.write('--------------------------------\n')
                            outfile.write('Отменено ' + str(summa_r) + 'KZT\n')
                if 'Glory.ManagerAPI |  | reset|' + session_id + "|null|" in line:
                    if '|entry|' in line:
                        outfile.write("\nСброс\n")
                    elif '|exit|' in line:
                        reset = line.split(';')
                        n = int(reset[1])
                        del reset[0:3]
                        if n == 2 or n == 3:
                            outfile.write('Ошибка: ' + reset[0] + reset[1] + reset[2] + reset[3])
                        elif n == 1:
                            outfile.write(
                                'Предупреждение: ' + reset[0] + reset[1] + reset[2] + reset[3])
                if 'Glory.ManagerAPI |  | cashInEnd|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nЗавершение операции по приему\n")
                if 'Glory.ManagerAPI |  | cashInEnd|' + session_id in line:
                    if 'null|exit' in line:
                        summar = 0
                        for csum in cash_end:
                            summar += int(csum)
                        cash_end = []
                        outfile.write('--------------------------------\n')
                        outfile.write('ИТОГО ПРИНЯТО ' + str(summar / 1) + 'KZT\n')
                        outfile.write('--------------------------------\n')
                if 'Glory.ManagerAPI |  | endTransaction|' + session_id in line:
                    if "|null|entry|" in line:
                        outfile.write("\nЗавершение транзакции\n")
                if 'Glory.ManagerAPI |  | retrieveInventory|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nИнвентаризация\n")
                if 'Glory.ManagerAPI |  | generateMix|' + session_id in line:
                    if '|entry|' in line:
                        outfile.write("\nСмешивания по номиналам\n")
                if 'Glory.ManagerAPI |  | generateMix|' + session_id in line:
                    if '|null|exit' in line:
                        generate_mix = line.split(';')
                        del generate_mix[0:8]
                        c = int(len(generate_mix) / 5)
                        if c != 0:
                            outfile.write('--------------------------------\n')
                            k = 0
                            for i in range(c):
                                a = int(generate_mix[k])
                                b = int(generate_mix[k + 1]) / 100
                                ab1 = a * b
                                if a > 0:
                                    outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                                i += 1
                                k += 5
                        outfile.write('--------------------------------\n')

                if 'Glory.ManagerAPI |  | dispense|' + session_id in line:
                    if "|entry" in line:
                        outfile.write("\nВыдача\n")
                    elif "|null|exit|" in line:

                        dispense = line.split(';')
                        n = int(dispense[1])
                        del dispense[0:3]
                        if n == 1:
                            outfile.write(
                                'Предупреждение: ' + dispense[0] + dispense[1] + dispense[2] + dispense[3] + '\n')
                        elif n == 2 or n == 3:
                            outfile.write('Ошибка: ' + dispense[0] + dispense[1] + dispense[2] + dispense[3] + '\n')
                        del dispense[0:5]
                        c = int(len(dispense) / 5)
                        if c != 0:
                            outfile.write('--------------------------------\n')
                            k = 0
                            dis_sum = 0.0
                            for i in range(c):
                                a = int(dispense[k])
                                b = int(dispense[k + 1]) / 100
                                ab1 = a * b
                                if a > 0:
                                    outfile.write(str(a) + " x " + str(b) + " = " + str(ab1) + 'KZT\n')
                                i += 1
                                k += 5
                                dis_sum += ab1
                        else:
                            dis_sum = 0
                        outfile.write('--------------------------------\n')
                        outfile.write('Выдано ' + str(dis_sum) + 'KZT\n')
                if 'Glory.ManagerAPI |  | logoff|' + session_id + '|null|null|entry|' in line:
                    outfile.write("\nЗакрытие сессии " + session_id + "\n")
                if 'Glory.ManagerAPI |  | emptyDevice|' + session_id + '|null|' in line:
                    outfile.write("\nРазгрузка устройства\n")
                if 'Glory.ManagerAPI |  | emptyDevice|' + session_id + '|null|null|exit|' in line:
                    sum_ed = 0
                    for esum in empty_end:
                        sum_ed += int(esum)
                    empty_end = []
                    outfile.write('--------------------------------\n')
                    outfile.write('ИТОГО ВЫГРУЖЕНО ' + str(sum_ed / 100) + 'KZT\n')
                    outfile.write('--------------------------------\n')
                if 'Glory.ManagerAPI |  | listDevices|' not in line:
                    if 'Glory.ManagerAPI |  | retrieveDeviceState|' not in line:
                        outfile.write(line)
    return 1
