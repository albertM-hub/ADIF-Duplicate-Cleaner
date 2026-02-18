# ADIF Duplicate Cleaner 🧹

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

Un outil simple et efficace pour nettoyer vos fichiers de log radioamateurs (ADIF, HRD XML) des doublons.

## 📥 Téléchargement

[Télécharger la dernière version (.exe)](https://github.com/VOTRE_NOM_UTILISATEUR/adif-duplicate-cleaner/releases/latest)

## ✨ Fonctionnalités

- ✅ Supprime les doublons basés sur CALL + BAND + MODE + DATE + HEURE
- ✅ Compatible avec les fichiers ADIF (.adi, .adif) et HRD XML (.xml)
- ✅ Génère un fichier propre et un fichier de doublons
- ✅ Gère automatiquement les encodages (UTF-8, Latin-1)
- ✅ Interface graphique simple (pas besoin de ligne de commande)

## 🚀 Utilisation

1. **Téléchargez** l'exécutable (ou exécutez le script Python)
2. **Lancez** `ADIF_Duplicate_Cleaner.exe`
3. **Sélectionnez** votre fichier de log
4. **Récupérez** les fichiers générés :
   - `*_CLEAN.adi` : Vos QSO sans doublons
   - `*_DOUBLONS.adi` : Les doublons identifiés
   - `*_SANS_INDICATIF.adi` : QSO problématiques (si présents)

## 📋 Capture d'écran

![Capture d'écran](screenshots/demo.png)

## 🛠️ Installation pour les développeurs

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_NOM_UTILISATEUR/adif-duplicate-cleaner.git
cd adif-duplicate-cleaner

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python adif_cleaner.py

# Créer un exécutable
pip install pyinstaller
pyinstaller --onefile --windowed --name "ADIF_Cleaner" adif_cleaner.py