from datetime import datetime
import pandas as pd

def search_sql(searchType,truckId,startDate,endDate,material):
    param=[]
    #ID and start date not empty   
    if truckId!='' and startDate!='' and endDate=='' and material=='':
        print('TruckId and startDate entered')
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[truckId,startDate]

    #ID and end date not empty    
    elif truckId!='' and endDate!='' and startDate=='' and material=='':
        print('TruckId and endDate entered')
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[truckId,endDate]
     
    elif material=='' and truckId!='' and startDate!='' and endDate!='':
        print('Search by id and Date range')
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND DATES BETWEEN %s AND %s LIMIT %s OFFSET %s'
        param=[truckId,startDate,endDate]
        
    #When user enters truckId and start and end dates and material
    elif truckId!='' and startDate!='' and endDate!='' and material=='':
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
        print(startDate)
        print(endDate)
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND MATERIAL=%s AND DATES BETWEEN %s AND %s LIMIT %s OFFSET %s'
        param=[truckId,material, startDate,endDate]
        
    #When user enters only truckId
    elif truckId and not startDate and not endDate and not material:
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s LIMIT %s OFFSET %s'
        param=[truckId]
        
    #When user enters start and end dates but not truckId
    elif startDate!=''  and endDate!=''  and truckId=='' and material=='':
        print('Dates only entered')
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
        print(startDate)
        print(endDate)
        Query=f'SELECT * FROM {searchType} WHERE DATES BETWEEN %s AND %s LIMIT %s OFFSET %s'
        param=[startDate,endDate]
        
    
    #When user enters only startDate
    elif startDate!=''  and endDate=='' and truckId=='' and material=='':
        print('Start date start')
        startDate = datetime.strptime(startDate, "%Y-%m-%d").date()
        print(startDate)
        Query=f'SELECT * FROM {searchType} WHERE DATES=%s LIMIT %s OFFSET %s'
        param=[startDate]
       

    #when user enters only end date
    elif endDate!='' and startDate==''  and truckId=='' and material=='':
        print('End date entered')
        endDate = datetime.strptime(endDate, "%Y-%m-%d").date()
        print(endDate)
        Query=f'SELECT * FROM {searchType} WHERE DATES=%s LIMIT %s OFFSET %s'
        param=[endDate]
    

    elif material!='' and truckId=='' and startDate=='' and endDate=='':
        print('Search by material type only start')
        Query=f'SELECT * FROM {searchType} WHERE MATERIAL=%s LIMIT %s OFFSET %s'
        param=[material]

    elif material!='' and truckId!='' and startDate=='' and endDate=='':
        print('Search by material and truckid')
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND MATERIAL=%s LIMIT %s OFFSET %s'
        param=[truckId,material]
    
    elif material!='' and truckId!='' and startDate!='' and endDate=='':
        print('Search by material, id and start date')
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND MATERIAL=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[truckId,material,startDate]

    elif material!='' and truckId!='' and startDate=='' and endDate!='':
        print('Search by material, id and endDate')
        Query=f'SELECT * FROM {searchType} WHERE EQUIPID=%s AND MATERIAL=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[truckId,material,endDate]

    
    elif material!='' and truckId=='' and startDate!='' and endDate=='':
        print('Search by material and startDate')
        Query=f'SELECT * FROM {searchType} WHERE MATERIAL=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[material,startDate]
    
    elif material!='' and truckId=='' and startDate=='' and endDate!='':
        print('Search by material and endDate')
        Query=f'SELECT * FROM {searchType} WHERE MATERIAL=%s AND DATES=%s LIMIT %s OFFSET %s'
        param=[material,endDate]
    
    elif material!='' and truckId=='' and startDate!='' and endDate!='':
        print('Search by material and Date range')
        Query=f'SELECT * FROM {searchType} WHERE MATERIAL=%s AND DATES BETWEEN %s AND %s LIMIT %s OFFSET %s'
        param=[material,startDate,endDate]
    
    return Query,param


def graph_sql(truckId, material, startDate, endDate):

    params=[]
    Query=[]
    if truckId!='' and material!='' and startDate!='' and endDate!='':
        print('Graph of total trips/material usage per date per range')
        TripQ=f'SELECT COUNT(EQUIPID) FROM weighout WHERE EQUIPID=%s AND MATERIAL=%s AND DATES=%s'
        MatQ=f'SELECT SUM(NET) FROM weighout WHERE EQUIPID=%s AND MATERIAL=%s AND DATES=%s'
        setDate=pd.date_range(start=startDate,end=endDate).date
        mode=1
        params=[truckId,material]
        Query=[TripQ,MatQ]

    
    elif truckId!='' and material=='' and startDate!='' and endDate!='':
        print('Graph of total trips per day per range')
        TripQ=f'SELECT COUNT(EQUIPID) FROM weighout WHERE EQUIPID=%s AND DATES=%s'
        setDate=pd.date_range(start=startDate,end=endDate).date
        print(setDate)
        mode=2
        params=[truckId]
        Query=[TripQ]
    

    elif truckId=='' and material!='' and startDate!='' and endDate!='':
        print('Graph of total material used per day per range')
        MatQ=f'SELECT SUM(NET) FROM weighout WHERE MATERIAL=%s AND DATES=%s'
        setDate=pd.date_range(start=startDate,end=endDate).date
        mode=3
        params=[material]
        Query=[MatQ]
    
    elif truckId!='' and material=='' and startDate!='' and endDate=='':
        print('Graph of total trips in a day')
        setDate=startDate
        TripQ=f'SELECT COUNT(EQUIPID) FROM weighout WHERE EQUIPID=%s AND DATES=%s'
        mode=4
        params=[truckId]
        Query=[TripQ]

    elif truckId!='' and material=='' and startDate=='' and endDate!='':
        print('Graph of total trips in a day')
        setDate=endDate
        TripQ=f'SELECT COUNT(EQUIPID) FROM weighout WHERE EQUIPID=%s AND DATES=%s'
        mode=4
        params=[truckId]
        Query=[TripQ]
    
    elif truckId=='' and material!='' and startDate!='' and endDate=='':
        print('Graph of material used per day')
        setDate=startDate
        MatQ=f'SELECT SUM(NET) FROM weighout WHERE MATERIAL=%s AND DATES=%s'
        mode=5
        params=[material]
        Query=[MatQ]

    elif truckId=='' and material!='' and startDate=='' and endDate!='':
        print('Graph of material used per day')
        setDate=endDate
        MatQ=f'SELECT SUM(NET) FROM weighout WHERE MATERIAL=%s AND DATES=%s'
        mode=5
        params=[material]
        Query=[MatQ]


    return mode, Query, params,setDate



       