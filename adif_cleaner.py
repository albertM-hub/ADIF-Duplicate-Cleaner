import adif_io
import tkinter as tk
from tkinter import filedialog, messagebox

def write_adif(filename, qso_list, header_obj):
    """Génère le fichier ADIF en gérant correctement l'objet Header."""
    with open(filename, "w", encoding="latin-1") as f:
        # On convertit l'objet Header en texte proprement
        header_text = str(header_obj)
        if "<EOH>" not in header_text.upper():
            f.write(f"{header_text}\n<EOH>\n\n")
        else:
            f.write(f"{header_text}\n\n")
            
        for qso in qso_list:
            line = ""
            for field, value in qso.items():
                if value is not None:
                    val_str = str(value)
                    line += f"<{field}:{len(val_str)}>{val_str} "
            f.write(line + "<EOR>\n")

def process_file():
    input_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier ADIF",
        filetypes=[("Fichiers ADIF", "*.adi *.adif"), ("Tous les fichiers", "*.*")]
    )
    
    if not input_path:
        return

    try:
        # Lecture avec l'encodage latin-1 pour éviter l'erreur 'utf-8'
        with open(input_path, 'r', encoding='latin-1') as adif_file:
            adif_content = adif_file.read()
            qsos, header = adif_io.read_from_string(adif_content)

        unique_qsos = []
        duplicate_qsos = []
        seen_signatures = set()

        for qso in qsos:
            # Création d'une empreinte unique pour chaque contact
            call = str(qso.get('CALL', '')).upper().strip()
            date = str(qso.get('QSO_DATE', '')).strip()
            time = str(qso.get('TIME_ON', ''))[:4]
            band = str(qso.get('BAND', '')).upper().strip()
            mode = str(qso.get('MODE', '')).upper().strip()

            signature = f"{call}|{date}|{time}|{band}|{mode}"

            if signature in seen_signatures:
                duplicate_qsos.append(qso)
            else:
                seen_signatures.add(signature)
                unique_qsos.append(qso)

        # Sauvegarde sur le bureau ou dans le dossier source
        base_path = input_path.rsplit('.', 1)[0]
        write_adif(f"{base_path}_CLEAN.adi", unique_qsos, header)
        
        result_msg = f"Succès !\n\n- Contacts uniques : {len(unique_qsos)}\n- Doublons retirés : {len(duplicate_qsos)}"
        
        if duplicate_qsos:
            write_adif(f"{base_path}_DOUBLONS.adi", duplicate_qsos, header)
            result_msg += f"\n\nLes fichiers '_CLEAN' et '_DOUBLONS' ont été créés."

        messagebox.showinfo("Résultat du traitement", result_msg)

    except Exception as e:
        messagebox.showerror("Erreur technique", f"Détails de l'erreur :\n{e}")

# --- Fenêtre principale ---
root = tk.Tk()
root.title("ADIF Duplicate Cleaner")
root.geometry("400x180")

tk.Label(root, text="Nettoyeur de doublons pour Logbook", font=("Arial", 10, "bold"), pady=20).pack()
tk.Button(root, text="Choisir le fichier .adi", command=process_file, bg="#2E7D32", fg="white", font=("Arial", 10), padx=20, pady=10).pack()

root.mainloop()