import os
import datetime
import time
import tkinter as tk
import csv
import winsound  
from PIL import Image, ImageTk 

def show_popup():
    root = tk.Tk()
    root.title("上課提醒計時器")
    root.state('zoomed') #最大化
    root.attributes("-topmost", True) #最上層
    
    remaining_seconds = 60
    screen_width = root.winfo_screenwidth() #寬
    screen_height = root.winfo_screenheight() #長

    #讀取檔案
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(BASE_DIR, "background.png")
    bell_path = os.path.join(BASE_DIR, "bell.wav")  

    #關閉視窗
    def on_closing():
        winsound.PlaySound(None, winsound.SND_PURGE) 
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #主程式
    try:
        bg_image_pil = Image.open(image_path)
        bg_image_resized = bg_image_pil.resize((screen_width, screen_height))
        bg_image = ImageTk.PhotoImage(bg_image_resized)
    except FileNotFoundError:
        tk.Label(root, text="找不到 background.png！", font=("Arial", 50), fg="red").pack(expand=True)
    else:
        #建立Canvas並放上圖片
        canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_image, anchor="nw")

        #加入倒數計時數字
        text_id = canvas.create_text(
            screen_width * (5.5 / 10),    #x座標
            screen_height / 2 * 1.2,   #y座標
            text="01:00",               
            font=("Arial", 120, "bold"), 
            fill="#E09EAA"              
        )

    # 音檔 背景播放
    if os.path.exists(bell_path):
        winsound.PlaySound(bell_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def update_countdown():
        nonlocal remaining_seconds
        if not root.winfo_exists():
            return
            
        if remaining_seconds > 0:
            remaining_seconds -= 1
            mins = remaining_seconds // 60 #剩下幾分
            secs = remaining_seconds % 60 #剩下幾秒
            
            if 'canvas' in locals(): #更新
                canvas.itemconfig(text_id, text=f"{mins:02d}:{secs:02d}")
            root.after(1000, update_countdown) #一秒執行一次
        else: #秒數歸零
            on_closing()
            
    update_countdown()
    root.mainloop()

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    schedule_path = os.path.join(BASE_DIR, "schedule.csv")

    weekday_map = {
        0: "星期一", 1: "星期二", 2: "星期三",
        3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"
    }
    
    last_triggered_time = None #避免同一分鐘重複觸發

    while True: #無限迴圈
        reminder_times = []
        now = datetime.datetime.now()
        
        current_weekday_index = now.weekday()
        current_weekday_str = weekday_map.get(current_weekday_index)

        # 讀取csv
        try:
            with open(schedule_path, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    target_time_str = row.get(current_weekday_str, "").strip()
                    
                    if not target_time_str:
                        continue
                        
                    today = datetime.date.today()
                    target_time = datetime.datetime.strptime(target_time_str, "%H:%M").time()
                    target_datetime = datetime.datetime.combine(today, target_time)
                    
                    reminder_datetime = target_datetime - datetime.timedelta(minutes=1)
                    reminder_times.append(reminder_datetime.strftime("%H:%M"))
        except FileNotFoundError:
            pass
            
        current_time_str = now.strftime("%H:%M")
        
        if current_time_str in reminder_times and current_time_str != last_triggered_time:
            last_triggered_time = current_time_str
            show_popup()
            
        time.sleep(1)