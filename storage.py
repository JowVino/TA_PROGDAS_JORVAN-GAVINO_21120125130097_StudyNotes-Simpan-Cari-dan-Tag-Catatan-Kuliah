import sqlite3
from models import Note

class NoteStorage:
    def __init__(self, db_path="notes.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                tags TEXT,
                course TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            """
        )
        conn.commit()
        conn.close()

    # ---------- CREATE ----------
    def insert_note(self, note):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO notes (title, content, tags, course, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (note.title, note.content, note.tags, note.course,
             note.created_at, note.updated_at)
        )
        note_id = cur.lastrowid
        conn.commit()
        conn.close()
        note.id = note_id
        return note

    # ---------- READ ----------
    def get_all_notes(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, content, tags, course, created_at, updated_at
            FROM notes
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        conn.close()

        notes = []
        for row in rows:
            notes.append(Note.from_db_row(row))
        return notes

    def get_note_by_id(self, note_id):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, content, tags, course, created_at, updated_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )
        row = cur.fetchone()
        conn.close()
        if row is None:
            return None
        return Note.from_db_row(row)

    def search_notes(self, keyword):
        pattern = f"%{keyword}%"
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, content, tags, course, created_at, updated_at
            FROM notes
            WHERE title LIKE ?
               OR content LIKE ?
               OR tags LIKE ?
               OR course LIKE ?
            ORDER BY created_at DESC
            """,
            (pattern, pattern, pattern, pattern)
        )
        rows = cur.fetchall()
        conn.close()

        notes = []
        for row in rows:
            notes.append(Note.from_db_row(row))
        return notes

    # ---------- UPDATE ----------
    def update_note(self, note):
        if note.id is None:
            return
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE notes
            SET title = ?, content = ?, tags = ?, course = ?, created_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                note.title, note.content, note.tags, note.course,
                note.created_at, note.updated_at, note.id
            )
        )
        conn.commit()
        conn.close()

    # ---------- DELETE ----------
    def delete_note(self, note_id):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
