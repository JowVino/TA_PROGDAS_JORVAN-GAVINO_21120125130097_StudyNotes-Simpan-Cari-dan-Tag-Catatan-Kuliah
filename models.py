from datetime import datetime

class Note:
    def __init__(self, title, content="", tags="", course="",
                 created_at=None, updated_at=None, note_id=None):
        self.id = note_id
        self.title = title
        self.content = content
        self.tags = tags
        self.course = course
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")
        self.updated_at = updated_at or datetime.now().isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "course": self.course,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_db_row(cls, row):
        # row: (id, title, content, tags, course, created_at, updated_at)
        return cls(
            title=row[1],
            content=row[2],
            tags=row[3],
            course=row[4],
            created_at=row[5],
            updated_at=row[6],
            note_id=row[0]
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            tags=data.get("tags", ""),
            course=data.get("course", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            note_id=data.get("id"),
        )

    def __repr__(self):
        return f"<Note id={self.id} title={self.title!r}>"

def tags_to_list(tags_str):
    parts = tags_str.split(",")
    clean_list = []
    for t in parts:
        cleaned = t.strip()
        if cleaned == "":
            continue
        clean_list.append(cleaned.lower())
    return clean_list

def touch():
    return datetime.now().isoformat(timespec="seconds")
