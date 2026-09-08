#!/usr/bin/env python3
"""
Сборка TimSyn Server и TimSyn Client в один .exe / один бинарник.
Требует: pip install pyinstaller

Запуск:
  python build/build.py

Результат в build/dist/
"""

import subprocess
import sys
import os
from pathlib import Path

ROOT  = Path(__file__).parent.parent
BUILD = Path(__file__).parent

TARGETS = [
    {
        "script":   ROOT / "server" / "timsyn_server.py",
        "name":     "TimSyn_Server",
        "icon":     None,
    },
    {
        "script":   ROOT / "client" / "timsyn_client.py",
        "name":     "TimSyn_Client",
        "icon":     None,
    },
]


def build(target: dict):
    script  = str(target["script"])
    name    = target["name"]
    distdir = str(BUILD / "dist")
    workdir = str(BUILD / "work" / name)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",               # один файл
        "--windowed",              # без консольного окна (GUI)
        "--name", name,
        "--distpath", distdir,
        "--workpath", workdir,
        "--specpath", str(BUILD / "spec"),
        "--clean",
        "--noconfirm",
    ]

    if target.get("icon"):
        cmd += ["--icon", str(target["icon"])]

    cmd.append(script)

    print(f"\n{'='*60}")
    print(f"  Сборка: {name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  ОШИБКА при сборке {name}")
        sys.exit(1)
    print(f"  OK → {distdir}/{name}")


def main():
    # Проверить наличие PyInstaller
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                       capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("PyInstaller не найден. Установите: pip install pyinstaller")
        sys.exit(1)

    for t in TARGETS:
        build(t)

    print(f"\n{'='*60}")
    print(f"  Готово!  Файлы: {BUILD / 'dist'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
