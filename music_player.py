# 🎧 Premium Vertical Python Music Player
# By ChatGPT – Fullscreen + Colorful + Icon/Text Buttons

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from tkinter import ttk
from pygame import mixer
from mutagen.mp3 import MP3

mixer.pre_init(44100, -16, 2, 4096)
mixer.init()


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("🎶 Python Music Player Pro")

        # 🔲 Full Screen
        self.root.state("zoomed")

        # Vars
        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.duration = 0
        self.seek_offset = 0
        self._was_playing = False

        self.build_ui()
        self.root.after(700, self.update_progress)

    # 🧱 GUI LAYOUT
    def build_ui(self):
        header = tb.Frame(self.root, bootstyle="info", padding=15)
        header.pack(fill="x")
        tb.Label(
            header,
            text="🎵 Python Music Player Pro",
            font=("Helvetica", 30, "bold"),
            bootstyle="inverse-info",
        ).pack()

        main_frame = tb.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 🎶 Playlist (Left)
        playlist_frame = tb.Labelframe(main_frame, text="Playlist 🎧", bootstyle="success", padding=10)
        playlist_frame.pack(side="left", fill="y", padx=15)

        self.listbox = tk.Listbox(
            playlist_frame,
            width=45,
            height=28,
            bg="#101010",
            fg="white",
            font=("Segoe UI", 13),
            selectbackground="#1DB954",
            relief="flat",
        )
        self.listbox.pack(side="left", fill="y")
        scroll = ttk.Scrollbar(playlist_frame, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        # 🎛 Controls (Right)
        right = tb.Frame(main_frame)
        right.pack(side="left", fill="both", expand=True, padx=30)

        self.song_label = tb.Label(
            right,
            text="No Song Loaded",
            font=("Helvetica", 18, "bold"),
            bootstyle="inverse-success",
        )
        self.song_label.pack(pady=10)

        # Progress
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Scale(
            right,
            from_=0,
            to=100,
            orient="horizontal",
            length=600,
            variable=self.progress_var,
            style="success.Horizontal.TScale",
        )
        self.progress.pack(pady=10)
        self.progress.bind("<ButtonRelease-1>", self.on_seek)

        self.time_label = tb.Label(right, text="00:00 / 00:00", font=("Consolas", 14))
        self.time_label.pack(pady=8)

        # 🔘 Vertical Buttons
        btn_frame = tb.Labelframe(right, text="Controls", bootstyle="info", padding=10)
        btn_frame.pack(side="left", padx=20, pady=10)

        button_specs = [
            ("▶ Play", "success", self.play_song),
            ("⏸ Pause", "warning", self.pause_song),
            ("⏹ Stop", "danger", self.stop_song),
            ("⏮ Prev", "info", self.prev_song),
            ("⏭ Next", "info", self.next_song),
            ("📁 Load Folder", "secondary", self.load_folder),
        ]

        for text, style, cmd in button_specs:
            tb.Button(
                btn_frame,
                text=text,
                bootstyle=f"{style}-outline",
                width=18,
                command=cmd,
            ).pack(pady=8)

        # 🔊 Volume Slider (Right Side)
        vol_frame = tb.Labelframe(right, text="Volume", bootstyle="success", padding=10)
        vol_frame.pack(side="left", padx=30, pady=10)
        tb.Label(vol_frame, text="🔊", font=("Segoe UI", 20)).pack(pady=5)
        self.vol = tk.DoubleVar(value=0.7)
        self.vol_slider = ttk.Scale(
            vol_frame,
            from_=0.0,
            to=1.0,
            orient="vertical",
            length=200,
            variable=self.vol,
            command=self.set_volume,
        )
        self.vol_slider.pack()
        mixer.music.set_volume(0.7)

        tb.Label(
            self.root,
            text="✨ Designed with ❤️ using ttkbootstrap + pygame",
            bootstyle="secondary",
            font=("Segoe UI", 11),
        ).pack(side="bottom", pady=5)

    # 📁 Load Folder
    def load_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.playlist.clear()
        self.listbox.delete(0, tk.END)
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith(".mp3"):
                path = os.path.join(folder, f)
                duration = 0
                try:
                    duration = int(MP3(path).info.length)
                except:
                    pass
                self.playlist.append({"path": path, "title": f, "duration": duration})
                self.listbox.insert(tk.END, f)
        if not self.playlist:
            messagebox.showerror("No Songs", "No .mp3 files found in this folder!")
        else:
            self.song_label.config(text=f"Loaded {len(self.playlist)} Songs 🎶")

    # ▶ Play
    def play_song(self):
        if not self.playlist:
            messagebox.showinfo("No Songs", "Please load a folder first.")
            return
        sel = self.listbox.curselection()
        if sel:
            self.current_index = sel[0]
        entry = self.playlist[self.current_index]
        mixer.music.load(entry["path"])
        mixer.music.play()
        self.paused = False
        self.seek_offset = 0
        self.duration = entry["duration"]
        self.song_label.config(text=f"🎵 Playing: {entry['title']}")
        self._was_playing = True

    # ⏸ Pause / Resume
    def pause_song(self):
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.song_label.config(text="▶ Resumed")
        else:
            mixer.music.pause()
            self.paused = True
            self.song_label.config(text="⏸ Paused")

    # ⏹ Stop
    def stop_song(self):
        mixer.music.stop()
        self.seek_offset = 0
        self.progress_var.set(0)
        self.song_label.config(text="⏹ Stopped")

    # ⏭ Next
    def next_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_index)
        self.play_song()

    # ⏮ Prev
    def prev_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_index)
        self.play_song()

    # 🔊 Volume
    def set_volume(self, _=None):
        mixer.music.set_volume(float(self.vol.get()))

    # ⏩ Seek
    def on_seek(self, _):
        if not self.playlist or not self.duration:
            return
        pct = float(self.progress_var.get())
        sec = (pct / 100) * self.duration
        self.seek_offset = sec
        try:
            mixer.music.play(start=sec)
        except Exception:
            mixer.music.rewind()
        self.paused = False

    # ⏱ Update Progress + Time
    def update_progress(self):
        if self.playlist and mixer.get_init():
            pos = mixer.music.get_pos() / 1000.0
            current_time = self.seek_offset + pos
            if current_time > self.duration:
                current_time = self.duration
            if self.duration:
                pct = (current_time / self.duration) * 100
                self.progress_var.set(pct)
                mins, secs = divmod(int(current_time), 60)
                total_mins, total_secs = divmod(self.duration, 60)
                self.time_label.config(
                    text=f"{mins:02d}:{secs:02d} / {total_mins:02d}:{total_secs:02d}"
                )
            else:
                self.time_label.config(text=f"{int(current_time)} sec / --:--")

            if self._was_playing and not mixer.music.get_busy() and not self.paused:
                self.next_song()

        self.root.after(700, self.update_progress)


if __name__ == "__main__":
    # 🎨 Try themes: minty, superhero, cyborg, vapor, pulse, flatly, morph
    app = tb.Window(themename="morph")
    MusicPlayer(app)
    app.mainloop()
