import sys
import csv
import chardet
from glob import glob
from typing import List
import time
from datetime import datetime, timedelta, date
import shutil
import os

def predict_encoding(file_path, n_lines=20):
    '''Predict a file's encoding using chardet'''
    import chardet

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

def get_reader(csvfile, delimiter=";"):
    dialect1 = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    if delimiter:
        dialect1.delimiter = delimiter
    return csv.reader(csvfile, dialect1)


def csv2table(csv_file, enc, delimiter=";"):
    with open(csv_file, encoding=enc, newline='') as csvfile1:
            reader1 = get_reader(csvfile1, delimiter=delimiter)
            table = [row for row in reader1 if row!=[] and row[0]!='']
            for row in table:
                row[0] = row[0].zfill(8)
                row[2] = row[2].zfill(8)
            return table

def HHMMSS(HHMM,delta_minutes=0,format="%H:%M"):
    hhmm = datetime.strptime(HHMM, format)
    hhmm+=timedelta(minutes=delta_minutes)
    return hhmm.strftime("%H:%M:%S")



def lt(time1,time2,form="%H:%M:%S"):
    # return time.strptime(time1.zfill(8), form) < time.strptime(time1.zfill(8), form)
    return time1 < time2

def week_table_to_playlists(week_table="week_table.csv",
                            channel="1plus1.analog",
                            rolik="mpg",
                            duration=5,n_repeat=2,
                            obligate_sign="*",
                            wdays=["понедельник","вторник","среда","четверг","пятница","суббота","воскресенье"],
                            start_date=None,
                            date_format="%Y.%m.%d"):
    encoding = predict_encoding(week_table)
    csvs = glob("*.csv")
    with  open(week_table, encoding=encoding, newline='') as week_csv:
        table = list(get_reader(week_csv))[1:]
        for wd in range(7):
            if start_date:
                yyyymmdd = datetime.strptime(start_date, date_format)
                week_day = yyyymmdd.weekday()
                if wd < week_day:
                    continue
                yyyymmdd += timedelta(days=wd-week_day)
                YYMMDD = yyyymmdd.strftime(date_format)
                file_name = f"{channel}.{YYMMDD}.csv"
            else:
                file_name = f"{channel}.{wd+1}.{wdays[wd]}.csv"
            with open(file_name,"w",newline='') as daycsv:
                writer = csv.writer(daycsv, delimiter=';')
                for row in table:
                    for _ in range(n_repeat):
                        block_start = HHMMSS(row[wd],-1)
                        play_time = HHMMSS(row[wd])
                        secs = str(duration*n_repeat)
                        block_id = ((row[wd].replace(':',''))*2)[:6]
                        writer.writerow([block_start,rolik,play_time,secs,block_id,obligate_sign])
                    print(row[wd])

def mix_csvs(argv, outcsv=None):
    if len(argv)>2:
        return None
    if argv == None:
        csv_files = glob("*.csv")[:2]
    else:
        csv_files = argv
    encs = map(predict_encoding, csv_files)
    tables = [csv2table(csv_file,enc) for csv_file,enc in zip(csv_files,encs)]

    table1, table2 = map(lambda t: list(reversed(t)), tables)

    mixed_table = []


    while table1 and table2:
        row1, row2 = table1[-1], table2[-1]
        time1, time2 = row1[0], row2[0]

        if lt(time1,time2):
            if row1:
                row1 = table1.pop()
                mixed_table.append(row1)
                print("tbl1", row1)
        else:
            if row2:
                row2=table2.pop()
                mixed_table.append(row2)
                print("tbl2", row2)

    mixed_table+=reversed(table2) if table2 else reversed(table1)

    out = 'out.csv'
    if outcsv:
        with open(out, 'w', newline='') as f:
            writer = csv.writer(f,delimiter=';')
            writer.writerows(mixed_table)
    else:
        with open(out, 'w', newline='') as f:
            writer = csv.writer(f,delimiter=';')
            writer.writerows(mixed_table)
        shutil.copy(argv[0], f"{argv[0]}.bak")
        os.remove(argv[0])
        shutil.copy(out,argv[0])
        os.remove(out)


if __name__ == "__main__":
    week_table_to_playlists(channel="1plus1.analog", rolik="koduvanya_11_ostatochno_28_sichnya")
    mix_csvs(["1plus1.analog.2020.01.18.csv",
              "1plus1.analog.6.суббота.csv"])
    mix_csvs(["1plus1.analog.2020.01.19.csv",
              "1plus1.analog.7.воскресенье.csv"])

    week_table_to_playlists(channel="TET.analog", rolik="koduvanya_28_sichnya_tet",start_date="2020.01.17")

    week_table_to_playlists(channel="twoplustwo.analog", rolik="koduvanya_sd_2")
    mix_csvs(["twoplustwo.analog.2020.01.18.csv",
              "twoplustwo.analog.6.суббота.csv"])
    mix_csvs(["1plus1.analog.2020.01.19.csv",
              "twoplustwo.analog.7.воскресенье.csv"])



