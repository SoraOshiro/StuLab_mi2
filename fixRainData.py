import csv

file_path = 'RainData/20090616/20090616_rain.csv'
export_data = []

with open(file_path) as file:
    reader = csv.reader(file)
    cnt = 0
    for r in reader:
        if cnt < 2:
            cnt += 1
            continue
        r[1] = str(int(r[1]) * 0.0083333 * 60)
        export_data.append(r)
        cnt += 1

for i in export_data:
    print(i)
