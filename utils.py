async def gui_huong_dan(u_obj, loai="user"): # ghd
    if loai == "admin":
        txt = "👑 <b>HƯỚNG DẪN ADMIN</b>\n• /cong [id] [tiền]\n• /tru [id] [tiền]\n• /crcode [mã] [số_người] [tiền]\n• /addadmin [id]\n• /kickadmin [id]\n• /rut [stk] [tên] [tiền]"
    else:
        txt = "📖 <b>HƯỚNG DẪN NGƯỜI CHƠI</b>\n• Nhắn T[tiền] hoặc X[tiền]\n• /rut [stk] [tên] [tiền]\n• Nhập mã BNDZ_XXXXXXXX"
    await u_obj.message.reply_text(txt, parse_mode="HTML")