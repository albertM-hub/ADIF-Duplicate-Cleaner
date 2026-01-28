import adif_io
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

def write_adif(filename, qso_list, header_obj):
    """Génère le fichier ADIF final en UTF-8 pour accepter tous les caractères."""
    with open(filename, "w", encoding="utf-8") as f:
        header_text = str(header_obj) if header_obj else "ADIF Duplicate Cleaner Export"
        f.write(f"{header_text}\n<EOH>\n\n")
        for qso in qso_list:
            line = ""
            for field, value in qso.items():
                if value is not None:
                    val_str = str(value)
                    val_str = val_str.replace('\r', ' ').replace('\n', ' ')
                    # Calcul de la longueur en octets pour UTF-8
                    line += f"<{field}:{len(val_str.encode('utf-8'))}>{val_str} "
            f.write(line + "<EOR>\n")

def read_xml_log(filename):
    """Lit un fichier XML (Standard ou HRD) et extrait les données."""
    tree = ET.parse(filename)
    root = tree.getroot()
    qsos = []
    # Recherche des enregistrements (HRD utilise 'Record', d'autres 'record')
    records = root.findall('.//Record') or root.findall('.//record')
    for record in records:
        qso_dict = {}
        # Lecture des attributs (format spécifique à Ham Radio Deluxe)
        for attr_name, attr_value in record.attrib.items():
            key = attr_name.upper().replace('COL_', '')
            qso_dict[key] = attr_value
        # Lecture des balises enfants (format XML standard)
        for child in record:
            key = child.tag.upper().replace('COL_', '')
            qso_dict[key] = child.text
        if qso_dict: qsos.append(qso_dict)
    return qsos

def process_file():
    input_path = filedialog.askopenfilename(
        title="Sélectionnez votre fichier (ADIF ou HRD XML)",
        filetypes=[("Logs Radio", "*.adi *.adif *.xml"), ("Tous les fichiers", "*.*")]
    )
    if not input_path: return
    try:
        is_xml = input_path.lower().endswith('.xml')
        if is_xml:
            qsos = read_xml_log(input_path)
            header = "Source: HRD XML Import"
        else:
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    adif_content = f.read()
            except:
                with open(input_path, 'r', encoding='latin-1') as f:
                    adif_content = f.read()
            qsos, header = adif_io.read_from_string(adif_content)

        if not qsos:
            messagebox.showwarning("Attention", "Aucun contact trouvé dans le fichier.")
            return

        unique_qsos = []
        duplicate_qsos = []
        seen_signatures = set()

        for qso in qsos:
            call = str(qso.get('CALL', '')).upper().strip()
            band = str(qso.get('BAND', '')).upper().strip()
            mode = str(qso.get('MODE', '')).upper().strip()
            # On utilise les 8 premiers caractères de TIME_ON pour la signature (date + début heure)
            raw_time = str(qso.get('TIME_ON', '')).replace('-', '').replace(':', '').strip()
            signature = f"{call}|{band}|{mode}|{raw_time[:8]}"

            if signature in seen_signatures:
                duplicate_qsos.append(qso)
            else:
                seen_signatures.add(signature)
                unique_qsos.append(qso)

        base_path = input_path.rsplit('.', 1)[0]
        write_adif(f"{base_path}_CLEAN.adi", unique_qsos, header)
        msg = f"Succès !\n\n- Total traités : {len(qsos)}\n- Uniques : {len(unique_qsos)}\n- Doublons : {len(duplicate_qsos)}"
        if duplicate_qsos:
            write_adif(f"{base_path}_DOUBLONS.adi", duplicate_qsos, header)
            msg += "\n\nFichiers '_CLEAN' et '_DOUBLONS' créés sur votre disque."
        messagebox.showinfo("Résultat du traitement", msg)
    except Exception as e:
        messagebox.showerror("Erreur technique", f"Détails :\n{e}")

# --- Fenêtre principale ---
root = tk.Tk()
root.title("ADIF & HRD Duplicate Cleaner - v2.0")
root.geometry("500x320")
root.configure(padx=20, pady=20)

tk.Label(root, text="ADIF Duplicate Cleaner", font=("Arial", 14, "bold")).pack()
description = (
    "Cet utilitaire identifie et supprime les doublons dans vos carnets de trafic.\n"
    "Compatible avec les exports ADIF standards et Ham Radio Deluxe (XML)."
)
tk.Label(root, text=description, font=("Arial", 10), pady=10, justify="center").pack()

frame_info = tk.LabelFrame(root, text=" Informations ", padx=10, pady=10)
frame_info.pack(fill="both", expand="yes", pady=10)
tk.Label(frame_info, text="• Formats acceptés : .adi, .adif, .xml", font=("Arial", 9)).pack(anchor="w")
tk.Label(frame_info, text="• Format de sortie : ADIF (.adi) en UTF-8", font=("Arial", 9)).pack(anchor="w")
tk.Label(frame_info, text="• Signature : CALL, BAND, MODE, DATE/HEURE", font=("Arial", 9)).pack(anchor="w")

tk.Button(
    root, text="SÉLECTIONNER UN FICHIER ET NETTOYER", command=process_file, 
    bg="#0056b3", fg="white", font=("Arial", 10, "bold"), padx=20, pady=10, cursor="hand2"
).pack(pady=10)

tk.Label(root, text="Développé pour la communauté radioamateur", fg="gray", font=("Arial", 8)).pack(side="bottom")
root.mainloop()