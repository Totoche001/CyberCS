import tkinter as tk
from tkinter import messagebox, ttk
import os
from fpdf import FPDF

CATEGORIES = ["CheatSheets", "Pentest", "Défense"]
FILENAMES = {
    "CheatSheets": "cheatsheets.txt",
    "Pentest": "pentest.txt",
    "Défense": "defense.txt"
}

class CheatSheetManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire d'Astuces Pentest & Défense")

        self.selected_category = tk.StringVar(value=CATEGORIES[0])

        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Catégorie :").grid(row=0, column=0)
        self.category_menu = ttk.Combobox(top_frame, values=CATEGORIES, textvariable=self.selected_category)
        self.category_menu.grid(row=0, column=1)
        self.category_menu.bind("<<ComboboxSelected>>", self.load_entries)

        tk.Label(top_frame, text="Recherche :").grid(row=0, column=2)
        self.search_entry = tk.Entry(top_frame)
        self.search_entry.grid(row=0, column=3)
        tk.Button(top_frame, text="🔍", command=self.search_entries).grid(row=0, column=4)

        self.entries_listbox = tk.Listbox(root, width=80, height=10)
        self.entries_listbox.pack(pady=5)
        self.entries_listbox.bind("<Double-Button-1>", self.display_entry_details)

        form_frame = tk.LabelFrame(root, text="Ajouter une nouvelle entrée", padx=10, pady=10)
        form_frame.pack(pady=5, fill="both", expand=True)

        tk.Label(form_frame, text="Titre :").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(form_frame, width=60)
        self.title_entry.grid(row=0, column=1, sticky="w")

        tk.Label(form_frame, text="Contenu :").grid(row=1, column=0, sticky="nw")
        self.content_text = tk.Text(form_frame, height=6, width=60)
        self.content_text.grid(row=1, column=1, sticky="w")

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Ajouter", command=self.add_entry).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Supprimer", command=self.delete_entry).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Supprimer tout", command=self.delete_all).grid(row=0, column=2, padx=5)

        self.load_entries()

    def get_current_filename(self):
        return FILENAMES[self.selected_category.get()]

    def load_entries(self, event=None):
        self.entries_listbox.delete(0, tk.END)
        filename = self.get_current_filename()
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|', 1)
                    if parts:
                        title = parts[0]
                        self.entries_listbox.insert(tk.END, title)


    def search_entries(self):
        query = self.search_entry.get().lower()
        self.entries_listbox.delete(0, tk.END)
        filename = self.get_current_filename()
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|', 1)
                    title = parts[0]
                    if query in title.lower():
                        self.entries_listbox.insert(tk.END, title)

    def display_entry_details(self, event):
        index = self.entries_listbox.curselection()
        if index:
            details_window = tk.Toplevel(self.root)
            details_window.title("Détails de l'entrée")
            details_window.geometry("600x400")

            filename = self.get_current_filename()
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if index[0] < len(lines):
                parts = lines[index[0]].strip().split('|', 1)
                title = parts[0]
                encoded_content = parts[1] if len(parts) > 1 else ""
                content = encoded_content.replace('\\n', '\n')  # décodage

                tk.Label(details_window, text="Titre :").pack(anchor="w", padx=5)
                title_entry = tk.Entry(details_window, width=60)
                title_entry.insert(0, title)
                title_entry.pack(padx=5, pady=(0, 10))

                tk.Label(details_window, text="Contenu :").pack(anchor="w", padx=5)
                content_text = tk.Text(details_window, height=10, width=60, wrap=tk.WORD)
                content_text.insert("1.0", content)
                content_text.pack(padx=5, pady=(0, 10))

                scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=content_text.yview)
                scrollbar.pack(side="right", fill="y")
                content_text.configure(yscrollcommand=scrollbar.set)

                def save_changes():
                    new_title = title_entry.get().strip()
                    new_content = content_text.get("1.0", tk.END).strip()

                    if not new_title or not new_content:
                        messagebox.showerror("Erreur", "Titre et contenu requis.")
                        return
                    
                    encoded_new_content = new_content.replace('\n', '\\n')
                    lines[index[0]] = f"{new_title}|{encoded_new_content}\n"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.load_entries()
                    details_window.destroy()
                    messagebox.showinfo("Succès", "Modifications enregistrées avec succès!")

                button_frame = tk.Frame(details_window)
                button_frame.pack(pady=5)
                
                tk.Button(button_frame, text="Enregistrer les modifications", command=save_changes).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Exporter en PDF", command=lambda: self.export_to_pdf()).pack(side=tk.LEFT, padx=5)
    def add_entry(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not title or not content:
            messagebox.showerror("Erreur", "Titre et contenu requis.")
            return

        # Remplacer les sauts de ligne par \n littéral
        encoded_content = content.replace('\n', '\\n')

        with open(self.get_current_filename(), 'a', encoding='utf-8') as f:
            f.write(f"{title}|{encoded_content}\n")

        self.load_entries()
        self.clear_fields()


    def delete_entry(self):
        index = self.entries_listbox.curselection()
        if not index:
            return
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette entrée ?"):
            filename = self.get_current_filename()
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            del lines[index[0]]
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.load_entries()
            self.clear_fields()

    def delete_all(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer toutes les entrées ?"):
            filename = self.get_current_filename()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("")
            self.load_entries()
            self.clear_fields()

    def clear_fields(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        
    def export_to_pdf(self):
        index = self.entries_listbox.curselection()
        if not index:
            messagebox.showinfo("Info", "Sélectionnez une entrée à exporter.")
            return
        filename = self.get_current_filename()
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        parts = lines[index[0]].strip().split('|')
        if len(parts) >= 2:
            pdf = FPDF('P', 'mm', 'A4')
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            pdf.cell(200, 10, txt=f"Catégorie : {self.selected_category.get()}".encode('latin-1', 'ignore').decode('latin-1'), ln=1)
            pdf.cell(200, 10, txt=f"Titre : {parts[0]}".encode('latin-1', 'ignore').decode('latin-1'), ln=1)
            content = parts[1].replace('\\n', '\n')
            pdf.multi_cell(0, 10, txt=f"Contenu :\n{content}".encode('latin-1', 'ignore').decode('latin-1'))
            safe_title = parts[0].replace(' ', '_').replace('/', '_')
            pdf.output(f"{safe_title}.pdf", 'F')
            messagebox.showinfo("Succès", f"Exporté sous {safe_title}.pdf")

    def export_all_to_pdf(self):
        category = self.selected_category.get()
        filename = self.get_current_filename()
        if not os.path.exists(filename):
            messagebox.showerror("Erreur", "Aucune entrée à exporter.")
            return
        pdf = FPDF('P', 'mm', 'A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, txt=f"Catégorie : {category}".encode('latin-1', 'ignore').decode('latin-1'), ln=1)
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(200, 10, txt=f"Titre : {parts[0]}".encode('latin-1', 'ignore').decode('latin-1'), ln=1)
                    pdf.set_font('Arial', '', 12)
                    content = parts[1].replace('\\n', '\n')
                    pdf.multi_cell(0, 10, txt=f"Contenu :\n{content}".encode('latin-1', 'ignore').decode('latin-1'))
                    pdf.cell(0, 10, txt="-------------------------------", ln=1)
        export_name = f"{category}_export.pdf"
        pdf.output(export_name, 'F')
        messagebox.showinfo("Succès", f"Toutes les entrées exportées dans {export_name}")
if __name__ == "__main__":
    root = tk.Tk()
    app = CheatSheetManager(root)
    root.mainloop()
