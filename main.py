import csv
import requests
import json
import pandas as pd
from datetime import datetime

urls = {
    'daily': {
        'url': 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDd.xls',
        'remote-name': 'RNGWHHDd.xls',
        'local-name': 'daily-natural-gas-prices.csv'
    },
    'weekly': {
        'url': 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDw.xls',
        'remote-name': 'RNGWHHDw.xls',
        'local-name': 'weekly-natural-gas-prices.csv'
    },
    'monthly': {
        'url': 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls',
        'remote-name': 'RNGWHHDm.xls',
        'local-name': 'monthly-natural-gas-prices.csv'
    },
    'yearly': {
        'url': 'https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDa.xls',
        'remote-name': 'RNGWHHDa.xls',
        'local-name': 'yearly-natural-gas-prices.csv'
    }
}

def cleanUpCSV(inp_file, out_file, data_time):
    # open file for read and write
    with open(inp_file, 'r') as inp, open(out_file, 'w') as out:
        seperator = ","
        # convert to list of rows
        row_list = inp.read().split('\n')
        # remove not need rows
        row_list.pop(0)
        # formalize first header
        row_list[0] = ',Date,Price'
        for row in row_list:
            # convert rows to list of cells
            cell_list = row.split(seperator)
            # remove serial number
            cell_list.pop(0)
            # convert date to first day of the month for months
            if data_time == 'monthly' and len(cell_list) > 0 and cell_list[0] != 'Date':
                cell_list[0] = datetime.strptime(cell_list[0][:7], '%Y-%m').strftime("%Y-%m-%d %H:%M:%S")
            # join cell list to row
            row = seperator.join(cell_list)
            # write to file
            out.writelines(row + '\n')

def updateDataPackage():
    # open data package file
    with open('datapackage.json', 'r+') as datapackage:
        # convert to json
        data = json.load(datapackage)
        # update last_updated field to current time
        data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # save write json to file and close
        datapackage.seek(0)
        json.dump(data, datapackage, indent=4)
        datapackage.truncate()

def main(data):
    keys = data.keys()
    for key in keys:
        fetchInfo = data[key]
        # fetch the xls file form url
        response = requests.get(fetchInfo['url'], allow_redirects=True)
        fileName = 'xls/' + fetchInfo['remote-name']
        # save xls to drive
        open(fileName, 'wb').write(response.content)
        # load xls to memory
        xl = pd.ExcelFile(fileName)
        # load data sheet
        df1 = xl.parse('Data 1')
        # drop rows that are not needed
        df1 = df1.drop([0], axis=0)
        # convert dataframe to csv
        df1.to_csv('temp/' + fetchInfo['local-name'])
        # clean up csv
        cleanUpCSV('temp/' + fetchInfo['local-name'], fetchInfo['local-name'], key)

    # update datapackage last_updated property to current date
    updateDataPackage()

main(urls)
