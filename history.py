import os # o
from config import l_f, q, lich_su_nap_rut

async def xem_lich_su_user(u_obj, user_data, uid): # xlsu
    hl = user_data.get("history", [])
    ht = "📜 <b>LỊCH SỬ CƯỢC CÁ NHÂN</b>\n" + "—"*15 + "\n"
    if not hl: ht += "• Chưa có lịch sử cược.\n"
    else: ht += "\n".join([f"• {x}" for x in hl]) + "\n"

    ht += "\n💳 <b>LỊCH SỬ NẠP/RÚT GIAO DỊCH:</b>\n" + "—"*15 + "\n"
    found = False
    if os.path.exists(lich_su_nap_rut):
        with open(lich_su_nap_rut, 'r', encoding='utf-8') as f:
            for line in f:
                if f"USER:{uid}" in line:
                    found = True
                    parts = line.split("|")
                    if len(parts) > 1:
                        ht += f"• {parts[1].strip()}\n"
    if not found:
        ht += "• Chưa có giao dịch nạp rút nào."

    await u_obj.message.reply_text(ht, parse_mode="HTML")

async def xem_lich_su_admin(u_obj): # xlsa
    txt = ""
    if os.path.exists(l_f):
        with open(l_f, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        txt += "📜 <b>LỊCH SỬ PHIÊN SERVER (10 phiên gần nhất)</b>\n" + "".join(lines[-10:]) + "\n\n"
    else:
        txt += "📜 Chưa có lịch sử phiên server.\n\n"

    txt += "💸 <b>YÊU CẦU NẠP / RÚT GIAO DỊCH GẦN ĐÂY:</b>\n"
    if os.path.exists(lich_su_nap_rut):
        with open(lich_su_nap_rut, 'r', encoding='utf-8') as f:
            nr_lines = f.readlines()
        txt += "".join([f"• {line.strip()}\n" for line in nr_lines[-10:]]) + "\n"
        txt += "💡 <i>Duyệt: <code>/duyet [id] [số_tiền]</code> | Từ chối: <code>/tuchoi [id] [số_tiền]</code></i>\n\n"
    else:
        txt += "• Chưa có lịch sử giao dịch.\n\n"

    from config import g
    txt += "🎟️ <b>THỐNG KÊ GIFTCODE:</b>\n"
    for mk, mv in g.items():
        used_list = ", ".join(mv.get("used", [])) if mv.get("used") else "Chưa có"
        txt += f"• Mã <code>{mk}</code> ({mv.get('amount', 0):,.0f}đ) - Dùng: {len(mv.get('used', []))}/{mv.get('max_uses', 1)} | [ID: {used_list}]\n"
    
    await u_obj.message.reply_text(txt, parse_mode="HTML")