<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** est une application de bureau pour créer et éditer des **arrière-plans Game Boy Advance (GBA)**. Elle permet de convertir des images en tilesets et tilemaps compatibles GBA, d'éditer visuellement les tuiles et les palettes, et d'exporter des assets prêts à l'emploi pour vos projets GBA.

> ⚠️ Cette application est conçue pour les développeurs, ROM hackers et pixel artists qui ont besoin d'un contrôle précis sur les arrière-plans GBA.

---

## 🌐 Traductions

Ce README est disponible dans les langues suivantes :

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Fonctionnalités

- **Conversion d'image vers GBA**
  - Convertit des images standard en tilesets et tilemaps compatibles GBA.
  - Configure la taille de sortie et la profondeur de couleur (4bpp et 8bpp).
  - Aperçu du résultat avant l'exportation.

- **Édition de Tileset**
  - Sélection et édition visuelle des tuiles.
  - Outils de dessin interactifs sur la grille de la tilemap.
  - Niveaux de zoom de 100% à 800% pour une édition pixel par pixel.

- **Édition de Palettes**
  - Édition jusqu'à 256 couleurs par palette.
  - Synchronisation des modifications de palette avec les aperçus et les tuiles.
  - Réorganisation, remplacement ou ajustement des couleurs individuelles.

- **Onglet Aperçu**
  - Visualisation de l'arrière-plan final sur un écran similaire à la GBA.
  - Validation rapide des configurations de tuiles et de palettes.

- **Historique Annuler/Rétablir**
  - Suivi complet de l'historique des modifications.
  - Opérations d'annulation et de rétablissement avec un large tampon d'historique.

- **Interface et barre d'état configurables**
  - Barre d'état détaillée avec sélection de tuile, coordonnées de la tilemap, ID de palette, état de miroir et niveau de zoom.
  - Barre d'outils contextuelle par onglet (aperçu, tuiles, palettes).

- **Support multilingue**
  - Système de traduction interne (Translator) avec sélection de langue via les paramètres.
  - Conçu pour prendre en charge plusieurs langues dans l'interface.

---

## 🖼️ Captures d'écran

<p align="center"><img width="896" height="590" src="../assets/readme/fra_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="946" height="676" src="../assets/readme/fra_preview.png" alt="Image" /></p>

<p align="center"><img width="946" height="676" src="../assets/readme/fra_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="946" height="676" src="../assets/readme/fra_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Description de l'Architecture

GBA Background Studio est construit avec **Python** et **PySide6 / PySide2** (hybride), suivant une conception d'interface modulaire :

- **Fenêtre principale (`GBABackgroundStudio`)**
  - Gère l'état de l'application (BPP actuel, niveau de zoom, sélection de tuile et de palette).
  - Héberge les onglets principaux et la barre d'état personnalisée.
  - Charge et applique la configuration (y compris la dernière session de sortie).

- **Onglets**
  - `PreviewTab` – Aperçu de l'arrière-plan dans le style GBA.
  - `EditTilesTab` – Outils d'édition de tuiles et de tilemap.
  - `EditPalettesTab` – Éditeur de palettes et outils de manipulation des couleurs.

- **Composants et utilitaires de l'interface**
  - `MenuBar` – Opérations de fichier (ouvrir une image, exporter des fichiers, quitter) et actions de l'éditeur.
  - `CustomGraphicsView` – `QGraphicsView` étendu avec interaction basée sur les tuiles (survol, dessin, sélection, aperçu de collage).
  - `TilemapUtils` – Logique partagée pour l'interaction et la sélection de la tilemap.
  - `HistoryManager` – Gestion de l'annulation/rétablissement pour les opérations de l'éditeur.
  - `HoverManager`, `GridManager` – Aides visuelles pour les effets de survol et les superpositions de grille.
  - `Translator`, `ConfigManager` – Localisation et configuration persistante.

---

## 📦 Installation

### Option 1 — Installateur (recommandé)

Téléchargez la dernière version depuis [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases) :

| Installateur | Python | OS |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | Inclus (aucune installation requise) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | Inclus (aucune installation requise) | Windows 7 / 8 / 8.1 |

Il suffit de lancer l'installateur et de démarrer l'application — aucun Python ni pip requis.

---

### Option 2 — Exécuter depuis les sources

#### Configuration requise

| Environnement | Python | Backend Qt | OS |
|---|---|---|---|
| **Moderne** | 3.10+ | PySide6 (auto) | Windows 10/11, macOS 11+, Linux |
| **Legacy** | 3.8 / 3.9 | PySide2 5.15.2 (auto) | Windows 7 / 8 / 8.1 |

L'application détecte automatiquement quel backend Qt utiliser selon votre version de Python — aucune configuration manuelle requise.

#### Dépendances

```bash
pip install -r requirements.txt
```

`requirements.txt` installe automatiquement le bon backend Qt :
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

Autres dépendances : `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ Support pour les Systèmes Legacy (Windows 7 / 8 / 8.1)

L'interface graphique complète fonctionne sur Windows 7 et versions ultérieures. Utilisez **Python 3.8** et `requirements.txt` installera automatiquement **PySide2 5.15.2**.

Alternativement, l'**Assistant en Ligne de Commande Multilingue** (`GBA_Studio_Wizard.bat`) est disponible pour les conversions par lot sans l'interface graphique, et fonctionne sur toute version de Windows avec Python 3.8+ :

1. Naviguez jusqu'à la racine du projet.
2. Exécutez **`GBA_Studio_Wizard.bat`**.
3. Sélectionnez votre langue (18 langues supportées).
4. Suivez les instructions étape par étape pour convertir votre image.

---

## 🚀 Démarrage Rapide

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Créer et activer un environnement virtuel** (optionnel mais recommandé)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Sous Windows : .venv\Scripts\activate
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**

   ```bash
   python main.py
   ```

---

## 🧭 Utilisation de Base

1. **Ouvrir une Image**
   - Allez dans **Fichier → Ouvrir une image** ou appuyez sur `Ctrl+O`.
   - Sélectionnez l'image que vous souhaitez convertir en arrière-plan GBA.

2. **Configurer la Conversion**
   - Sélectionnez le **Mode BG** (**Mode Texte** ou **Rotation/Mise à l'échelle**).
   - Choisissez la ou les palette(s) ou la Tilemap à utiliser (uniquement pour le **Mode Texte 4bpp**).
   - Définissez la couleur qui sera utilisée comme transparente.
   - Ajustez la taille de sortie et les autres paramètres nécessaires.
   - Cliquez sur **Convertir** et l'application s'occupe du reste.

3. **Éditer Tuiles**
   - Passez à l'onglet **Éditer Tuiles**.
   - Utilisez la vue de la tilemap pour dessiner et modifier des tuiles individuelles.
   - Sélectionnez des zones entières pour copier, couper, coller ou faire pivoter des groupes de tuiles.
   - Synchronisez les modifications en temps réel pour des résultats instantanés.
   - Ajustez le niveau de **Zoom** pour une précision parfaite.
   - Optimiser/Désoptimiser les tuiles pour économiser de l'espace ou garantir la compatibilité matérielle.
   - Convertir les assets entre les formats **4bpp** et **8bpp**.
   - Basculer entre le **Mode Texte** et la **Rotation/Mise à l'échelle** sans problème.

4. **Éditer Palettes**
   - Allez à l'onglet **Éditer Palettes**.
   - Modifiez les couleurs dans la grille de palettes et ajustez-les avec l'éditeur de couleurs.
   - Sélectionnez des zones spécifiques ou toutes les tuiles appartenant à une palette pour les remplacer ou les échanger avec une autre.

5. **Aperçu de l'Arrière-plan**
   - Passez à l'onglet **Aperçu** pour une représentation fidèle de l'apparence sur un vrai GBA.
   - Vérifiez que vos configurations de tuiles et de palettes fonctionnent parfaitement ensemble.

6. **Exporter les Assets**
   - Allez dans **Fichier → Exporter les fichiers** ou appuyez sur `Ctrl+E`.
   - Exportez les tilesets, tilemaps et palettes dans des formats prêts à être intégrés dans votre chaîne d'outils de développement GBA.
   - Exportez des assets individuels séparément depuis leurs menus respectifs si nécessaire.

---

## 🔄 Annuler/Rétablir

L'application suit vos actions d'édition avec un **gestionnaire d'historique** :

- **Annuler** – annule la dernière opération.
- **Rétablir** – réapplique une opération annulée.

Le système d'historique maintient un tampon d'états récents, incluant les modifications de tuiles, les changements de palette et les opérations de tilemap.

---

## ⚙️ Configuration et Localisation

### Configuration

L'application utilise un gestionnaire de configuration pour stocker des paramètres tels que :

- Dernière langue utilisée
- Dernier niveau de zoom utilisé
- Si la dernière sortie doit être chargée au démarrage
- Autres préférences d'interface et d'éditeur

La configuration est chargée au démarrage et appliquée à l'interface et aux menus.

### Localisation

Un composant `Translator` gère les textes de l'interface :

- La langue par défaut est configurée via les paramètres.
- Les fichiers de traduction peuvent être ajoutés ou modifiés pour prendre en charge d'autres langues.
- Les textes de l'interface (menus, dialogues, étiquettes) passent par le traducteur.

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez aider :

1. Forkez ce dépôt.
2. Créez une branche de fonctionnalité :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. Validez vos modifications :
   ```bash
   git commit -am "Ajouter ma nouvelle fonctionnalité"
   ```
4. Poussez la branche :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
5. Ouvrez une Pull Request décrivant vos modifications.

Veuillez maintenir votre code cohérent avec le style existant et inclure des tests si possible.

---

## 📄 Licence

Ce projet est sous licence **GNU General Public License v3.0 (GPL-3.0)**.  
Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- Merci aux communautés homebrew et ROM hacking GBA pour leur documentation et leurs outils.
- Inspiré par les éditeurs de pixel art classiques et les utilitaires de développement GBA.

---

## 📩 Contact et Support

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Si vous trouvez cet outil utile et souhaitez soutenir son développement, pensez à m'offrir un café !

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
