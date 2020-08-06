import glob
import re
import csv

f_list = glob.glob("fixData/RainData/**", recursive=True)
pattern_file = r'.*/[0-9]*_rain\.csv$'
f_name_list = []

for sep in f_list:
    res_file = re.match(pattern_file, sep)
    if res_file:
        f_name_list.append(sep)

# 最大値，刻み幅の設定
max_val = 150
tau = 3
size_list = int(max_val/tau)

# 理想の総データ数
num_all_data = 175680

# 各階級の度数，累積度数を格納する配列
freq_distribution = [0 for i in range(size_list)]
cu_distribution = [0 for i in range(size_list)]
# 出力用のデータを格納する配列，パス
output_data = []
output_path = 'fixData/RxRainCuDistribution.txt'

for file_name in f_name_list:
    with open(file_name) as file:
        reader = csv.reader(file)
        for data in reader:
            cnt = 0
            tmp = max_val
            val = float(data[1])
            while tmp - val > tau:
                tmp -= tau
                cnt += 1
            freq_distribution[cnt] += 1

cu = 0
cnt = 0
tmp = 0
for freq in freq_distribution:
    ds = 100 * freq/num_all_data
    cu += ds
    cu_distribution[cnt] = cu
    tmp = max_val - (tau * (cnt+1))
    if cnt == 49:
        output_data.append([tmp, 100])
    else:
        output_data.append([tmp, cu])
    cnt += 1

output_data.reverse()

with open(output_path, 'w') as exp:
    writer = csv.writer(exp)
    writer.writerows(output_data)
