from os import listdir, system
from os.path import isfile, join
from pandas import read_csv, DataFrame
from datetime import datetime, timedelta

# Input
# The .fit file that needs heart rate should be located in ./input/fit/.
# The .csv file(s) from ecglogger should be located in ./input/ecglogger/.
# If you want to use a subfolder within the input folders, replace subfolder_name. Otherwise use "".
# A subfolder will also be created in the output folder

subfolder_name = "240131/"
fitcsv_path = "FitSDKRelease_21.158.00" # Path to FitSDK (Download: https://developer.garmin.com/fit/fitcsvtool/)
# timezone = timezone("Europe/Berlin")

# Get .fit filename
fit_path = f"./input/fit/{subfolder_name}"
fit_file = [f for f in listdir(fit_path) if isfile(join(fit_path, f))]
for f in fit_file:
    if not f.endswith(".fit"): fit_file.remove(f)
print(fit_file)

# Get ecglogger filenames
ecg_path = f"./input/ecglogger/{subfolder_name}"
ecg_file = [f for f in listdir(ecg_path) if isfile(join(ecg_path, f))]
for f in ecg_file:
    if not f.endswith(".csv"): ecg_file.remove(f)
print(ecg_file)

# Convert .fit to .csv
system(f"java -jar ./{fitcsv_path}/java/FitCSVTool.jar {fit_path}{fit_file[0]}")

# Parse fit
original = read_csv(f"{fit_path}{fit_file[0].replace(".fit",".csv")}", sep=",", low_memory=False)
df_original = DataFrame(original)

# Parse and merge ecglogger csv records

df_no = 0
dataframes = []
rows = []
for record in ecg_file:
    f = open(f"{ecg_path}{record}")
    for row in f:
        if len(row.split(",")) < 3 or row.split(",")[0] == "time": continue # erase rows without hr data
        else: 
            if row.split(",")[2] == "": continue # erase leftover rows without hr data
            else:
                rows.append([datetime.fromtimestamp((int(row.split(",")[0]) // 1_000_000_000)), row.split(",")[2]])

print(rows[:20])

# # Garmin Epoch Time: 1989–12–31T00:00:00Z (https://developer.garmin.com/fit/cookbook/decoding-activity-files/#:~:text=Timestamps%20in%20FIT%20messages%20are,in%20the%20user's%20local%20timezone.)
# print("TEST TIMESTAMP")
# print(datetime.fromtimestamp(1106836735))
# zwift = 1107252091
# print(f"zwift = {zwift}")
# print(datetime.fromtimestamp(zwift))
# print(datetime(2025, 1, 31, 11, 1, 0) - timedelta(seconds=zwift))
# ecg = 1738317622493314701
# s_ecg = ecg // 1_000_000_000
# print(datetime.fromtimestamp(s_ecg))
# print(f"ecg = {ecg}")


df = DataFrame(rows, columns=["time", "hr"])
df.to_csv(f"./output/hr.csv")
