#!/usr/bin/env python3
"""
TimSyn Server
Синхронизирует время с NTP-серверами и раздаёт как NTP-сервер в локальную сеть.
Только стандартная библиотека Python — дополнительные пакеты не нужны.
"""

import ctypes
import datetime
import json
import os
import platform
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# ═══════════════════════════════════════════════════════════════════════════════
#  Переводы / Translations / Tarjimalar
# ═══════════════════════════════════════════════════════════════════════════════

LANGS = {
    "RU": {
        "title":          "TimSyn Сервер",
        "fr_upstream":    " Источник синхронизации ",
        "src_ntp":        "🌐  NTP-сервер (интернет)",
        "src_timsyn":     "🔗  TimSyn / NTP сервер",
        "lbl_address":    "Адрес:",
        "lbl_outport":    "Порт:",
        "hint_ntp":       "Публичные NTP-серверы в интернете (pool.ntp.org)",
        "hint_timsyn":    "Другой TimSyn-сервер или NTP-сервер в локальной сети",
        "lbl_ntpserver":  "NTP-сервер:",
        "lbl_interval":   "Интервал синхр. (сек):",
        "chk_autoset":    "Авто-установка времени на этом ПК",
        "fr_server":      " NTP-сервер для локальной сети ",
        "lbl_iface":      "Интерфейс:",
        "lbl_inport":     "Порт входящий:",
        "btn_start":      "▶  Запустить сервер",
        "btn_stop":       "■  Остановить",
        "btn_sync":       "⟳  Синхр. с NTP",
        "btn_apply_time": "🕐  Установить время на ПК",
        "btn_save":       "✎  Сохранить",
        "fr_status":      " Состояние ",
        "lbl_localtime":  "Местное время:",
        "lbl_ntptime":    "NTP-время:",
        "lbl_offset":     "Отклонение:",
        "srv_stopped":    "Сервер остановлен",
        "srv_running":    "Сервер работает",
        "saved":          "Настройки сохранены",
        "err_start":      "Ошибка запуска",
        "log_srv_listen": "Слушаем {}:{}",
        "log_srv_stop":   "Сервер остановлен",
        "log_srv_req":    "Запрос от {}:{}",
        "log_srv_pkterr": "Ошибка пакета: {}",
        "log_sync_ok":    "[SYNC] {} → отклонение {}{:.3f} с",
        "log_sync_err":   "[SYNC] Ошибка: {}",
        "log_time_set":   "[ВРЕМЯ] Установка: {}",
        "log_cfg_saved":  "[CFG] Настройки сохранены",
        "err_port":       "Не удалось открыть порт {}:\n{}\nПорты < 1024 требуют прав администратора/root.",
        "win_confirm":    "Вы уверены, что хотите выйти?",
        "win_close":      "Выход",
        "fr_lang":        " Язык / Language ",
        "btn_about":      "ℹ  Об авторе",
        "about_title":    "Об авторе",
        "about_body":     "TimSyn — NTP синхронизация времени\n\nРазработано: MIDGRO.UZ\nСайт: https://midgro.uz\nКонтакт: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nРаспространяется под лицензией MOAL v1.0\n(можно использовать и продавать при упоминании MIDGRO.UZ)",
        "chk_autostart":  "Автозапуск при старте системы",
        "chk_autorun_srv":"Запускать сервер автоматически",
        "tray_show":      "Открыть",
        "tray_sync":      "Синхр. сейчас",
        "tray_exit":      "Выход",
        "tray_tooltip":   "TimSyn Сервер",
        "btn_runas":      "🔒  Перезапустить от Администратора",
        "lbl_priv_ok":    "✔  Права администратора",
        "lbl_priv_no":    "⚠  Нет прав администратора — порт 123 недоступен",
    },
    "EN": {
        "title":          "TimSyn Server",
        "fr_upstream":    " Sync Source ",
        "src_ntp":        "🌐  NTP Server (Internet)",
        "src_timsyn":     "🔗  TimSyn / NTP Server",
        "lbl_address":    "Address:",
        "lbl_outport":    "Port:",
        "hint_ntp":       "Public NTP servers on the internet (pool.ntp.org)",
        "hint_timsyn":    "Another TimSyn or NTP server on the local network",
        "lbl_ntpserver":  "NTP Server:",
        "lbl_interval":   "Sync Interval (sec):",
        "chk_autoset":    "Auto-set time on this PC",
        "fr_server":      " NTP Server for Local Network ",
        "lbl_iface":      "Interface:",
        "lbl_inport":     "Listen Port:",
        "btn_start":      "▶  Start Server",
        "btn_stop":       "■  Stop",
        "btn_sync":       "⟳  Sync from NTP",
        "btn_apply_time": "🕐  Set Time on This PC",
        "btn_save":       "✎  Save Settings",
        "fr_status":      " Status ",
        "lbl_localtime":  "Local Time:",
        "lbl_ntptime":    "NTP Time:",
        "lbl_offset":     "Offset:",
        "srv_stopped":    "Server stopped",
        "srv_running":    "Server running",
        "saved":          "Settings saved",
        "err_start":      "Start Error",
        "log_srv_listen": "Listening on {}:{}",
        "log_srv_stop":   "Server stopped",
        "log_srv_req":    "Request from {}:{}",
        "log_srv_pkterr": "Packet error: {}",
        "log_sync_ok":    "[SYNC] {} → offset {}{:.3f} s",
        "log_sync_err":   "[SYNC] Error: {}",
        "log_time_set":   "[TIME] Set result: {}",
        "log_cfg_saved":  "[CFG] Settings saved",
        "err_port":       "Cannot open port {}:\n{}\nPorts < 1024 require administrator/root.",
        "win_confirm":    "Are you sure you want to exit?",
        "win_close":      "Exit",
        "fr_lang":        " Language ",
        "btn_about":      "ℹ  About",
        "about_title":    "About",
        "about_body":     "TimSyn — NTP Time Synchronization\n\nDeveloped by: MIDGRO.UZ\nWebsite: https://midgro.uz\nContact: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nDistributed under MOAL v1.0\n(free to use and sell with attribution to MIDGRO.UZ)",
        "chk_autostart":  "Run at system startup",
        "chk_autorun_srv":"Start server automatically",
        "tray_show":      "Open",
        "tray_sync":      "Sync Now",
        "tray_exit":      "Exit",
        "tray_tooltip":   "TimSyn Server",
        "btn_runas":      "🔒  Restart as Administrator",
        "lbl_priv_ok":    "✔  Running as Administrator",
        "lbl_priv_no":    "⚠  No admin rights — port 123 unavailable",
    },
    "UZ": {
        "title":          "TimSyn Server",
        "fr_upstream":    " Sinxronizatsiya Manbai ",
        "src_ntp":        "🌐  NTP Server (Internet)",
        "src_timsyn":     "🔗  TimSyn / NTP Server",
        "lbl_address":    "Manzil:",
        "lbl_outport":    "Port:",
        "hint_ntp":       "Internetdagi ommaviy NTP serverlar (pool.ntp.org)",
        "hint_timsyn":    "Lokal tarmoqdagi boshqa TimSyn yoki NTP server",
        "lbl_ntpserver":  "NTP Server:",
        "lbl_interval":   "Sinxr. Intervali (sek):",
        "chk_autoset":    "Ushbu PK vaqtini avtomatik o'rnatish",
        "fr_server":      " Lokal Tarmoq uchun NTP Server ",
        "lbl_iface":      "Interfeys:",
        "lbl_inport":     "Kirish Porti:",
        "btn_start":      "▶  Serverni Ishga Tushirish",
        "btn_stop":       "■  To'xtatish",
        "btn_sync":       "⟳  NTP dan Sinxr.",
        "btn_apply_time": "🕐  Bu PK ga vaqt o'rnatish",
        "btn_save":       "✎  Saqlash",
        "fr_status":      " Holat ",
        "lbl_localtime":  "Mahalliy Vaqt:",
        "lbl_ntptime":    "NTP Vaqti:",
        "lbl_offset":     "Farq:",
        "srv_stopped":    "Server to'xtatildi",
        "srv_running":    "Server ishlayapti",
        "saved":          "Sozlamalar saqlandi",
        "err_start":      "Ishga tushirish xatosi",
        "log_srv_listen": "Tinglanmoqda {}:{}",
        "log_srv_stop":   "Server to'xtatildi",
        "log_srv_req":    "So'rov {}:{}",
        "log_srv_pkterr": "Paket xatosi: {}",
        "log_sync_ok":    "[SYNC] {} → farq {}{:.3f} s",
        "log_sync_err":   "[SYNC] Xato: {}",
        "log_time_set":   "[VAQT] O'rnatish natijasi: {}",
        "log_cfg_saved":  "[CFG] Sozlamalar saqlandi",
        "err_port":       "Port {} ochib bo'lmadi:\n{}\n1024 dan kichik portlar administrator/root huquqi talab qiladi.",
        "win_confirm":    "Haqiqatan ham chiqmoqchimisiz?",
        "win_close":      "Chiqish",
        "fr_lang":        " Til / Language ",
        "btn_about":      "ℹ  Muallif haqida",
        "about_title":    "Muallif haqida",
        "about_body":     "TimSyn — NTP Vaqt Sinxronizatsiyasi\n\nIshlab chiqaruvchi: MIDGRO.UZ\nSayt: https://midgro.uz\nAloqa: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nMOAL v1.0 litsenziyasi asosida tarqatiladi\n(MIDGRO.UZ ni eslatgan holda foydalanish va sotish mumkin)",
        "chk_autostart":  "Tizim ishga tushganda avtomatik yoqilsin",
        "chk_autorun_srv":"Serverni avtomatik ishga tushirish",
        "tray_show":      "Ochish",
        "tray_sync":      "Hozir sinxr.",
        "tray_exit":      "Chiqish",
        "tray_tooltip":   "TimSyn Server",
        "btn_runas":      "🔒  Administrator sifatida qayta ishga tushirish",
        "lbl_priv_ok":    "✔  Administrator huquqlari mavjud",
        "lbl_priv_no":    "⚠  Administrator huquqi yo'q — 123 port mavjud emas",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#  NTP protokol
# ═══════════════════════════════════════════════════════════════════════════════

NTP_DELTA = 2208988800
_FMT      = "!B B b b I I I I I I I I I I I"   # 48 байт


def _to_ntp(unix: float):
    t = unix + NTP_DELTA
    s = int(t)
    f = int((t - s) * 2**32)
    return s, f


def _from_ntp(s: int, f: int) -> float:
    return s + f / 2**32 - NTP_DELTA


def _make_client_pkt() -> bytes:
    ts, tf = _to_ntp(time.time())
    return struct.pack(_FMT,
        (0 << 6) | (3 << 3) | 3,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ts, tf,
    )


def _make_server_pkt(orig_s: int, orig_f: int) -> bytes:
    now     = time.time()
    rs, rf  = _to_ntp(now)
    ts, tf  = _to_ntp(time.time())
    return struct.pack(_FMT,
        (0 << 6) | (3 << 3) | 4,
        2, 4, -20,
        0, 0, 0,
        rs, rf,
        orig_s, orig_f,
        rs, rf,
        ts, tf,
    )


def query_ntp(host: str, port: int = 123, timeout: float = 5.0) -> float:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        s.sendto(_make_client_pkt(), (host, port))
        data, _ = s.recvfrom(1024)
    u = struct.unpack(_FMT, data[:48])
    return _from_ntp(u[13], u[14])


# ═══════════════════════════════════════════════════════════════════════════════
#  Системное время
# ═══════════════════════════════════════════════════════════════════════════════

def set_system_time(unix_ts: float):
    try:
        if platform.system() == "Windows":
            return _set_win(unix_ts)
        return _set_linux(unix_ts)
    except Exception as e:
        return False, str(e)


def _set_win(unix_ts: float):
    class _ST(ctypes.Structure):
        _fields_ = [
            ("wYear",         ctypes.c_uint16),
            ("wMonth",        ctypes.c_uint16),
            ("wDayOfWeek",    ctypes.c_uint16),
            ("wDay",          ctypes.c_uint16),
            ("wHour",         ctypes.c_uint16),
            ("wMinute",       ctypes.c_uint16),
            ("wSecond",       ctypes.c_uint16),
            ("wMilliseconds", ctypes.c_uint16),
        ]
    dt = datetime.datetime.utcfromtimestamp(unix_ts)
    st = _ST(wYear=dt.year, wMonth=dt.month, wDay=dt.day,
             wHour=dt.hour, wMinute=dt.minute, wSecond=dt.second,
             wMilliseconds=dt.microsecond // 1000)
    ok = bool(ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st)))
    return ok, "OK" if ok else "SetSystemTime failed (run as Administrator)"


def _set_linux(unix_ts: float):
    try:
        class _TS(ctypes.Structure):
            _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        ts   = _TS(tv_sec=int(unix_ts),
                   tv_nsec=int((unix_ts % 1) * 1_000_000_000))
        if libc.clock_settime(0, ctypes.byref(ts)) == 0:
            return True, "OK"
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))
    except Exception:
        pass
    try:
        dt  = datetime.datetime.utcfromtimestamp(unix_ts)
        cmd = ["sudo", "date", "-u", "-s", dt.strftime("%Y-%m-%d %H:%M:%S")]
        r   = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return True, "OK (sudo date)"
        return False, r.stderr.strip() or "sudo date failed"
    except Exception as e2:
        return False, f"clock_settime: permission denied; sudo date: {e2}"


# ═══════════════════════════════════════════════════════════════════════════════
#  Привилегии
# ═══════════════════════════════════════════════════════════════════════════════

def is_admin() -> bool:
    try:
        if platform.system() == "Windows":
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:
        return False


def restart_as_admin():
    """Перезапустить текущий процесс с правами администратора."""
    exe = sys.executable
    if platform.system() == "Windows":
        # ShellExecute с глаголом "runas" вызывает UAC-диалог
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, "", None, 1)
    else:
        # Linux/macOS: pkexec (графический sudo), иначе gksudo, иначе sudo
        for launcher in ("pkexec", "gksudo", "kdesudo"):
            if subprocess.call(["which", launcher],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL) == 0:
                subprocess.Popen([launcher, exe])
                break
        else:
            # Нет GUI-sudo — открываем терминал с sudo
            subprocess.Popen(["sudo", exe])
    # Текущий процесс завершается — новый запустится с правами
    os._exit(0)


# ═══════════════════════════════════════════════════════════════════════════════
#  Автозапуск
# ═══════════════════════════════════════════════════════════════════════════════

def set_autostart(app_name: str, enable: bool):
    exe = _get_exe()
    if platform.system() == "Windows":
        _autostart_win(app_name, exe, enable)
    else:
        _autostart_linux(app_name, exe, enable)


def _get_exe() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    return f'"{sys.executable}" "{os.path.abspath(__file__)}"'


def _autostart_win(name: str, exe: str, enable: bool):
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                         winreg.KEY_SET_VALUE)
    if enable:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe)
    else:
        try:
            winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass
    winreg.CloseKey(key)


def _autostart_linux(name: str, exe: str, enable: bool):
    desktop_dir  = Path.home() / ".config" / "autostart"
    desktop_file = desktop_dir / f"{name.lower()}.desktop"
    if enable:
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file.write_text(
            f"[Desktop Entry]\nType=Application\nName={name}\n"
            f"Exec={exe}\nHidden=false\nX-GNOME-Autostart-enabled=true\n"
        )
    else:
        desktop_file.unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  Конфиг
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_PATH = Path.home() / ".timsyn_server.json"

DEFAULTS = {
    "upstream_ntp":    "pool.ntp.org",
    "upstream_port":   123,
    "source_type":     "ntp",        # "ntp" | "timsyn"
    "listen_host":     "0.0.0.0",
    "listen_port":     123,
    "sync_interval":   300,
    "auto_apply":      True,
    "autostart":       False,
    "autorun_server":  True,
    "language":        "RU",
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = dict(DEFAULTS)
            cfg.update(data)
            return cfg
        except Exception:
            pass
    return dict(DEFAULTS)


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════════════════
#  NTP-сервер (UDP listener thread)
# ═══════════════════════════════════════════════════════════════════════════════

class NTPServer:
    def __init__(self, host: str, port: int, log_cb):
        self.host     = host
        self.port     = port
        self.log_cb   = log_cb
        self._sock    = None
        self._thread  = None
        self._running = False

    def start(self, tr):
        if self._running:
            return
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind((self.host, self.port))
            self._sock.settimeout(1.0)
        except OSError as e:
            raise RuntimeError(tr("err_port").format(self.port, e))
        self._running = True
        self._thread  = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        self.log_cb(tr("log_srv_listen").format(self.host, self.port))

    def stop(self, tr):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self.log_cb(tr("log_srv_stop"))

    def _serve(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(1024)
            except socket.timeout:
                continue
            except Exception:
                break
            try:
                u        = struct.unpack(_FMT, data[:48])
                response = _make_server_pkt(u[13], u[14])
                self._sock.sendto(response, addr)
                # log через callback — нельзя передавать tr напрямую в поток,
                # поэтому кладём текст готовым
                self.log_cb(f"REQ {addr[0]}:{addr[1]}")
            except Exception as e:
                self.log_cb(f"ERR {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  GUI
# ═══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg       = load_config()
        self._lang     = self.cfg.get("language", "RU")
        self.ntp_srv   = None
        self._sync_job = None
        self._tray     = None
        self.resizable(False, False)
        self._build_ui()
        self._apply_lang()
        self._set_window_icon()
        self._tick()
        self._init_tray()
        # запустить сервер автоматически после инициализации UI
        if self.cfg.get("autorun_server", True):
            self.after(500, self._start)

    # ── перевод ──────────────────────────────────────────────────────────────

    def tr(self, key: str) -> str:
        return LANGS[self._lang].get(key, key)

    # ── построение виджетов ───────────────────────────────────────────────────

    def _build_ui(self):
        P = {"padx": 8, "pady": 4}

        # — Язык —
        self.fr_lang = ttk.LabelFrame(self, text="")
        self.fr_lang.grid(row=0, column=0, columnspan=2, sticky="ew", **P)
        self.v_lang = tk.StringVar(value=self._lang)
        for code in ("RU", "EN", "UZ"):
            ttk.Radiobutton(self.fr_lang, text=code, value=code,
                            variable=self.v_lang,
                            command=self._on_lang_change).pack(side="left", padx=6, pady=2)

        # — Источник NTP —
        self.fr_up = ttk.LabelFrame(self, text="")
        self.fr_up.grid(row=1, column=0, columnspan=2, sticky="ew", **P)
        self.fr_up.columnconfigure(1, weight=1)

        # — Переключатель источника —
        self.v_source_type = tk.StringVar(value=self.cfg.get("source_type", "ntp"))
        self.rb_ntp = ttk.Radiobutton(self.fr_up, text="", value="ntp",
                                       variable=self.v_source_type,
                                       command=self._on_source_change)
        self.rb_ntp.grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(6, 2))

        self.rb_timsyn = ttk.Radiobutton(self.fr_up, text="", value="timsyn",
                                          variable=self.v_source_type,
                                          command=self._on_source_change)
        self.rb_timsyn.grid(row=0, column=2, columnspan=2, sticky="w", padx=8, pady=(6, 2))

        ttk.Separator(self.fr_up, orient="horizontal").grid(
            row=1, column=0, columnspan=4, sticky="ew", padx=8, pady=2)

        # — Адрес и порт —
        self.lbl_address = ttk.Label(self.fr_up, text="")
        self.lbl_address.grid(row=2, column=0, sticky="w", **P)
        self.v_upstream = tk.StringVar(value=self.cfg["upstream_ntp"])
        self.ent_upstream = ttk.Entry(self.fr_up, textvariable=self.v_upstream, width=26)
        self.ent_upstream.grid(row=2, column=1, sticky="ew", **P)

        self.lbl_outport = ttk.Label(self.fr_up, text="")
        self.lbl_outport.grid(row=2, column=2, sticky="w", **P)
        self.v_up_port = tk.IntVar(value=self.cfg["upstream_port"])
        ttk.Spinbox(self.fr_up, textvariable=self.v_up_port,
                    from_=1, to=65535, width=7).grid(row=2, column=3, **P)

        # — Подсказка (меняется при переключении) —
        self.lbl_src_hint = ttk.Label(self.fr_up, text="", foreground="gray",
                                       font=("TkDefaultFont", 8))
        self.lbl_src_hint.grid(row=3, column=0, columnspan=4, sticky="w", padx=10, pady=(0, 4))

        ttk.Separator(self.fr_up, orient="horizontal").grid(
            row=4, column=0, columnspan=4, sticky="ew", padx=8, pady=2)

        # — Интервал и авто-установка —
        self.lbl_interval = ttk.Label(self.fr_up, text="")
        self.lbl_interval.grid(row=5, column=0, sticky="w", **P)
        self.v_interval = tk.IntVar(value=self.cfg["sync_interval"])
        ttk.Spinbox(self.fr_up, textvariable=self.v_interval,
                    from_=30, to=86400, width=7).grid(row=5, column=1, sticky="w", **P)

        self.v_auto_apply = tk.BooleanVar(value=self.cfg["auto_apply"])
        self.chk_auto = ttk.Checkbutton(self.fr_up, text="", variable=self.v_auto_apply)
        self.chk_auto.grid(row=5, column=2, columnspan=2, sticky="w", **P)

        # — Автозапуск —
        self.v_autorun_srv = tk.BooleanVar(value=self.cfg.get("autorun_server", True))
        self.chk_autorun_srv = ttk.Checkbutton(self.fr_up, text="", variable=self.v_autorun_srv)
        self.chk_autorun_srv.grid(row=6, column=0, columnspan=2, sticky="w", **P)

        self.v_autostart = tk.BooleanVar(value=self.cfg.get("autostart", False))
        self.chk_autostart = ttk.Checkbutton(self.fr_up, text="",
                                              variable=self.v_autostart,
                                              command=self._toggle_autostart)
        self.chk_autostart.grid(row=6, column=2, columnspan=2, sticky="w", **P)

        # — Сервер локалки —
        self.fr_srv = ttk.LabelFrame(self, text="")
        self.fr_srv.grid(row=2, column=0, columnspan=2, sticky="ew", **P)

        self.lbl_iface = ttk.Label(self.fr_srv, text="")
        self.lbl_iface.grid(row=0, column=0, sticky="w", **P)
        self.v_listen_host = tk.StringVar(value=self.cfg["listen_host"])
        self.cb_host = ttk.Combobox(self.fr_srv, textvariable=self.v_listen_host,
                                    width=18, values=["0.0.0.0"] + self._local_ips())
        self.cb_host.grid(row=0, column=1, **P)

        self.lbl_inport = ttk.Label(self.fr_srv, text="")
        self.lbl_inport.grid(row=0, column=2, sticky="w", **P)
        self.v_listen_port = tk.IntVar(value=self.cfg["listen_port"])
        ttk.Spinbox(self.fr_srv, textvariable=self.v_listen_port,
                    from_=1, to=65535, width=7).grid(row=0, column=3, **P)

        # — Кнопки —
        fr_btn = ttk.Frame(self)
        fr_btn.grid(row=3, column=0, columnspan=2, **P)

        self.btn_start = ttk.Button(fr_btn, text="", command=self._start)
        self.btn_start.pack(side="left", padx=4)
        self.btn_stop = ttk.Button(fr_btn, text="", command=self._stop, state="disabled")
        self.btn_stop.pack(side="left", padx=4)
        self.btn_sync = ttk.Button(fr_btn, text="", command=self._sync_now)
        self.btn_sync.pack(side="left", padx=4)
        self.btn_apply_time = ttk.Button(fr_btn, text="", command=self._apply_time_now)
        self.btn_apply_time.pack(side="left", padx=4)
        self.btn_save = ttk.Button(fr_btn, text="", command=self._save_cfg)
        self.btn_save.pack(side="left", padx=4)
        self.btn_about = ttk.Button(fr_btn, text="", command=self._show_about)
        self.btn_about.pack(side="left", padx=4)

        # — Строка привилегий + кнопка перезапуска —
        fr_priv = ttk.Frame(self)
        fr_priv.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 2))

        self._admin = is_admin()
        priv_color  = "#22863a" if self._admin else "#d73a49"
        priv_key    = "lbl_priv_ok" if self._admin else "lbl_priv_no"
        self.lbl_priv = ttk.Label(fr_priv, text="", foreground=priv_color,
                                   font=("TkDefaultFont", 9, "bold"))
        self.lbl_priv.pack(side="left")

        # Кнопка показывается только если НЕ администратор
        if not self._admin:
            self.btn_runas = ttk.Button(fr_priv, text="",
                                        command=self._do_restart_as_admin)
            self.btn_runas.pack(side="right", padx=4)
        else:
            self.btn_runas = None

        ttk.Separator(self, orient="horizontal").grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=8, pady=2)

        # — Статус —
        self.fr_st = ttk.LabelFrame(self, text="")
        self.fr_st.grid(row=6, column=0, columnspan=2, sticky="ew", **P)

        self.lbl_lt_key = ttk.Label(self.fr_st, text="")
        self.lbl_lt_key.grid(row=0, column=0, sticky="w", **P)
        self.lbl_local = ttk.Label(self.fr_st, text="—",
                                   foreground="#005cc5", font=("Courier", 11, "bold"))
        self.lbl_local.grid(row=0, column=1, sticky="w", **P)

        self.lbl_nt_key = ttk.Label(self.fr_st, text="")
        self.lbl_nt_key.grid(row=1, column=0, sticky="w", **P)
        self.lbl_ntp = ttk.Label(self.fr_st, text="—",
                                  foreground="#22863a", font=("Courier", 11, "bold"))
        self.lbl_ntp.grid(row=1, column=1, sticky="w", **P)

        self.lbl_off_key = ttk.Label(self.fr_st, text="")
        self.lbl_off_key.grid(row=2, column=0, sticky="w", **P)
        self.lbl_offset = ttk.Label(self.fr_st, text="—")
        self.lbl_offset.grid(row=2, column=1, sticky="w", **P)

        self.lbl_status = ttk.Label(self.fr_st, text="", foreground="gray")
        self.lbl_status.grid(row=3, column=0, columnspan=2, sticky="w", **P)

        # — Лог —
        self.log = scrolledtext.ScrolledText(self, height=12, width=74,
                                              state="disabled", font=("Courier", 9))
        self.log.grid(row=7, column=0, columnspan=2, padx=8, pady=4)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    # ── применить язык ────────────────────────────────────────────────────────

    def _apply_lang(self):
        t = self.tr
        self.title(t("title"))
        self.fr_lang.config(text=t("fr_lang"))
        self.fr_up.config(text=t("fr_upstream"))
        self.rb_ntp.config(text=t("src_ntp"))
        self.rb_timsyn.config(text=t("src_timsyn"))
        self.lbl_address.config(text=t("lbl_address"))
        self.lbl_outport.config(text=t("lbl_outport"))
        self.lbl_interval.config(text=t("lbl_interval"))
        self._on_source_change()   # обновить подсказку
        self.chk_auto.config(text=t("chk_autoset"))
        self.chk_autorun_srv.config(text=t("chk_autorun_srv"))
        self.chk_autostart.config(text=t("chk_autostart"))
        priv_key = "lbl_priv_ok" if self._admin else "lbl_priv_no"
        self.lbl_priv.config(text=t(priv_key))
        if self.btn_runas:
            self.btn_runas.config(text=t("btn_runas"))
        self.fr_srv.config(text=t("fr_server"))
        self.lbl_iface.config(text=t("lbl_iface"))
        self.lbl_inport.config(text=t("lbl_inport"))
        self.btn_start.config(text=t("btn_start"))
        self.btn_stop.config(text=t("btn_stop"))
        self.btn_sync.config(text=t("btn_sync"))
        self.btn_apply_time.config(text=t("btn_apply_time"))
        self.btn_save.config(text=t("btn_save"))
        self.btn_about.config(text=t("btn_about"))
        self.fr_st.config(text=t("fr_status"))
        self.lbl_lt_key.config(text=t("lbl_localtime"))
        self.lbl_nt_key.config(text=t("lbl_ntptime"))
        self.lbl_off_key.config(text=t("lbl_offset"))
        if self.ntp_srv:
            self.lbl_status.config(
                text=f"{t('srv_running')}  ·  {self.cfg['listen_host']}:{self.cfg['listen_port']}",
                foreground="#22863a")
        else:
            self.lbl_status.config(text=t("srv_stopped"), foreground="gray")

    def _on_lang_change(self):
        self._lang = self.v_lang.get()
        self._apply_lang()

    def _on_source_change(self):
        """Обновить подсказку и дефолтный адрес при смене источника."""
        src = self.v_source_type.get()
        hint = self.tr("hint_ntp") if src == "ntp" else self.tr("hint_timsyn")
        self.lbl_src_hint.config(text=hint)
        # предложить адрес по умолчанию если поле пустое или содержит дефолт другого типа
        current = self.v_upstream.get().strip()
        if src == "ntp" and current == "":
            self.v_upstream.set("pool.ntp.org")
        elif src == "timsyn" and current in ("pool.ntp.org", ""):
            self.v_upstream.set("")

    # ── вспомогательные ───────────────────────────────────────────────────────

    @staticmethod
    def _local_ips():
        ips = []
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None):
                ip = info[4][0]
                if ip not in ips and ":" not in ip:
                    ips.append(ip)
        except Exception:
            pass
        return ips

    def _log(self, msg: str):
        ts   = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log.configure(state="normal")
        self.log.insert("end", line)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _tick(self):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.lbl_local.config(text=now_str)
        self.after(1000, self._tick)

    # ── действия ──────────────────────────────────────────────────────────────

    def _collect_cfg(self):
        self.cfg.update({
            "upstream_ntp":   self.v_upstream.get().strip(),
            "upstream_port":  self.v_up_port.get(),
            "source_type":    self.v_source_type.get(),
            "listen_host":    self.v_listen_host.get().strip(),
            "listen_port":    self.v_listen_port.get(),
            "sync_interval":  self.v_interval.get(),
            "auto_apply":     self.v_auto_apply.get(),
            "autostart":      self.v_autostart.get(),
            "autorun_server": self.v_autorun_srv.get(),
            "language":       self._lang,
        })

    def _save_cfg(self):
        self._collect_cfg()
        save_config(self.cfg)
        self._log(self.tr("log_cfg_saved"))

    def _start(self):
        self._collect_cfg()
        save_config(self.cfg)
        srv = NTPServer(self.cfg["listen_host"], self.cfg["listen_port"], self._log)
        try:
            srv.start(self.tr)
        except RuntimeError as e:
            messagebox.showerror(self.tr("err_start"), str(e))
            return
        self.ntp_srv = srv
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_status.config(
            text=f"{self.tr('srv_running')}  ·  {self.cfg['listen_host']}:{self.cfg['listen_port']}",
            foreground="#22863a")
        self._sync_now()
        self._schedule_sync()

    def _stop(self):
        if self.ntp_srv:
            self.ntp_srv.stop(self.tr)
            self.ntp_srv = None
        if self._sync_job:
            self.after_cancel(self._sync_job)
            self._sync_job = None
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.lbl_status.config(text=self.tr("srv_stopped"), foreground="gray")

    def _sync_now(self):
        host    = self.v_upstream.get().strip()
        port    = self.v_up_port.get()
        auto    = self.v_auto_apply.get()
        lang    = self._lang

        if not host:
            self._log(LANGS[lang]["log_sync_err"].format("No upstream address set"))
            return

        def _do():
            try:
                t      = query_ntp(host, port)
                offset = t - time.time()
                sign   = "+" if offset >= 0 else ""
                color  = ("#22863a" if abs(offset) < 1
                           else "#b08800" if abs(offset) < 60
                           else "#d73a49")
                ts_str = (datetime.datetime.utcfromtimestamp(t)
                          .strftime("%Y-%m-%d  %H:%M:%S") + " UTC")
                log_msg = LANGS[lang]["log_sync_ok"].format(host, sign, abs(offset))

                def _ui():
                    self.lbl_ntp.config(text=ts_str)
                    self.lbl_offset.config(
                        text=f"{sign}{abs(offset):.3f} s", foreground=color)
                    self._log(log_msg)
                    if auto:
                        ok, msg = set_system_time(t)
                        self._log(LANGS[self._lang]["log_time_set"].format(msg))

                self.after(0, _ui)
            except Exception as e:
                self.after(0, lambda: self._log(
                    LANGS[self._lang]["log_sync_err"].format(e)))

        threading.Thread(target=_do, daemon=True).start()

    def _apply_time_now(self):
        """Синхронизировать время на этом ПК с собственного NTP (или последнего NTP-времени)."""
        host = self.v_listen_host.get().strip()
        port = self.v_listen_port.get()
        # если сервер запущен — берём с себя, иначе — с upstream
        if self.ntp_srv:
            src_host = "127.0.0.1"
            src_port = port
        else:
            src_host = self.v_upstream.get().strip()
            src_port = self.v_up_port.get()

        def _do():
            try:
                t = query_ntp(src_host, src_port)
                ok, msg = set_system_time(t)
                self.after(0, lambda: self._log(
                    LANGS[self._lang]["log_time_set"].format(msg)))
            except Exception as e:
                self.after(0, lambda: self._log(
                    LANGS[self._lang]["log_sync_err"].format(e)))

        threading.Thread(target=_do, daemon=True).start()

    def _schedule_sync(self):
        ms = self.v_interval.get() * 1000
        self._sync_job = self.after(ms, self._on_auto_sync)

    def _on_auto_sync(self):
        if self.ntp_srv:
            self._sync_now()
            self._schedule_sync()

    # ── трей и автозапуск ─────────────────────────────────────────────────────

    @staticmethod
    def _load_icon(size: int = 64):
        from PIL import Image
        candidates = [
            Path(__file__).parent.parent / "icon.png",
            Path(__file__).parent / "icon.png",
        ]
        for p in candidates:
            if p.exists():
                return Image.open(p).convert("RGBA").resize((size, size))
        # fallback — рисуем часы
        from PIL import ImageDraw
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([2, 2, size-2, size-2], fill="#005cc5", outline="#003a8c", width=2)
        cx, cy = size//2, size//2
        d.line([cx, cy, cx, cy-size//4], fill="white", width=max(2, size//16))
        d.line([cx, cy, cx+size//5, cy+size//12], fill="white", width=max(2, size//20))
        d.ellipse([cx-3, cy-3, cx+3, cy+3], fill="white")
        return img

    def _make_tray_icon(self):
        return self._load_icon(64)

    def _set_window_icon(self):
        try:
            from PIL import ImageTk
            img = self._load_icon(32)
            self._tk_icon = ImageTk.PhotoImage(img)
            self.iconphoto(True, self._tk_icon)
        except Exception:
            pass

    def _init_tray(self):
        try:
            import pystray
            lang = self._lang
            icon = pystray.Icon(
                "TimSyn_Server",
                self._make_tray_icon(),
                title=LANGS[lang]["tray_tooltip"],
                menu=pystray.Menu(
                    pystray.MenuItem(
                        lambda i: LANGS[self._lang]["tray_show"],
                        self._tray_show, default=True),
                    pystray.MenuItem(
                        lambda i: LANGS[self._lang]["tray_sync"],
                        lambda i: self.after(0, self._sync_now)),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(
                        lambda i: LANGS[self._lang]["tray_exit"],
                        self._tray_exit),
                ),
            )
            self._tray = icon
            threading.Thread(target=icon.run, daemon=True).start()
        except Exception:
            self._tray = None

    def _hide_to_tray(self):
        self.withdraw()
        if self._tray:
            self._tray.visible = True

    def _tray_show(self, icon=None, item=None):
        if self._tray:
            self._tray.visible = False
        self.after(0, self.deiconify)

    def _tray_exit(self, icon=None, item=None):
        if self._tray:
            self._tray.stop()
        self.after(0, self._quit)

    def _quit(self):
        self._stop()
        self.destroy()

    def _do_restart_as_admin(self):
        self._collect_cfg()
        save_config(self.cfg)   # сохранить настройки перед перезапуском
        self._stop()
        restart_as_admin()

    def _toggle_autostart(self):
        self._collect_cfg()
        save_config(self.cfg)
        set_autostart("TimSyn_Server", self.v_autostart.get())

    # ── об авторе ─────────────────────────────────────────────────────────────

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title(self.tr("about_title"))
        win.resizable(False, False)
        win.grab_set()

        # логотип / название
        ttk.Label(win, text="TimSyn", font=("TkDefaultFont", 18, "bold"),
                  foreground="#005cc5").pack(pady=(16, 0))
        ttk.Label(win, text="NTP Time Synchronization Suite",
                  foreground="gray").pack(pady=(0, 12))

        ttk.Separator(win).pack(fill="x", padx=16)

        body = self.tr("about_body")
        ttk.Label(win, text=body, justify="center",
                  font=("TkDefaultFont", 10)).pack(padx=24, pady=12)

        ttk.Separator(win).pack(fill="x", padx=16)

        # кликабельные ссылки
        fr_links = ttk.Frame(win)
        fr_links.pack(pady=8)

        lnk_site = tk.Label(fr_links, text="🌐  https://midgro.uz",
                             foreground="#005cc5", cursor="hand2",
                             font=("TkDefaultFont", 10, "underline"))
        lnk_site.pack()
        lnk_site.bind("<Button-1>", lambda e: self._open_url("https://midgro.uz"))

        lnk_mail = tk.Label(fr_links, text="✉  info@midgro.uz",
                             foreground="#005cc5", cursor="hand2",
                             font=("TkDefaultFont", 10, "underline"))
        lnk_mail.pack()
        lnk_mail.bind("<Button-1>", lambda e: self._open_url("mailto:info@midgro.uz"))

        ttk.Button(win, text="OK", command=win.destroy, width=12).pack(pady=12)

    @staticmethod
    def _open_url(url: str):
        import webbrowser
        webbrowser.open(url)

    def on_close(self):
        if self._tray:
            self._hide_to_tray()
        else:
            self._quit()


# ═══════════════════════════════════════════════════════════════════════════════

_INSTANCE_LOCK = None


def _acquire_instance_lock() -> bool:
    global _INSTANCE_LOCK
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 50791))
        _INSTANCE_LOCK = sock
        return True
    except OSError:
        sock.close()
        return False


def main():
    if not _acquire_instance_lock():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("TimSyn Server", "TimSyn Server is already running.")
        root.destroy()
        return
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
