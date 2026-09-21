import json
from datetime import datetime

from apophenia.schedule import Schedule


def test_schedule_open_hours(cfg):
    cfg["schedule"].update({"open": "11:00", "close": "20:00", "days": [1, 2, 3, 4, 5]})
    s = Schedule(cfg)
    assert s.is_open(datetime(2026, 9, 21, 12, 0))       # понедельник
    assert not s.is_open(datetime(2026, 9, 21, 20, 0))   # закрытие не включительно
    assert not s.is_open(datetime(2026, 9, 26, 12, 0))   # суббота
    assert s.next_open(datetime(2026, 9, 26, 12, 0)) == datetime(2026, 9, 28, 11, 0)
    assert s.next_open(datetime(2026, 9, 21, 12, 0)) == datetime(2026, 9, 22, 11, 0)


def test_service_once_and_reprint(cfg, tmp_path, main_mod):
    svc = main_mod.Service(cfg, mock=True, scenario="drift")
    rec = svc.run_cycle(do_print=True)
    assert rec["cycle"] == 1
    archive = tmp_path / "archive"
    assert (archive / "cycle_00001.json").exists() and (archive / "cycle_00001.pdf").exists()
    assert (tmp_path / "queue" / "cycle_00001.pdf").exists()  # в очереди, рабочий поток не запущен
    assert json.loads((tmp_path / "state" / "state.json").read_text(encoding="utf-8"))["last_cycle"] == 1
    disp = json.loads((tmp_path / "state" / "display.json").read_text(encoding="utf-8"))
    assert disp["phase"] == "idle" and disp["cycle"] == 1 and len(disp["quotes"]) >= 3
    main_mod.cmd_reprint(svc, 1, render_only=True)
    svc2 = main_mod.Service(cfg, mock=True, scenario="stabilize")
    assert svc2.run_cycle(do_print=False)["cycle"] == 2  # сквозная нумерация после перезапуска
