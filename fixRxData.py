import glob
import re
import codecs
import pathlib

# 定数の定義
NUM_HOUR = 0
NUM_MINUTE = 1
NUM_SECOND = 2
NUM_VALUE = 3


# データを出力する形に変換する関数
def chg_output_str(tm):
    if tm < 10:
        output_tm = '0' + str(tm)
    else:
        output_tm = str(tm)
    return output_tm


# 時間を秒単位に変換する関数
def time_to_sec(data):
    time_sec = data[NUM_HOUR] * 3600 + data[NUM_MINUTE] * 60 + data[NUM_SECOND]
    return time_sec


# 以前の時間と現在の時間の差を計算する関数
def time_diff(now_time, bfr_time):
    diff = now_time - bfr_time
    return diff


# 秒の10の位が変わったかどうかを判断する関数，変わった場合にTrueを返す
def chg_time(now_time, ct_time):
    check = now_time - ct_time
    if check > 0:
        return True
    else:
        return False


# データが格納されている配列を出力する文字列に変換するための関数
def output_data_str(data):
    o_f_hour = chg_output_str(data[NUM_HOUR])
    o_f_minute = chg_output_str(data[NUM_MINUTE])
    o_f_sec = chg_output_str(data[NUM_SECOND])
    f_val = data[NUM_VALUE]
    output_data = o_f_hour + ':' + o_f_minute + ':' + o_f_sec + ',' + str(f_val) + '\n'
    return output_data


# RxDataに格納されているファイルおよびディレクトリのパスを探索する
f_list = glob.glob("RxData/**", recursive=True)

# データが格納されているファイルかディレクトリかを判断するために使用する正規表現
pattern_file = r'.*/192.168.100.[0-9]*_csv.log$'
pattern_dir = r'.*/2009([0-9]*)/[0-9]*$'
# データから時間と値を抜き取るための正規表現
pattern_time = r'^([0-9]+):([0-9]+):([0-9]+),(-?[0-9]+),.*'
# ファイルとディレクトリのパスをそれぞれ格納する配列
f_data = []
direc = []

# ファイルかディレクトリか判断
for sep in f_list:
    res_file = re.match(pattern_file, sep)
    res_dir = re.match(pattern_dir, sep)
    if res_file:
        f_data.append(sep)
    if res_dir:
        direc.append(sep)

# fixData下にディレクトリを生成
for d in direc:
    d = 'fixData/'+d
    p = pathlib.Path(d)
    p.mkdir(parents=True)

# データ処理を行う
for f in f_data:
    # ファイルを開く
    original_file = codecs.open(f, 'r', encoding='utf8', errors='ignore')
    # データを1行ずつ格納
    f_lines = original_file.readlines()
    # データ数が12時間以上分ない場合は処理をしない
    if len(f_lines) < 21600:
        continue

    # [0];Hour, [1];Minute, [2];Second; [3];Value
    # bfr;前のデータ
    bfr = [0, 0, 0, 0]
    # tmp;10の位が変わったタイミングのデータ
    tmp = [0, 0, 0, 0]
    # now;現在のデータ
    now = [0, 0, 0, 0]
    # 編集したデータを格納する配列
    dat_10s = []

    i = 2
    cnt = 0
    ab = 0
    while i < len(f_lines):
        # Group(1):hour
        # Group(2):minute
        # Group(3):sec
        # Group(4):value
        # データを拾う
        res = re.match(pattern_time, f_lines[i])
        # データが拾えたら処理を行う
        if res:
            # nowにそれぞれデータを格納
            now = [int(res.group(1)), int(res.group(2)), int(res.group(3)), int(res.group(4))]
            # nowの時間を秒単位に変換
            now_time_sec = time_to_sec(now)
            # 秒の10の位が変わったかの真偽値
            is_chg_sec_ten_place = chg_time(now_time_sec, cnt)
            # 最初のデータ
            if cnt == 0:
                # 以前に10の位が変わった時の時間（ここでは0s）
                tmp_time_sec = time_to_sec(tmp)
                # 現在の時間と以前に10の位が変わった時の時間の比較
                diff_time = time_diff(now_time_sec, tmp_time_sec)
                if 0 <= diff_time <= 1:  # データ欠損がない場合
                    dat_10s.append(output_data_str(now))
                    tmp = now
                    bfr = now
                    cnt += 10
                elif 2 <= diff_time <= 9:  # 数秒程度のデータ欠損の処理
                    now[NUM_SECOND] -= now[NUM_SECOND] % 10
                    dat_10s.append(output_data_str(now))
                    tmp = now
                    bfr = now
                    cnt += 10

                else:  # 数十秒以上のデータ欠損の例外処理
                    tmp[NUM_VALUE] = int(0.5 * (now[NUM_VALUE] + bfr[NUM_VALUE]))
                    error_cnt = 0
                    while error_cnt < (diff_time * 0.1):
                        if tmp[NUM_SECOND] < 50:
                            tmp[NUM_SECOND] += 10
                        else:
                            tmp[NUM_SECOND] -= 50
                            tmp[NUM_MINUTE] += 1
                            if tmp[NUM_MINUTE] == 60:
                                tmp[NUM_MINUTE] = 0
                                tmp[NUM_HOUR] += 1
                        dat_10s.append(output_data_str(tmp))
                        error_cnt += 1
                        cnt += 10
                    bfr = tmp

            if is_chg_sec_ten_place:
                # 秒の10の位が変わった
                # 処理
                if 2 <= (now[NUM_SECOND] % 10) <= 9:  # 通常処理
                    now[NUM_SECOND] -= now[NUM_SECOND] % 10
                    now[NUM_VALUE] = int(0.5 * (now[NUM_VALUE] + bfr[NUM_VALUE]))
                    now_time_sec = time_to_sec(now)
                tmp_time_sec = time_to_sec(tmp)
                diff_time = time_diff(now_time_sec, tmp_time_sec)
                if 9 <= diff_time <= 11:
                    dat_10s.append(output_data_str(now))
                    tmp = now
                    bfr = now
                    cnt += 10

                else:  # 例外処理（データ欠損対応）
                    tmp[NUM_VALUE] = int(0.5 * (now[NUM_VALUE] + bfr[NUM_VALUE]))
                    tmp[NUM_SECOND] -= tmp[NUM_SECOND] % 10
                    error_cnt = 0
                    while error_cnt < (diff_time * 0.1):
                        if tmp[NUM_SECOND] < 50:
                            tmp[NUM_SECOND] += 10
                        else:
                            tmp[NUM_SECOND] -= 50
                            tmp[NUM_MINUTE] += 1
                            if tmp[NUM_MINUTE] == 60:
                                tmp[NUM_MINUTE] = 0
                                tmp[NUM_HOUR] += 1
                        dat_10s.append(output_data_str(tmp))
                        error_cnt += 1
                        cnt += 10
                    bfr = tmp
            else:
                bfr = now
        i += 1

    original_file.close()
    # ファイルを出力
    exp_path = "fixData/"+f
    with open(exp_path, 'a', encoding='utf-8') as export_file:
        for j in dat_10s:
            export_file.write('{}'.format(j))

