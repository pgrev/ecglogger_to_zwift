# ecglogger_to_zwift

Adds heart rate data from ECGlogger (https://www.ecglogger.com/) records to Zwift (https://www.zwift.com/) activity (.fit)

## **Next Steps:**

* Bug: when running the program twice, csv in input is bring used instead of .fit
* Logging implementation
* Error handling
* Testing

## **How to use:**

1. Download FitCSVTool from the Garmin Developer Website (https://developer.garmin.com/fit/fitcsvtool/)
2. Unpack the FitCSVTool in the root directory of the application
3. Export Zwift Activity-File (.fit)
   * Login to your account on https://www.zwift.com/
   * Find the activity, click the gear icon -> "Download Fit File"
4. Place the .fit file in ./input/fit/ `<subfolder>`
5. Place the .csv file(s) aka recording from ECGlogger in ./input/ecglogger/ `<subfolder>`
6. run `ecglogger_to_zwift.py`
