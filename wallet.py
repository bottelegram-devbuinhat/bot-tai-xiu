import os # o
import aiohttp # ah
from datetime import datetime # dt
from config import u, f_w, p, lich_su_nap_rut, c # cfg
from ngan_hang_checker import chuan_hoa_va_check_ngan_hang # nhc

q_dir = "QRCODE" # qd
if not os.path.exists(q_dir):
    os.makedirs(q_dir)

def ghi_ls_nap_rut(i, t): # glsnr
    with open(lich_su_nap_rut, 'a', encoding='utf-8') as f:
        f.write(f"USER:{i} | [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {t}\n")

async def tai_va_luu_qr(i): # tvlqr
    i = str(i)
    fp = os.path.join(q_dir, f"{i}.png")
    stk = "860671050278271" # stk
    mn = "MB" # mn
    nd = f"NAPTIEN_{i}" # nd
    qu = f"https://vietqr.io/{mn}-{stk}-compact2.png?addInfo={nd}" # qu
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(qu) as r:
                if r.status == 200:
                    with open(fp, "wb") as f:
                        f.write(await r.read())
                    return fp
    except Exception as e:
        print(f"Lỗi QR {i}: {e}")
    return None

async def cmd_nap(u_obj, x_obj): # cn
    a = x_obj.args # a
    if not a:
        await u_obj.message.reply_text("⚠️ Nhập số tiền cần nạp! Cú pháp: <code>/nap [số_tiền]</code>\n(Tối thiểu: 10.000đ)", parse_mode="HTML")
        return
    try:
        t = int(a[0]) # t
    except ValueError:
        await u_obj.message.reply_text("❌ Số tiền không hợp lệ!", parse_mode="HTML")
        return

    if t < 10000:
        await u_obj.message.reply_text("❌ Nạp tối thiểu <b>10.000 VNĐ</b>!", parse_mode="HTML")
        return

    i = str(u_obj.effective_user.id) # i
    nd = f"NAPTIEN_{i}" # nd
    fp = os.path.join(q_dir, f"{i}.png") # fp

    if not os.path.exists(fp):
        cm = await u_obj.message.reply_text("⏳ Đang khởi tạo QR...", parse_mode="HTML")
        dp = await tai_va_luu_qr(i) # dp
        try: await cm.delete()
        except: pass
        if not dp:
            await u_obj.message.reply_text("❌ Lỗi tạo QR, thử lại sau!", parse_mode="HTML")
            return
            
    ghi_ls_nap_rut(i, f"YÊU CẦU QR NẠP: {t:,.0f}đ | Nội dung: {nd}")
    cp = ( # cp
        f"<b>🏦 THÔNG TIN CHUYỂN KHOẢN NẠP TIỀN</b>\n\n"
        f"🏧 Ngân hàng: <b>MB BANK</b>\n"
        f"💳 Số tài khoản: <code>860671050278271</code>\n"
        f"👤 Chủ tài khoản: <b>BUI NGUYEN XUAN NHAT</b>\n"
        f"💵 Số tiền: <b>{t:,.0f} VNĐ</b>\n"
        f"📝 Nội dung bắt buộc: <code>{nd}</code>\n\n"
        f"⚠️ <i>Chuyển chính xác số tiền và nội dung để hệ thống tự động cộng!</i>"
    )
    with open(fp, "rb") as pf:
        await u_obj.message.reply_photo(photo=pf, caption=cp, parse_mode="HTML")

async def cmd_cong(u_obj, x_obj): # cc
    if u_obj.effective_user.id not in c["admin_ids"]: return
    a = x_obj.args # a
    if len(a) < 2: return
    try:
        ti = a[0] # ti
        amt = int(a[1]) # amt
    except ValueError: return
    if ti in u:
        u[ti]["balance"] += amt
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"CỘNG TIỀN: +{amt:,.0f}đ")
        await u_obj.message.reply_text(f"✅ Đã cộng {amt:,.0f}đ cho <code>{ti}</code>!", parse_mode="HTML")

async def cmd_tru(u_obj, x_obj): # ct
    if u_obj.effective_user.id not in c["admin_ids"]: return
    a = x_obj.args # a
    if len(a) < 2: return
    try:
        ti = a[0] # ti
        amt = int(a[1]) # amt
    except ValueError: return
    if ti in u:
        u[ti]["balance"] = max(0, u[ti]["balance"] - amt)
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"TRỪ TIỀN: -{amt:,.0f}đ")
        await u_obj.message.reply_text(f"✅ Đã trừ {amt:,.0f}đ của <code>{ti}</code>!", parse_mode="HTML")

async def cmd_rut(u_obj, x_obj): # cr
    a = x_obj.args # a
    if len(a) < 4:
        await u_obj.message.reply_text(
            "⚠️ Cú pháp rút: <code>/rut [ngân_hàng] [stk] [tên_tk] [số_tiền]</code>\n"
            "<i>(Ví dụ: /rut MB 860671050278271 BUI NGUYEN XUAN NHAT 150000)</i>\n"
            "👉 Số tiền rút phải > 100.000đ!", parse_mode="HTML"
        )
        return
    try:
        amt = int(a[-1]) # amt
        tk = a[-2] # tk
        stk = a[-3] # stk
        nr = " ".join(a[:-3]) # nr
    except ValueError: return
    
    hl, mn = chuan_hoa_va_check_ngan_hang(nr) # hl, mn
    if not hl:
        await u_obj.message.reply_text("❌ Tên ngân hàng không hợp lệ!", parse_mode="HTML")
        return
    if amt <= 100000:
        await u_obj.message.reply_text("❌ Số tiền rút phải <b>lớn hơn 100.000 VNĐ</b>!", parse_mode="HTML")
        return
    if amt > 1000000:
        await u_obj.message.reply_text("❌ Tối đa <b>1.000.000 VNĐ</b> mỗi lần rút!", parse_mode="HTML")
        return

    i = str(u_obj.effective_user.id) # i
    if i in u:
        if u[i]["balance"] < amt:
            await u_obj.message.reply_text("❌ Số dư không đủ!", parse_mode="HTML")
            return
        u[i]["balance"] -= amt
        f_w(p, u)
        ghi_ls_nap_rut(i, f"YÊU CẦU RÚT: {amt:,.0f}đ | {mn} | STK: {stk} | TÊN: {tk} | Đang xử lý")
        await u_obj.message.reply_text("⏳ <b>Đã gửi yêu cầu rút tiền...</b> Vui lòng chờ Admin duyệt.", parse_mode="HTML")

async def cmd_duyet(u_obj, x_obj): # cd
    if u_obj.effective_user.id not in c["admin_ids"]: return
    a = x_obj.args # a
    if len(a) < 2: return
    try:
        ti = a[0] # ti
        amt = int(a[1]) # amt
    except ValueError: return
    if ti in u:
        ghi_ls_nap_rut(ti, f"ĐÃ DUYỆT RÚT: {amt:,.0f}đ")
        try: await x_obj.bot.send_message(chat_id=int(ti), text=f"🎉 <b>Rút {amt:,.0f}đ thành công!</b>", parse_mode="HTML")
        except: pass
        await u_obj.message.reply_text(f"✅ Đã duyệt rút cho <code>{ti}</code>!", parse_mode="HTML")

async def cmd_tuchoi(u_obj, x_obj): # ctc
    if u_obj.effective_user.id not in c["admin_ids"]: return
    a = x_obj.args # a
    if len(a) < 2: return
    try:
        ti = a[0] # ti
        amt = int(a[1]) # amt
    except ValueError: return
    if ti in u:
        u[ti]["balance"] += amt
        f_w(p, u)
        ghi_ls_nap_rut(ti, f"TỪ CHỐI RÚT: {amt:,.0f}đ | Đã hoàn tiền")
        try: await x_obj.bot.send_message(chat_id=int(ti), text=f"❌ <b>Yêu cầu rút {amt:,.0f}đ bị từ chối!</b> Đã hoàn tiền về ví.", parse_mode="HTML")
        except: pass
        await u_obj.message.reply_text(f"❌ Đã từ chối và hoàn tiền cho <code>{ti}</code>!", parse_mode="HTML")
