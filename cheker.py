import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from googleapiclient.discovery import build
import re
import threading
from datetime import datetime, timezone
import dateutil.parser
import os
import sys

class YouTubeChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Stats Checker v1.0")
        self.root.geometry("1400x700")
        
        # Отримання шляху до папки з програмою
        if getattr(sys, 'frozen', False):
            # Якщо це exe файл
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Якщо це звичайний Python скрипт
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.api_key_file = os.path.join(self.app_dir, "api_key.txt")
        self.youtube = None
        
        self.init_ui()
        self.load_api_key()
        self.init_api()
    
    def load_api_key(self):
        """Завантажує API ключ з файлу"""
        try:
            if os.path.exists(self.api_key_file):
                with open(self.api_key_file, 'r', encoding='utf-8') as f:
                    self.API_KEY = f.read().strip()
                if not self.API_KEY:
                    self.create_api_key_file()
            else:
                self.create_api_key_file()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл API ключа: {str(e)}")
            self.create_api_key_file()
    
    def create_api_key_file(self):
        """Створює файл для API ключа"""
        try:
            with open(self.api_key_file, 'w', encoding='utf-8') as f:
                f.write("YOUR_YOUTUBE_API_KEY_HERE\n")
                f.write("# Замініть рядок вище на ваш YouTube API ключ\n")
                f.write("# Отримати ключ можна тут: https://console.developers.google.com/\n")
                f.write("# 1. Створіть новий проект або виберіть існуючий\n")
                f.write("# 2. Увімкніть YouTube Data API v3\n")
                f.write("# 3. Створіть API ключ у розділі 'Credentials'\n")
                f.write("# 4. Замініть перший рядок цього файлу на ваш ключ\n")
            
            messagebox.showinfo(
                "Налаштування API ключа", 
                f"Створено файл api_key.txt у папці програми.\n\n"
                f"Будь ласка:\n"
                f"1. Відкрийте файл {self.api_key_file}\n"
                f"2. Замініть 'YOUR_YOUTUBE_API_KEY_HERE' на ваш YouTube API ключ\n"
                f"3. Перезапустіть програму\n\n"
                f"Інструкції по отриманню ключа знаходяться у файлі."
            )
            self.API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити файл API ключа: {str(e)}")
            self.API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
    
    def init_api(self):
        """Ініціалізація YouTube API"""
        if self.API_KEY == "YOUR_YOUTUBE_API_KEY_HERE" or not self.API_KEY:
            self.status_var.set("Потрібно налаштувати API ключ")
            return
            
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.API_KEY)
            self.status_var.set("API підключено успішно")
        except Exception as e:
            messagebox.showerror("Помилка API", f"Не вдалося ініціалізувати YouTube API: {str(e)}")
            self.status_var.set("Помилка підключення API")
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        # Головна рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Налаштування розширення
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Змінено з 2 на 3
        
        # Панель API статусу
        self.create_api_status_panel(main_frame)
        
        # Панель вибору файлу
        self.create_file_panel(main_frame)
        
        # Кнопка запуску
        self.create_control_panel(main_frame)
        
        # Таблиця результатів
        self.create_results_table(main_frame)
        
        # Панель статусу та підсумків
        self.create_status_panel(main_frame)
    
    def create_api_status_panel(self, parent):
        """Створює панель статусу API"""
        api_frame = ttk.LabelFrame(parent, text="Статус API", padding="5")
        api_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="API статус:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.api_status_var = tk.StringVar(value="Завантаження...")
        ttk.Label(api_frame, textvariable=self.api_status_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(api_frame, text="Оновити API ключ", command=self.reload_api_key).grid(row=0, column=2, padx=(10, 0))
    
    def reload_api_key(self):
        """Перезавантажує API ключ"""
        self.load_api_key()
        self.init_api()
        if self.youtube:
            self.api_status_var.set("API підключено успішно")
        else:
            self.api_status_var.set("Потрібно налаштувати API ключ")
    
    def create_file_panel(self, parent):
        """Створює панель для вибору файлу"""
        top_frame = ttk.Frame(parent)
        top_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)
        
        ttk.Label(top_frame, text="Файл з посиланнями:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(top_frame, textvariable=self.file_path_var, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(top_frame, text="Обрати файл", command=self.select_file).grid(row=0, column=2)
    
    def create_control_panel(self, parent):
        """Створює панель керування"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=10)
        
        self.check_button = ttk.Button(button_frame, text="Перевірити відео", command=self.start_checking)
        self.check_button.pack()
    
    def create_results_table(self, parent):
        """Створює таблицю результатів"""
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Створення таблиці з новою колонкою
        columns = ('№', 'Назва', 'Тип', 'Перегляди', 'Лайки', 'Опубліковано', 'Статус')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Налаштування заголовків та ширини стовпчиків
        column_config = {
            '№': (50, 40),
            'Назва': (350, 200),
            'Тип': (120, 100),
            'Перегляди': (120, 100),
            'Лайки': (100, 80),
            'Опубліковано': (150, 120),
            'Статус': (100, 80)
        }
        
        for col, (width, minwidth) in column_config.items():
            self.tree.heading(col, text=col if col == '№' else f'{col}')
            self.tree.column(col, width=width, minwidth=minwidth)
        
        # Прокручування
        scrollbar_v = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def create_status_panel(self, parent):
        """Створює панель статусу та підсумків"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Прогрес бар
        self.progress = ttk.Progressbar(bottom_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Статус
        self.status_var = tk.StringVar(value="Завантаження...")
        ttk.Label(bottom_frame, textvariable=self.status_var).grid(row=1, column=0, pady=(0, 10))
        
        # Підсумки
        self.create_summary_panel(bottom_frame)
    
    def create_summary_panel(self, parent):
        """Створює панель підсумків"""
        summary_frame = ttk.LabelFrame(parent, text="Підсумки", padding="10")
        summary_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Змінні для підсумків
        self.stats_vars = {
            'total_videos': tk.StringVar(value="0"),
            'successful': tk.StringVar(value="0"),
            'failed': tk.StringVar(value="0"),
            'total_views': tk.StringVar(value="0"),
            'total_likes': tk.StringVar(value="0"),
            'avg_views': tk.StringVar(value="0"),
            'low_views': tk.StringVar(value="0"),
            'execution_time': tk.StringVar(value="0 сек")
        }
        
        # Перша лінія
        labels_row1 = [
            ("Загалом відео:", 'total_videos', 'normal'),
            ("Успішно:", 'successful', 'green'),
            ("Помилок:", 'failed', 'red')
        ]
        
        # Друга лінія
        labels_row2 = [
            ("Загалом переглядів:", 'total_views', 'normal'),
            ("Загалом лайків:", 'total_likes', 'normal'),
            ("Час виконання:", 'execution_time', 'normal')
        ]
        
        # Третя лінія
        labels_row3 = [
            ("Середньо переглядів:", 'avg_views', 'blue'),
            ("< 3 переглядів:", 'low_views', 'orange'),
            ("", None, 'normal')  # Пустий стовпчик для симетрії
        ]
        
        for row, labels in enumerate([labels_row1, labels_row2, labels_row3]):
            for col, (text, var_key, color) in enumerate(labels):
                if text:  # Пропустити пусті стовпчики
                    ttk.Label(summary_frame, text=text).grid(row=row, column=col*2, sticky=tk.W, padx=(0, 5), pady=(5 if row else 0, 0))
                    label = ttk.Label(summary_frame, textvariable=self.stats_vars[var_key], font=('TkDefaultFont', 9, 'bold'))
                    if color == 'green':
                        label.configure(foreground="green")
                    elif color == 'red':
                        label.configure(foreground="red")
                    elif color == 'blue':
                        label.configure(foreground="blue")
                    elif color == 'orange':
                        label.configure(foreground="orange")
                    label.grid(row=row, column=col*2+1, sticky=tk.W, padx=(0, 20), pady=(5 if row else 0, 0))
    
    def select_file(self):
        """Вибір файлу з посиланнями"""
        file_path = filedialog.askopenfilename(
            title="Оберіть txt файл з YouTube посиланнями",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.app_dir
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def extract_video_id(self, url):
        """Витягує ID відео з YouTube URL"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def format_number(self, number):
        """Форматує числа для відображення"""
        if number >= 1000000000:
            return f"{number/1000000000:.1f}B"
        elif number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
        else:
            return str(number)
    
    def format_time_ago(self, published_at):
        """Форматує час публікації у форматі 'X часу тому'"""
        try:
            # Парсинг дати публікації
            published_date = dateutil.parser.parse(published_at)
            
            # Переконуємось що дата має часову зону
            if published_date.tzinfo is None:
                published_date = published_date.replace(tzinfo=timezone.utc)
            
            # Поточний час
            now = datetime.now(timezone.utc)
            
            # Різниця у часі
            time_diff = now - published_date
            
            total_seconds = int(time_diff.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds} сек тому"
            elif total_seconds < 3600:  # менше години
                minutes = total_seconds // 60
                return f"{minutes} хв тому"
            elif total_seconds < 86400:  # менше дня
                hours = total_seconds // 3600
                return f"{hours} год тому"
            elif total_seconds < 2592000:  # менше місяця (30 днів)
                days = total_seconds // 86400
                return f"{days} д тому"
            elif total_seconds < 31536000:  # менше року
                months = total_seconds // 2592000
                return f"{months} міс тому"
            else:
                years = total_seconds // 31536000
                return f"{years} р тому"
                
        except Exception as e:
            return "Невідомо"
    
    def get_video_stats_api(self, video_id):
        """Отримує статистику відео через YouTube API"""
        try:
            # Запит до API
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return None, "Відео не знайдено"
            
            video = response['items'][0]
            snippet = video['snippet']
            stats = video['statistics']
            
            # Визначення типу відео (Shorts мають тривалість ≤ 60 секунд)
            duration_request = self.youtube.videos().list(
                part="contentDetails",
                id=video_id
            )
            duration_response = duration_request.execute()
            
            is_shorts = False
            if duration_response['items']:
                duration = duration_response['items'][0]['contentDetails']['duration']
                # Парсинг ISO 8601 duration (PT1M30S -> 90 секунд)
                import re
                duration_match = re.findall(r'(\d+)([HMS])', duration)
                total_seconds = 0
                for value, unit in duration_match:
                    if unit == 'H':
                        total_seconds += int(value) * 3600
                    elif unit == 'M':
                        total_seconds += int(value) * 60
                    elif unit == 'S':
                        total_seconds += int(value)
                is_shorts = total_seconds <= 60
            
            # Форматування часу публікації
            published_at = snippet.get('publishedAt', '')
            time_ago = self.format_time_ago(published_at)
            
            return {
                'title': snippet.get('title', 'Невідома назва'),
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'type': 'YouTube Shorts' if is_shorts else 'Звичайне відео',
                'published_ago': time_ago
            }, None
            
        except Exception as e:
            return None, f"Помилка API: {str(e)}"
    
    def check_videos(self):
        """Перевіряє всі відео з файлу"""
        if not self.youtube:
            messagebox.showerror("Помилка", "YouTube API не ініціалізовано. Перевірте налаштування API ключа.")
            return
            
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Помилка", "Оберіть файл з посиланнями")
            return
        
        # Читання файлу
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip()]
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл: {str(e)}")
            return
        
        if not urls:
            messagebox.showwarning("Попередження", "Файл порожній")
            return
        
        # Підготовка до перевірки
        self.prepare_checking(len(urls))
        
        start_time = datetime.now()
        successful = failed = total_views = total_likes = low_views_count = 0
        successful_videos_views = []  # Для розрахунку середнього
        
        # Перевірка кожного відео
        for i, url in enumerate(urls, 1):
            self.status_var.set(f"Перевіряється відео {i} з {len(urls)}...")
            self.root.update()
            
            video_id = self.extract_video_id(url)
            if not video_id:
                self.add_table_row(i, 'Невірне посилання', '-', '-', '-', '-', 'Помилка')
                failed += 1
                continue
            
            stats, error = self.get_video_stats_api(video_id)
            
            if stats:
                self.add_table_row(
                    i, 
                    stats['title'][:50] + ('...' if len(stats['title']) > 50 else ''),
                    stats['type'],
                    self.format_number(stats['views']),
                    self.format_number(stats['likes']),
                    stats['published_ago'],
                    'Успішно'
                )
                successful += 1
                total_views += stats['views']
                total_likes += stats['likes']
                successful_videos_views.append(stats['views'])
                
                # Перевірка на малу кількість переглядів
                if stats['views'] < 3:
                    low_views_count += 1
            else:
                self.add_table_row(i, 'Помилка завантаження', '-', '-', '-', '-', error[:20] + ('...' if len(error) > 20 else ''))
                failed += 1
            
            # Оновлення статистики
            avg_views = sum(successful_videos_views) // len(successful_videos_views) if successful_videos_views else 0
            self.update_stats(len(urls), successful, failed, total_views, total_likes, avg_views, low_views_count)
        
        # Завершення
        duration = (datetime.now() - start_time).total_seconds()
        self.finish_checking(duration, successful, failed)
    
    def prepare_checking(self, total_count):
        """Підготовка до перевірки"""
        # Очистити таблицю
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Скинути статистику
        self.stats_vars['total_videos'].set(str(total_count))
        for key in ['successful', 'failed', 'total_views', 'total_likes', 'avg_views', 'low_views']:
            self.stats_vars[key].set("0")
        self.stats_vars['execution_time'].set("0 сек")
        
        self.progress.start(10)
        self.check_button.config(state="disabled")
    
    def add_table_row(self, *values):
        """Додає рядок до таблиці"""
        self.tree.insert('', 'end', values=values)
        # Прокрутити до останнього елементу
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])
    
    def update_stats(self, total, successful, failed, total_views, total_likes, avg_views, low_views_count):
        """Оновлює статистику"""
        self.stats_vars['successful'].set(str(successful))
        self.stats_vars['failed'].set(str(failed))
        self.stats_vars['total_views'].set(self.format_number(total_views))
        self.stats_vars['total_likes'].set(self.format_number(total_likes))
        self.stats_vars['avg_views'].set(self.format_number(avg_views))
        self.stats_vars['low_views'].set(str(low_views_count))
    
    def finish_checking(self, duration, successful, failed):
        """Завершення перевірки"""
        self.stats_vars['execution_time'].set(f"{duration:.1f} сек")
        self.progress.stop()
        self.check_button.config(state="disabled" if not self.youtube else "normal")
        self.status_var.set("Перевірка завершена")
        
        messagebox.showinfo("Готово", f"Перевірка завершена!\nУспішно: {successful}, Помилок: {failed}")
    
    def start_checking(self):
        """Запускає перевірку в окремому потоці"""
        thread = threading.Thread(target=self.check_videos, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeChecker(root)
    root.mainloop()