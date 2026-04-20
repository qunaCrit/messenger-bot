import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_sheet(order):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
        client = gspread.authorize(creds)
        sheet = client.open("Đơn hàng Messenger").sheet1

        sheet.append_row([
            order['time'],
            order['name'],
            order['phone'],
            order['quantity'],
            order['content'],
            f"fb.com/{order['fb_id']}"
        ])
        print("✅ Đã lưu đơn vào Google Sheet")
    except Exception as e:
        print(f"Lỗi lưu Sheet: {e}")
