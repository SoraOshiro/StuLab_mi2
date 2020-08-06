import glob
import re
import csv

f_list = glob.glob("fixData/RxData/**", recursive=True)
pattern_file_18 = r'.*/192\.168\.100\.9_csv\.log$'
pattern_file_26 = r'.*/192\.168\.100\.11_csv\.log$'
f_name_list_18 = []
f_name_list_26 = []

for sep in f_list:
    res_file_18 = re.match(pattern_file_18, sep)
    res_file_26 = re.match(pattern_file_26, sep)
    if res_file_18:
        f_name_list_18.append(sep)
    if res_file_26:
        f_name_list_26.append(sep)

f_name_list = [f_name_list_18, f_name_list_26]

max_val = -40
min_val = -130
r = max_val - min_val
tau = 3
size_list = int(r/tau)
print(size_list)
output_path = ['gp/RxData18GHzCuDistribution.txt', 'gp/RxData26GHzCuDistribution.txt']
f_cnt = 0
num_all_data = 1054080

for file_list in f_name_list:
    freq_distribution = [0 for i in range(size_list)]
    cu_distribution = [0 for i in range(size_list)]
    output_data = []

    for file_name in file_list:
        with open(file_name) as file:
            reader = csv.reader(file)
            for data in reader:
                cnt = 0
                tmp = max_val
                val = float(data[1])
                while (tmp - val > tau) and (tmp != min_val):
                    tmp -= tau
                    cnt += 1
                if cnt == 20:
                    continue
                freq_distribution[cnt] += 1

    freq_distribution.reverse()

    cu = 0
    cnt = 0
    tmp = 0
    for freq in freq_distribution:
        ds = 100 * freq/num_all_data
        cu += ds
        cu_distribution[cnt] = cu
        tmp = min_val + (tau * (cnt+1))
        if cnt == 29:
            output_data.append([tmp, 100])
        else:
            output_data.append([tmp, cu])
        cnt += 1

    output_data.reverse()
    with open(output_path[f_cnt], 'w') as exp:
        writer = csv.writer(exp)
        writer.writerows(output_data)

    f_cnt += 1
