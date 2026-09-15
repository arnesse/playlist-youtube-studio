import os
import sys
import threading
import queue
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

APP_NAME = "Playlist YouTube Studio"


def resource_path(*parts):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


class DownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("920x680")
        self.minsize(780, 580)
        self.configure(bg="#f4f7fb")
        self.events = queue.Queue()
        self.worker = None
        self.cancel_event = threading.Event()
        self.total_items = 0
        self.completed_items = 0
        self._build_style()
        self._build_ui()
        self.after(100, self._poll_events)

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background="#f4f7fb")
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", background="#f4f7fb", foreground="#152238", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#f4f7fb", foreground="#617087", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="white", foreground="#152238", font=("Segoe UI", 11, "bold"))
        style.configure("Body.TLabel", background="white", foreground="#40506a", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Status.TLabel", background="#edf2f8", foreground="#40506a", padding=8)

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=26)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Playlist YouTube Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Téléchargez vos playlists en MP3 ou MP4, simplement et localement.", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 20))

        card = ttk.Frame(root, style="Card.TFrame", padding=20)
        card.pack(fill="x")
        ttk.Label(card, text="1. Lien de la playlist", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(card, text="Collez l’URL d’une playlist YouTube publique ou accessible.", style="Body.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 10))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(card, textvariable=self.url_var, font=("Segoe UI", 11))
        self.url_entry.grid(row=2, column=0, columnspan=3, sticky="ew", ipady=7)
        card.columnconfigure(0, weight=1)

        options = ttk.Frame(root, style="Card.TFrame", padding=20)
        options.pack(fill="x", pady=(14, 0))
        ttk.Label(options, text="2. Options de téléchargement", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(options, text="Format", style="Body.TLabel").grid(row=1, column=0, sticky="w", pady=(14, 4))
        self.format_var = tk.StringVar(value="MP3 — audio")
        self.format_box = ttk.Combobox(options, textvariable=self.format_var, values=["MP3 — audio", "MP4 — vidéo"], state="readonly", width=22)
        self.format_box.grid(row=2, column=0, sticky="w")
        ttk.Label(options, text="Qualité", style="Body.TLabel").grid(row=1, column=1, sticky="w", padx=(25, 0), pady=(14, 4))
        self.quality_var = tk.StringVar(value="Meilleure disponible")
        self.quality_box = ttk.Combobox(options, textvariable=self.quality_var, values=["Meilleure disponible", "1080p", "720p", "480p"], state="readonly", width=22)
        self.quality_box.grid(row=2, column=1, sticky="w", padx=(25, 0))
        ttk.Label(options, text="Dossier de destination", style="Body.TLabel").grid(row=1, column=2, columnspan=2, sticky="w", padx=(25, 0), pady=(14, 4))
        self.output_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Playlists YouTube"))
        ttk.Entry(options, textvariable=self.output_var, width=38).grid(row=2, column=2, sticky="ew", padx=(25, 8))
        ttk.Button(options, text="Parcourir…", command=self._choose_folder).grid(row=2, column=3, sticky="e")
        options.columnconfigure(2, weight=1)

        action = ttk.Frame(root, style="App.TFrame")
        action.pack(fill="x", pady=(16, 10))
        self.start_btn = ttk.Button(action, text="Démarrer le téléchargement", style="Accent.TButton", command=self.start_download)
        self.start_btn.pack(side="left", ipadx=12, ipady=5)
        self.cancel_btn = ttk.Button(action, text="Annuler", command=self.cancel_download, state="disabled")
        self.cancel_btn.pack(side="left", padx=(10, 0), ipadx=8, ipady=5)
        self.progress = ttk.Progressbar(action, mode="determinate", length=260)
        self.progress.pack(side="right", fill="x", expand=True, padx=(20, 0))

        log_card = ttk.Frame(root, style="Card.TFrame", padding=15)
        log_card.pack(fill="both", expand=True)
        ttk.Label(log_card, text="Journal d’activité", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.log = tk.Text(log_card, height=12, state="disabled", wrap="word", bg="#fbfcfe", fg="#33445d", relief="flat", font=("Consolas", 9), padx=10, pady=8)
        self.log.pack(fill="both", expand=True)
        self.status_var = tk.StringVar(value="Prêt — choisissez une playlist pour commencer.")
        ttk.Label(root, textvariable=self.status_var, style="Status.TLabel").pack(fill="x", pady=(12, 0))
        self._log("Bienvenue. Utilisez uniquement des contenus que vous êtes autorisé à télécharger.")

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_download(self):
        if yt_dlp is None:
            messagebox.showerror("Dépendance manquante", "yt-dlp n’est pas installé. Réinstallez l’application.")
            return
        url = self.url_var.get().strip()
        if not url or "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showwarning("Lien invalide", "Veuillez coller un lien de playlist YouTube valide.")
            return
        output = Path(self.output_var.get()).expanduser()
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Dossier inaccessible", str(exc))
            return
        self.cancel_event.clear()
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.url_entry.configure(state="disabled")
        self.format_box.configure(state="disabled")
        self.quality_box.configure(state="disabled")
        self.progress.configure(value=0, maximum=100)
        self.completed_items = 0
        self._log("Analyse de la playlist en cours…")
        self.status_var.set("Analyse de la playlist…")
        self.worker = threading.Thread(target=self._download_worker, args=(url, output), daemon=True)
        self.worker.start()

    def cancel_download(self):
        self.cancel_event.set()
        self.status_var.set("Annulation demandée…")
        self._log("Annulation demandée. Les opérations en cours vont se terminer proprement.")

    def _download_worker(self, url, output):
        ffmpeg = resource_path("bin", "ffmpeg.exe")
        fmt_mp3 = self.format_var.get().startswith("MP3")
        quality = self.quality_var.get()
        if fmt_mp3:
            fmt = "bestaudio/best"
            postprocessors = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            height = {"1080p": 1080, "720p": 720, "480p": 480}.get(quality)
            selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]" if height else "bestvideo+bestaudio/best"
            fmt = selector
            postprocessors = []
        opts = {
            "outtmpl": str(output / "%(playlist_index)03d - %(title)s.%(ext)s"),
            "format": fmt,
            "postprocessors": postprocessors,
            "noplaylist": False,
            "ignoreerrors": True,
            "retries": 3,
            "continuedl": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._progress_hook],
            "ffmpeg_location": str(ffmpeg.parent) if ffmpeg.exists() else None,
        }
        opts = {k: v for k, v in opts.items() if v is not None}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and info.get("entries"):
                    self.total_items = len([e for e in info["entries"] if e])
                    self.events.put(("total", self.total_items))
                if self.cancel_event.is_set():
                    return
                ydl.download([url])
            self.events.put(("done", None))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _progress_hook(self, data):
        if self.cancel_event.is_set():
            raise yt_dlp.utils.DownloadCancelled("Annulé par l’utilisateur")
        status = data.get("status")
        if status == "finished":
            self.events.put(("item", data.get("filename", "Fichier terminé")))
        elif status == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            percent = downloaded / total * 100 if total else 0
            speed = data.get("speed") or 0
            self.events.put(("progress", (percent, speed, data.get("filename", ""))))

    def _poll_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "total":
                    self.total_items = payload
                    self._log(f"Playlist détectée : {payload} élément(s). Téléchargement…")
                elif kind == "progress":
                    percent, speed, filename = payload
                    self.progress.configure(value=percent)
                    mbps = speed / 1024 / 1024 if speed else 0
                    self.status_var.set(f"Téléchargement : {percent:.0f}% — {mbps:.1f} Mo/s")
                elif kind == "item":
                    self.completed_items += 1
                    self._log(f"Terminé ({self.completed_items}/{self.total_items or '?'}): {Path(payload).name}")
                elif kind == "done":
                    self.progress.configure(value=100)
                    self._finish("Téléchargement terminé. Les fichiers sont disponibles dans le dossier choisi.")
                elif kind == "error":
                    if "DownloadCancelled" in payload or self.cancel_event.is_set():
                        self._finish("Téléchargement annulé.")
                    else:
                        self._finish("Une erreur est survenue.")
                        self._log("Erreur : " + payload)
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _finish(self, status):
        self.status_var.set(status)
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.url_entry.configure(state="normal")
        self.format_box.configure(state="readonly")
        self.quality_box.configure(state="readonly")


if __name__ == "__main__":
    DownloaderApp().mainloop()
