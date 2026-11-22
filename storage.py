import json


def load_notes(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(
        not isinstance(note, str) or not note.strip() for note in data
    ):
        raise ValueError("Некорректный формат заметок")
    return data


def save_notes(path, notes):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


