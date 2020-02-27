import pymongo as pm
import K_line
import tushare as ts
import datetime

myclient = pm.MongoClient("mongodb://localhost:27017/")
mydb = myclient["tusharedb"]

dblist = myclient.list_database_names()
for names in dblist:
    print(names)

collist = mydb.list_collection_names()
for names in collist:
    print(names)
mycol = mydb["000001_sz"]
# mydict = [{"_id": 20191031, "open": 10.1, "close": 12}, ]
# x = mycol.insert_many(mydict)
# print(x.inserted_id)


test = K_line.K_line('600060.SH', '20190102', '20190120')
test.get_daily_lists()
test_d = test.k_lines
test_d = test_d.drop('ts_code', axis=1)
test_d = test_d.rename(columns={'trade_date': '_id'})
test_l = test_d.to_dict(orient='records')
for x in test_l:
    docs= mycol.update_many(x, {'$setOnInsert': x}, upsert=True)
    # print(x)
doc = mycol.find().sort('_id', -1).limit(1)
for x in doc:
    print(datetime.datetime.strptime(x['_id'], "%Y%m%d").strftime("%Y-%m-%d"))
    t = datetime.datetime.strptime(x['_id'], "%Y%m%d")
    print(t.strftime("%Y-%m-%d"))
    # print(datetime.datetime.strptime())

pro = ts.pro_api('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')



