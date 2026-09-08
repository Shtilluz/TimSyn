#!/usr/bin/env python3
"""
TimSyn Client
Получает точное время от TimSyn Server в локальной сети и устанавливает на ПК.
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
        "title":         "TimSyn Клиент",
        "fr_server":     " Сервер TimSyn ",
        "lbl_server":    "Адрес сервера:",
        "lbl_port":      "Порт:",
        "lbl_interval":  "Авто-синхр. (сек, 0 = выкл.):",
        "chk_autoset":   "Авто-установка времени на этом ПК",
        "btn_sync":      "⟳  Синхронизировать",
        "btn_save":      "✎  Сохранить",
        "fr_status":     " Состояние ",
        "lbl_localtime": "Местное время:",
        "lbl_srvtime":   "Время сервера:",
        "lbl_offset":    "Отклонение:",
        "lbl_rtt":       "RTT:",
        "st_idle":       "Ожидание",
        "st_syncing":    "Синхронизация...",
        "st_ok":         "OK",
        "st_error":      "Ошибка",
        "log_sync_ok":   "[SYNC] offset={}{:.3f} с  RTT={:.1f} мс",
        "log_sync_err":  "[SYNC] Ошибка: {}",
        "log_time_set":  "[ВРЕМЯ] Установка: {}",
        "log_auto_on":   "[АВТО] Автосинхр. каждые {} сек",
        "log_auto_off":  "[АВТО] Автосинхр. отключена",
        "log_cfg_saved": "[CFG] Настройки сохранены",
        "err_notip":     "Введите адрес сервера",
        "fr_lang":       " Язык / Language ",
        "btn_about":     "ℹ  Об авторе",
        "about_title":   "Об авторе",
        "about_body":    "TimSyn — NTP синхронизация времени\n\nРазработано: MIDGRO.UZ\nСайт: https://midgro.uz\nКонтакт: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nРаспространяется под лицензией MOAL v1.0\n(можно использовать и продавать при упоминании MIDGRO.UZ)",
        "chk_autostart": "Автозапуск при старте системы",
        "tray_show":     "Открыть",
        "tray_sync":     "Синхр. сейчас",
        "tray_exit":     "Выход",
        "tray_tooltip":  "TimSyn Клиент",
        "btn_runas":     "🔒  Перезапустить от Администратора",
        "lbl_priv_ok":   "✔  Права администратора",
        "lbl_priv_no":   "⚠  Нет прав администратора — установка времени может не работать",
    },
    "EN": {
        "title":         "TimSyn Client",
        "fr_server":     " TimSyn Server ",
        "lbl_server":    "Server Address:",
        "lbl_port":      "Port:",
        "lbl_interval":  "Auto-sync (sec, 0 = off):",
        "chk_autoset":   "Auto-set time on this PC",
        "btn_sync":      "⟳  Synchronize",
        "btn_save":      "✎  Save",
        "fr_status":     " Status ",
        "lbl_localtime": "Local Time:",
        "lbl_srvtime":   "Server Time:",
        "lbl_offset":    "Offset:",
        "lbl_rtt":       "RTT:",
        "st_idle":       "Idle",
        "st_syncing":    "Syncing...",
        "st_ok":         "OK",
        "st_error":      "Error",
        "log_sync_ok":   "[SYNC] offset={}{:.3f} s  RTT={:.1f} ms",
        "log_sync_err":  "[SYNC] Error: {}",
        "log_time_set":  "[TIME] Set result: {}",
        "log_auto_on":   "[AUTO] Auto-sync every {} sec",
        "log_auto_off":  "[AUTO] Auto-sync disabled",
        "log_cfg_saved": "[CFG] Settings saved",
        "err_notip":     "Please enter server address",
        "fr_lang":       " Language ",
        "btn_about":     "ℹ  About",
        "about_title":   "About",
        "about_body":    "TimSyn — NTP Time Synchronization\n\nDeveloped by: MIDGRO.UZ\nWebsite: https://midgro.uz\nContact: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nDistributed under MOAL v1.0\n(free to use and sell with attribution to MIDGRO.UZ)",
        "chk_autostart": "Run at system startup",
        "tray_show":     "Open",
        "tray_sync":     "Sync Now",
        "tray_exit":     "Exit",
        "tray_tooltip":  "TimSyn Client",
        "btn_runas":     "🔒  Restart as Administrator",
        "lbl_priv_ok":   "✔  Running as Administrator",
        "lbl_priv_no":   "⚠  No admin rights — time sync may fail",
    },
    "UZ": {
        "title":         "TimSyn Mijoz",
        "fr_server":     " TimSyn Server ",
        "lbl_server":    "Server Manzili:",
        "lbl_port":      "Port:",
        "lbl_interval":  "Auto-sinxr. (sek, 0 = o'ch.):",
        "chk_autoset":   "Ushbu PK vaqtini avtomatik o'rnatish",
        "btn_sync":      "⟳  Sinxronlash",
        "btn_save":      "✎  Saqlash",
        "fr_status":     " Holat ",
        "lbl_localtime": "Mahalliy Vaqt:",
        "lbl_srvtime":   "Server Vaqti:",
        "lbl_offset":    "Farq:",
        "lbl_rtt":       "RTT:",
        "st_idle":       "Kutish",
        "st_syncing":    "Sinxronlanmoqda...",
        "st_ok":         "OK",
        "st_error":      "Xato",
        "log_sync_ok":   "[SYNC] farq={}{:.3f} s  RTT={:.1f} ms",
        "log_sync_err":  "[SYNC] Xato: {}",
        "log_time_set":  "[VAQT] O'rnatish: {}",
        "log_auto_on":   "[AUTO] Har {} sekundda auto-sinxr.",
        "log_auto_off":  "[AUTO] Auto-sinxronlash o'chirildi",
        "log_cfg_saved": "[CFG] Sozlamalar saqlandi",
        "err_notip":     "Server manzilini kiriting",
        "fr_lang":       " Til / Language ",
        "btn_about":     "ℹ  Muallif haqida",
        "about_title":   "Muallif haqida",
        "about_body":    "TimSyn — NTP Vaqt Sinxronizatsiyasi\n\nIshlab chiqaruvchi: MIDGRO.UZ\nSayt: https://midgro.uz\nAloqa: info@midgro.uz\n\n© 2026 MIDGRO.UZ\nMOAL v1.0 litsenziyasi asosida tarqatiladi\n(MIDGRO.UZ ni eslatgan holda foydalanish va sotish mumkin)",
        "chk_autostart": "Tizim ishga tushganda avtomatik yoqilsin",
        "tray_show":     "Ochish",
        "tray_sync":     "Hozir sinxr.",
        "tray_exit":     "Chiqish",
        "tray_tooltip":  "TimSyn Mijoz",
        "btn_runas":     "🔒  Administrator sifatida qayta ishga tushirish",
        "lbl_priv_ok":   "✔  Administrator huquqlari mavjud",
        "lbl_priv_no":   "⚠  Administrator huquqi yo'q — vaqt o'rnatish ishlamasligi mumkin",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#  NTP protokol
# ═══════════════════════════════════════════════════════════════════════════════

NTP_DELTA = 2208988800
_FMT      = "!B B b b I I I I I I I I I I I"


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


def query_ntp(host: str, port: int = 123, timeout: float = 5.0):
    """Вернуть (server_unix_time, rtt_ms) или бросить исключение."""
    t0 = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        s.sendto(_make_client_pkt(), (host, port))
        data, _ = s.recvfrom(1024)
    t1 = time.time()
    u       = struct.unpack(_FMT, data[:48])
    srv_ts  = _from_ntp(u[13], u[14])
    rtt_ms  = (t1 - t0) * 1000.0
    return srv_ts, rtt_ms


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
#  Автозапуск
# ═══════════════════════════════════════════════════════════════════════════════

def set_autostart(app_name: str, enable: bool):
    """Добавить/убрать приложение из автозапуска."""
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
    exe = sys.executable
    if platform.system() == "Windows":
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, "", None, 1)
    else:
        for launcher in ("pkexec", "gksudo", "kdesudo"):
            if subprocess.call(["which", launcher],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL) == 0:
                subprocess.Popen([launcher, exe])
                break
        else:
            subprocess.Popen(["sudo", exe])
    os._exit(0)


# ═══════════════════════════════════════════════════════════════════════════════
#  Конфиг
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_PATH = Path.home() / ".timsyn_client.json"

DEFAULTS = {
    "server":        "",
    "port":          123,
    "sync_interval": 0,
    "auto_apply":    True,
    "language":      "RU",
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
#  GUI
# ═══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg       = load_config()
        self._lang     = self.cfg.get("language", "RU")
        self._auto_job = None
        self._tray     = None
        self.resizable(False, False)
        self._build_ui()
        self._apply_lang()
        self._set_window_icon()
        self._tick()
        self._init_tray()
        if self.cfg.get("sync_interval", 0) > 0:
            self.after(1500, self._restart_auto)

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

        # — Настройки сервера —
        self.fr_srv = ttk.LabelFrame(self, text="")
        self.fr_srv.grid(row=1, column=0, columnspan=2, sticky="ew", **P)

        self.lbl_server = ttk.Label(self.fr_srv, text="")
        self.lbl_server.grid(row=0, column=0, sticky="w", **P)
        self.v_server = tk.StringVar(value=self.cfg["server"])
        ttk.Entry(self.fr_srv, textvariable=self.v_server, width=26).grid(row=0, column=1, **P)

        self.lbl_port = ttk.Label(self.fr_srv, text="")
        self.lbl_port.grid(row=0, column=2, sticky="w", **P)
        self.v_port = tk.IntVar(value=self.cfg["port"])
        ttk.Spinbox(self.fr_srv, textvariable=self.v_port,
                    from_=1, to=65535, width=7).grid(row=0, column=3, **P)

        self.lbl_interval = ttk.Label(self.fr_srv, text="")
        self.lbl_interval.grid(row=1, column=0, sticky="w", **P)
        self.v_interval = tk.IntVar(value=self.cfg["sync_interval"])
        ttk.Spinbox(self.fr_srv, textvariable=self.v_interval,
                    from_=0, to=86400, width=7).grid(row=1, column=1, sticky="w", **P)

        self.v_auto_apply = tk.BooleanVar(value=self.cfg["auto_apply"])
        self.chk_auto = ttk.Checkbutton(self.fr_srv, text="", variable=self.v_auto_apply)
        self.chk_auto.grid(row=1, column=2, columnspan=2, sticky="w", **P)

        self.v_autostart = tk.BooleanVar(value=self.cfg.get("autostart", False))
        self.chk_autostart = ttk.Checkbutton(self.fr_srv, text="",
                                              variable=self.v_autostart,
                                              command=self._toggle_autostart)
        self.chk_autostart.grid(row=2, column=0, columnspan=4, sticky="w", **P)

        # — Кнопки —
        fr_btn = ttk.Frame(self)
        fr_btn.grid(row=2, column=0, columnspan=2, **P)

        self.btn_sync = ttk.Button(fr_btn, text="", command=self._sync_now)
        self.btn_sync.pack(side="left", padx=4)

        self.btn_save = ttk.Button(fr_btn, text="", command=self._save_cfg)
        self.btn_save.pack(side="left", padx=4)
        self.btn_about = ttk.Button(fr_btn, text="", command=self._show_about)
        self.btn_about.pack(side="left", padx=4)

        # — Строка привилегий —
        fr_priv = ttk.Frame(self)
        fr_priv.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 2))

        self._admin = is_admin()
        priv_color  = "#22863a" if self._admin else "#d73a49"
        self.lbl_priv = ttk.Label(fr_priv, text="", foreground=priv_color,
                                   font=("TkDefaultFont", 9, "bold"))
        self.lbl_priv.pack(side="left")

        if not self._admin:
            self.btn_runas = ttk.Button(fr_priv, text="",
                                        command=self._do_restart_as_admin)
            self.btn_runas.pack(side="right", padx=4)
        else:
            self.btn_runas = None

        ttk.Separator(self, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=2)

        # — Статус —
        self.fr_st = ttk.LabelFrame(self, text="")
        self.fr_st.grid(row=5, column=0, columnspan=2, sticky="ew", **P)

        self.lbl_lt_key = ttk.Label(self.fr_st, text="")
        self.lbl_lt_key.grid(row=0, column=0, sticky="w", **P)
        self.lbl_local = ttk.Label(self.fr_st, text="—",
                                   foreground="#005cc5", font=("Courier", 11, "bold"))
        self.lbl_local.grid(row=0, column=1, sticky="w", **P)

        self.lbl_st_key = ttk.Label(self.fr_st, text="")
        self.lbl_st_key.grid(row=1, column=0, sticky="w", **P)
        self.lbl_srv_time = ttk.Label(self.fr_st, text="—",
                                      foreground="#22863a", font=("Courier", 11, "bold"))
        self.lbl_srv_time.grid(row=1, column=1, sticky="w", **P)

        self.lbl_off_key = ttk.Label(self.fr_st, text="")
        self.lbl_off_key.grid(row=2, column=0, sticky="w", **P)
        self.lbl_offset = ttk.Label(self.fr_st, text="—")
        self.lbl_offset.grid(row=2, column=1, sticky="w", **P)

        self.lbl_rtt_key = ttk.Label(self.fr_st, text="")
        self.lbl_rtt_key.grid(row=3, column=0, sticky="w", **P)
        self.lbl_rtt = ttk.Label(self.fr_st, text="—")
        self.lbl_rtt.grid(row=3, column=1, sticky="w", **P)

        self.lbl_status = ttk.Label(self.fr_st, text="", foreground="gray",
                                    font=("TkDefaultFont", 9, "bold"))
        self.lbl_status.grid(row=4, column=0, columnspan=2, sticky="w", **P)

        # — Лог —
        self.log = scrolledtext.ScrolledText(self, height=10, width=66,
                                              state="disabled", font=("Courier", 9))
        self.log.grid(row=6, column=0, columnspan=2, padx=8, pady=4)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    # ── применить язык ────────────────────────────────────────────────────────

    def _apply_lang(self):
        t = self.tr
        self.title(t("title"))
        self.fr_lang.config(text=t("fr_lang"))
        self.fr_srv.config(text=t("fr_server"))
        self.lbl_server.config(text=t("lbl_server"))
        self.lbl_port.config(text=t("lbl_port"))
        self.lbl_interval.config(text=t("lbl_interval"))
        self.chk_auto.config(text=t("chk_autoset"))
        self.btn_sync.config(text=t("btn_sync"))
        self.btn_save.config(text=t("btn_save"))
        self.btn_about.config(text=t("btn_about"))
        self.chk_autostart.config(text=t("chk_autostart"))
        self.fr_st.config(text=t("fr_status"))
        self.lbl_lt_key.config(text=t("lbl_localtime"))
        self.lbl_st_key.config(text=t("lbl_srvtime"))
        self.lbl_off_key.config(text=t("lbl_offset"))
        self.lbl_rtt_key.config(text=t("lbl_rtt"))
        self.lbl_status.config(text=t("st_idle"), foreground="gray")
        priv_key = "lbl_priv_ok" if self._admin else "lbl_priv_no"
        self.lbl_priv.config(text=t(priv_key))
        if self.btn_runas:
            self.btn_runas.config(text=t("btn_runas"))

    def _on_lang_change(self):
        self._lang = self.v_lang.get()
        self._apply_lang()

    # ── вспомогательные ───────────────────────────────────────────────────────

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
            "server":        self.v_server.get().strip(),
            "port":          self.v_port.get(),
            "sync_interval": self.v_interval.get(),
            "auto_apply":    self.v_auto_apply.get(),
            "autostart":     self.v_autostart.get(),
            "language":      self._lang,
        })

    def _save_cfg(self):
        self._collect_cfg()
        save_config(self.cfg)
        self._log(self.tr("log_cfg_saved"))
        self._restart_auto()

    def _restart_auto(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
            self._auto_job = None
        interval = self.v_interval.get()
        if interval > 0:
            self._log(self.tr("log_auto_on").format(interval))
            self._schedule_auto(interval)
        else:
            self._log(self.tr("log_auto_off"))

    def _schedule_auto(self, interval: int):
        self._auto_job = self.after(interval * 1000, self._on_auto_sync)

    def _on_auto_sync(self):
        self._sync_now()
        interval = self.v_interval.get()
        if interval > 0:
            self._schedule_auto(interval)

    def _sync_now(self):
        host = self.v_server.get().strip()
        if not host:
            messagebox.showwarning(self.tr("title"), self.tr("err_notip"))
            return
        port     = self.v_port.get()
        auto     = self.v_auto_apply.get()
        lang     = self._lang

        self.lbl_status.config(text=LANGS[lang]["st_syncing"], foreground="#b08800")
        self.btn_sync.config(state="disabled")

        def _do():
            try:
                srv_ts, rtt = query_ntp(host, port)
                offset = srv_ts - time.time()
                sign   = "+" if offset >= 0 else ""
                color  = ("#22863a" if abs(offset) < 1
                           else "#b08800" if abs(offset) < 60
                           else "#d73a49")
                ts_str = (datetime.datetime.utcfromtimestamp(srv_ts)
                          .strftime("%Y-%m-%d  %H:%M:%S") + " UTC")
                log_ok = LANGS[lang]["log_sync_ok"].format(sign, abs(offset), rtt)

                def _ui():
                    self.lbl_srv_time.config(text=ts_str)
                    self.lbl_offset.config(
                        text=f"{sign}{abs(offset):.3f} s", foreground=color)
                    self.lbl_rtt.config(text=f"{rtt:.1f} ms")
                    self.lbl_status.config(
                        text=LANGS[self._lang]["st_ok"], foreground="#22863a")
                    self.btn_sync.config(state="normal")
                    self._log(log_ok)
                    if auto:
                        ok, msg = set_system_time(srv_ts)
                        self._log(LANGS[self._lang]["log_time_set"].format(msg))

                self.after(0, _ui)

            except Exception as e:
                err_msg = str(e)
                def _ui_err():
                    self.lbl_status.config(
                        text=LANGS[self._lang]["st_error"], foreground="#d73a49")
                    self.btn_sync.config(state="normal")
                    self._log(LANGS[self._lang]["log_sync_err"].format(err_msg))
                self.after(0, _ui_err)

        threading.Thread(target=_do, daemon=True).start()

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
            icon = pystray.Icon(
                "TimSyn_Client",
                self._make_tray_icon(),
                title=LANGS[self._lang]["tray_tooltip"],
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
        if self._auto_job:
            self.after_cancel(self._auto_job)
        self.destroy()

    def _do_restart_as_admin(self):
        self._collect_cfg()
        save_config(self.cfg)
        restart_as_admin()

    def _toggle_autostart(self):
        self._collect_cfg()
        save_config(self.cfg)
        set_autostart("TimSyn_Client", self.v_autostart.get())

    # ── об авторе ─────────────────────────────────────────────────────────────

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title(self.tr("about_title"))
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="TimSyn", font=("TkDefaultFont", 18, "bold"),
                  foreground="#005cc5").pack(pady=(16, 0))
        ttk.Label(win, text="NTP Time Synchronization Suite",
                  foreground="gray").pack(pady=(0, 12))

        ttk.Separator(win).pack(fill="x", padx=16)

        ttk.Label(win, text=self.tr("about_body"), justify="center",
                  font=("TkDefaultFont", 10)).pack(padx=24, pady=12)

        ttk.Separator(win).pack(fill="x", padx=16)

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
        sock.bind(("127.0.0.1", 50792))
        _INSTANCE_LOCK = sock
        return True
    except OSError:
        sock.close()
        return False


def main():
    if not _acquire_instance_lock():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("TimSyn Client", "TimSyn Client is already running.")
        root.destroy()
        return
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
