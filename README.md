# TimSyn — NTP Time Synchronization Suite

<div align="center">

**Локальный NTP-сервер + клиент для синхронизации времени в сети без интернета**

[![Build](https://github.com/midgrouz/timsyn/actions/workflows/build.yml/badge.svg)](https://github.com/midgrouz/timsyn/actions)
[![License: MOAL](https://img.shields.io/badge/License-MOAL_v1.0-blue.svg)](LICENSE)

---

### Разработано [MIDGRO.UZ](https://midgro.uz)
**info@midgro.uz**

</div>

---

## Что это

TimSyn — это пара лёгких программ с графическим интерфейсом для синхронизации времени в изолированных локальных сетях без доступа в интернет.

```
[Интернет] ──► [TimSyn Server] ──► [Локальная сеть]
  pool.ntp.org   (1 машина)         TimSyn Client ×N
                                     (все остальные ПК)
```

**Сервер** ставится на одну машину с интернетом — тянет точное время с NTP и раздаёт его в локалку.  
**Клиент** ставится на все остальные ПК — получает время с сервера и устанавливает на системные часы.

---

## Возможности

| Функция | Сервер | Клиент |
|---|:---:|:---:|
| Синхронизация с публичным NTP | ✓ | — |
| Работа как NTP-сервер | ✓ | — |
| Получение времени из локальной сети | — | ✓ |
| Установка системного времени | ✓ | ✓ |
| Авто-синхронизация по таймеру | ✓ | ✓ |
| Настройка портов (вх./исх.) | ✓ | ✓ |
| Выбор сетевого интерфейса | ✓ | — |
| Показ отклонения и RTT | ✓ | ✓ |
| Интерфейс EN / RU / UZ | ✓ | ✓ |
| Работа без установки доп. ПО | ✓ | ✓ |

---

## Скачать

> Готовые бинарники собираются автоматически через GitHub Actions.

| Платформа | Файл |
|---|---|
| Windows | `TimSyn_Server.exe`, `TimSyn_Client.exe` |
| Linux x86-64 | `TimSyn_Server`, `TimSyn_Client` |

Скачать последнюю сборку: **[Actions → последний успешный run → Artifacts](../../actions)**

---

## Быстрый старт

### Windows
```
1. Скачать TimSyn_Server.exe → запустить от Администратора
2. Указать NTP-сервер (по умолчанию pool.ntp.org)
3. Нажать "Запустить сервер"

На клиентских ПК:
1. Скачать TimSyn_Client.exe → запустить
2. Указать IP сервера и порт
3. Нажать "Синхронизировать"
```

### Linux
```bash
chmod +x TimSyn_Server TimSyn_Client
sudo ./TimSyn_Server    # sudo нужен для порта 123
./TimSyn_Client
```

> **Порт 123** требует прав администратора/root.  
> Альтернатива — поставить любой порт выше 1024 (например **1234**) в настройках сервера и клиента.

---

## Запуск из исходников

Требуется Python 3.8+ с tkinter (входит в стандартную установку).

```bash
git clone https://github.com/midgrouz/timsyn.git
cd timsyn

python server/timsyn_server.py   # на машине с интернетом
python client/timsyn_client.py   # на локальных машинах
```

---

## Сборка .exe / бинарника

```bash
pip install pyinstaller
python build/build.py
# Результат: build/dist/TimSyn_Server  и  build/dist/TimSyn_Client
```

На Windows те же команды дадут `.exe` файлы.

---

## Структура проекта

```
TimSyn/
├── server/
│   └── timsyn_server.py     # NTP-сервер с GUI
├── client/
│   └── timsyn_client.py     # NTP-клиент с GUI
├── build/
│   └── build.py             # скрипт сборки бинарников
├── .github/
│   └── workflows/
│       └── build.yml        # GitHub Actions (Windows + Linux)
├── LICENSE                  # MIDGRO Open Attribution License
└── README.md
```

---

## Лицензия

Распространяется под **MIDGRO Open Attribution License (MOAL) v1.0**.  
Можно использовать, изменять и продавать — при обязательном упоминании [MIDGRO.UZ](https://midgro.uz).  
Подробности: [LICENSE](LICENSE)

---

<div align="center">

Сделано с ♥ командой **[MIDGRO.UZ](https://midgro.uz)**  
По вопросам: **info@midgro.uz**

</div>
