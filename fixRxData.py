import glob
import re
import codecs
import pathlib

# 定数の定義
NUM_HOUR = 0
NUM_MINUTE = 1
NUM_SECOND = 2
NUM_VALUE = 3


def chg_output_str(tm):
    if tm < 10:
        output_tm = '0' + str(tm)
    else:
        output_tm = str(tm)
    return output_tm


def time_to_sec(data):
    time_sec = data[NUM_HOUR] * 3600 + data[NUM_MINUTE] * 60 + data[NUM_SECOND]
    return time_sec


def time_diff(now_time, bfr_time):
    diff = now_time - bfr_time
    return diff


def chg_time(now_time, ct_time):
    check = now_time - ct_time
    if check > 0:
        return True
    else:
        return False


def output_data_str(data):
    o_f_hour = chg_output_str(data[NUM_HOUR])
    o_f_minute = chg_output_str(data[NUM_MINUTE])
    o_f_sec = chg_output_str(data[NUM_SECOND])
    f_val = data[NUM_VALUE]
    output_data = o_f_hour + ':' + o_f_minute + ':' + o_f_sec + ',' + str(f_val) + '\n'
    return output_data


f_list = glob.glob("RxData/**", recursive=True)

pattern_file = r'.*/192.168.100.[0-9]*_csv.log$'
pattern_dir = r'.*/2009([0-9]*)/[0-9]*$'
pattern_time = r'^([0-9]+):([0-9]+):([0-9]+),(-?[0-9]+),.*'

f_data = []
direc = []

for sep in f_list:
    res_file = re.match(pattern_file, sep)
    res_dir = re.match(pattern_dir, sep)
    if res_file:
        f_data.append(sep)
    if res_dir:
        direc.append(sep)

for d in direc:
    d = 'fixData/'+d
    p = pathlib.Path(d)
    p.mkdir(parents=True)


for f in f_data:
    # ファイルを開く
    original_file = codecs.open(f, 'r', encoding='utf8', errors='ignore')
    f_lines = original_file.readlines()
    if len(f_lines) < 21600:
        continue

    # bfr
    bfr = [0, 0, 0, 0]
    # tmp
    tmp = [0, 0, 0, 0]
    # now
    now = [0, 0, 0, 0]

    dat_10s = []

    # Group(1):hour
    # Group(2):minute
    # Group(3):sec
    # Group(4):value

    i = 2
    cnt = 0
    ab = 0
    while i < len(f_lines):
        res = re.match(pattern_time, f_lines[i])

        if res:
            now = [int(res.group(1)), int(res.group(2)), int(res.group(3)), int(res.group(4))]
            now_time_sec = time_to_sec(now)
            is_chg_sec_ten_place = chg_time(now_time_sec, cnt)
            if cnt == 0:
                tmp_time_sec = time_to_sec(tmp)
                diff_time = time_diff(now_time_sec, tmp_time_sec)
                if 0 <= diff_time <= 1:
                    dat_10s.append(output_data_str(now))
                    tmp = now
                    bfr = now
                    cnt += 10

                elif 2 <= diff_time <= 9:
                    now[NUM_SECOND] -= now[NUM_SECOND] % 10
                    dat_10s.append(output_data_str(now))
                    tmp = now
                    bfr = now
                    cnt += 10

                else:
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
                if 2 <= (now[NUM_SECOND] % 10) <= 9:
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

                else:
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

    exp_path = "fixData/"+f
    with open(exp_path, 'a', encoding='utf-8') as export_file:
        for j in dat_10s:
            export_file.write('{}'.format(j))

