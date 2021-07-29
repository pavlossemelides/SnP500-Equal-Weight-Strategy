import numpy as np  #numpy is a c++ module.
import pandas as pd #meaning panel data. Useful for handling tabular data.  Uses the data structure used the Pandas Dataframe.
# Dataframe is a data structure that holds tabular data.  So pandas allows you to store data in a dataframe and use many 
# different builtin pandas functions and methods to manipulate the data within the dataframe.
import requests #used to send an http request, in our case to an API to request/get data.
import xlsxwriter #used to save/write well formated excel files.
import math #library of maths functions.

print('hello')

stocks = pd.read_csv('sp_500_stocks.csv')
print(type(stocks))

#below print will return 'object', which means string in our case.
print(stocks['Ticker'].dtypes)
print(stocks)

from secrets import IEX_CLOUD_API_TOKEN

#Go to https://iexcloud.io/docs/api/ for IEX Cloud API resource documentation.
#IEX has really good documentation compared to others.
symbol = 'AAPL'
#Make api_url f-string implementation so can input field and symbol as variables.
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}' #base url (ending in .com) appended with "Quote" end-point url.
#added "stable" keyword to api_url.
print(api_url)
data = requests.get(api_url)
print(data)
print(data.status_code)

#get stock quote for 'AAPL'
data = requests.get(api_url).json()
print(data)

#data is passed in dictionary set of key:data pairs.
#see dictionary example below.
dictionary = {
    'a' : 1,
    'b' : 2
    }
print(dictionary['a'])

price = data['latestPrice']
print(price)
market_cap = data['marketCap']
print(market_cap/1000000000000) #convert to trillions

#create string list/array my_columns to use as dataFrame column headers
my_columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
#create pandas dataframe called final_dataframe. Set columns using my_columns
final_dataframe = pd.DataFrame(columns = my_columns)
print(final_dataframe)

#Use append method to populate our dataframe with 'AAPL' info we got from our api request.
final_dataframe = final_dataframe.append(
    #Use pd.Series to create a row to append our dataframe with.
    #Our data is passed in the square brackets, and allocated according to our index my_columns.
    pd.Series(
        [
            symbol,
            price,
            market_cap,
            'N/A'
            ],
        index = my_columns
        ),
        ignore_index = True #If True, the resulting axis will be labelled 0, 1, ..., n-1, where n is number of rows/series' added.
    )
print(final_dataframe)
print('hey whats up')

#Reset final_dataframe.  Iterate through stocks csv list using stock string variable, up until 5th stock.
#Do a get request for each stock, create a series from retrieved data and append to final_dataframe.
final_dataframe = pd.DataFrame(columns = my_columns)
for symbol in stocks['Ticker'][:5]: #['Ticker'] designates the word in stocks as a column title/index; [:5] means execute for loop for first 5 entries.
    #print(stock)
    
    #For each iteration of symbol, get stock quote data for the correpsonding stock.
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}' #Tutorial uses {stock} instead of {symbol}. Dont know why...
    data = requests.get(api_url).json()
    #Note that executing an http request (like the get below) is one of the slowest things in Python
    #Can perform batch API requests to make it more efficient; more advanced topic.
    
    #Use retrieved data to populate final_dataframe.
    final_dataframe = final_dataframe.append(
        pd.Series(
            [
              symbol,
              data['latestPrice'],  
              data['marketCap'], 
              'N/A'
            ],
            index = my_columns),
    ignore_index = True
    )
#apparently indention matters in Python.  If following print statement is indented it will run in for loop above.
print(final_dataframe)

#Using batch API calls to improve performance. Important!
#I assume def defines a function.
#We define a function chunks to break our n=505 list into n=100 lists.
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n): #syntax for range is range(first value in range, last value in range, step size).
        yield lst[i:i + n] #yield a string array for each 100 strings in stocks.

#Call chunks function to our case.  Note that function lists can take iterator objects, such as our function chunks.
#symbol_groups is a list of lists.
symbol_groups = list(chunks(stocks['Ticker'], 100))
print(symbol_groups[1])
print ('hello world haha')

#create symbol_strings out of symbol_groups, where elements in each symbol string are separated by ','.
#Note this is still a list of lists.  We are just arranging the symbols/data in the format accepted by the IEX url, i.e. comma-separated.
symbol_strings = []
print(len(symbol_groups)) #returns 6, i.e. number of lists in our list.
#Create 6 entries (len(symbol_groups)) in symbol_strings, each created by comma-separated join.
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    #print(symbol_strings[i])
print(symbol_strings)


#reset final_dataframe
final_dataframe = pd.DataFrame(columns = my_columns)
#create iterated string variable symbol_string, to be used in IEX api url
for symbol_string in symbol_strings: #add [:1] so it only loops over first string group.
    #print(symbol_string)
    #Use different endpoint in our url made for batch calls.  Takes a string of symbols as input, here {symbol_string}.
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    #Note & prefix instead of ? before token in above url.
    #print(batch_api_call_url)
    
    #Perform get request for each batch
    data = requests.get(batch_api_call_url)
    print(data.status_code)
    data = requests.get(batch_api_call_url).json()
    #print('pavlos')
    #print(data)
    #print(symbol_string.split(','))
    #Loop over our returned batch data and populate final_dataframe row-by-row.
    for symbol in symbol_string.split(','):  #split method is reverse of .join
        final_dataframe = final_dataframe.append(
            pd.Series(
            [
                symbol,
                data[symbol]['quote']['latestPrice'], #This is how data is arranged in the json.
                data[symbol]['quote']['marketCap'], #Stock data falls under 'quote' which in turn falls under 'symbol'
                'N/A'
                ],
            index = my_columns),
            ignore_index = True
            )
print(final_dataframe)
    
#Our dataframe is populated much faster using the batch request method!    
#We only need one call per 100 stocks instead of 1 call per 1 stock.   

#Calculating Number of Shares to Buy

portfolio_size = input('Enter the value of your portfolio: ')  

try:
    val = float(portfolio_size)
    print(val)
except ValueError:
    print('Please enter an integer')
    portfolio_size = input('Enter the value of your portfolio: ')
    val = float(portfolio_size)
  
print(final_dataframe.index)  
position_size = val/len(final_dataframe.index)
print(position_size)

for i in range(0, len(final_dataframe.index)):
    final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_dataframe.loc[i, 'Stock Price'])

print(final_dataframe)



#Save our Pandas Dataframe into an xlsx file using xlsxwriter.
#Pandas is closely linked to xlsxwriter to can use pandas method for this as below.
writer = pd.ExcelWriter('recommended trades.xlsx', engine = 'xlsxwriter')
#Write our final_dataframe as a sheet in 'recommended trades' called 'Recommended Trades'
final_dataframe.to_excel(writer, 'Recommended Trades', index = False)

#Formatting excel files with xlsxwriter is a science! It can get complicated.
#I guess the below are hexadecimal color codes.
background_color = '#0a0a23'
font_color = '#ffffff'

#add_format method takes dictionary as input, defined using curly {} brackets.
string_format = writer.book.add_format(
    {
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1 #1 means to add a solid border around each one.
        }
    )

dollar_format = writer.book.add_format(
    {
        'num_format' : '$0.00',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1 #1 means to add a solid border around each one.
        }
    )

integer_format = writer.book.add_format(
    {
        'num_format' : '0',
        'font_color' : font_color,
        'bg_color' : background_color,
        'border' : 1 #1 means to add a solid border around each one.
        }
    )

#Applying the Formats to the Columns of our .xlsx File
#set_column arguments: (excel column, column pixel width, format dictionary).
# writer.sheets['Recommended Trades'].set_column('A:A', 18, string_format)
# writer.sheets['Recommended Trades'].set_column('B:B', 18, string_format)
# writer.sheets['Recommended Trades'].set_column('C:C', 18, string_format)
# writer.sheets['Recommended Trades'].set_column('D:D', 18, string_format)
#save our writer object.
#writer.save()

#write() method takes cell location, what information you want stored in the cell and the format diction.
#We are basically overwriting what's in the cell, just using the same info, i.e. 'Ticker' etc.
# writer.sheets['Recommended Trades'].write('A1', 'Ticker', string_format)
# writer.sheets['Recommended Trades'].write('B1', 'Stock Price', dollar_format)
# writer.sheets['Recommended Trades'].write('C1', 'Market Capitalization', dollar_format)
# writer.sheets['Recommended Trades'].write('D1', 'Number of Shares to Buy', integer_format)

#Doing the above (block-commented) using a dictionary and a for loop. Better practice!
column_formats = {
    'A' : ['Ticker', string_format],
    'B' : ['Stock Price', dollar_format],
    'C' : ['Market Capitalization', dollar_format],
    'D' : ['Number of Shares to Buy', integer_format]
    }

for column in column_formats.keys(): #.keys returns the dictionary keys
    print(column)
    #column:column selects all rows in the column, i.e. A:A selects the entirety of column A
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 18, column_formats[column][1]) 
    #set_column() method ignores column titles so we format column titles using write() below.
    #Do our excel column title formating here as well. See latest block comment above.
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

#Save our excel file using writer.save()
#Note that .save() will also do .close() so further changes cannot be done.
#This has to do with 'xlsxwriter' engine.  'openpyxl' engine will just save and not .close().
writer.save()



     