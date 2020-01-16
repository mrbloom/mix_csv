import sys
import csv
import chardet
from glob import glob
from typing import List
import time
from datetime import datetime, timedelta

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

def HHMMSS(HHMM,delta_minutes,format="%H:%M"):
    hhmm = datetime.strptime(HHMM, format)
    if delta_minutes:
        hhmm+=timedelta(minutes=delta_minutes)
    return hhmm.strftime("%H:%M:%S")



def lt(time1,time2,form="%H:%M:%S"):
    # return time.strptime(time1.zfill(8), form) < time.strptime(time1.zfill(8), form)
    return time1 < time2

def week_table_to_playlists(week_table="week_table.csv",channel="1plus1.analog",rolik="mpg",n=2,druration=5,start_date=datetime.today()):
    encoding = predict_encoding(week_table)
    csvs = glob("*.csv")
    with  open(week_table, encoding=encoding, newline='') as week_csv:
        table = list(get_reader(week_csv))[1:]
        for wd in range(7):

            with open(f"{channel}.{str(wd).zfill(2)}.csv","w",newline='') as daycsv:
                writer = csv.writer(daycsv, delimiter=';')
                for row in table:
                    for _ in range(n):
                        start = HHMMSS(row[wd],-10)
                        writer.writerow([start,rolik,row[wd]])
                    print(row[wd])



if __name__ == "__main__":
    # if len(sys.argv)==3:
    #     csv_files: List[str] = [sys.argv[1], sys.argv[2]]
    # else:
    #     csv_files: List[str] = glob("*.csv")[:2]
    # encs = map(predict_encoding, csv_files)
    # tables = [csv2table(csv_file,enc) for csv_file,enc in zip(csv_files,encs)]
    # # print(tables)
    #
    # table1, table2 = map(lambda t: list(reversed(t)), tables)
    #
    # mixed_table = []
    #
    #
    # while table1 and table2:
    #     row1, row2 = table1[-1], table2[-1]
    #     time1, time2 = row1[0], row2[0]
    #
    #     if lt(time1,time2):
    #         if row1:
    #
    #             row1 = table1.pop()
    #             mixed_table.append(row1)
    #             print("tbl1", row1)
    #     else:
    #         if row2:
    #
    #             row2=table2.pop()
    #             mixed_table.append(row2)
    #             print("tbl2", row2)
    #
    #
    # mixed_table+=reversed(table2) if table2 else reversed(table1)
    #
    # with open('out.csv', 'w', newline='') as f:
    #     writer = csv.writer(f,delimiter=';')
    #     writer.writerows(mixed_table)

    # print(mixed_table)
    week_table_to_playlists()





