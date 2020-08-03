import glob
import re
import codecs
import pathlib


def chg_output_str(tm):
    if tm < 10:
        output_tm = '0' + str(tm)
    else:
        output_tm = str(tm)
    return output_tm


def time_to_sec(data):
    time_sec = data[0] * 3600 + data[1] * 60 + data[2]
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
    o_f_hour = chg_output_str(data[0])
    o_f_minute = chg_output_str(data[1])
    o_f_sec = chg_output_str(data[2])
    f_val = data[3]
    fix_data = o_f_hour + ':' + o_f_minute + ':' + o_f_sec + ',' + str(f_val) + '\n'
    return fix_data


f_list = glob.glob("RxData/**", recursive=True)
test_path = "RxData/200910/20091012/192.168.100.9_csv.log"

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

error_data_file = 0
error_loss_data = 0

for f in f_data:
    # ファイルを開く
    original_file = codecs.open(f, 'r', encoding='utf8', errors='ignore')
    f_lines = original_file.readlines()
    if len(f_lines) < 21600:
        error_data_file += 1
        continue

    # bfr
    bfr_hour = 0
    bfr_minute = 0
    bfr_sec = 0
    bfr_val = 0
    bfr_data = [bfr_hour, bfr_minute, bfr_sec, bfr_val]

    # tmp
    tmp_hour = 0
    tmp_minute = 0
    tmp_sec = 0
    tmp_val = 0

    # now
    now_hour = 0
    now_minute = 0
    now_sec = 0
    now_val = 0
    now_data = [now_hour, now_minute, now_sec, now_val]

    dat_10s = []
    erd = []
    error_sec = []
    error_minute = []

    fix_minute_cnt = 0

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
            now_hour = int(res.group(1))
            now_minute = int(res.group(2))
            now_sec = int(res.group(3))
            now_val = int(res.group(4))
            now_time_l = [now_hour, now_minute, now_sec, now_val]
            now_time_sec = time_to_sec(now_time_l)
            is_chg_sec_ten_place = chg_time(now_time_sec, cnt)
            if cnt == 0:
                tmp_time_l = [tmp_hour, tmp_minute, tmp_sec, tmp_val]
                tmp_time_sec = time_to_sec(tmp_time_l)
                diff_time = time_diff(now_time_sec, tmp_time_sec)
                if 0 <= diff_time <= 1:
                    dat_10s.append(output_data_str(now_time_l))
                    tmp_hour = now_hour
                    tmp_minute = now_minute
                    tmp_sec = now_sec
                    tmp_val = now_val

                    bfr_hour = now_hour
                    bfr_minute = now_minute
                    bfr_sec = now_sec
                    bfr_val = now_val
                    cnt += 10

                elif 2 <= diff_time <= 9:
                    now_sec -= now_sec % 10
                    now_time_l = [now_hour, now_minute, now_sec, now_val]
                    dat_10s.append(output_data_str(now_time_l))
                    tmp_hour = now_hour
                    tmp_minute = now_minute
                    tmp_sec = now_sec
                    tmp_val = now_val

                    bfr_hour = now_hour
                    bfr_minute = now_minute
                    bfr_sec = now_sec
                    bfr_val = now_val
                    cnt += 10

                else:
                    fix_val = int(0.5 * (now_val + bfr_val))
                    error_cnt = 0
                    while error_cnt < (diff_time * 0.1):
                        if tmp_sec < 50:
                            tmp_sec += 10
                        else:
                            tmp_sec -= 50
                            tmp_minute = tmp_minute + 1
                            if tmp_minute == 60:
                                tmp_minute = 0
                                tmp_hour += 1
                        tmp_time_l = [tmp_hour, tmp_minute, tmp_sec, fix_val]
                        dat_10s.append(output_data_str(tmp_time_l))
                        error_cnt += 1
                        cnt += 10
                    bfr_hour = tmp_hour
                    bfr_minute = tmp_minute
                    bfr_sec = tmp_sec
                    bfr_val = fix_val

            if is_chg_sec_ten_place:
                # 秒の10の位が変わった
                # 処理
                if 2 <= (now_sec % 10) <= 9:
                    now_sec -= now_sec % 10
                    now_val = int(0.5 * (now_val + bfr_val))
                    now_time_l = [now_hour, now_minute, now_sec, now_val]
                    now_time_sec = time_to_sec(now_time_l)
                tmp_time_l = [tmp_hour, tmp_minute, tmp_sec, tmp_val]
                tmp_time_sec = time_to_sec(tmp_time_l)
                diff_time = time_diff(now_time_sec, tmp_time_sec)
                if 9 <= diff_time <= 11:
                    now_time_l = [now_hour, now_minute, now_sec, now_val]
                    dat_10s.append(output_data_str(now_time_l))
                    tmp_hour = now_hour
                    tmp_minute = now_minute
                    tmp_sec = now_sec
                    tmp_val = now_val

                    bfr_hour = now_hour
                    bfr_minute = now_minute
                    bfr_sec = now_sec
                    bfr_val = now_val
                    cnt += 10

                else:
                    fix_val = int(0.5 * (now_val + bfr_val))
                    tmp_sec -= tmp_sec % 10
                    error_cnt = 0
                    while error_cnt < (diff_time * 0.1):
                        if tmp_sec < 50:
                            tmp_sec += 10
                        else:
                            tmp_sec -= 50
                            tmp_minute = tmp_minute + 1
                            if tmp_minute == 60:
                                tmp_minute = 0
                                tmp_hour += 1
                        tmp_time_l = [tmp_hour, tmp_minute, tmp_sec, fix_val]
                        dat_10s.append(output_data_str(tmp_time_l))
                        error_cnt += 1
                        cnt += 10
                    bfr_hour = tmp_hour
                    bfr_minute = tmp_minute
                    bfr_sec = tmp_sec
                    bfr_val = fix_val

            else:
                bfr_hour = now_hour
                bfr_minute = now_minute
                bfr_sec = now_sec
                bfr_val = now_val
        i += 1

    original_file.close()

    # print('file is : {}'.format(f))
    # print("dat_10s:{0}".format(len(dat_10s)))
    if len(dat_10s) != 8640:
        error_loss_data += 1

    exp_path = "fixData/"+f
    with open(exp_path, 'a', encoding='utf-8') as export_file:
        for j in dat_10s:
            export_file.write('{}'.format(j))


print(error_data_file, error_loss_data)
"""
print("-------------")
for n in dat_10s:
    print(n)
print('-------------')
for v in erd:
    print(v)
print('-------------')
for z in error_minute:
    print(z)
"""
