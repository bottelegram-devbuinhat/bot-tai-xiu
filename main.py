# main.py
import logging # l
import os # o
import asyncio # a
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton # t
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters # e

import bxh # b
from config import c, u, g, f_w, p, q, t_f # c
from game import chay_vong_quay_game # g
from notif import cmd_tat_tb, cmd_bat_tb, ds_tat_tb # n
from wallet import cmd_cong, cmd_tru, cmd_rut, cmd_duyet, cmd_tuchoi, cmd_nap # w
from giftcode import cmd_crcode, check_code # gc
from admin import cmd_addadmin, cmd_kickadmin # a
from utils import gui_huong_dan # ut
from history import xem_lich_su_user, xem_lich_su_admin # h

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) # log

def g_u(i, n=""): # gu
    s = str(i) # s
    if s not in u: u[s] = {} # u
    dv = {
        "name": n,
        "balance": c.get("default_balance", 10000),
        "wins": 0,
        "bets_count": 0,
        "refs": 0,
        "blocked": False,
        "current_bet": None,
        "history": [],
        "nhan_thong_bao": False
    } # dv
    x = False # x
    for k in dv: # k
        if k not in u[s]: # c
            u[s][k] = dv[k] # a
            x = True # t
    if x: f_w(p, u) # w
    return u[s] # r

async def c_s(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # cs
    i = u_obj.effective_user.id # i
    name = u_obj.effective_user.first_name # n
    w = g_u(i, name) # w
    if w["blocked"]: # b
        await u_obj.message.reply_text("<b>Tài khoản bị khóa!</b>", parse_mode="HTML") # m
        return # r
    
    ss = f"#{c.get('session_id', 1):04d}" # ss
    if i in c["admin_ids"]: # a
        welcome_admin = (
            f"👑 <b>CHÀO MỪNG QUẢN TRỊ VIÊN ĐẾN VỚI HỆ THỐNG!</b> 👑\n"
            f"—"*1 + "\n"
            f"• Xin chào Admin: <b>{name}</b>\n"
            f"• ID Telegram: <code>{i}</code>\n"
            f"• Trạng thái phiên hiện tại: <b>{ss}</b>\n\n"
            f"💡 <i>Sử dụng các phím bên dưới để quản lý hệ thống, duyệt nạp rút, sửa cầu hoặc cấu hình tỉ lệ.</i>"
        ) # wa
        k = ReplyKeyboardMarkup([
            [KeyboardButton("👥 Quản lý người chơi"), KeyboardButton("👑 Quản lý Admin")],
            [KeyboardButton("⚖️ Chỉnh tỉ lệ cược"), KeyboardButton("🎲 Sửa Cầu Toàn Server")],
            [KeyboardButton("🎟️ Tạo code"), KeyboardButton("📜 Lịch sử Server & Code")],
            [KeyboardButton("💰 Cộng/Trừ tiền"), KeyboardButton("📊 Thống kê hệ thống")],
            [KeyboardButton("📖 Hướng dẫn Admin"), KeyboardButton("🛑 Tắt bot")]
        ], resize_keyboard=True) # k
        await u_obj.message.reply_text(welcome_admin, reply_markup=k, parse_mode="HTML") # m
    else:
        st = "🟢 Đang mở" if c["bet_active"] else "🔴 Đang khóa" # st
        welcome_user = (
            f"🎮 <b>CHÀO MỪNG BẠN ĐẾN VỚI SẢNH TÀI XỈU VIP!</b> 🎮\n"
            f"—"*18 + "\n"
            f"• Chào mừng: <b>{name}</b>\n"
            f"• Số dư khả dụng: <b>{w['balance']:,.0f} VNĐ</b>\n"
            f"• Phiên hiện tại: <b>{ss}</b> ({st})\n\n"
            f"💡 <i>Nhắn nhanh <code>T[số_tiền]</code> (Tài) hoặc <code>X[số_tiền]</code> (Xỉu) để tham gia đặt cược ngay!</i>"
        ) # wu
        k = ReplyKeyboardMarkup([
            [KeyboardButton("🎲 Sảnh game"), KeyboardButton("💰 Thông tin tài khoản")],
            [KeyboardButton("💳 Nạp tiền"), KeyboardButton("💸 Rút tiền")],
            [KeyboardButton("🔗 Mời bạn"), KeyboardButton("🏆 Bảng xếp hạng")],
            [KeyboardButton("📜 Lịch sử cược cá nhân"), KeyboardButton("🔕 Tắt/Bật thông báo")],
            [KeyboardButton("🎟️ Nhập code"), KeyboardButton("📖 Hướng dẫn")]
        ], resize_keyboard=True) # k
        await u_obj.message.reply_text(welcome_user, reply_markup=k, parse_mode="HTML") # m

async def h_m(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # hm
    m = u_obj.message.text.strip() # m
    i = u_obj.effective_user.id # i
    w = g_u(i, u_obj.effective_user.first_name) # w
    if w["blocked"]: return # b

    if i in c["admin_ids"]: # a
        if m == "👥 Quản lý người chơi": # ql
            kl = [[InlineKeyboardButton(f"{vv['name']} ({kk})", callback_data=f"us_view_{kk}")] for kk, vv in u.items()] # kl
            await u_obj.message.reply_text("👥 <b>QUẢN LÝ USER</b>", reply_markup=InlineKeyboardMarkup(kl), parse_mode="HTML") # m
            return # r
        elif m == "👑 Quản lý Admin": # qla
            await u_obj.message.reply_text(f"👑 <b>ADMINS</b>: <code>{c['admin_ids']}</code>\n• Thêm: <code>/addadmin [id]</code>\n• Kick: <code>/kickadmin [id]</code>", parse_mode="HTML") # m
            return # r
        elif m == "⚖️ Chỉnh tỉ lệ cược": # ctl
            kr = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Tỉ lệ TÀI: {c.get('tai_ratio', 1.95)}", callback_data="set_tai_ratio")],
                [InlineKeyboardButton(f"Tỉ lệ XỈU: {c.get('xiu_ratio', 1.95)}", callback_data="set_xiu_ratio")]
            ]) # kr
            await u_obj.message.reply_text("⚖️ <b>CHỈNH TỈ LỆ</b>", reply_markup=kr, parse_mode="HTML") # m
            return # r
        elif m == "🎲 Sửa Cầu Toàn Server": # sc
            krd = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 Luôn ra TÀI", callback_data="g_road_tai"), InlineKeyboardButton("🎲 Luôn ra XỈU", callback_data="g_road_xiu")],
                [InlineKeyboardButton("🔄 Tắt sửa cầu", callback_data="g_road_rand")]
            ]) # krd
            await u_obj.message.reply_text("🎲 <b>SỬA CẦU TOÀN SERVER</b>", reply_markup=krd, parse_mode="HTML") # m
            return # r
        elif m == "🎟️ Tạo code": # tc
            await u_obj.message.reply_text("🎟️ Lệnh tạo code: <code>/crcode [mã] [số_người] [tiền]</code>\n(Ví dụ: <code>/crcode BNDZ_VIP 10 50000</code>)", parse_mode="HTML") # m
            return # r
        elif m == "📜 Lịch sử Server & Code": # ls
            await xem_lich_su_admin(u_obj) # xl
            return # r
        elif m == "💰 Cộng/Trừ tiền": # ct
            await u_obj.message.reply_text("💰 Lệnh:\n• <code>/cong [id] [tiền]</code>\n• <code>/tru [id] [tiền]</code>\n• Duyệt rút: <code>/duyet [id] [tiền]</code>\n• Từ chối rút: <code>/tuchoi [id] [tiền]</code>", parse_mode="HTML") # m
            return # r
        elif m == "📊 Thống kê hệ thống": # tk
            tb = sum(acc.get("balance", 0) for acc in u.values()) # tb
            await u_obj.message.reply_text(f"📊 <b>THỐNG KÊ</b>\n• Tổng user: {len(u)}\n• Tổng tiền: <b>{tb:,.0f} VNĐ</b>", parse_mode="HTML") # m
            return # r
        elif m == "📖 Hướng dẫn Admin": # hd
            await gui_huong_dan(u_obj, loai="admin") # gh
            return # r
        elif m == "🛑 Tắt bot": # tb
            await u_obj.message.reply_text("🛑 Đang tắt...", parse_mode="HTML") # m
            os._exit(0) # e

    if m == "🎲 Sảnh game": # sg
        ss = f"#{c.get('session_id', 1):04d}" # ss
        st = "🟢 Mở" if c["bet_active"] else "🔴 Khóa" # st
        await u_obj.message.reply_text(f"🎲 <b>SẢNH - {ss}</b> ({st})\n• Nhắn <code>T[tiền]</code> hoặc <code>X[tiền]</code> (1k - 100k).", parse_mode="HTML") # m
    elif m == "💰 Thông tin tài khoản": # tt
        cb = w["current_bet"] # cb
        bs = f"{cb['type']} - {cb['amount']:,.0f}đ" if cb else "Chưa đặt" # bs
        it = (
            f"👤 <b>THÔNG TIN TÀI KHOẢN</b>\n"
            f"• Tên: {w['name']}\n"
            f"• ID Telegram: <code>{i}</code>\n"
            f"• Số dư: <b>{w['balance']:,.0f} VNĐ</b>\n"
            f"• Lượt Ref: {w['refs']}\n"
            f"• Số trận thắng: {w['wins']}\n"
            f"• Cược phiên hiện tại: {bs}"
        ) # it
        await u_obj.message.reply_text(it, parse_mode="HTML") # m
    elif m == "💳 Nạp tiền": # nt
        await u_obj.message.reply_text("💳 Lệnh nạp tiền: <code>/nap [số_tiền]</code>\n(Ví dụ: <code>/nap 50000</code>)", parse_mode="HTML") # m
    elif m == "💸 Rút tiền": # rt
        await u_obj.message.reply_text("💸 Cú pháp rút tiền:\n<code>/rut [stk] [tên_ngân_hàng] [số_tiền]</code>\n(Mỗi lần rút từ 100.000đ đến 1.000.000đ)", parse_mode="HTML") # m
    elif m == "🔗 Mời bạn": # mb
        await u_obj.message.reply_text(f"🔗 Link giới thiệu:\nhttps://t.me/madeinnhatdz_bot?start={i}", parse_mode="HTML") # m
    elif m == "🏆 Bảng xếp hạng": # bxh
        await u_obj.message.reply_text(bxh.tao_noi_dung_bxh(), parse_mode="HTML") # m
    elif m == "📜 Lịch sử cược cá nhân": # ls
        await xem_lich_su_user(u_obj, w, str(i)) # xl
        return # r
    elif m == "🔕 Tắt/Bật thông báo": # tb
        str_i = str(i) # str_i
        if str_i in ds_tat_tb: # c
            ds_tat_tb.remove(str_i) # rm
            f_w(t_f, ds_tat_tb) # fw
            await u_obj.message.reply_text("🔔 Đã <b>BẬT</b> thông báo phiên!", parse_mode="HTML") # m
        else:
            ds_tat_tb.append(str_i) # ap
            f_w(t_f, ds_tat_tb) # fw
            await u_obj.message.reply_text("🔕 Đã <b>TẮT</b> thông báo phiên!", parse_mode="HTML") # m
    elif m == "🎟️ Nhập code": # nc
        await u_obj.message.reply_text("🎟️ Nhắn mã dạng <code>BNDZ_XXXXXXXX</code> để nhận thưởng.", parse_mode="HTML") # m
    elif m == "📖 Hướng dẫn": # hd
        await gui_huong_dan(u_obj, loai="user") # gh
    else:
        tu = m.upper() # tu
        if tu.startswith("/CODE ") or check_code(tu): # c
            ck = tu.replace("/CODE ", "").strip() # ck
            if not check_code(ck): # c
                await u_obj.message.reply_text("❌ Sai định dạng mã! Mã phải có dạng <code>BNDZ_XXXXXXXX</code>", parse_mode="HTML") # m
                return # r
            if ck in g: # g
                gd = g[ck] # gd
                if "used" not in gd: gd["used"] = [] # u
                if len(gd["used"]) >= gd.get("max_uses", 1): # m
                    await u_obj.message.reply_text("❌ Mã đã hết lượt sử dụng!", parse_mode="HTML") # m
                    return # r
                if str(i) in gd["used"]: # c
                    await u_obj.message.reply_text("❌ Bạn đã dùng mã này rồi!", parse_mode="HTML") # m
                else:
                    gd["used"].append(str(i)) # a
                    w["balance"] += gd["amount"] # b
                    f_w(q, g) # fw
                    f_w(p, u) # fw
                    await u_obj.message.reply_text(f"🎉 Nhận thành công +<b>{gd['amount']:,.0f} VNĐ</b> từ mã <code>{ck}</code>!", parse_mode="HTML") # m
            else:
                await u_obj.message.reply_text("❌ Mã quà tặng không tồn tại!", parse_mode="HTML") # m
        elif tu.startswith("T") or tu.startswith("X"): # tx
            if not c["bet_active"]: # a
                await u_obj.message.reply_text("🔴 Đã hết giờ cược phiên này!", parse_mode="HTML") # m
                return # r
            
            if w.get("current_bet") is not None: # c
                await u_obj.message.reply_text("⚠️ Bạn đã đặt cược trong phiên này rồi! Mỗi phiên chỉ được phép cược 1 cửa duy nhất.", parse_mode="HTML") # m
                return # r

            try:
                bt = "TAI" if tu.startswith("T") else "XIU" # bt
                amt = int(tu[1:]) # amt
                if amt < 1000 or amt > 100000: # c
                    await u_obj.message.reply_text("⚠️ Mức cược hợp lệ từ 1.000đ đến 100.000đ!", parse_mode="HTML") # m
                    return # r
                if w["balance"] < amt: # c
                    await u_obj.message.reply_text("❌ Số dư tài khoản không đủ để đặt cược!", parse_mode="HTML") # m
                    return # r
                
                w["balance"] -= amt # b
                w["bets_count"] += 1 # c
                w["current_bet"] = {"type": bt, "amount": amt} # cb
                w["nhan_thong_bao"] = True # nt
                
                str_i = str(i) # str_i
                if str_i in ds_tat_tb: # c
                    ds_tat_tb.remove(str_i) # rm
                    f_w(t_f, ds_tat_tb) # fw

                f_w(p, u) # fw
                nt = "TÀI 🎲" if bt == "TAI" else "XỈU 🎲" # nt
                await u_obj.message.reply_text(f"✅ Đặt cược thành công <b>{amt:,.0f}đ</b> vào cửa <b>{nt}</b>!", parse_mode="HTML") # m
            except: pass # e

async def f_c(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # fc
    q_obj = u_obj.callback_query # q
    await q_obj.answer() # a
    d = q_obj.data # d

    if d == "set_tai_ratio": # tr
        c["tai_ratio"] = 1.98 if c.get("tai_ratio", 1.95) == 1.95 else 1.95 # c
        f_w("config.json", c) # fw
        await q_obj.answer("Đã đổi tỉ lệ Tài thành công!", show_alert=True) # a
    elif d == "set_xiu_ratio": # xr
        c["xiu_ratio"] = 1.98 if c.get("xiu_ratio", 1.95) == 1.95 else 1.95 # c
        f_w("config.json", c) # fw
        await q_obj.answer("Đã đổi tỉ lệ Xỉu thành công!", show_alert=True) # a
    elif d == "g_road_tai": # rt
        c["global_road"] = "TAI" # c
        f_w("config.json", c) # fw
        await q_obj.answer("Đã sửa cầu toàn server: TÀI", show_alert=True) # a
    elif d == "g_road_xiu": # rx
        c["global_road"] = "XIU" # c
        f_w("config.json", c) # fw
        await q_obj.answer("Đã sửa cầu toàn server: XỈU", show_alert=True) # a
    elif d == "g_road_rand": # rr
        c["global_road"] = None # c
        f_w("config.json", c) # fw
        await q_obj.answer("Đã tắt sửa cầu (Về ngẫu nhiên)!", show_alert=True) # a
    elif d.startswith("us_view_"): # uv
        ti = d.split("_")[2] # ti
        if ti in u: # c
            tu = u[ti] # tu
            msg = f"👤 <b>USER: {ti}</b>\n- Tên: {tu['name']}\n- Số dư: {tu['balance']:,.0f}đ\n- Thắng: {tu['wins']}" # m
            await q_obj.edit_message_text(msg, parse_mode="HTML") # e

def main(): # main
    tk = c.get("token", "") # tk
    if not tk: return # r
    
    app = Application.builder().token(tk).build() # app
    app.add_handler(CommandHandler("start", c_s)) # h
    app.add_handler(CommandHandler("nap", cmd_nap)) # h
    app.add_handler(CommandHandler("naptien", cmd_nap)) # h
    app.add_handler(CommandHandler("cong", cmd_cong)) # h
    app.add_handler(CommandHandler("tru", cmd_tru)) # h
    app.add_handler(CommandHandler("rut", cmd_rut)) # h
    app.add_handler(CommandHandler("duyet", cmd_duyet)) # h
    app.add_handler(CommandHandler("tuchoi", cmd_tuchoi)) # h
    app.add_handler(CommandHandler("crcode", cmd_crcode)) # h
    app.add_handler(CommandHandler("code", cmd_crcode)) # h
    app.add_handler(CommandHandler("addadmin", cmd_addadmin)) # h
    app.add_handler(CommandHandler("kickadmin", cmd_kickadmin)) # h
    app.add_handler(CommandHandler("tatthongbao", cmd_tat_tb)) # h
    app.add_handler(CommandHandler("batthongbao", cmd_bat_tb)) # h
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_m)) # h
    app.add_handler(CallbackQueryHandler(f_c)) # h
    
    async def pi(app_obj): # pi
        asyncio.create_task(chay_vong_quay_game(app_obj)) # t
        
    app.post_init = pi # pi
    app.run_polling(drop_pending_updates=True) # run

if __name__ == "__main__":
    main() # run
