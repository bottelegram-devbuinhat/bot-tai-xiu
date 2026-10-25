import logging # l
import os # o
import asyncio # a
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton # t
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters # e

import bxh
from config import c, u, g, f_w, p, q, t_f
from game import chay_vong_quay_game
from notif import cmd_tat_tb, cmd_bat_tb, ds_tat_tb
from wallet import cmd_cong, cmd_tru, cmd_rut, cmd_duyet, cmd_tuchoi
from giftcode import cmd_crcode, check_code
from admin import cmd_addadmin, cmd_kickadmin
from utils import gui_huong_dan
from history import xem_lich_su_user, xem_lich_su_admin

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) # log

def g_u(i, n=""): # gu
    s = str(i)
    if s not in u: u[s] = {}
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
    }
    x = False
    for k in dv:
        if k not in u[s]:
            u[s][k] = dv[k]
            x = True
    if x: f_w(p, u)
    return u[s]

async def c_s(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # cs
    i = u_obj.effective_user.id
    name = u_obj.effective_user.first_name
    w = g_u(i, name)
    if w["blocked"]:
        await u_obj.message.reply_text("<b>Tài khoản bị khóa!</b>", parse_mode="HTML")
        return
    
    ss = f"#{c.get('session_id', 1):04d}"
    if i in c["admin_ids"]:
        # WELCOME DÀNH RIÊNG CHO ADMIN
        welcome_admin = (
            f"👑 <b>CHÀO MỪNG QUẢN TRỊ VIÊN ĐẾN VỚI HỆ THỐNG!</b> 👑\n"
            f"—"*1 + "\n"
            f"• Xin chào Admin: <b>{name}</b>\n"
            f"• ID Telegram: <code>{i}</code>\n"
            f"• Trạng thái phiên hiện tại: <b>{ss}</b>\n\n"
            f"💡 <i>Sử dụng các phím bên dưới để quản lý hệ thống, duyệt nạp rút, sửa cầu hoặc cấu hình tỉ lệ.</i>"
        )
        k = ReplyKeyboardMarkup([
            [KeyboardButton("👥 Quản lý người chơi"), KeyboardButton("👑 Quản lý Admin")],
            [KeyboardButton("⚖️ Chỉnh tỉ lệ cược"), KeyboardButton("🎲 Sửa Cầu Toàn Server")],
            [KeyboardButton("🎟️ Tạo code"), KeyboardButton("📜 Lịch sử Server & Code")],
            [KeyboardButton("💰 Cộng/Trừ tiền"), KeyboardButton("📊 Thống kê hệ thống")],
            [KeyboardButton("📖 Hướng dẫn Admin"), KeyboardButton("🛑 Tắt bot")]
        ], resize_keyboard=True)
        await u_obj.message.reply_text(welcome_admin, reply_markup=k, parse_mode="HTML")
    else:
        # WELCOME DÀNH RIÊNG CHO NGƯỜI CHƠI
        st = "🟢 Đang mở" if c["bet_active"] else "🔴 Đang khóa"
        welcome_user = (
            f"🎮 <b>CHÀO MỪNG BẠN ĐẾN VỚI SẢNH TÀI XỈU VIP!</b> 🎮\n"
            f"—"*18 + "\n"
            f"• Chào mừng: <b>{name}</b>\n"
            f"• Số dư khả dụng: <b>{w['balance']:,.0f} VNĐ</b>\n"
            f"• Phiên hiện tại: <b>{ss}</b> ({st})\n\n"
            f"💡 <i>Nhắn nhanh <code>T[số_tiền]</code> (Tài) hoặc <code>X[số_tiền]</code> (Xỉu) để tham gia đặt cược ngay!</i>"
        )
        k = ReplyKeyboardMarkup([
            [KeyboardButton("🎲 Sảnh game"), KeyboardButton("💰 Thông tin tài khoản")],
            [KeyboardButton("💳 Nạp tiền"), KeyboardButton("💸 Rút tiền")],
            [KeyboardButton("🔗 Mời bạn"), KeyboardButton("🏆 Bảng xếp hạng")],
            [KeyboardButton("📜 Lịch sử cược cá nhân"), KeyboardButton("🔕 Tắt/Bật thông báo")],
            [KeyboardButton("🎟️ Nhập code"), KeyboardButton("📖 Hướng dẫn")]
        ], resize_keyboard=True)
        await u_obj.message.reply_text(welcome_user, reply_markup=k, parse_mode="HTML")

async def h_m(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # hm
    m = u_obj.message.text.strip()
    i = u_obj.effective_user.id
    w = g_u(i, u_obj.effective_user.first_name)
    if w["blocked"]: return

    if i in c["admin_ids"]:
        if m == "👥 Quản lý người chơi":
            kl = [[InlineKeyboardButton(f"{vv['name']} ({kk})", callback_data=f"us_view_{kk}")] for kk, vv in u.items()]
            await u_obj.message.reply_text("👥 <b>QUẢN LÝ USER</b>", reply_markup=InlineKeyboardMarkup(kl), parse_mode="HTML")
            return
        elif m == "👑 Quản lý Admin":
            await u_obj.message.reply_text(f"👑 <b>ADMINS</b>: <code>{c['admin_ids']}</code>\n• Thêm: <code>/addadmin [id]</code>\n• Kick: <code>/kickadmin [id]</code>", parse_mode="HTML")
            return
        elif m == "⚖️ Chỉnh tỉ lệ cược":
            kr = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Tỉ lệ TÀI: {c.get('tai_ratio', 1.95)}", callback_data="set_tai_ratio")],
                [InlineKeyboardButton(f"Tỉ lệ XỈU: {c.get('xiu_ratio', 1.95)}", callback_data="set_xiu_ratio")]
            ])
            await u_obj.message.reply_text("⚖️ <b>CHỈNH TỈ LỆ</b>", reply_markup=kr, parse_mode="HTML")
            return
        elif m == "🎲 Sửa Cầu Toàn Server":
            krd = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 Luôn ra TÀI", callback_data="g_road_tai"), InlineKeyboardButton("🎲 Luôn ra XỈU", callback_data="g_road_xiu")],
                [InlineKeyboardButton("🔄 Tắt sửa cầu", callback_data="g_road_rand")]
            ])
            await u_obj.message.reply_text("🎲 <b>SỬA CẦU TOÀN SERVER</b>", reply_markup=krd, parse_mode="HTML")
            return
        elif m == "🎟️ Tạo code":
            await u_obj.message.reply_text("🎟️ Lệnh tạo code: <code>/crcode [mã] [số_người] [tiền]</code>\n(Ví dụ: <code>/crcode BNDZ_VIP 10 50000</code>)", parse_mode="HTML")
            return
        elif m == "📜 Lịch sử Server & Code":
            await xem_lich_su_admin(u_obj)
            return
        elif m == "💰 Cộng/Trừ tiền":
            await u_obj.message.reply_text("💰 Lệnh:\n• <code>/cong [id] [tiền]</code>\n• <code>/tru [id] [tiền]</code>\n• Duyệt rút: <code>/duyet [id] [tiền]</code>\n• Từ chối rút: <code>/tuchoi [id] [tiền]</code>", parse_mode="HTML")
            return
        elif m == "📊 Thống kê hệ thống":
            tb = sum(acc.get("balance", 0) for acc in u.values())
            await u_obj.message.reply_text(f"📊 <b>THỐNG KÊ</b>\n• Tổng user: {len(u)}\n• Tổng tiền: <b>{tb:,.0f} VNĐ</b>", parse_mode="HTML")
            return
        elif m == "📖 Hướng dẫn Admin":
            await gui_huong_dan(u_obj, loai="admin")
            return
        elif m == "🛑 Tắt bot":
            await u_obj.message.reply_text("🛑 Đang tắt...", parse_mode="HTML")
            os._exit(0)

    if m == "🎲 Sảnh game":
        ss = f"#{c.get('session_id', 1):04d}"
        st = "🟢 Mở" if c["bet_active"] else "🔴 Khóa"
        await u_obj.message.reply_text(f"🎲 <b>SẢNH - {ss}</b> ({st})\n• Nhắn <code>T[tiền]</code> hoặc <code>X[tiền]</code> (1k - 100k).", parse_mode="HTML")
    elif m == "💰 Thông tin tài khoản":
        cb = w["current_bet"]
        bs = f"{cb['type']} - {cb['amount']:,.0f}đ" if cb else "Chưa đặt"
        it = (
            f"👤 <b>THÔNG TIN TÀI KHOẢN</b>\n"
            f"• Tên: {w['name']}\n"
            f"• ID Telegram: <code>{i}</code>\n"
            f"• Số dư: <b>{w['balance']:,.0f} VNĐ</b>\n"
            f"• Lượt Ref: {w['refs']}\n"
            f"• Số trận thắng: {w['wins']}\n"
            f"• Cược phiên hiện tại: {bs}"
        )
        await u_obj.message.reply_text(it, parse_mode="HTML")
    elif m == "💳 Nạp tiền":
        await u_obj.message.reply_text("💳 Liên hệ Admin để nạp tiền vào tài khoản(https://t.me/koka113).", parse_mode="HTML")
    elif m == "💸 Rút tiền":
        await u_obj.message.reply_text("💸 Cú pháp rút tiền:\n<code>/rut [stk] [tên_ngân_hàng] [số_tiền]</code>\n(Mỗi lần rút từ 100.000đ đến 1.000.000đ)", parse_mode="HTML")
    elif m == "🔗 Mời bạn":
        await u_obj.message.reply_text(f"🔗 Link giới thiệu:\nhttps://t.me/madeinnhatdz_bot?start={i}", parse_mode="HTML")
    elif m == "🏆 Bảng xếp hạng":
        await u_obj.message.reply_text(bxh.tao_noi_dung_bxh(), parse_mode="HTML")
    elif m == "📜 Lịch sử cược cá nhân":
        await xem_lich_su_user(u_obj, w, str(i))
        return
    elif m == "🔕 Tắt/Bật thông báo":
        str_i = str(i)
        if str_i in ds_tat_tb:
            ds_tat_tb.remove(str_i)
            f_w(t_f, ds_tat_tb)
            await u_obj.message.reply_text("🔔 Đã <b>BẬT</b> thông báo phiên!", parse_mode="HTML")
        else:
            ds_tat_tb.append(str_i)
            f_w(t_f, ds_tat_tb)
            await u_obj.message.reply_text("🔕 Đã <b>TẮT</b> thông báo phiên!", parse_mode="HTML")
    elif m == "🎟️ Nhập code":
        await u_obj.message.reply_text("🎟️ Nhắn mã dạng <code>BNDZ_XXXXXXXX</code> để nhận thưởng.", parse_mode="HTML")
    elif m == "📖 Hướng dẫn":
        await gui_huong_dan(u_obj, loai="user")
    else:
        tu = m.upper()
        if tu.startswith("/CODE ") or check_code(tu):
            ck = tu.replace("/CODE ", "").strip()
            if not check_code(ck):
                await u_obj.message.reply_text("❌ Sai định dạng mã! Mã phải có dạng <code>BNDZ_XXXXXXXX</code>", parse_mode="HTML")
                return
            if ck in g:
                gd = g[ck]
                if "used" not in gd: gd["used"] = []
                if len(gd["used"]) >= gd.get("max_uses", 1):
                    await u_obj.message.reply_text("❌ Mã đã hết lượt sử dụng!", parse_mode="HTML")
                    return
                if str(i) in gd["used"]:
                    await u_obj.message.reply_text("❌ Bạn đã dùng mã này rồi!", parse_mode="HTML")
                else:
                    gd["used"].append(str(i))
                    w["balance"] += gd["amount"]
                    f_w(q, g)
                    f_w(p, u)
                    await u_obj.message.reply_text(f"🎉 Nhận thành công +<b>{gd['amount']:,.0f} VNĐ</b> từ mã <code>{ck}</code>!", parse_mode="HTML")
            else:
                await u_obj.message.reply_text("❌ Mã quà tặng không tồn tại!", parse_mode="HTML")
        elif tu.startswith("T") or tu.startswith("X"):
            if not c["bet_active"]:
                await u_obj.message.reply_text("🔴 Đã hết giờ cược phiên này!", parse_mode="HTML")
                return
            
            if w.get("current_bet") is not None:
                await u_obj.message.reply_text("⚠️ Bạn đã đặt cược trong phiên này rồi! Mỗi phiên chỉ được phép cược 1 cửa duy nhất.", parse_mode="HTML")
                return

            try:
                bt = "TAI" if tu.startswith("T") else "XIU"
                amt = int(tu[1:])
                if amt < 1000 or amt > 100000:
                    await u_obj.message.reply_text("⚠️ Mức cược hợp lệ từ 1.000đ đến 100.000đ!", parse_mode="HTML")
                    return
                if w["balance"] < amt:
                    await u_obj.message.reply_text("❌ Số dư tài khoản không đủ để đặt cược!", parse_mode="HTML")
                    return
                
                w["balance"] -= amt
                w["bets_count"] += 1
                w["current_bet"] = {"type": bt, "amount": amt}
                w["nhan_thong_bao"] = True
                
                str_i = str(i)
                if str_i in ds_tat_tb:
                    ds_tat_tb.remove(str_i)
                    f_w(t_f, ds_tat_tb)

                f_w(p, u)
                nt = "TÀI 🎲" if bt == "TAI" else "XỈU 🎲"
                await u_obj.message.reply_text(f"✅ Đặt cược thành công <b>{amt:,.0f}đ</b> vào cửa <b>{nt}</b>!", parse_mode="HTML")
            except: pass

async def f_c(u_obj: Update, x_obj: ContextTypes.DEFAULT_TYPE): # fc
    q_obj = u_obj.callback_query
    await q_obj.answer()
    d = q_obj.data

    if d == "set_tai_ratio":
        c["tai_ratio"] = 1.98 if c.get("tai_ratio", 1.95) == 1.95 else 1.95
        f_w("config.json", c)
        await q_obj.answer("Đã đổi tỉ lệ Tài thành công!", show_alert=True)
    elif d == "set_xiu_ratio":
        c["xiu_ratio"] = 1.98 if c.get("xiu_ratio", 1.95) == 1.95 else 1.95
        f_w("config.json", c)
        await q_obj.answer("Đã đổi tỉ lệ Xỉu thành công!", show_alert=True)
    elif d == "g_road_tai":
        c["global_road"] = "TAI"
        f_w("config.json", c)
        await q_obj.answer("Đã sửa cầu toàn server: TÀI", show_alert=True)
    elif d == "g_road_xiu":
        c["global_road"] = "XIU"
        f_w("config.json", c)
        await q_obj.answer("Đã sửa cầu toàn server: XỈU", show_alert=True)
    elif d == "g_road_rand":
        c["global_road"] = None
        f_w("config.json", c)
        await q_obj.answer("Đã tắt sửa cầu (Về ngẫu nhiên)!", show_alert=True)
    elif d.startswith("us_view_"):
        ti = d.split("_")[2]
        if ti in u:
            tu = u[ti]
            msg = f"👤 <b>USER: {ti}</b>\n- Tên: {tu['name']}\n- Số dư: {tu['balance']:,.0f}đ\n- Thắng: {tu['wins']}"
            await q_obj.edit_message_text(msg, parse_mode="HTML")

def main(): # main
    tk = c.get("token", "")
    if not tk: return
    
    app = Application.builder().token(tk).build()
    app.add_handler(CommandHandler("start", c_s))
    app.add_handler(CommandHandler("cong", cmd_cong))
    app.add_handler(CommandHandler("tru", cmd_tru))
    app.add_handler(CommandHandler("rut", cmd_rut))
    app.add_handler(CommandHandler("duyet", cmd_duyet))
    app.add_handler(CommandHandler("tuchoi", cmd_tuchoi))
    app.add_handler(CommandHandler("crcode", cmd_crcode))
    app.add_handler(CommandHandler("addadmin", cmd_addadmin))
    app.add_handler(CommandHandler("kickadmin", cmd_kickadmin))
    app.add_handler(CommandHandler("tatthongbao", cmd_tat_tb))
    app.add_handler(CommandHandler("batthongbao", cmd_bat_tb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_m))
    app.add_handler(CallbackQueryHandler(f_c))
    
    async def pi(app_obj):
        asyncio.create_task(chay_vong_quay_game(app_obj))
        
    app.post_init = pi
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
