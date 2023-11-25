from datetime import datetime, timedelta
import pytz
import tkinter as tk
from PIL import Image, ImageTk

# Tableau des boss et de leurs horaires
boss_schedule = {
    "MON": [("00:15", "Kutum"), ("02:00", "Karanda"), ("05:00", "Kzarka"), ("09:00", "Kzarka"), ("12:00", "Offin"), 
            ("14:00", "Garmoth"), ("16:00", "Kutum"), ("19:00", "Nouver"), ("22:15", "Kzarka"), ("23:15", "Garmoth")],
    "TUE": [("00:15", "Karanda"), ("02:00", "Kutum"), ("05:00", "Kzarka"), ("09:00", "Nouver"), ("12:00", "Kutum"), 
            ("14:00", "Garmoth"), ("16:00", "Nouver"), ("19:00", "Karanda"), ("22:15", "Quint & Muraka"), ("23:15", "Garmoth")],
    "WED": [("00:15", "Kutum & Kzarka"), ("02:00", "Karanda"), ("05:00", "Kzarka"), ("09:00", "Karanda"), 
            ("16:00", "Kutum & Offin"), ("19:00", "Vell"), ("22:15", "Kzarka & Karanda"), ("23:15", "Garmoth")],
    "THU": [("00:15", "Nouver"), ("02:00", "Kutum"), ("05:00", "Nouver"), ("09:00", "Kutum"), ("12:00", "Nouver"), 
            ("14:00", "Garmoth"), ("16:00", "Kzarka"), ("19:00", "Kutum"), ("22:15", "Quint & Muraka"), ("23:15", "Garmoth")],
    "FRI": [("00:15", "Kzarka & Karanda"), ("02:00", "Nouver"), ("05:00", "Karanda"), ("09:00", "Kutum"), ("12:00", "Karanda"), 
            ("14:00", "Garmoth"), ("16:00", "Nouver"), ("19:00", "Kzarka"), ("22:15", "Kutum & Kzarka"), ("23:15", "Garmoth")],
    "SAT": [("00:15", "Karanda"), ("02:00", "Offin"), ("05:00", "Nouver"), ("09:00", "Kutum"), ("12:00", "Nouver"), 
            ("14:00", "Garmoth"), ("16:00", "Black Shadow"), ("19:00", "Kzarka & Karanda")],
    "SUN": [("00:15", "Kutum & Nouver"), ("02:00", "Kzarka"), ("05:00", "Kutum"), ("09:00", "Nouver"), ("12:00", "Kzarka"), 
            ("14:00", "Garmoth"), ("16:00", "Vell"), ("19:00", "Garmoth"), ("22:15", "Kzarka & Nouver"), ("23:15", "Garmoth")]
}

def find_next_boss(current_datetime):
    timezone = pytz.timezone('Europe/Paris')
    day = current_datetime.strftime("%a").upper()
    current_time = current_datetime.strftime("%H:%M")

    for time, boss in boss_schedule.get(day, []):
        if time > current_time:
            next_spawn_time_str = f"{current_datetime.strftime('%Y-%m-%d')} {time}"
            next_spawn_time = timezone.localize(datetime.strptime(next_spawn_time_str, "%Y-%m-%d %H:%M"))
            time_diff = next_spawn_time - current_datetime
            return boss, time_diff

    next_day_index = (current_datetime.weekday() + 1) % 7
    next_day = list(boss_schedule.keys())[next_day_index]
    next_spawn_time_str = f"{(current_datetime + timedelta(days=1)).strftime('%Y-%m-%d')} {boss_schedule[next_day][0][0]}"
    next_spawn_time = timezone.localize(datetime.strptime(next_spawn_time_str, "%Y-%m-%d %H:%M"))
    time_diff = next_spawn_time - current_datetime

    return boss_schedule[next_day][0][1], time_diff


def format_time_diff(time_diff):
    # Convertir la différence en heures et secondes
    hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"

def update_time_label(label, end_time, image_frames, boss_name, window, close_button):
    now = datetime.now(pytz.timezone('Europe/Paris'))
    time_diff = end_time - now
    formatted_time = format_time_diff(time_diff)
    label.config(text=f"Temps avant spawn: {formatted_time}")
    # Réajuster la position du bouton de fermeture
    close_button.pack_forget()
    close_button.pack(side="top", anchor="ne", padx=5, pady=5)
    if time_diff.total_seconds() > 0:
        label.after(1000, update_time_label, label, end_time, image_frames, boss_name, window, close_button)
    else:
        next_boss, new_end_time = find_next_boss(now)
        update_boss_images(image_frames, next_boss)
        label.after(1000, update_time_label, label, now + new_end_time, image_frames, next_boss, window, close_button)

def start_move(event, window):
    window._drag_start_x = event.x
    window._drag_start_y = event.y

def on_drag(event, window):
    dx = event.x - window._drag_start_x
    dy = event.y - window._drag_start_y
    x = window.winfo_x() + dx
    y = window.winfo_y() + dy
    window.geometry(f"+{x}+{y}")

def create_window(next_boss, end_time):
    window = tk.Tk()
    window.title("Prochain Boss")

    # Fenêtre sans barre de titre standard
    window.overrideredirect(True)

    # S'assurer que la fenêtre reste toujours au premier plan
    window.attributes("-topmost", True)

    # Style de la fenêtre
    window.configure(bg='#A9B2C3')
    window.geometry("+100+0")

    # Drag and move functionality
    window.bind("<ButtonPress-1>", lambda event: start_move(event, window))
    window.bind("<B1-Motion>", lambda event: on_drag(event, window))

    # Chargement de l'image du bouton de fermeture et redimensionnement
    close_img = Image.open("close_button.png")  # Assurez-vous d'avoir une image pour le bouton close
    close_img = close_img.resize((25, 25), Image.Resampling.LANCZOS)
    close_photo = ImageTk.PhotoImage(close_img)

    close_button = tk.Button(window, image=close_photo, command=window.destroy, bg="#A9B2C3", borderwidth=0, highlightthickness=0)
    close_button.image = close_photo
    close_button.pack(side="top", anchor="ne", padx=5, pady=5)
    # Labels pour les images des boss
    image_frame1 = tk.Label(window, bg='#A9B2C3')
    image_frame2 = tk.Label(window, bg='#A9B2C3')
    image_frames = [image_frame1, image_frame2]
    update_boss_images(image_frames, next_boss)

    # Label pour le nom du boss
    boss_label = tk.Label(window, text=f"Prochain boss: {next_boss}", font=("Helvetica", 14, "bold"), fg="#30475E", bg='#A9B2C3')
    boss_label.pack(side="top", pady=(10, 0))

    # Label pour le temps restant
    time_label = tk.Label(window, font=("Helvetica", 14), fg="#30475E", bg='#A9B2C3')
    time_label.pack(side="top", pady=10)

    update_time_label(time_label, end_time, image_frames, next_boss, window, close_button)

    window.mainloop()

def update_boss_images(frames, boss_name):
    # Cacher les frames avant de mettre à jour
    for frame in frames:
        frame.pack_forget()

    boss_names = boss_name.split(" & ")
    for i, name in enumerate(boss_names):
        try:
            image_path = f"{name.replace(' ', '')}.png"
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)

            frames[i].config(image=img)
            frames[i].image = img
            frames[i].pack(side="left", padx=(10, 0))
        except Exception as e:
            print(f"Erreur lors du chargement de l'image pour {name}: {e}")

# Exemple d'utilisation
now = datetime.now(pytz.timezone('Europe/Paris'))
next_boss, time_to_spawn = find_next_boss(now)
end_time = now + time_to_spawn

create_window(next_boss, end_time)