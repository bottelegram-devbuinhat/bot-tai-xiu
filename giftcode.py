import re # re
from config import g, q, u, f_w, p

def check_code(s): # cc
    return bool(re.match(r"^BNDZ_[A-Z0-9_]+$", s.upper()))

async def cmd_crcode(u_obj, x_obj): # crc
    from config import c
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if len(args) < 3:
        await u_obj.message.reply_text("⚠️ Dùng: <code>/crcode [mã_BNDZ] [số_người] [mệnh_giá]</code>", parse_mode="HTML")
        return
    ck = args[0].upper()
    try:
        gn, mg = int(args[1]), int(args[2])
    except ValueError: return
    if not check_code(ck): return
    g[ck] = {"amount": mg, "max_uses": gn, "used": []}
    f_w(q, g)
    await u_obj.message.reply_text(f"🎟️ Đã tạo code <code>{ck}</code> (Mệnh giá: {mg:,.0f}đ, Số người: {gn})", parse_mode="HTML")