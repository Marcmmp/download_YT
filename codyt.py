import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re

class YouTubeDownloaderPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader Pro 🚀")
        self.root.geometry("800x600")
        self.root.configure(bg='#0f0f0f')
        
        # Estilo
        self.setup_styles()
        
        # Variables
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")
        os.makedirs(self.download_path, exist_ok=True)
        
        self.current_video_info = None
        self.download_thread = None
        
        # Crear interfaz
        self.create_ui()
        
    def setup_styles(self):
        """Configurar estilos modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores YouTube
        bg_color = '#0f0f0f'
        fg_color = '#ffffff'
        accent_color = '#ff0000'
        
        style.configure('Title.TLabel', 
                       background=bg_color, 
                       foreground=accent_color,
                       font=('Arial', 24, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=bg_color,
                       foreground=fg_color,
                       font=('Arial', 12, 'bold'))
        
        style.configure('Info.TLabel',
                       background=bg_color,
                       foreground='#aaaaaa',
                       font=('Arial', 10))
        
        style.configure('Red.TButton',
                       background=accent_color,
                       foreground=fg_color,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        
        style.map('Red.TButton',
                 background=[('active', '#cc0000')])
    
    def create_ui(self):
        """Crear interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#0f0f0f')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = ttk.Label(main_frame, text="YouTube Downloader Pro", style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # Frame de entrada
        input_frame = tk.Frame(main_frame, bg='#0f0f0f')
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_frame, text="URL del video:", style='Heading.TLabel').pack(anchor=tk.W)
        
        url_frame = tk.Frame(input_frame, bg='#0f0f0f')
        url_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.url_entry = tk.Entry(url_frame, 
                                 bg='#1a1a1a', 
                                 fg='white', 
                                 insertbackground='white',
                                 font=('Arial', 12),
                                 relief=tk.FLAT,
                                 bd=10)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.bind('<Return>', lambda e: self.get_video_info())
        
        tk.Button(url_frame,
                 text="Obtener Info",
                 bg='#ff0000',
                 fg='white',
                 font=('Arial', 10, 'bold'),
                 relief=tk.FLAT,
                 bd=0,
                 padx=20,
                 cursor='hand2',
                 command=self.get_video_info).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Frame de información del video
        self.info_frame = tk.Frame(main_frame, bg='#1a1a1a')
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        self.info_frame.pack_forget()  # Ocultar inicialmente
        
        # Frame de progreso
        self.progress_frame = tk.Frame(main_frame, bg='#0f0f0f')
        self.progress_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="", style='Info.TLabel')
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                          mode='determinate',
                                          style='Red.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Frame de configuración
        config_frame = tk.Frame(main_frame, bg='#0f0f0f')
        config_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(config_frame, text=f"Carpeta de descarga:", style='Info.TLabel').pack(anchor=tk.W)
        
        path_frame = tk.Frame(config_frame, bg='#0f0f0f')
        path_frame.pack(fill=tk.X)
        
        self.path_label = ttk.Label(path_frame, 
                                   text=self.download_path, 
                                   style='Info.TLabel')
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(path_frame,
                 text="Cambiar",
                 bg='#333333',
                 fg='white',
                 font=('Arial', 9),
                 relief=tk.FLAT,
                 bd=0,
                 padx=15,
                 cursor='hand2',
                 command=self.change_download_path).pack(side=tk.RIGHT)
    
    def get_video_info(self):
        """Obtener información del video"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Por favor ingresa una URL")
            return
        
        # Limpiar UI
        self.info_frame.pack_forget()
        self.progress_label.config(text="Obteniendo información del video...")
        
        # Thread para no bloquear UI
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()
    
    def _fetch_video_info(self, url):
        """Obtener info del video en thread separado"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_video_info = info
                
                # Actualizar UI en thread principal
                self.root.after(0, self._display_video_info, info)
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo obtener información: {str(e)}"))
            self.root.after(0, lambda: self.progress_label.config(text=""))
    
    def _display_video_info(self, info):
        """Mostrar información del video"""
        # Limpiar frame
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Container principal
        container = tk.Frame(self.info_frame, bg='#1a1a1a')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame superior con thumbnail y info
        top_frame = tk.Frame(container, bg='#1a1a1a')
        top_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Thumbnail
        if 'thumbnail' in info:
            try:
                response = requests.get(info['thumbnail'])
                img = Image.open(BytesIO(response.content))
                img = img.resize((200, 112), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                thumb_label = tk.Label(top_frame, image=photo, bg='#1a1a1a')
                thumb_label.image = photo
                thumb_label.pack(side=tk.LEFT, padx=(0, 15))
            except:
                pass
        
        # Info del video
        info_text_frame = tk.Frame(top_frame, bg='#1a1a1a')
        info_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título
        title = info.get('title', 'Sin título')
        title_label = tk.Label(info_text_frame, 
                              text=title[:60] + '...' if len(title) > 60 else title,
                              bg='#1a1a1a',
                              fg='white',
                              font=('Arial', 14, 'bold'),
                              wraplength=350,
                              justify=tk.LEFT)
        title_label.pack(anchor=tk.W)
        
        # Canal
        channel = info.get('uploader', 'Desconocido')
        tk.Label(info_text_frame,
                text=f"Canal: {channel}",
                bg='#1a1a1a',
                fg='#aaaaaa',
                font=('Arial', 10)).pack(anchor=tk.W, pady=(5, 0))
        
        # Duración
        duration = info.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "En vivo"
        tk.Label(info_text_frame,
                text=f"Duración: {duration_str}",
                bg='#1a1a1a',
                fg='#aaaaaa',
                font=('Arial', 10)).pack(anchor=tk.W)
        
        # Frame de formatos
        formats_frame = tk.Frame(container, bg='#1a1a1a')
        formats_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(formats_frame,
                text="Selecciona calidad:",
                bg='#1a1a1a',
                fg='white',
                font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Botones de descarga
        buttons_frame = tk.Frame(formats_frame, bg='#1a1a1a')
        buttons_frame.pack(fill=tk.X)
        
        # Mejores formatos disponibles
        formats = [
            ("🎬 Mejor Calidad (MP4)", "best[ext=mp4]/best", '#ff0000'),
            ("🎵 Solo Audio (MP3)", "bestaudio/best", '#ff6600'),
            ("📱 720p", "best[height<=720]", '#0066ff'),
            ("💾 480p", "best[height<=480]", '#00aa00'),
        ]
        
        for format_name, format_code, color in formats:
            btn = tk.Button(buttons_frame,
                          text=format_name,
                          bg=color,
                          fg='white',
                          font=('Arial', 10, 'bold'),
                          relief=tk.FLAT,
                          bd=0,
                          padx=20,
                          pady=10,
                          cursor='hand2',
                          command=lambda fc=format_code, fn=format_name: self.download_video(fc, fn))
            btn.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        # Mostrar frame
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.progress_label.config(text="")
    
    def download_video(self, format_code, format_name):
        """Descargar video con formato seleccionado"""
        if not self.current_video_info:
            return
        
        # Deshabilitar botones durante descarga
        self.progress_label.config(text=f"Descargando {format_name}...")
        self.progress_bar['value'] = 0
        
        # Iniciar descarga en thread
        self.download_thread = threading.Thread(
            target=self._download_video_thread,
            args=(self.current_video_info['webpage_url'], format_code),
            daemon=True
        )
        self.download_thread.start()
    
    def _download_video_thread(self, url, format_code):
        """Thread de descarga"""
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Calcular progreso
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    speed_str = self._format_bytes(speed) + '/s' if speed else ''
                    
                    # Actualizar UI
                    self.root.after(0, lambda: self.progress_bar.config(value=percentage))
                    self.root.after(0, lambda: self.progress_label.config(
                        text=f"Descargando... {percentage:.1f}% - {speed_str}"
                    ))
            
            elif d['status'] == 'finished':
                self.root.after(0, lambda: self.progress_label.config(text="Procesando..."))
        
        try:
            # Configurar yt-dlp
            ydl_opts = {
                'format': format_code,
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            # Si es audio, convertir a mp3
            if 'audio' in format_code:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # Descargar
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Éxito
            self.root.after(0, lambda: self.progress_bar.config(value=100))
            self.root.after(0, lambda: self.progress_label.config(text="✅ ¡Descarga completada!"))
            self.root.after(0, lambda: messagebox.showinfo("Éxito", "¡Descarga completada!"))
            
            # Abrir carpeta
            if sys.platform == 'win32':
                os.startfile(self.download_path)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.download_path}"')
            else:
                os.system(f'xdg-open "{self.download_path}"')
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en la descarga: {str(e)}"))
            self.root.after(0, lambda: self.progress_label.config(text=""))
            self.root.after(0, lambda: self.progress_bar.config(value=0))
    
    def _format_bytes(self, bytes):
        """Formatear bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    def change_download_path(self):
        """Cambiar carpeta de descarga"""
        new_path = filedialog.askdirectory(initialdir=self.download_path)
        if new_path:
            self.download_path = new_path
            self.path_label.config(text=new_path)
    
    def run(self):
        """Ejecutar aplicación"""
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Instrucciones iniciales
        self.progress_label.config(text="💡 Pega una URL de YouTube y presiona Enter")
        
        self.root.mainloop()

if __name__ == "__main__":
    # Instalar dependencias si no están
    try:
        import yt_dlp
    except ImportError:
        print("Instalando yt-dlp...")
        os.system(f"{sys.executable} -m pip install yt-dlp")
        import yt_dlp
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Instalando Pillow...")
        os.system(f"{sys.executable} -m pip install Pillow")
        from PIL import Image, ImageTk
    
    app = YouTubeDownloaderPro()
    app.run()
