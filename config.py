import os # o
import json # j
from datetime import datetime # d

p = "data.json" # p
q = "giftcodes.json" # q
r = "config.json" # r
l_f = "lich_su_chung.txt" # ls
t_f = "danh_sach_tat_tb.json" # dsttb
lich_su_nap_rut = "lich_su_nap_rut.txt" # lsnr

def f_r(n, d): # fr
    if not os.path.exists(n):
        with open(n, 'w', encoding='utf-8') as b: json.dump(d, b, ensure_ascii=False, indent=4)
    try:
        with open(n, 'r', encoding='utf-8') as b: return json.load(b)
    except: return d

def f_w(n, v): # fw
    with open(n, 'w', encoding='utf-8') as b: json.dump(v, b, ensure_ascii=False, indent=4)

u = f_r(p, {}) # ud
g = f_r(q, {}) # gd
ds_tat_tb = f_r(t_f, []) # dsttb_data
c = f_r(r, {
    "token": "8978297117:AAG9-QJwd2s3YJ-5QhHiVE-pUovhan99qtM", # tk
    "admin_ids": [8792000582], # adm
    "default_balance": 10000, # bal
    "tai_ratio": 1.95, # tr
    "xiu_ratio": 1.95, # xr
    "bet_active": True, # act
    "session_id": 1, # sid
    "session_date": datetime.now().strftime("%Y-%m-%d"), # sdate
    "global_road": None, # road
    "max_profit": 500000, # maxp
    "max_loss": -200000 # minl
})