import datetime
import pandas as pd

date_range = pd.date_range(start='2024-01-01', end='2024-01-10').date

#datesOnly=date_range.date

print(date_range)



# dates=[]
# material=[]


# data=({'id': 1, 'EQUIPID': 70682, 'BADGENUM': 35127, 'DEPARTMENT': 'CELL LINE', 'MATERIAL': 'ALUMINA', 'GROSS': '100000', 'TARE': '50000', 'NET': '50000', 'DATES': datetime.date(2024, 5, 6), 'TIMES': datetime.timedelta(seconds=45000)}, {'id': 2, 'EQUIPID': 70683, 'BADGENUM': 35337, 'DEPARTMENT': 'CARBON', 'MATERIAL': 'PET COKE', 'GROSS': '100000', 'TARE': '50000', 'NET': '50000', 'DATES': datetime.date(2024, 6, 6), 'TIMES': datetime.timedelta(seconds=48600)}, {'id': 3, 'EQUIPID': 
# 70674, 'BADGENUM': 36337, 'DEPARTMENT': 'CELL', 'MATERIAL': 'ALUMINA', 'GROSS': '100000', 'TARE': '60000', 'NET': '40000', 'DATES': datetime.date(2024, 6, 7), 'TIMES': datetime.timedelta(seconds=52200)}, {'id': 4, 'EQUIPID': 70874, 'BADGENUM': 36337, 'DEPARTMENT': 'CELL', 'MATERIAL': 'ALUMINA', 'GROSS': '100000', 'TARE': '70000', 'NET': '30000', 'DATES': datetime.date(2024, 6, 7), 
# 'TIMES': datetime.timedelta(seconds=52200)})

# for records in data:
#     dates.append(records['DATES'])
#     material.append(int(records['NET']))

#pip install -r requirements. txt
# print(dates)
# print(material)