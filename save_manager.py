import json
import os
from datetime import datetime

SAVE_SLOT_COUNT = 3
DEFAULT_ACTION = {
    'satiety': 100,
    'toilet': 100,
    'happy': 100,
    'health': 100,
    'logiki': 50,
}


def get_save_dir():
    save_dir = os.path.join(os.path.dirname(__file__), 'saves')
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def _slot_name(slot_index):
    return f'Save {slot_index}'


def _slot_path(slot_index):
    return os.path.join(get_save_dir(), f'slot_{int(slot_index)}.json')


def save_slot(slot_index, game_data, save_name=None, days_lived=0):
    slot_index = int(slot_index)
    data = dict(DEFAULT_ACTION)
    if game_data:
        data.update(game_data)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_path = _slot_path(slot_index)
    existing = {}
    if os.path.exists(save_path):
        with open(save_path, 'r', encoding='utf-8') as save_file:
            existing = json.load(save_file)

    payload = {
        'slot_index': slot_index,
        'save_name': save_name or existing.get('save_name') or _slot_name(slot_index),
        'days_lived': int(days_lived),
        'created_at': existing.get('created_at') or timestamp,
        'last_saved_at': timestamp,
        'game_data': data,
    }

    with open(save_path, 'w', encoding='utf-8') as save_file:
        json.dump(payload, save_file, indent=2)

    return payload


def load_slot(slot_index):
    slot_index = int(slot_index)
    save_path = _slot_path(slot_index)
    if not os.path.exists(save_path):
        return {
            'slot_index': slot_index,
            'save_name': _slot_name(slot_index),
            'days_lived': 0,
            'created_at': None,
            'last_saved_at': None,
            'game_data': dict(DEFAULT_ACTION),
        }

    with open(save_path, 'r', encoding='utf-8') as save_file:
        data = json.load(save_file)

    return {
        'slot_index': data.get('slot_index', slot_index),
        'save_name': data.get('save_name') or _slot_name(slot_index),
        'days_lived': int(data.get('days_lived', data.get('daysCount', 0))),
        'created_at': data.get('created_at'),
        'last_saved_at': data.get('last_saved_at'),
        'game_data': data.get('game_data', dict(DEFAULT_ACTION)),
    }


def get_save_slot_summary(slot_index):
    slot_index = int(slot_index)
    save_path = _slot_path(slot_index)
    if not os.path.exists(save_path):
        return {
            'used': False,
            'name': _slot_name(slot_index),
            'days_lived': 0,
            'last_saved_at': None,
        }

    data = load_slot(slot_index)
    return {
        'used': True,
        'name': data.get('save_name') or _slot_name(slot_index),
        'days_lived': int(data.get('days_lived', 0)),
        'last_saved_at': data.get('last_saved_at'),
    }
