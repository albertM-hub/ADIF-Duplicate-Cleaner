import adif_io
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os

def write_adif(filename, qso_list, header_obj=None):
    """Génère le fichier ADIF final en UTF-8 pour accepter tous les caractères."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            header_text = str(header_obj) if header_obj else "ADIF Duplicate Cleaner Export"
            f.write(f"{header_text}\n<EOH>\n\n")
            for qso in qso_list:
                line = ""
                for field, value in qso.items():
                    if value is not None and value != "":
                        val_str = str(value)
                        val_str = val_str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
                        # Supprimer les espaces multiples
                        val_str = ' '.join(val_str.split())
                        if val_str:  # N'ajouter que si la valeur n'est pas vide
                            # Calcul de la longueur en octets pour UTF-8
                            line += f"<{field}:{len(val_str.encode('utf-8'))}>{val_str} "
                if line:  # On évite d'écrire une ligne vide
                    f.write(line + "<EOR>\n")
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {filename}: {e}")
        return False

def read_xml_log(filename):
    """Lit un fichier XML (Standard ou HRD) et extrait les données."""
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        qsos = []
        
        # Recherche des enregistrements (différents formats possibles)
        records = root.findall('.//Record') or root.findall('.//record') or root.findall('.//RECORD')
        
        # Si pas de records, chercher directement les QSOs
        if not records:
            qso_elements = root.findall('.//QSO') or root.findall('.//qso')
            if qso_elements:
                records = qso_elements
        
        for record in records:
            qso_dict = {}
            
            # Lecture des attributs (format spécifique à Ham Radio Deluxe)
            for attr_name, attr_value in record.attrib.items():
                key = attr_name.upper().replace('COL_', '').replace('_', '')
                if attr_value:
                    qso_dict[key] = attr_value.strip()
            
            # Lecture des balises enfants (format XML standard)
            for child in record:
                key = child.tag.upper().replace('COL_', '').replace('_', '')
                if child.text and child.text.strip():
                    qso_dict[key] = child.text.strip()
            
            if qso_dict:
                qsos.append(qso_dict)
        
        return qsos
    except ET.ParseError as e:
        raise Exception(f"Erreur de parsing XML : {e}")
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier XML : {e}")

def normalize_time(time_value):
    """Normalise le format de l'heure pour la signature."""
    if not time_value:
        return ""
    # Enlever les séparateurs et ne garder que les chiffres
    time_str = ''.join(c for c in str(time_value) if c.isdigit())
    # Retourner les 6 premiers caractères (HHMMSS) ou moins si pas assez
    return time_str[:6]

def create_signature(qso):
    """Crée une signature unique pour identifier un QSO."""
    call = str(qso.get('CALL', '')).upper().strip()
    band = str(qso.get('BAND', '')).upper().strip()
    mode = str(qso.get('MODE', '')).upper().strip()
    date = str(qso.get('QSO_DATE', qso.get('DATE', ''))).strip()
    time = normalize_time(qso.get('TIME_ON', qso.get('TIME', '')))
    
    # Si pas de QSO_DATE, essayer de construire à partir de DATE_OFF, etc.
    if not date:
        date = str(qso.get('DATE_OFF', '')).strip() or str(qso.get('DATE_ON', '')).strip()
    
    # Nettoyer la date (enlever les tirets, etc.)
    date = ''.join(c for c in date if c.isdigit())[:8]
    
    # Créer la signature avec les éléments disponibles
    signature_parts = [call, band, mode]
    if date:
        signature_parts.append(date)
    if time:
        signature_parts.append(time)
    
    return '|'.join(signature_parts)

def process_file():
    try:
        input_path = filedialog.askopenfilename(
            title="Sélectionnez votre fichier (ADIF ou HRD XML)",
            filetypes=[("Logs Radio", "*.adi *.adif *.xml *.adx"), ("Tous les fichiers", "*.*")]
        )
        if not input_path:
            return
            
        # Vérifier si le fichier existe
        if not os.path.exists(input_path):
            messagebox.showerror("Erreur", "Le fichier sélectionné n'existe pas.")
            return
            
        is_xml = input_path.lower().endswith('.xml') or input_path.lower().endswith('.adx')
        
        if is_xml:
            qsos = read_xml_log(input_path)
            header = "Source: HRD XML Import"
        else:
            # Lecture du fichier ADIF
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                qsos = adif_io.read_from_string(content)[0]
                header = "Source: ADIF Import"
            except UnicodeDecodeError:
                # Essayer avec latin-1 si utf-8 échoue
                with open(input_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                qsos = adif_io.read_from_string(content)[0]
                header = "Source: ADIF Import (Latin-1)"

        if not qsos:
            messagebox.showwarning("Attention", "Aucun contact trouvé dans le fichier.")
            return

        unique_qsos = []
        duplicate_qsos = []
        seen_signatures = set()
        ambiguous_qsos = []  # QSOs sans CALL (impossible à traiter)

        for qso in qsos:
            # Vérifier si le QSO a un indicatif
            if not qso.get('CALL'):
                ambiguous_qsos.append(qso)
                continue
                
            signature = create_signature(qso)

            if signature in seen_signatures:
                duplicate_qsos.append(qso)
            else:
                seen_signatures.add(signature)
                unique_qsos.append(qso)

        # Générer les noms de fichiers de sortie
        base_path = input_path.rsplit('.', 1)[0]
        
        # Écrire les fichiers de sortie
        success = True
        if not write_adif(f"{base_path}_CLEAN.adi", unique_qsos, header):
            success = False
        
        if duplicate_qsos and not write_adif(f"{base_path}_DOUBLONS.adi", duplicate_qsos, header):
            success = False
            
        if ambiguous_qsos and not write_adif(f"{base_path}_SANS_INDICATIF.adi", ambiguous_qsos, header):
            success = False

        # Préparer le message de résultat
        msg_parts = []
        msg_parts.append(f"✅ Total traités : {len(qsos)}")
        msg_parts.append(f"✅ Uniques : {len(unique_qsos)}")
        msg_parts.append(f"⚠️  Doublons : {len(duplicate_qsos)}")
        
        if ambiguous_qsos:
            msg_parts.append(f"❌ Sans indicatif : {len(ambiguous_qsos)}")
        
        msg_parts.append("")
        
        if success:
            if unique_qsos:
                msg_parts.append("📁 Fichier '_CLEAN.adi' créé")
            if duplicate_qsos:
                msg_parts.append("📁 Fichier '_DOUBLONS.adi' créé")
            if ambiguous_qsos:
                msg_parts.append("📁 Fichier '_SANS_INDICATIF.adi' créé")
            msg_parts.append("")
            msg_parts.append("Tous les fichiers sont en UTF-8")
        else:
            msg_parts.append("⚠️  Attention : Certains fichiers n'ont pas pu être créés")

        messagebox.showinfo("Résultat du traitement", "\n".join(msg_parts))
        
    except Exception as e:
        messagebox.showerror("Erreur technique", f"Une erreur est survenue :\n\n{str(e)}")

# --- Fenêtre principale ---
root = tk.Tk()
root.title("ADIF & HRD Duplicate Cleaner - v2.1")
root.geometry("550x350")
root.configure(padx=20, pady=20)

# Style
root.option_add('*Font', 'Arial 10')

tk.Label(root, text="🧹 ADIF Duplicate Cleaner", font=("Arial", 16, "bold")).pack()

description = (
    "Identifie et supprime les doublons dans vos carnets de trafic.\n"
    "Compatible avec ADIF standard et Ham Radio Deluxe (XML)."
)
tk.Label(root, text=description, font=("Arial", 10), pady=10, justify="center").pack()

frame_info = tk.LabelFrame(root, text=" ℹ️  Informations ", padx=15, pady=10)
frame_info.pack(fill="both", expand="yes", pady=10)

info_items = [
    "• Formats acceptés : .adi, .adif, .xml, .adx",
    "• Format de sortie : ADIF (.adi) en UTF-8",
    "• Signature : CALL + BAND + MODE + DATE + HEURE",
    "• Gère les QSO sans indicatif (fichier séparé)"
]

for item in info_items:
    tk.Label(frame_info, text=item, font=("Arial", 9), anchor="w").pack(anchor="w", pady=2)

tk.Button(
    root, 
    text="📂 SÉLECTIONNER UN FICHIER ET NETTOYER", 
    command=process_file, 
    bg="#0056b3", 
    fg="white", 
    font=("Arial", 11, "bold"), 
    padx=20, 
    pady=12, 
    cursor="hand2",
    activebackground="#003d80",
    activeforeground="white"
).pack(pady=15)

tk.Label(root, text="Développé pour la communauté radioamateur - 73", 
         fg="gray", font=("Arial", 8)).pack(side="bottom")

root.mainloop()