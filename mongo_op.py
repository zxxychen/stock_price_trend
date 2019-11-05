import pymongo as pm 
import datetime
import pandas as pd 
import K_line
import tushare as ts
import candle_render

def access_to_db():
    # access to database tushare
    myclient = pm.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["tusharedb"]
    return mydb

def access_to_col(db, code):
    # access to the col
    # 新建/链接 集合，用于存放K线数据
    code_list = code.split('.')
    code_name = '_'.join(code_list)
    print('access to the db cols name is {}'.format(code_name))
    mycol = db[code_name]
    return mycol

def save_to_col(col, klines:pd.DataFrame):
    # save klines information to cols
    # 把tushare 返回的dataframe格式数据存入集合。
    if klines.empty:
        print('error!! the input klines is 0, return')
        return
    test_d = klines.drop('ts_code', axis=1)
    test_d = test_d.rename(columns={'trade_date': '_id'})
    test_l = test_d.to_dict(orient='records')
    for x in test_l:
        filt = {'_id': x['_id']}
        docs = col.update_one(filt, {"$set": x}, upsert=True)
        # print(docs)
    print('finished save to col {}'.format(col.name))
    return

def save_list_of_codes(mydb, tu_list):
    # 设置所有起始时间为20100101
    ts.set_token('d5741f23ebd206c762d2e593573499d5a479b8955ae9b5152c646ba2')
    pro = ts.pro_api()
    if len(tu_list) == 0:
        # 所有代码合集
        tu_list_frame = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
        # 上证成分合集
        # tu_list_frame  = pro.hs_const(hs_type='SH') 
        tu_list = tu_list_frame['ts_code'].tolist()
        print(tu_list)
    
    for code in tu_list:
        test = K_line.K_line(code, '20100101', '20190718')
        test.get_daily_lists()
    
        # 保存入集合
        mycol = access_to_col(mydb, tu_code)
        save_to_col(mycol, test.k_lines)
        print('{} from date 20100101 to 20190718 has been loaded to tushare DB'.format(code))
    return 
 

def update_to_col(mydb, code):
    # 更新集合，应当先读取集合中最近日期的文档，然后从最新的日期开始更新
    # 注意 ma 数据，可能为Nan
    mycol = access_to_col(mydb, code)
    latest_doc = mycol.find().sort('_id', -1)
    last_date = latest_doc[0]['_id']
    # print(last_date)
    now_date = datetime.date.today()
    now_date = now_date.strftime("%Y%m%d")
    # print(now_date)
    test = K_line.K_line(code, last_date, now_date)
    test.get_daily_lists()
    save_to_col(mycol, test.k_lines)
    print('update col {} from {} to {}'.format(mycol.name, last_date, now_date))
    return




def load_from_col(db, code, types:list=[]):
    col = access_to_col(db, code)
    if len(types) is 0:
        docs = col.find().sort('_id')
    else:
        dic_names = dict()
        for type in types:
            dic_names[type] = 1
        print(dic_names)
        docs = col.find({}, dic_names).sort('_id')
    out_df = pd.DataFrame()
    
    for x in docs:
        # print(x)
        out_df = out_df.append(pd.Series(x), ignore_index=True)
    print('load kline infos from db {} col {}'.format(db.name, col.name))
    return out_df


if __name__ == "__main__":
    tu_code = '000001.SZ'
    # test = K_line.K_line(tu_code, '20180102', '20180120')
    # test.get_daily_lists()
    
    mydb = access_to_db()
    # save_list_of_codes(mydb, [])
    # save_list_of_codes(mydb, [tu_code])
    update_to_col(mydb, tu_code)
    data = load_from_col(mydb, tu_code, ['_id', 'open', 'close', 'low', 'high', 'amount'])
    xdata = data.loc[0:200, '_id'].tolist()
    vol_data = data.loc[0:200, 'amount'].tolist()
    # print(xdata)
    ydata_df = data.loc[0:200, ['open', 'close', 'low', 'high']]
    # print(ydata.values.tolist())
    ydata = ydata_df.values.tolist()
    grid = candle_render.Candle_render_output(xdata, ydata, vol_data)
    candle_render.Kline_save_to_render(grid)
