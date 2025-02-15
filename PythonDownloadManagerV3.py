import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import threading
import re
import webbrowser
import yt_dlp
import traceback

class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.DEFAULT_FONT = ctk.CTkFont(family="San-Serif", size=14, weight="bold")
        self.TITLE_FONT = ctk.CTkFont(family="San-Serif", size=24, weight="bold")
        self.BUTTON_FONT = ctk.CTkFont(family="San-Serif", size=16, weight="bold")
        self.FOOTER_FONT = ctk.CTkFont(family="San-Serif", size=12, weight="bold")
        self.title("YouTube Downloader")
        self.geometry("500x450")
        self.resizable(False, False)
        self.download_type_var = ctk.StringVar(value="single")
        self.playlist_link = ctk.StringVar()
        self.quality = ctk.StringVar(value="720p")
        self.format = ctk.StringVar(value="mp4")
        self.output_directory = ctk.StringVar(value="./downloads")
        self.dark_mode = ctk.BooleanVar(value=True)
        self.download_progress = ctk.DoubleVar()
        self.download_status = ctk.StringVar()
        self.progress_label_text = ctk.StringVar()
        self.current_downloading_number = ctk.StringVar()
        self.downloading_percentage = ctk.StringVar()
        self.remaining_number = ctk.StringVar()
        self.quality_options = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        self.cancel_download = False
        self.create_widgets()
        self.toggle_appearance_mode()

    def create_widgets(self):
        title_label = ctk.CTkLabel(self, text="YouTube Downloader", font=self.TITLE_FONT)
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        theme_switch = ctk.CTkSwitch(self, text="Dark Mode", variable=self.dark_mode, command=self.toggle_appearance_mode, fg_color="gray", font=self.DEFAULT_FONT)
        theme_switch.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        link_frame = ctk.CTkFrame(self)
        link_frame.grid(row=1, columnspan=2, pady=10, padx=20, sticky="ew")
        playlist_radio = ctk.CTkRadioButton(link_frame, text="Playlist", variable=self.download_type_var, value="playlist", fg_color="#16A4FA")
        playlist_radio.pack(side="left", padx=5)
        single_video_radio = ctk.CTkRadioButton(link_frame, text="Single Video", variable=self.download_type_var, value="single", fg_color="#16A4FA")
        single_video_radio.pack(side="left", padx=5)
        link_label = ctk.CTkLabel(link_frame, text="Link:")
        link_label.pack(side="left", padx=10)
        link_entry = ctk.CTkEntry(link_frame, textvariable=self.playlist_link)
        link_entry.pack(side="right", padx=10, expand=True, fill="x")
        directory_frame = ctk.CTkFrame(self)
        directory_frame.grid(row=2, columnspan=2, pady=10, padx=20, sticky="ew")
        directory_label = ctk.CTkLabel(directory_frame, text="Output Directory:")
        directory_label.pack(side="left", padx=10)
        directory_entry = ctk.CTkEntry(directory_frame, textvariable=self.output_directory)
        directory_entry.pack(side="left", padx=10, expand=True, fill="x")
        browse_button = ctk.CTkButton(directory_frame, text="Browse", command=self.browse_directory, font=self.DEFAULT_FONT, fg_color="#16A4FA")
        browse_button.pack(side="right", padx=10)
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, columnspan=2, pady=10, padx=20, sticky="ew")
        quality_label = ctk.CTkLabel(options_frame, text="Video Quality:")
        quality_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.quality_optionmenu = ctk.CTkOptionMenu(options_frame, values=self.quality_options, variable=self.quality, font=self.DEFAULT_FONT, fg_color="#16A4FA")
        self.quality_optionmenu.grid(row=0, column=1, padx=10, pady=5)
        format_label = ctk.CTkLabel(options_frame, text="Format:")
        format_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        format_optionmenu = ctk.CTkOptionMenu(options_frame, values=["mp3", "mp4"], variable=self.format, font=self.DEFAULT_FONT, fg_color="#16A4FA")
        format_optionmenu.grid(row=1, column=1, padx=10, pady=5)
        self.updates_button = ctk.CTkButton(self, text="Updates", command=self.open_github_releases, font=self.DEFAULT_FONT, fg_color="#16A4FA")
        self.updates_button.grid(row=3, column=1, padx=10, pady=(0,10), sticky="w")
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=4, columnspan=2, pady=10, padx=20, sticky="ew")
        progress_info_frame = ctk.CTkFrame(progress_frame)
        progress_info_frame.pack(fill="x", pady=(0,10))
        current_downloading_label = ctk.CTkLabel(progress_info_frame, textvariable=self.current_downloading_number)
        current_downloading_label.pack(side="left", padx=(0,10))
        downloading_percentage_label = ctk.CTkLabel(progress_info_frame, textvariable=self.downloading_percentage)
        downloading_percentage_label.pack(side="left", padx=(0,10))
        remaining_number_label = ctk.CTkLabel(progress_info_frame, textvariable=self.remaining_number)
        remaining_number_label.pack(side="right")
        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.download_progress)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0,10))
        self.status_label = ctk.CTkLabel(progress_frame, textvariable=self.download_status)
        self.status_label.pack()
        self.download_button = ctk.CTkButton(self, text="Download", font=self.BUTTON_FONT, command=self.download_videos, fg_color="#ac5434", hover_color="#16A4FA")
        self.download_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.stop_button = ctk.CTkButton(self, text="Stop", font=self.BUTTON_FONT, command=self.toggle_download, fg_color="#edeff0", hover_color="#ac5434", state="disabled")
        self.stop_button.grid(row=5, column=1, padx=10, pady=10, sticky="e")
        self.version_label = ctk.CTkLabel(self, text="Python Youtube Downloader V3", font=self.FOOTER_FONT)
        self.version_label.grid(row=6, column=0, padx=10, pady=(0,10), sticky="w")
        self.developer_label = ctk.CTkLabel(self, text="Developed By Tris", font=self.FOOTER_FONT)
        self.developer_label.grid(row=6, column=1, padx=10, pady=(0,10), sticky="e")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        ctk.set_appearance_mode("dark")

    def toggle_appearance_mode(self):
        ctk.set_appearance_mode("dark" if self.dark_mode.get() else "light")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def open_github_releases(self):
        webbrowser.open("https://github.com/TrisTheKitten/Python-Download-Manager/releases")

    def is_valid_url(self, url):
        download_type = self.download_type_var.get()
        if download_type == "single":
            if "list=" in url:
                return False
            video_patterns = [r"^https?://(?:www\.)?youtube\.com/watch\?v=[^&]+(?:&.*)?$", r"^https?://(?:www\.)?youtube\.com/shorts/[^?]+", r"^https?://youtu\.be/[^?]+"]
            return any(re.match(pattern, url) for pattern in video_patterns)
        elif download_type == "playlist":
            playlist_pattern = r"^https?://(?:www\.)?youtube\.com/playlist\?list=.+"
            return re.match(playlist_pattern, url) is not None
        else:
            return False

    def download_videos(self):
        url = self.playlist_link.get()
        output_path = self.output_directory.get()
        if not url:
            messagebox.showerror("Empty Link", "Please provide a YouTube link.")
            return
        if not self.is_valid_url(url):
            link_type = "playlist" if self.download_type_var.get() == "playlist" else "video"
            messagebox.showerror("Invalid Link", f"Please provide a valid YouTube {link_type} link.")
            return
        if not os.path.isdir(output_path):
            messagebox.showerror("Invalid Directory", "The provided output directory is invalid.")
            return
        self.stop_button.configure(state="normal")
        threading.Thread(target=self.download_videos_thread, daemon=True).start()

    def toggle_download(self):
        if not self.cancel_download:
            self.cancel_download = True
            self.stop_button.configure(text="Resume")
        else:
            self.cancel_download = False
            self.stop_button.configure(text="Stop")
            threading.Thread(target=self.download_videos_thread, daemon=True).start()

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')

    def download_videos_thread(self):
        try:
            self.cancel_download = False
            url = self.playlist_link.get()
            file_format = self.format.get()
            quality = self.quality.get()
            output_path = self.output_directory.get()
            quality_value = quality[:-1] if quality.endswith("p") else quality
            ydl_opts = {
                'format': f'bestvideo[height<={quality_value}]+bestaudio/best[height<={quality_value}]',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.ydl_progress_hook],
                'concurrent_fragment_downloads': 10,
                'throttledratelimit': 100000,
            }
            if file_format == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                })
            self.download_status.set("Download started.")
            self.download_progress.set(0)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.download_status.set("Download completed.")
            self.download_progress.set(1)
            messagebox.showinfo("Download Complete", "All videos have been downloaded successfully.")
        except Exception as e:
            if str(e) == "Download cancelled by user":
                self.download_status.set("Download cancelled.")
                messagebox.showinfo("Download Cancelled", "The download was cancelled by the user.")
            else:
                self.download_status.set("Download failed.")
                messagebox.showerror("Download Error", f"An error occurred: {str(e)}")
        finally:
            self.stop_button.configure(state="disabled", text="Stop")

    def ydl_progress_hook(self, d):
        if self.cancel_download:
            raise Exception("Download cancelled by user")
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            filename = os.path.basename(d.get('filename', ''))
            max_filename_length = 20
            if len(filename) > max_filename_length:
                filename = filename[:max_filename_length-3] + '...'
            progress_text = f"{percent} | {filename} | {eta}"
            self.downloading_percentage.set(percent)
            self.progress_label_text.set(progress_text)
            try:
                progress = float(percent.rstrip('%'))
                self.download_progress.set(progress / 100)
            except ValueError:
                print(f"Could not convert percentage: {percent}")
            self.current_downloading_number.set(f"Speed: {speed}")
            self.remaining_number.set(f"ETA: {eta}")
        elif d['status'] == 'finished':
            self.download_status.set("Download finished, now processing...")
            self.download_progress.set(1)
            self.progress_label_text.set("100% | Processing | Completed")

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
