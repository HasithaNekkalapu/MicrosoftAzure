from flask import Flask,render_template,request
from os import listdir
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService
import pyodbc
import os,os.path
from os.path import isfile, join
import csv
import time
import random
import sys
app = Flask(__name__)

server = ''
database = ''
username = ''
password = ''
driver= '{SQL Server}'
db = pyodbc.connect('DRIVER='+driver+';PORT=1433;SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)

ACCOUNT_NAME = ""
ACCOUNT_KEY = ""
CONTAINER_NAME = "mycontainer"
LOCAL_DIRECT = "C:\\Users\\Documents\\images"
block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

# find all files in the LOCAL_DIRECT (excluding directory)
from azure.storage.blob import PublicAccess
block_blob_service.create_container(CONTAINER_NAME, public_access=PublicAccess.Container)

local_file_list = [f for f in listdir(LOCAL_DIRECT) if isfile(join(LOCAL_DIRECT, f))]
file_num = len(local_file_list)
for i in range(file_num):
    local_file = join(LOCAL_DIRECT, local_file_list[i])
    blob_name = local_file_list[i]
    try:
        print (blob_name)
        block_blob_service.create_blob_from_path('mycontainer',    'myblockblob',    local_file,    content_settings=ContentSettings(content_type='image/png')
            )
        #blob_service.put_block_blob_from_path(CONTAINER_NAME, blob_name, local_file)
    except:
        print ("something wrong happened when uploading the data %s"%blob_name)

        
@app.route('/')
def hello_world():
    #after = time.time()
    #timediff = after-before
    #return "Time taken to load page is "+str(timediff)
    return render_template('dbview.html')
@app.route('/createtable' ,methods=['POST', 'GET'])
def createtable():
    before = time.time()
    cursor = db.cursor()
    cursor.execute('DROP TABLE IF EXISTS FoodData;')
    cursor.commit()
    cursor.execute("CREATE TABLE FoodData(filename varchar(30), quantity varchar(25),ingredients varchar(175),cusine varchar(20));")
    cursor.commit()
    csvfiles = os.listdir("C:\\Users\\Documents\\csv")
    print (csvfiles)
    for file in csvfiles:
        filename = os.path.splitext(file)[0]
        with open("C:\\Users\\Documents\\csv\\"+filename+".csv") as f:
            print (filename)
            for i,line in enumerate(f):
                if i==0:
                    quantity = line.rstrip(",\n")
                    #print (quantity)
                if i==1:
                    ingredients = line.rstrip(",\n")
                    #print (ingredients)
                if i==2:
                    cusine = line.rstrip(",\n")
                    #print (cusine)             
         
        cursor.execute('INSERT INTO FoodData (filename,quantity,ingredients,cusine) values (\''+filename+'\',\''+quantity+'\',\''+ingredients+'\',\''+cusine+'\');')
        cursor.commit()
        cursor.execute('SELECT * FROM FoodData;')
        result = cursor.fetchall()
    after = time.time()
    print (str(after-before))
    return render_template('index.html', tableData=result)
@app.route('/querydatabase' ,methods=['POST', 'GET'])
def querydatabase() :
    cursor = db.cursor()
    text1 = request.form.get('text1')
    text2 = request.form.get('text2')
    beforeTime = time.time()
    #cursor.execute('SELECT * FROM FoodData where ingredients like \'%'+text1+'%\';')
    cursor.execute('SELECT * FROM FoodData where quantity between \''+text1+'\'and \''+text2+'\';')
    result = cursor.fetchall()
    afterTime = time.time()
    timediff = beforeTime-afterTime
    print ("Time is " + str(timediff))
    return render_template('index.html', tableData=result)
@app.route('/querydatabase2' ,methods=['POST', 'GET'])
def querydatabase2() :
    beforeTime = time.time()
    cursor = db.cursor()
    text3 = request.form.get('text3')
    cursor.execute('SELECT * FROM FoodData where ingredients like \'%'+text3+'%\';')
    #cursor.execute('SELECT * FROM FoodData where quantity between \''+text1+'\'and \''+text2+'\';')
    result = cursor.fetchall()
    afterTime = time.time()
    timediff = beforeTime-afterTime
    print ("querydatabase2 time difference " + str(timediff))
    return render_template('index.html', tableData=result)
@app.route('/query3' ,methods=['POST', 'GET'])
def query3() :
    cursor = db.cursor()
    text3 = request.form.get('text3')
    text1 = request.form.get('text1')
    text2 = request.form.get('text2')
    beforeTime = time.time()
    cursor.execute('SELECT cusine,filename FROM FoodData where cusine like \'%'+text3+'%\' and quantity between \''+text1+'\'and \''+text2+'\';')
    #cursor.execute('SELECT * FROM FoodData where quantity between \''+text1+'\'and \''+text2+'\';')
    result = cursor.fetchall()
    afterTime = time.time()
    timediff = beforeTime-afterTime
    print ("Count is " + str(result))
    return render_template('index.html', tableData=result)
port = os.getenv('PORT', '8088')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))
