import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Настройки ---
DATA_FILE = 'movies.json'

# --- Функции работы с данными ---
def load_movies():
    """Загружает фильмы из файла JSON. Если файла нет, возвращает пустой список."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_movies(movies_list):
    """Сохраняет список фильмов в файл JSON."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies_list, f, ensure_ascii=False, indent=4)

# --- Функции логики приложения ---
def add_movie():
    """Обрабатывает добавление нового фильма."""
    title = entry_title.get().strip()
    genre = entry_genre.get().strip()
    year = entry_year.get().strip()
    rating = entry_rating.get().strip()

    if not (title and genre and year and rating):
        messagebox.showwarning("Ошибка", "Заполните все поля!")
        return

    try:
        year = int(year)
        rating = float(rating)
        if not (0 <= rating <= 10):
            raise ValueError("Рейтинг должен быть от 0 до 10")
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e) if "Рейтинг" in str(e) else "Год и рейтинг должны быть числами!")
        return

    movie = {"title": title, "genre": genre, "year": year, "rating": rating}
    movies.append(movie)
    save_movies(movies)
    update_table()
    clear_entries()

def clear_entries():
    """Очищает поля ввода после добавления фильма."""
    entry_title.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_year.delete(0, tk.END)
    entry_rating.delete(0, tk.END)

def update_table(movie_list=None):
    """Обновляет таблицу в GUI. Если movie_list не передан, выводит все фильмы."""
    for i in tree.get_children():
        tree.delete(i)

    data_source = movie_list if movie_list is not None else movies
    for m in data_source:
        tree.insert('', tk.END, values=(m['title'], m['genre'], m['year'], m['rating']))

def filter_movies():
    """Фильтрует фильмы по выбранным критериям и обновляет таблицу."""
    filtered = movies.copy()

    # Фильтр по жанру
    genre = combo_genre_filter.get()
    if genre:
        filtered = [m for m in filtered if m['genre'].lower() == genre.lower()]

    # Фильтр по году
    year_text = entry_year_filter.get().strip()
    if year_text:
        try:
            year = int(year_text)
            filtered = [m for m in filtered if m['year'] == year]
        except ValueError:
            messagebox.showerror("Ошибка", "В поле года должно быть число!")
            return

    update_table(filtered)

def reset_filters():
    """Сбрасывает фильтры и показывает полный список."""
    combo_genre_filter.set('')
    entry_year_filter.delete(0, tk.END)
    update_table()

# --- Основное окно ---
root = tk.Tk()
root.title("🎬 Movie Library")
root.geometry("950x600")

# Загрузка данных при старте
movies = load_movies()

# --- Вкладки (Notebook) ---
tab_control = ttk.Notebook(root)
tab_add = ttk.Frame(tab_control)
tab_filter = ttk.Frame(tab_control)
tab_control.add(tab_add, text='➕ Добавить фильм')
tab_control.add(tab_filter, text='🔎 Фильтр')
tab_control.pack(expand=1, fill="both")

# ================= Вкладка 1: Добавление фильма =================
# Поля ввода
tk.Label(tab_add, text="Название:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=5, sticky='e')
tk.Label(tab_add, text="Жанр:", font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=5, sticky='e')
tk.Label(tab_add, text="Год выпуска:", font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=5, sticky='e')
tk.Label(tab_add, text="Рейтинг (0-10):", font=('Arial', 10)).grid(row=3, column=0, padx=10, pady=5, sticky='e')

entry_title = tk.Entry(tab_add, width=40)
entry_genre = tk.Entry(tab_add, width=40)
entry_year = tk.Entry(tab_add, width=40)
entry_rating = tk.Entry(tab_add, width=40)

entry_title.grid(row=0, column=1, padx=10, pady=5)
entry_genre.grid(row=1, column=1, padx=10, pady=5)
entry_year.grid(row=2, column=1, padx=10, pady=5)
entry_rating.grid(row=3, column=1, padx=10, pady=5)

btn_add = tk.Button(tab_add, text="Добавить фильм", bg='#4CAF50', fg='white', command=add_movie)
btn_add.grid(row=4, columnspan=2, pady=20)

# Таблица фильмов
columns = ('Название', 'Жанр', 'Год', 'Рейтинг')
tree_style = ttk.Style()
tree_style.configure("Treeview", rowheight=25)
tree_style.configure("Treeview.Heading", font=(None, 10))

tree = ttk.Treeview(tab_add, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.column("Название", width=250)
tree.column("Жанр", width=150)
tree.column("Год", width=80)
tree.column("Рейтинг", width=80)
tree.grid(row=5, columnspan=2, sticky='nsew', padx=10)

# Прокрутка для таблицы
scrollbar_y = ttk.Scrollbar(tab_add, orient="vertical", command=tree.yview)
scrollbar_y.grid(row=5, column=3, sticky='ns')
tree.configure(yscrollcommand=scrollbar_y.set)

tab_add.grid_rowconfigure(5, weight=1)
tab_add.grid_columnconfigure(1, weight=1)
update_table() # Загрузка данных в таблицу при старте

# ================= Вкладка 2: Фильтрация =================
# Фильтр по жанру (Combobox с автозаполнением)
unique_genres = sorted({m['genre'] for m in movies})
tk.Label(tab_filter, text="Жанр:", font=('Arial', 10)).grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky='e')
combo_genre_filter = ttk.Combobox(tab_filter, values=list(unique_genres), state='readonly')
combo_genre_filter.grid(row=0, column=1, padx=(5, 10), pady=(20, 5), sticky='w')
combo_genre_filter.set('') # Пустое значение по умолчанию

# Фильтр по году
tk.Label(tab_filter, text="Год:", font=('Arial', 10)).grid(row=1, column=0, padx=(20, 5), pady=(5, 30), sticky='e')
entry_year_filter = tk.Entry(tab_filter)
entry_year_filter.grid(row=1, column=1, padx=(5, 10), pady=(5, 30), sticky='w')

btn_filter = tk.Button(tab_filter, text="Применить фильтр", bg='#2196F3', fg='white', command=filter_movies)
btn_filter.grid(row=2, columnspan=2)

btn_reset = tk.Button(tab_filter, text="Сбросить фильтры", bg='#9E9E9E', fg='white', command=reset_filters)
btn_reset.grid(row=3, columnspan=2)

# ================= Запуск =================
if __name__ == "__main__":
    root.mainloop()
