from config import u, f_w, p, lich_su_nap_rut
from datetime import datetime

def ghi_ls_nap_rut(uid, txt): # glsnr
    with open(lich_su_nap_rut, 'a', encoding='utf-8') as f:
        f.write(f"USER:{uid} | [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {txt}\n")

async def cmd_cong(u_obj, x_obj): # cc
    from config import c
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if len(args) < 2: return
    ti, amt = args[0], int(args[1])
    if ti in u:
        u[ti]["balance"] += amt
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"CỘNG TIỀN: Admin cộng +{amt:,.0f}đ")
        await u_obj.message.reply_text(f"✅ Đã cộng {amt:,.0f}đ cho <code>{ti}</code>!", parse_mode="HTML")

async def cmd_tru(u_obj, x_obj): # ct
    from config import c
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if len(args) < 2: return
    ti, amt = args[0], int(args[1])
    if ti in u:
        u[ti]["balance"] = max(0, u[ti]["balance"] - amt)
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"TRỪ TIỀN: Admin trừ -{amt:,.0f}đ")
        await u_obj.message.reply_text(f"✅ Đã trừ {amt:,.0f}đ của <code>{ti}</code>!", parse_mode="HTML")

async def cmd_rut(u_obj, x_obj): # crut
    args = x_obj.args
    if len(args) < 3:
        await u_obj.message.reply_text("⚠️ Cú pháp rút: <code>/rut [stk] [tên_ngân_hàng] [số_tiền]</code>\n(Mỗi lần rút từ 100.000đ đến 1.000.000đ)", parse_mode="HTML")
        return
    stk, ten_tk, amt = args[0], args[1], int(args[2])
    
    if amt < 100000 or amt > 1000000:
        await u_obj.message.reply_text("❌ Số tiền rút mỗi lần phải từ <b>100.000 VNĐ</b> đến <b>1.000.000 VNĐ</b>!", parse_mode="HTML")
        return

    i = str(u_obj.effective_user.id)
    if i in u:
        if u[i]["balance"] < amt:
            await u_obj.message.reply_text("❌ Số dư không đủ để rút!", parse_mode="HTML")
            return
        u[i]["balance"] -= amt
        f_w(p, u)
        ghi_ls_nap_rut(i, f"YÊU CẦU RÚT: {amt:,.0f}đ | STK: {stk} ({ten_tk}) | Trạng thái: Đang xử lý")
        await u_obj.message.reply_text("⏳ <b>Yêu cầu rút tiền của bạn đang được xử lý...</b> Vui lòng chờ Admin phê duyệt.", parse_mode="HTML")

async def cmd_duyet(u_obj, x_obj): # cduyet
    from config import c
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if len(args) < 2: return
    ti, amt = args[0], int(args[1])
    if ti in u:
        ghi_ls_nap_rut(ti, f"ĐÃ DUYỆT RÚT: {amt:,.0f}đ thành công")
        try:
            await x_obj.bot.send_message(chat_id=int(ti), text=f"🎉 <b>Yêu cầu rút {amt:,.0f}đ của bạn đã được Admin ĐỒNG Ý!</b> Tiền đã được chuyển thành công.", parse_mode="HTML")
        except: pass
        await u_obj.message.reply_text(f"✅ Đã duyệt lệnh rút cho user <code>{ti}</code> thành công!", parse_mode="HTML")

async def cmd_tuchoi(u_obj, x_obj): # ctuchoi
    from config import c
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if len(args) < 2: return
    ti, amt = args[0], int(args[1])
    if ti in u:
        u[ti]["balance"] += amt 
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"TỪ CHỐI RÚT: {amt:,.0f}đ | Đã hoàn tiền về tài khoản")
        try:
            await x_obj.bot.send_message(chat_id=int(ti), text=f"❌ <b>Yêu cầu rút {amt:,.0f}đ của bạn đã bị từ chối!</b> Số tiền đã được hoàn lại vào tài khoản.", parse_mode="HTML")
        except: pass
        await u_obj.message.reply_text(f"❌ Đã từ chối lệnh rút và hoàn tiền cho user <code>{ti}</code>!", parse_mode="HTML")