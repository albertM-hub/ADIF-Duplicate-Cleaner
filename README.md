# ADIF Duplicate Cleaner

## Description
Cet utilitaire est conçu pour les radioamateurs souhaitant nettoyer et organiser leurs carnets de trafic (logbooks). Il permet d'identifier et de supprimer automatiquement les doublons dans les fichiers de log, garantissant ainsi une base de données propre pour vos statistiques et vos futurs exports.

## Fonctionnalités principales
- **Multi-formats** : Supporte les fichiers standard ADIF (`.adi`, `.adif`) et les exports XML spécifiques de Ham Radio Deluxe (HRD).
- **Encodage Universel (UTF-8)** : Gère parfaitement les caractères spéciaux (comme le symbole `ƒ`) pour éviter toute perte de données lors du traitement.
- **Signature Intelligente** : Détecte les doublons en comparant l'indicatif (CALL), la bande (BAND), le mode (MODE) et la date/heure du contact.
- **Interface Graphique** : Utilisation simplifiée via une fenêtre Tkinter intuitive, sans ligne de commande complexe.

## Installation
1. Assurez-vous que **Python 3.x** est installé sur votre système.
2. Installez la bibliothèque nécessaire pour la gestion de l'ADIF via votre terminal :
   ```bash
   pip install adif_io
   Pour installer rapidement toutes les dépendances, utilisez :

pip install -r requirements.txt
---

## Contributions
Les contributions sont les bienvenues ! Si vous avez des idées d'amélioration ou si vous rencontrez un bug :
1. Ouvrez une **Issue** pour en discuter.
2. Proposez une **Pull Request** avec vos modifications.

Les retours d'utilisateurs de logiciels de log spécifiques (comme Ham Radio Deluxe) sont particulièrement appréciés pour continuer d'améliorer la compatibilité du script.

## Remerciements
- À la communauté radioamateur pour ses retours et tests.
- Aux développeurs de la bibliothèque `adif_io`.
- Un merci particulier pour l'aide apportée à la gestion des caractères spéciaux et des formats XML propriétaires.
