import json
import os

from save_manager import get_save_slot_summary, save_slot, load_slot, get_save_dir


def test_save_slot_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr('save_manager.get_save_dir', lambda: str(tmp_path))

    slot = 1
    save_data = {
        'satiety': 75,
        'toilet': 80,
        'happy': 90,
        'health': 85,
        'logiki': 42,
    }

    save_slot(slot, save_data, 'My Pet')
    summary = get_save_slot_summary(slot)

    assert summary['used'] is True
    assert summary['name'] == 'My Pet'
    assert summary['days_lived'] == 0
    assert summary['last_saved_at'] is not None

    loaded = load_slot(slot)
    assert loaded['game_data'] == save_data
    assert loaded['save_name'] == 'My Pet'

    assert os.path.exists(os.path.join(tmp_path, 'slot_1.json'))
    with open(os.path.join(tmp_path, 'slot_1.json'), 'r', encoding='utf-8') as f:
        raw = json.load(f)
    assert raw['save_name'] == 'My Pet'
