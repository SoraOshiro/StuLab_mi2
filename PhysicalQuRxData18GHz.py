import csv
import re
import glob

f_d_list = glob.glob("fixData/RxData/**", recursive=True)
pattern_file = r'.*/192\.168\.100\.9_csv\.log$'
file_name_list = []

for sep in f_d_list:
    res_file = re.match(pattern_file, sep)
    if res_file:
        file_name_list.append(sep)

for file_name in file_name_list:
    export_data_list = []
    with open(file_name) as ori_file:
        ori_data = csv.reader(ori_file)
        # 18GHzのRxDataの処理
        for d in ori_data:
            val = int(d[1])
            if val < 0:
                val += 256
            val = int(val/2 - 121)
            d[1] = str(val)
            export_data_list.append(d)

    with open(file_name, 'w') as exp_file:
        exp_data = csv.writer(exp_file)
        exp_data.writerows(export_data_list)

