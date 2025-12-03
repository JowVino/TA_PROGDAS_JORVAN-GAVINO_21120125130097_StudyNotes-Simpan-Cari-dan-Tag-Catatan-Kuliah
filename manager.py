from models import Note, touch
from storage import NoteStorage

class NoteManager:
    def __init__(self, storage):
        self.storage = storage
        self.undo_stack = []   # untuk Modul 7 (Stack)
        self.redo_stack = []   # stack kedua untuk redo

    # ---------- Akses data ----------
    def get_all_notes(self):
        return self.storage.get_all_notes()

    def search_notes(self, keyword):
        if not keyword:
            return self.get_all_notes()
        return self.storage.search_notes(keyword)

    # ---------- Operasi utama (mencatat history) ----------
    def add_note(self, title, content, tags, course):
        note = Note(title=title, content=content, tags=tags, course=course)
        note = self.storage.insert_note(note)

        cmd = {
            "action": "add",
            "data": note.to_dict(),  # simpan snapshot
        }
        self.undo_stack.append(cmd)
        self.redo_stack.clear()
        return note

    def edit_note(self, note_id, title, content, tags, course):
        old_note = self.storage.get_note_by_id(note_id)
        if old_note is None:
            return None

        new_note = Note(
            title=title,
            content=content,
            tags=tags,
            course=course,
            created_at=old_note.created_at,
            updated_at=touch(),
            note_id=old_note.id
        )
        self.storage.update_note(new_note)

        cmd = {
            "action": "edit",
            "old": old_note.to_dict(),
            "new": new_note.to_dict(),
        }
        self.undo_stack.append(cmd)
        self.redo_stack.clear()
        return new_note

    def delete_note(self, note_id):
        note = self.storage.get_note_by_id(note_id)
        if note is None:
            return False

        self.storage.delete_note(note_id)

        cmd = {
            "action": "delete",
            "data": note.to_dict(),
        }
        self.undo_stack.append(cmd)
        self.redo_stack.clear()
        return True

    # ---------- UNDO / REDO ----------
    def undo(self):
        if not self.undo_stack:
            return False

        cmd = self.undo_stack.pop()

        if cmd["action"] == "add":
            # undo add = hapus note
            data = cmd["data"]
            note_id = data.get("id")
            if note_id is not None:
                self.storage.delete_note(note_id)

        elif cmd["action"] == "delete":
            # undo delete = tambah lagi note
            data = cmd["data"]
            data["id"] = None  # biar dapat id baru
            note = Note.from_dict(data)
            note = self.storage.insert_note(note)
            # update id terbaru ke command
            cmd["data"]["id"] = note.id

        elif cmd["action"] == "edit":
            # undo edit = balikin ke old
            old_data = cmd["old"]
            old_note = Note.from_dict(old_data)
            self.storage.update_note(old_note)

        self.redo_stack.append(cmd)
        return True

    def redo(self):
        if not self.redo_stack:
            return False

        cmd = self.redo_stack.pop()

        if cmd["action"] == "add":
            # redo add = tambah lagi
            data = cmd["data"]
            data["id"] = None
            note = Note.from_dict(data)
            note = self.storage.insert_note(note)
            cmd["data"]["id"] = note.id

        elif cmd["action"] == "delete":
            # redo delete = hapus lagi
            data = cmd["data"]
            note_id = data.get("id")
            if note_id is not None:
                self.storage.delete_note(note_id)

        elif cmd["action"] == "edit":
            # redo edit = terapkan new lagi
            new_data = cmd["new"]
            new_note = Note.from_dict(new_data)
            self.storage.update_note(new_note)

        self.undo_stack.append(cmd)
        return True
