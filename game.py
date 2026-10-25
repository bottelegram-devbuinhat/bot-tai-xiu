import random # r
import asyncio # a
from datetime import datetime # dt
from config import c, u, f_w, p, l_f

def ghi_lich_su_phien(txt): # glsp
    with open(l_f, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {txt}\n")

async def chay_vong_quay_game(app): # cvqg
    while True:
        nd = datetime.now()
        ndt = nd.strftime("%Y-%m-%d")
        if c.get("session_date") != ndt:
            c["session_date"] = ndt
            c["session_id"] = 1
        else:
            c["session_id"] += 1
        
        c["global_road"] = None
        c["bet_active"] = True
        f_w("config.json", c)
        
        ss = f"#{c['session_id']:04d}"
        
        from notif import ds_tat_tb
        for uid, acc in u.items():
            str_uid = str(uid)
            if acc.get("nhan_thong_bao", False) and str_uid not in ds_tat_tb and not acc.get("blocked", False):
                try:
                    await app.bot.send_message(chat_id=int(uid), text=f"🎲 <b>BẮT ĐẦU PHIÊN {ss}</b>\n• Nhắn <code>T[tiền]</code> hoặc <code>X[tiền]</code> (1k - 100k) để cược!", parse_mode="HTML")
                except: pass
        
        await asyncio.sleep(50)
        
        c["bet_active"] = False
        f_w("config.json", c)
        
        tt = sum(acc["current_bet"]["amount"] for acc in u.values() if acc.get("current_bet") and acc["current_bet"]["type"] == "TAI")
        tx = sum(acc["current_bet"]["amount"] for acc in u.values() if acc.get("current_bet") and acc["current_bet"]["type"] == "XIU")
        
        sr = c.get("global_road")
        if sr:
            ws = sr
        else:
            if tt == tx:
                ws = random.choice(["TAI", "XIU"])
            else:
                diff = abs(tt - tx)
                ts = tt + tx if (tt + tx) > 0 else 1
                rd = diff / ts
                px = 0.5 + (0.12 if tt > tx else -0.12) * rd
                ws = "XIU" if random.random() < px else "TAI"

        sn = "TÀI 🎲" if ws == "TAI" else "XỈU 🎲"
        phien_log = f"Phiên {ss} | Kết quả: {sn} | Tổng Tài: {tt:,.0f}đ | Tổng Xỉu: {tx:,.0f}đ"
        danh_sach_cuoc = []

        for uid, acc in u.items():
            if acc.get("current_bet"):
                bi = acc["current_bet"]
                aw = sr if sr else ws
                if bi["type"] == aw:
                    rt = c.get("tai_ratio" if aw == "TAI" else "xiu_ratio", 1.95)
                    rew = int(bi["amount"] * rt)
                    acc["balance"] += rew
                    acc["wins"] += 1
                    kq = f"THẮNG (+{rew:,.0f}đ)"
                    msg = f"🎉 <b>PHIÊN {ss}: {sn}</b>\n• Bạn đã <b>THẮNG</b>: +<b>{rew:,.0f} VNĐ</b>\n• Số dư: <b>{acc['balance']:,.0f} VNĐ</b>"
                else:
                    acc["balance"] = max(0, acc["balance"])
                    kq = f"THUA (-{bi['amount']:,.0f}đ)"
                    msg = f"😢 <b>PHIÊN {ss}: {sn}</b>\n• Bạn đã <b>THUA</b>: -<b>{bi['amount']:,.0f} VNĐ</b>\n• Số dư: <b>{acc['balance']:,.0f} VNĐ</b>"
                
                chitiet_user = f"User {acc['name']} ({uid}): Cược {bi['type']} {bi['amount']:,.0f}đ -> {kq}"
                danh_sach_cuoc.append(chitiet_user)
                acc["history"].insert(0, f"Phiên {ss} | Cược {bi['type']} {bi['amount']:,.0f}đ | {kq}")
                if len(acc["history"]) > 10: acc["history"].pop()
                
                acc["current_bet"] = None
                try:
                    await app.bot.send_message(chat_id=int(uid), text=msg, parse_mode="HTML")
                except: pass
            else:
                acc["nhan_thong_bao"] = False

        if not danh_sach_cuoc:
            phien_log += " | Không có ai đặt cược phiên này."
        else:
            phien_log += " | Chi tiết: " + " | ".join(danh_sach_cuoc)
        
        ghi_lich_su_phien(phien_log)
        f_w(p, u)
        await asyncio.sleep(10)