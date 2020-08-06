import glob
import re
import csv

f_list = glob.glob("RainData/**", recursive=True)
pattern_file = r'.*/[0-9]*_rain\.csv$'
pattern_dir = r'RainData/[0-9]+$'
f_name_list = []
direc = []


max_val = 150
tau = 3
size_list = int(max_val/tau)

FreqDistribution = [0 for i in range(size_list)]





