import csv
import sys
import shutil

file_path=sys.argv[1]
new_path=file_path.replace(".csv", "_fixed.csv")


def fix_csv(file_path):
    try:
        with open(file_path, "r") as csvFile:
            newCSV=open(new_path,  "w", newline='\n')
            rows=csv.reader(csvFile, delimiter=";", lineterminator='\n')
            writer=csv.writer(newCSV)
            i=0
            for row in rows:
                i=i+1
                if i>7:
                    print(i)
                    writer.writerows(rows)
        newCSV.close()
        csvFile.close()
        shutil.move(new_path, "C:\\solarfarmdata\new_solar_csv")
    except Exception as e:
        print("Error occurred.  " ,e)
        
fix_csv(file_path)
