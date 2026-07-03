import json
import os


def load_json(path):
    """JSON 파일을 읽어 list[dict]를 반환한다.
    파일이 없거나 잘못된 형식이면 빈 리스트를 반환한다.
    """
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(path, data):
    """list[dict]를 JSON 파일로 저장한다."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)