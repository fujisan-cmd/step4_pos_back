from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
import math
import json
import os
from pydantic import BaseModel
import pymysql

import crud

class Item(BaseModel):
    product_id: int
    barcode: str
    product_name: str
    price: int

class PurchaseRequest(BaseModel):
    employee_id: str
    store_id: str
    pos_id: str
    items: list[Item]

tax_percent = '10' # 現在の消費税率

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "Hello FastAPI!"}

@app.get("/search_prod_info")
def read_one_product(code: int=Query(...)):
    result = crud.myselect(crud.Products, code)

    if result is None:
        return {'error': '該当する商品が存在しません。'}
    
    return result

@app.post("/purchase")
def write_one_trade(request: PurchaseRequest):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.employee_id == '':
        request.employee_id = '9999999999'
    value = {
        'DATETIME': now,
        'EMP_CD': request.employee_id,
        'STORE_CD': request.store_id,
        'POS_NO': request.pos_id
    }
    trade_id = crud.insert_trade(crud.Trade, value)

    # 1アイテムごとにdetailテーブルに登録
    total_wo_tax = 0
    for idx, item in enumerate(request.items, start=1):
        value = {
            'TRD_ID': trade_id,
            'DTL_ID': idx,
            'PRD_ID': item.product_id,
            'PRD_CODE': item.barcode,
            'PRD_NAME': item.product_name,
            'PRD_PRICE': item.price,
            'TAX_CD': tax_percent
        }
        result = crud.insert_item(crud.Detail, value)
        total_wo_tax += item.price
    
    total_with_tax = total_wo_tax*(1+0.01*int(tax_percent))
    total_with_tax = math.floor(total_with_tax) # 消費税の端数は切り捨てに設定
    print(f'合計金額は{total_wo_tax}円(税抜き)、{total_with_tax}円(税込)')
    value = {
        'TRD_ID': trade_id,
        'TOTAL_AMT': total_with_tax,
        'TTL_AMT_EX_TAX': total_wo_tax
    }
    result = crud.update_trade(crud.Trade, value)

    return {'total_with_tax': total_with_tax, 'total_wo_tax': total_wo_tax}