import json
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Конвертер систем счисления"
DIGITS = "0123456789ABCDEF"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
MAPPING_FILE = DATA_DIR / "encoding_mapping.json"


from logger import logger


def decimal_to_base(number: int, base: int) -> str:
    """Переводит целое десятичное число в систему с основанием 2–16."""
    if not 2 <= base <= 16:
        logger.warning("Недопустимое основание: %s", base)
        raise ValueError("Основание системы счисления должно быть от 2 до 16.")
    if number == 0:
        return "0"
    sign = "-" if number < 0 else ""
    number = abs(number)
    digits = []
    while number:
        number, remainder = divmod(number, base)
        digits.append(DIGITS[remainder])
    return sign + "".join(reversed(digits))


def convert_text(number_text: str, base: int) -> str:
    """Проверяет введённое число, переводит его и записывает событие в лог."""
    number_text = number_text.strip()
    if not number_text:
        logger.warning("Пустое значение для преобразования")
        raise ValueError("Введите целое десятичное число.")
    try:
        number = int(number_text, 10)
    except ValueError as exc:
        logger.warning("Некорректное десятичное число: %r", number_text)
        raise ValueError(
            "Число должно быть целым и записанным в десятичной системе."
        ) from exc
    result = decimal_to_base(number, base)
    logger.info("Преобразование: число=%s, основание=%s, результат=%s",
                number, base, result)
    return result


def ensure_mapping_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MAPPING_FILE.exists():
        data = {
            "digits": {str(i): DIGITS[i] for i in range(16)},
            "bases_supported": list(range(2, 17)),
            "updated_at": datetime.now().isoformat(timespec="seconds")
        }
        MAPPING_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("Создана таблица соответствия: %s", MAPPING_FILE)


def backup_mapping() -> Path:
    ensure_mapping_file()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"encoding_mapping_{stamp}.json"
    i = 1
    while target.exists():
        target = BACKUP_DIR / f"encoding_mapping_{stamp}_{i}.json"
        i += 1
    target.write_bytes(MAPPING_FILE.read_bytes())
    logger.info("Создана резервная копия: %s", target)
    return target


def restore_mapping(backup_path):
    path = Path(backup_path)
    if not path.is_file():
        logger.error("Файл резервной копии не найден: %s", path)
        raise FileNotFoundError(f"Файл резервной копии не найден: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Резервная копия имеет неверный формат.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MAPPING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    logger.info("Таблица восстановлена из резервной копии: %s", path)


class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("680x520")
        self.minsize(600, 470)
        ensure_mapping_file()
        logger.info("Программа запущена в графическом режиме")
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self._build_ui()

    def close_app(self):
        logger.info("Программа закрыта")
        self.destroy()

    def _build_ui(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text=APP_TITLE, font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(root, text="Перевод целых десятичных чисел в системы счисления с основаниями от 2 до 16.").pack(anchor="w", pady=(4, 16))

        form = ttk.LabelFrame(root, text="Параметры преобразования", padding=12)
        form.pack(fill="x")
        ttk.Label(form, text="Десятичное целое число:").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        self.number_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.number_var, width=30).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Label(form, text="Основание (2–16):").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        self.base_var = tk.IntVar(value=2)
        ttk.Combobox(form, textvariable=self.base_var, values=list(range(2, 17)), state="readonly", width=27).grid(row=1, column=1, sticky="ew", pady=6)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Преобразовать", command=self.convert).pack(side="left")
        ttk.Button(actions, text="Загрузить из файла", command=self.load_input).pack(side="left", padx=8)
        ttk.Button(actions, text="Сохранить результат", command=self.save_output).pack(side="left")

        result_frame = ttk.LabelFrame(root, text="Результат", padding=12)
        result_frame.pack(fill="x")
        self.result_var = tk.StringVar(value="Здесь появится результат.")
        ttk.Label(result_frame, textvariable=self.result_var, font=("Consolas", 15, "bold"), wraplength=580).pack(anchor="w")

        file_frame = ttk.LabelFrame(root, text="Резервное копирование таблицы соответствия", padding=12)
        file_frame.pack(fill="x", pady=(12, 0))
        ttk.Label(file_frame, text=f"Файл таблицы: data/encoding_mapping.json\nРезервные копии сохраняются в папке: backups").pack(anchor="w")
        backup_actions = ttk.Frame(file_frame)
        backup_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(backup_actions, text="Создать резервную копию", command=self.make_backup).pack(side="left")
        ttk.Button(backup_actions, text="Восстановить из копии…", command=self.restore_backup).pack(side="left", padx=8)
        self.bind("<Return>", lambda _event: self.convert())

    def convert(self):
        try:
            base = int(self.base_var.get())
            result = convert_text(self.number_var.get(), base)
        except (ValueError, TypeError) as exc:
            logger.error("Ошибка преобразования из интерфейса: %s", exc)
            messagebox.showerror("Ошибка ввода", str(exc))
            return
        self.result_var.set(f"{self.number_var.get().strip()}₁₀ = {result} (основание {base})")

    def load_input(self):
        path = filedialog.askopenfilename(title="Выберите текстовый файл с десятичным числом", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Загрузка входного файла отменена")
            return
        try:
            content = Path(path).read_text(encoding="utf-8").strip()
            parts = content.replace(",", " ").split()
            if not parts:
                raise ValueError("Файл пуст.")
            self.number_var.set(parts[0])
            if len(parts) >= 2:
                base = int(parts[1])
                if not 2 <= base <= 16:
                    raise ValueError("В файле основание должно быть от 2 до 16.")
                self.base_var.set(base)
            logger.info("Входные данные загружены из файла: %s", path)
            self.convert()
        except (OSError, ValueError) as exc:
            logger.exception("Ошибка чтения файла %s", path)
            messagebox.showerror("Ошибка чтения файла", str(exc))

    def save_output(self):
        result = self.result_var.get()
        if result == "Здесь появится результат.":
            logger.warning("Попытка сохранить результат до преобразования")
            messagebox.showwarning("Нет результата", "Сначала выполните преобразование.")
            return
        path = filedialog.asksaveasfilename(title="Сохранить результат", defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Сохранение результата отменено")
            return
        try:
            Path(path).write_text(result + "\n", encoding="utf-8")
            logger.info("Результат сохранён в файл: %s", path)
            messagebox.showinfo("Готово", f"Результат сохранён в файл:\n{path}")
        except OSError as exc:
            logger.exception("Ошибка сохранения результата в %s", path)
            messagebox.showerror("Ошибка сохранения", str(exc))

    def make_backup(self):
        try:
            path = backup_mapping()
            messagebox.showinfo("Резервная копия создана", f"Файл сохранён:\n{path}")
        except OSError as exc:
            logger.exception("Ошибка создания резервной копии")
            messagebox.showerror("Ошибка резервного копирования", str(exc))

    def restore_backup(self):
        path = filedialog.askopenfilename(title="Выберите резервную копию таблицы", initialdir=str(BACKUP_DIR) if BACKUP_DIR.exists() else str(BASE_DIR), filetypes=[("JSON-файлы", "*.json"), ("Все файлы", "*.*")])
        if not path:
            logger.info("Выбор резервной копии отменён")
            return
        if not messagebox.askyesno("Подтверждение", "Заменить текущую таблицу соответствия выбранной копией?"):
            logger.info("Пользователь отказался от восстановления таблицы")
            return
        try:
            restore_mapping(path)
            messagebox.showinfo("Восстановление завершено", "Таблица соответствия успешно восстановлена.")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            logger.exception("Ошибка восстановления из %s", path)
            messagebox.showerror("Ошибка восстановления", str(exc))


def run_console():
    logger.info("Программа запущена в консольном режиме")
    while True:
        try:
            raw = input("Введите десятичное целое число (или q для выхода): ").strip()
            if raw.lower() == "q":
                logger.info("Программа закрыта пользователем в консольном режиме")
                break
            base = int(input("Введите основание (2–16): ").strip())
            print("Результат:", convert_text(raw, base))
        except (ValueError, EOFError) as exc:
            logger.error("Ошибка в консольном режиме: %s", exc)
            print("Ошибка:", exc)


if __name__ == "__main__":
    try:
        if "--console" in sys.argv:
            run_console()
        else:
            ConverterApp().mainloop()
    except Exception:
        logger.exception("Непредвиденная ошибка приложения")
        raise
