# Project-walker
web crawler in python. Its purpose is to obtain information from guatecompras.gt and generate csv's with it, so users have data suitable for machine and human analysis
## Installation
To install dependencies just run 
```cmd
pip install -r requirements.txt
```
## Usage
Open a command terminal inside the folder where you cloned the project and 
```cmd
EntryPoint.py [-h] [-y YEAR] [-m MONTH] [-d DAY]
```
### Obtain a whole year
```cmd
python EntryPoint.py -y 2016
```
executing above command will obtain data for 2016 
### Obtain a specific month
```cmd
python EntryPoint.py -y 2016 -m 1
```
executing above command will obtain data for January 2016
### Obtain a specific day
```cmd
python EntryPoint.py -y 2016 -m 1 -d 1
```
executing above command will obtain data for January 1st 2016

After execution program will output 3 csv files: 
**adjudicaciones.csv**, **compradores.csv**, **proveedores.csv**, column delimiter is '|'
