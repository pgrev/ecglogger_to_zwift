from os import listdir, system
import csv
from os.path import isfile, join
from datetime import datetime

# Input
# The .fit file that needs heart rate should be located in ./input/fit/.
# The .csv file(s) from ecglogger should be located in ./input/ecglogger/.
# If you want to use a subfolder within the input folders, replace subfolder_name. Otherwise use "".
# A subfolder will also be created in the output folder

subfolder_name = f"{input("Enter subfolder name -")}/"
fitcsv_path = "FitSDKRelease_21.158.00" # Path to FitSDK (Download: https://developer.garmin.com/fit/fitcsvtool/)

# Get .fit filename
fit_path = f"./input/fit/{subfolder_name}"
fit_file = [f for f in listdir(fit_path) if isfile(join(fit_path, f))]
for f in fit_file:
    if not f.endswith(".fit"): fit_file.remove(f)

# Get ecglogger filenames
ecg_path = f"./input/ecglogger/{subfolder_name}"
ecg_file = [f for f in listdir(ecg_path) if isfile(join(ecg_path, f))]
for f in ecg_file:
    if not f.endswith(".csv"): ecg_file.remove(f)

# Parse and merge ecglogger csv records
# Garmin Epoch Time: 1989–12–31T00:00:00Z (https://developer.garmin.com/fit/cookbook/decoding-activity-files/)

def convert_ecg_timestamp_to_zwift_timestamp(ecg_timestamp):
    garmin_epoch_start = datetime(1989, 12, 31, 0, 0, 0)
    ecg_seconds_utc = int(ecg_timestamp) // 1_000_000_000 -3600 # nanoseconds to seconds, UTC+1 to UTC (-1 hour)
    garmin_epoch_unix_seconds_utc = int(datetime.timestamp(garmin_epoch_start)) # Garmin epoch (1989-12-31 00:00:00 UTC) in Unix time
    zwift_timestamp = ecg_seconds_utc - garmin_epoch_unix_seconds_utc
    return zwift_timestamp

hr_rows = {}
for record in ecg_file:
    f = open(f"{ecg_path}{record}")
    for row in f:
        if len(row.split(",")) < 3 or row.split(",")[0] == "time": continue # erase rows without hr data
        else: 
            if row.split(",")[2] == "": continue # erase leftover rows without hr data
            else:
                zwift_timestamp = convert_ecg_timestamp_to_zwift_timestamp(row.split(",")[0])
                hr_rows[zwift_timestamp] = row.split(",")[2]

# Convert .fit to .csv
system(f"java -jar ./{fitcsv_path}/java/FitCSVTool.jar {fit_path}{fit_file[0]}")

# Parse .fit
zwift_rows = []
f = open(f"{fit_path}{fit_file[0].replace(".fit",".csv")}")
for row in f:
    zwift_rows.append(row.split(","))

# Replace heart rate based on timestamp
hr_values = []
for row in zwift_rows:
    if row[0] == "Data" and row[2] == "record":
        try:
            row[25] = hr_rows[int(row[4].strip().replace('"', ''))]
            hr_values.append(int(row[25]))
        except:
            i = 1
            while True: # Replaces missing value with next available value
                try:
                    row[25] = hr_rows[int(row[4].strip().replace('"', ''))+i]
                    hr_values.append(int(row[25]))
                    break
                except:
                    i += 1
                    continue

# Calculate and enter average and max heart rate
average_hr = sum(hr_values) // len(hr_values)
max_hr = max(hr_values)

for row in zwift_rows[-7:-1]:
    if row[0] == "Data" and "avg_heart_rate" in row:  
        index = row.index("avg_heart_rate") + 1
        row[index] = average_hr

for row in zwift_rows[-7:-1]:
    if row[0] == "Data" and "max_heart_rate" in row:
        index = row.index("max_heart_rate") + 1
        row[index] = max_hr

# remove "-characters from each field
for row in zwift_rows: 
    for i in range(len(row)):
        row[i] = str(row[i]).strip().replace('"', '')

output_path = f"./output/{subfolder_name}{fit_file[0].replace(".fit","_with_heartrate.csv")}"
system(f"mkdir -p ./output/{subfolder_name}")
with open(output_path, "w") as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    for row in zwift_rows:
        writer.writerow(row)

# Convert .csv to .fit
system(f"java -jar ./{fitcsv_path}/java/FitCSVTool.jar -c {output_path} {output_path.replace(".csv",".fit")}")