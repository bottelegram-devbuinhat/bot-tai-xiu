import os
from config import c  # Import cấu hình hệ thống chứa admin_ids

async def gui_huong_dan(u_obj):
    user_id = u_obj.effective_user.id
    
    # Tự động check id trong config. Khi dùng lệnh /addadmin, c["admin_ids"] sẽ tự tăng lên
    if user_id in c["admin_ids"]:
        file_name = "huong_dan_admin.txt"
    else:
        file_name = "huong_dan_nguoi_dung.txt"
    
    # Tiến hành đọc nội dung file văn bản tương ứng
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            txt = f.read()
    else:
        txt = "⚠️ Không tìm thấy file dữ liệu hướng dẫn trên hệ thống."
        
    await u_obj.message.reply_text(txt, parse_mode="HTML")
