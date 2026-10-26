from config import u, f_w, p, lich_su_nap_rut
from datetime import datetime
import re

def ghi_ls_nap_rut(uid, txt): # glsnr
    with open(lich_su_nap_rut, 'a', encoding='utf-8') as f:
        f.write(f"USER:{uid} | [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {txt}\n")

# --- BỔ SUNG: HÀM VÀ LỆNH TẠO QR NẠP TIỀN ---
def tao_link_qr_nap(stk, ngan_hang, so_tien, noi_dung): # tlqn
    # Tạo đường dẫn VietQR tự động kèm theo số tiền và nội dung chuyển khoản định danh
    return f"https://img.vietqr.io/image/{ngan_hang}-{stk}-compact2.png?amount={so_tien}&addInfo={noi_dung}"

async def cmd_nap(u_obj, x_obj): # cnap
    # Xử lý lệnh nạp tiền bằng mã QR (Ví dụ cú pháp: /nap 50000 hoặc /naptien 50000)
    args = x_obj.args
    if not args:
        await u_obj.message.reply_text("⚠️ Vui lòng nhập số tiền cần nạp! Cú pháp: <code>/nap [số_tiền]</code>\n(Số tiền tối thiểu: 10.000đ)", parse_mode="HTML")
        return
    
    try:
        amt = int(args[0])
    except ValueError:
        await u_obj.message.reply_text("❌ Số tiền không hợp lệ! Vui lòng nhập một số nguyên.", parse_mode="HTML")
        return

    if amt < 10000:
        await u_obj.message.reply_text("❌ Số tiền nạp tối thiểu là <b>10.000 VNĐ</b>!", parse_mode="HTML")
        return

    uid = str(u_obj.effective_user.id)
    noi_dung_ck = f"NAPTIEN_{uid}"
    
    # Cấu hình thông tin tài khoản nhận tiền của Bot (Bạn có thể thay STK và Mã ngân hàng ở đây)
    STK_NH = "123456789"
    MA_NH = "MB" # Ví dụ: MB, VCB, TCB, BIDV,...

    qr_url = tao_link_qr_nap(STK_NH, MA_NH, amt, noi_dung_ck)
    
    # Ghi log lịch sử yêu cầu nạp
    ghi_ls_nap_rut(uid, f"TẠO QR NẠP: {amt:,.0f}đ | Nội dung: {noi_dung_ck}")

    caption_text = (
        f"<b>🏦 QUÉT MÃ QR ĐỂ NẠP TIỀN</b>\n\n"
        f"💵 Số tiền: <b>{amt:,.0f} VNĐ</b>\n"
        f"📝 Nội dung chuyển khoản bắt buộc: <code>{noi_dung_ck}</code>\n\n"
        f"⚠️ <i>Lưu ý: Phải chuyển chính xác nội dung trên để hệ thống tự động cộng tiền!</i>"
    )
    
    await u_obj.message.reply_photo(photo=qr_url, caption=caption_text, parse_mode="HTML")
# --- KẾT THÚC PHẦN BỔ SUNG QR ---

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
