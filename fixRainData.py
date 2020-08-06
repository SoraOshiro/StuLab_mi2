import csv
import glob
import re
import pathlib

f_list = glob.glob("RainData/**", recursive=True)
pattern_file = r'.*/[0-9]*_rain\.csv$'
pattern_dir = r'RainData/[0-9]+$'
f_name_list = []
direc = []

for sep in f_list:
    res_file = re.match(pattern_file, sep)
    res_dir = re.match(pattern_dir, sep)
    if res_file:
        f_name_list.append(sep)
    if res_dir:
        direc.append(sep)

for di in direc:
    di = 'fixData/'+di
    p = pathlib.Path(di)
    p.mkdir(parents=True)


# 欠損csvファイル数
loss_csv_file = len(direc)-len(f_name_list)
for ori_file_name in f_name_list:
    # 出力用のパスとデータ格納用の配列を作成
    export_path = 'fixData/' + ori_file_name
    export_data = []
    with open(ori_file_name) as ori_file:
        reader = csv.reader(ori_file)  # csv形式で開く
        cnt = 0
        for r in reader:
            # 最初の2列は飛ばす
            if cnt < 2:
                cnt += 1
                continue
            # rebootなど途中で文字列が入った時も処理しない
            if len(r) != 2:
                cnt += 1
                continue
            r[1] = str(int(r[1]) * 0.0083333 * 60)
            export_data.append(r)
            cnt += 1

    # データか12時間以上分ない場合は出力の処理を行わない
    if cnt < 720:
        continue

    # csv形式で出力
    with open(export_path, 'w') as exp_file:
        writer = csv.writer(exp_file)
        writer.writerows(export_data)

