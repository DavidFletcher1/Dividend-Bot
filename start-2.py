import requests
import json
import math, copy, random
import sys
#from cmu_112_graphics.py import *
from datetime import datetime, timedelta


stock_ticker = input("Enter Stock Ticker Symbol: \n")

def return_date(dateObj):
    return datetime.strptime(dateObj['exDate'], '%Y-%m-%d')

def get_right_stock_dividend_dates(results):
    first_date = datetime.strptime(results[0]['exDate'], '%Y-%m-%d')
    current_date = datetime.now()
    days_diff = (current_date - first_date).days
    if days_diff < 15:
        return list(map(return_date, results[1:17]))
    else:
        return list(map(return_date, results[1:17]))

stock_dividends = requests.get("https://api.polygon.io/v2/reference/dividends/" + stock_ticker, headers={"Authorization": "Bearer YSB3smcV7460ocSpES4mSWvV0c7JovD1"}).json()

stock_dividend_dates = get_right_stock_dividend_dates(stock_dividends['results'])

#ALPHA VANTAGE API KEY: DHI6Q03VNVGH4NP5
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock_ticker}&apikey=DHI6Q03VNVGH4NP5&outputsize=full&datatype=json'
price_response = requests.get(url).json()
price_date_dictionary = price_response['Time Series (Daily)']

result = []

def get_right_before_date(date):
    date_track = date
    while date_track.strftime("%Y-%m-%d") not in price_date_dictionary:
        date_track = date_track - timedelta(1)
    return date_track
def get_right_after_date(date):
    date_track = date
    while date_track.strftime("%Y-%m-%d") not in price_date_dictionary:
        date_track = date_track + timedelta(1)
    return date_track

for i in range(len(stock_dividend_dates)):
    currResult = []
    curr_date = stock_dividend_dates[i]
    pivot_date = get_right_before_date(curr_date)
    before_start = pivot_date - timedelta(1)
    after_start = pivot_date + timedelta(1)
    for j in range(10):
        right_before_date = get_right_before_date(before_start)
        currResult.insert(0, float(price_date_dictionary[right_before_date.strftime('%Y-%m-%d')]['5. adjusted close']))
        before_start = right_before_date - timedelta(1)
    currResult.append(float(price_date_dictionary[pivot_date.strftime('%Y-%m-%d')]['5. adjusted close']))
    for p in range(10):
        right_after_date = get_right_after_date(after_start)
        currResult.append(float(price_date_dictionary[right_after_date.strftime('%Y-%m-%d')]['5. adjusted close']))
        after_start = right_after_date + timedelta(1)
    
    result.append(currResult)
    assert(len(currResult) == 21)

#assert(len(result) == 16) 
#print(stock_dividend_dates)
print(result)


#this function takes in a 2D array of values and shrinks it down into a 1D array
#emphasizes the most recent values with a .97 regression 
 
def shrink2d(list):
    rowLength=len(list)
    colLength=len(list[0])
    finalList=[0]*colLength
    tempList=[0]*rowLength
    for j in range(colLength):
        for i in range(rowLength):
            tempList[i]=list[i][j]
        finalList[j]=averageShrinkVal(tempList)
        tempList=[0]*rowLength
    return finalList

def averageShrinkVal(list):
    length = len(list)
    numerator=0
    denominator=0
    for i in range(length):
        numerator+=list[i]*(0.97**i)
    for i in range(length):
        denominator+=(0.97**i)
    return numerator/denominator

def differenceOf(list):
    length=len(list)
    finalList=[([0]*length) for i in range(length)]
    for i in range(length):
        for j in range(length):
            finalList[i][j]=list[j]-list[i]
    return finalList


def appStarted(app):
    app.startingList=result
    #[[1,12,14,15,1,1,4,32,1,3,4,5,4,1,22,3,21,17,7,7],
    #[1,12,14,15,1,1,4,32,1,3,4,5,4,1,22,3,21,17,7,7]]
    app.compressedList=shrink2d(app.startingList)
    app.realList=differenceOf(app.compressedList)
    app.rows = len(app.compressedList)
    app.cols = app.rows
    app.min = min([min(r) for r in app.realList])
    app.max = max([max(r) for r in app.realList]) 
    app.oneEighth = (app.max+7*app.min)/8
    app.twoEighth = (2*app.max+6*app.min)/8
    app.sixEighth = (6*app.max+2*app.min)/8
    app.sevenEighth = (7*app.max+app.min)/8
    app.margin = 80 # margin around grid
   


def getCellBounds(app, row, col):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    x0 = app.margin + gridWidth * col / app.cols
    x1 = app.margin + gridWidth * (col+1) / app.cols
    y0 = app.margin + gridHeight * row / app.rows
    y1 = app.margin + gridHeight * (row+1) / app.rows
    return (x0, y0, x1, y1)

def drawOutlines(app,canvas):
    for row in range(app.rows):
        (x0, y0, x1, y1) = getCellBounds(app, row, 0)
        canvas.create_text(x0//2,(y0+y1)//2, text=f"row {row}")
    for col in range(app.rows):
        (x0, y0, x1, y1) = getCellBounds(app, 0, col)
        canvas.create_text((x0+x1)//2,3*(y0)//4, text=f"col {col}")
    canvas.create_text(app.width//2,app.height-app.margin//2, 
    text="the row is the day you buy the item and col is the day you sell it")


def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            val=app.realList[row][col]
            color='white'
            if(val<=app.oneEighth):
                color="red"
            elif(val<=app.twoEighth):
                color="orange red"
            elif(val>=app.sevenEighth):
                color="dodgerblue"
            elif(val>=app.sixEighth):
                color="cyan"
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1,
                                    fill=color, outline='black')
            canvas.create_text((x0+x1)//2, (y0+y1)//2 , text=round(app.realList[row][col],4))


def redrawAll(app, canvas):
        drawBoard(app, canvas)
        drawOutlines(app, canvas)
runApp(width=1600, height=900)
















