import tkinter as tk
from tkinter import ttk, messagebox

from manager import NoteManager
from storage import NoteStorage


class StudyNote(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("StudyNote - Note Saver with Search & Tag ")
        self.geometry("1000x600")

        self.storage = NoteStorage("notes.db")
        self.manager = NoteManager(self.storage)

        self.selected_note_id = None
        self.notes_for_list = []

        self._build_widgets()
        self._bind_shortcuts()
        self.refresh_note_list()

    # ================== Build UI ==================
    def _build_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Kiri: form
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Kanan: list + search + preview
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Form input (kiri) ---
        ttk.Label(left_frame, text="Judul:").pack(anchor="w")
        self.title_entry = ttk.Entry(left_frame)
        self.title_entry.pack(fill=tk.X, pady=2)

        ttk.Label(left_frame, text="Mata Kuliah:").pack(anchor="w")
        self.course_entry = ttk.Entry(left_frame)
        self.course_entry.pack(fill=tk.X, pady=2)

        ttk.Label(left_frame, text="Tag (pisahkan dengan koma):").pack(anchor="w")
        self.tags_entry = ttk.Entry(left_frame)
        self.tags_entry.pack(fill=tk.X, pady=2)

        ttk.Label(left_frame, text="Isi Catatan:").pack(anchor="w")
        self.content_text = tk.Text(
            left_frame,
            height=15,
            undo=True,
            autoseparators=True,
            maxundo=100
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=2)

        # Tombol aksi
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Tambah", command=self.on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Update", command=self.on_update).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Hapus", command=self.on_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=2)

        # Undo/Redo aksi
        history_frame = ttk.Frame(left_frame)
        history_frame.pack(fill=tk.X, pady=5)

        ttk.Button(history_frame, text="Undo Aksi", command=self.on_undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(history_frame, text="Redo Aksi", command=self.on_redo).pack(side=tk.LEFT, padx=2)

        # --- Kanan: search + list + preview ---
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Cari", command=self.on_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Tampilkan Semua", command=self.refresh_note_list).pack(side=tk.LEFT, padx=2)

        # Listbox + scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.note_listbox = tk.Listbox(list_frame)
        self.note_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.count_label = ttk.Label(right_frame, text="")
        self.count_label.pack(anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.note_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.note_listbox.config(yscrollcommand=scrollbar.set)

        self.note_listbox.bind("<<ListboxSelect>>", self.on_note_selected)

        # Preview
        ttk.Label(right_frame, text="Preview:").pack(anchor="w")
        self.preview_text = tk.Text(right_frame, height=10, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

    # ================== Shortcuts ==================
    def _bind_shortcuts(self):
        # Ctrl+Z/Y hanya untuk teks isi catatan
        self.content_text.bind("<Control-z>", self.on_text_undo)
        self.content_text.bind("<Control-y>", self.on_text_redo)

    def on_text_undo(self, event=None):
        try:
            self.content_text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def on_text_redo(self, event=None):
        try:
            self.content_text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    # ================== Helper UI ==================
    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.course_entry.delete(0, tk.END)
        self.tags_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.selected_note_id = None
        self.note_listbox.selection_clear(0, tk.END)
        self._set_preview("")

    def _set_preview(self, text):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.config(state=tk.DISABLED)

    def refresh_note_list(self, notes=None):
        if notes is None:
            notes = self.manager.get_all_notes()

        self.note_listbox.delete(0, tk.END)
        for n in notes:
            display = f"{n.title} [{n.course}] ({n.tags})"
            self.note_listbox.insert(tk.END, display)

        self.notes_for_list = notes
        self._set_preview("")
        self.selected_note_id = None
        self.count_label.config(text=f"Total: {len(notes)} catatan")

    def _get_form_data(self):
        title = self.title_entry.get().strip()
        course = self.course_entry.get().strip()
        tags = self.tags_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        return title, course, tags, content

    # ================== Event Handler ==================
    def on_add(self):
        title, course, tags, content = self._get_form_data()
        if not title:
            messagebox.showwarning("Validasi", "Judul tidak boleh kosong.")
            return

        self.manager.add_note(title=title, content=content, tags=tags, course=course)
        self.refresh_note_list()
        self.clear_form()
        messagebox.showinfo("Info", "Catatan berhasil ditambahkan.")

    def on_update(self):
        if self.selected_note_id is None:
            messagebox.showwarning("Info", "Pilih catatan terlebih dahulu.")
            return

        title, course, tags, content = self._get_form_data()
        if not title:
            messagebox.showwarning("Validasi", "Judul tidak boleh kosong.")
            return

        updated = self.manager.edit_note(
            note_id=self.selected_note_id,
            title=title,
            content=content,
            tags=tags,
            course=course,
        )
        if updated is None:
            messagebox.showerror("Error", "Gagal meng-update catatan.")
            return

        self.refresh_note_list()
        messagebox.showinfo("Info", "Catatan berhasil di-update.")

    def on_delete(self):
        if self.selected_note_id is None:
            messagebox.showwarning("Info", "Pilih catatan yang akan dihapus.")
            return

        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus catatan ini?"):
            return

        success = self.manager.delete_note(self.selected_note_id)
        if not success:
            messagebox.showerror("Error", "Gagal menghapus catatan.")
            return

        self.refresh_note_list()
        self.clear_form()
        messagebox.showinfo("Info", "Catatan berhasil dihapus.")

    def on_search(self):
        keyword = self.search_entry.get().strip()
        notes = self.manager.search_notes(keyword)
        self.refresh_note_list(notes)

    def on_note_selected(self, event):
        selection = self.note_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < 0 or idx >= len(self.notes_for_list):
            return

        note = self.notes_for_list[idx]
        self.selected_note_id = note.id

        # Tampilkan ke form
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, note.title)

        self.course_entry.delete(0, tk.END)
        self.course_entry.insert(0, note.course)

        self.tags_entry.delete(0, tk.END)
        self.tags_entry.insert(0, note.tags)

        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, note.content)

        # Preview
        preview = (
            f"Judul : {note.title}\n"
            f"Mata Kuliah : {note.course}\n"
            f"Tag : {note.tags}\n"
            f"Dibuat : {note.created_at}\n"
            f"Diupdate : {note.updated_at}\n\n"
            f"{note.content}"
        )
        self._set_preview(preview)

    def on_undo(self):
        ok = self.manager.undo()
        if not ok:
            messagebox.showinfo(
                "Undo",
                "Tidak ada aksi (tambah/edit/hapus) untuk di-undo."
            )
        self.refresh_note_list()

    def on_redo(self):
        ok = self.manager.redo()
        if not ok:
            messagebox.showinfo(
                "Redo",
                "Tidak ada aksi (tambah/edit/hapus) untuk di-redo."
            )
        self.refresh_note_list()


if __name__ == "__main__":
    app = StudyNote()
    app.mainloop()
