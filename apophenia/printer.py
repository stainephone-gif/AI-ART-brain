"""Очередь печати. PDF копируется в queue/, рабочий поток печатает по одному и переносит в queue/printed/.

Если принтер недоступен, файл остаётся в очереди и печать повторяется через retry_seconds.
Windows: команда печати — SumatraPDF (portable), Linux: lp. Команда задаётся в config.yaml.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .config import path_dir, resolve

log = logging.getLogger("apophenia.printer")


class PrintQueue:
    def __init__(self, cfg: Dict[str, Any], on_error: Optional[Callable[[str], None]] = None):
        p = cfg.get("printer", {})
        self.enabled = bool(p.get("enabled", True))
        self.name = str(p.get("name", ""))
        self.command: List[str] = list(p.get("command", []))
        self.retry = float(p.get("retry_seconds", 60))
        self.copies = int(p.get("copies", 1))
        self.cfg = cfg
        self.dir = path_dir(cfg, "queue")
        self.printed = self.dir / "printed"
        self.printed.mkdir(exist_ok=True)
        self.on_error = on_error
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.last_error: Optional[str] = None

    # -- очередь --------------------------------------------------------------
    def enqueue(self, pdf: Path) -> Path:
        dst = self.dir / Path(pdf).name
        shutil.copy2(pdf, dst)
        log.info("В очередь печати: %s", dst.name)
        self._wake.set()
        return dst

    def print_now(self, pdf: Path) -> bool:
        """Синхронная печать (для reprint/test-print): в очередь, напечатать, при успехе перенести в printed/."""
        q = self.enqueue(pdf)
        ok = self.print_file(q)
        if ok:
            shutil.move(str(q), str(self.printed / q.name))
        return ok

    def pending(self) -> List[Path]:
        return sorted(p for p in self.dir.glob("*.pdf") if p.is_file())

    @staticmethod
    def installed_printers() -> List[str]:
        """Имена принтеров Windows (пустой список на других ОС или при ошибке)."""
        if os.name != "nt":
            return []
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Printer | Select-Object -ExpandProperty Name"],
                               capture_output=True, text=True, timeout=30)
            return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        except (OSError, subprocess.SubprocessError):
            return []

    def _build_command(self, pdf: Path) -> List[str]:
        cmd = []
        for part in self.command:
            if part == "-print-to" and self.name.lower() in ("", "default"):
                # printer.name: default → печать на принтер по умолчанию
                cmd.append("-print-to-default")
                continue
            if part == "{printer}" and self.name.lower() in ("", "default"):
                continue
            part = part.replace("{pdf}", str(pdf)).replace("{printer}", self.name)
            if part.lower().endswith((".exe", "sumatrapdf")) and not Path(part).is_absolute():
                part = str(resolve(self.cfg, part))
            cmd.append(part)
        return cmd

    def print_file(self, pdf: Path) -> bool:
        """Печать одного файла. Возвращает True при успехе (файл ушёл в спулер)."""
        if not self.enabled or not self.command:
            log.info("Печать отключена, файл считается напечатанным: %s", pdf.name)
            return True
        cmd = self._build_command(pdf)
        exe = Path(cmd[0])
        if exe.suffix.lower() == ".exe" and not exe.exists():
            self.last_error = f"Не найден {exe}"
            return False
        try:
            for _ in range(self.copies):
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if r.returncode != 0:
                    self.last_error = f"код {r.returncode}: {(r.stderr or r.stdout)[:200]}"
                    printers = self.installed_printers()
                    if printers and self.name not in printers:
                        self.last_error = (f"принтер «{self.name}» не найден в Windows. Установлены: "
                                           + "; ".join(printers) + ". Впишите точное имя в config.yaml (printer.name) "
                                           "или поставьте name: default")
                    elif printers:
                        self.last_error += " (принтер найден, но печать не прошла: проверьте, включён ли он и есть ли бумага)"
                    return False
            self.last_error = None
            return True
        except (OSError, subprocess.SubprocessError) as e:
            self.last_error = str(e)
            return False

    # -- рабочий поток ----------------------------------------------------------
    def start(self) -> None:
        if self._thread:
            return
        self._thread = threading.Thread(target=self._loop, name="printer", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()

    def _loop(self) -> None:
        reported = False
        while not self._stop.is_set():
            pending = self.pending()
            if not pending:
                self._wake.wait(timeout=self.retry)
                self._wake.clear()
                continue
            pdf = pending[0]
            if self.print_file(pdf):
                shutil.move(str(pdf), str(self.printed / pdf.name))
                log.info("Напечатано: %s", pdf.name)
                reported = False
                time.sleep(2)
            else:
                log.warning("Печать не удалась (%s), повтор через %ss; в очереди %d", self.last_error, self.retry, len(pending))
                if self.on_error and not reported:
                    self.on_error(f"Принтер: {self.last_error}. В очереди {len(pending)} лист(ов).")
                    reported = True
                self._wake.wait(timeout=self.retry)
                self._wake.clear()
