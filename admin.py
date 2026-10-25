from config import c, r, f_w, u

async def cmd_addadmin(u_obj, x_obj): # ca
    if u_obj.effective_user.id not in c["admin_ids"]: return
    args = x_obj.args
    if not args: return
    try:
        na = int(args[0])
        if na not in c["admin_ids"]:
            c["admin_ids"].append(na)
            f_w(r, c)
            await u_obj.message.reply_text(f"👑 Đã thêm Admin: <code>{na}</code>", parse_mode="HTML")
    except: pass

async def cmd_kickadmin(u_obj, x_obj): # cka
    cur = u_obj.effective_user.id
    if cur != 8792000582:
        await u_obj.message.reply_text("❌ Chỉ có ID tối cao <code>8792000582</code> mới có quyền kick admin!", parse_mode="HTML")
        return
    args = x_obj.args
    if not args: return
    try:
        tar = int(args[0])
        if tar == 8792000582:
            await u_obj.message.reply_text("❌ Không thể kick Admin tối cao!", parse_mode="HTML")
            return
        if tar in c["admin_ids"]:
            c["admin_ids"].remove(tar)
            f_w(r, c)
            await u_obj.message.reply_text(f"✅ Đã xóa quyền Admin của: <code>{tar}</code>", parse_mode="HTML")
    except: pass