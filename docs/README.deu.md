<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** ist eine Desktop-Anwendung zum Erstellen und Bearbeiten von **Game Boy Advance (GBA)-Hintergründen**. Sie ermöglicht die Konvertierung von Bildern in GBA-kompatible Tilesets und Tilemaps, die visuelle Bearbeitung von Tiles und Paletten sowie den Export von Assets für Ihre GBA-Projekte.

> ⚠️ Diese Anwendung richtet sich an Entwickler, ROM-Hacker und Pixel-Artists, die präzise Kontrolle über GBA-Hintergründe benötigen.

---

## 🌐 Übersetzungen

Diese README ist in folgenden Sprachen verfügbar:

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Funktionen

- **Bild-zu-GBA-Konvertierung**
  - Konvertiert Standardbilder in GBA-kompatible Tilesets und Tilemaps.
  - Konfiguriert Ausgabegröße und Farbtiefe (4bpp und 8bpp).
  - Vorschau des Ergebnisses vor dem Export.

- **Tileset-Bearbeitung**
  - Visuelle Auswahl und Bearbeitung von Tiles.
  - Interaktive Zeichenwerkzeuge auf dem Tilemap-Raster.
  - Zoom-Stufen von 100% bis 800% für pixelgenaue Bearbeitung.

- **Paletten-Bearbeitung**
  - Bearbeitung von bis zu 256 Farben pro Palette.
  - Synchronisierung von Palettenänderungen mit Vorschauen und Tiles.
  - Neuanordnung, Ersetzung oder Anpassung einzelner Farben.

- **Vorschau-Tab**
  - Visualisierung des finalen Hintergrunds auf einem GBA-ähnlichen Bildschirm.
  - Schnelle Validierung von Tile- und Palettenkonfigurationen.

- **Rückgängig/Wiederholen-Verlauf**
  - Vollständige Verfolgung des Bearbeitungsverlaufs.
  - Rückgängig- und Wiederholen-Operationen mit großem Verlaufspuffer.

- **Konfigurierbare Oberfläche und Statusleiste**
  - Detaillierte Statusleiste mit Tile-Auswahl, Tilemap-Koordinaten, Palette-ID, Spiegelungsstatus und Zoom-Stufe.
  - Kontextbezogene Symbolleiste pro Tab (Vorschau, Tiles, Paletten).

- **Mehrsprachige Unterstützung**
  - Internes Übersetzungssystem (Translator) mit Sprachauswahl über Einstellungen.
  - Für die Unterstützung mehrerer Sprachen in der Oberfläche ausgelegt.

---

## 🖼️ Screenshots

<p align="center"><img width="896" height="590" src="../assets/readme/deu_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="930" height="676" src="../assets/readme/deu_preview.png" alt="Image" /></p>

<p align="center"><img width="930" height="676" src="../assets/readme/deu_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="930" height="676" src="../assets/readme/deu_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Architekturbeschreibung

GBA Background Studio ist mit **Python** und **PySide6 / PySide2** (hybrid) entwickelt und folgt einem modularen Oberflächendesign:

- **Hauptfenster (`GBABackgroundStudio`)**
  - Verwaltet den Anwendungszustand (aktuelles BPP, Zoom-Stufe, Tile- und Palettenauswahl).
  - Beherbergt die Haupt-Tabs und die benutzerdefinierte Statusleiste.
  - Lädt und wendet Konfigurationen an (einschließlich der letzten Ausgabesitzung).

- **Tabs**
  - `PreviewTab` – GBA-stilige Hintergrundvorschau.
  - `EditTilesTab` – Werkzeuge zur Tile- und Tilemap-Bearbeitung.
  - `EditPalettesTab` – Paletten-Editor und Farbmanipulationswerkzeuge.

- **Oberflächenkomponenten und Hilfsprogramme**
  - `MenuBar` – Dateioperationen (Bild öffnen, Dateien exportieren, Beenden) und Editor-Aktionen.
  - `CustomGraphicsView` – Erweiterter `QGraphicsView` mit tile-basierter Interaktion (Hover, Zeichnen, Auswahl, Einfügevorschau).
  - `TilemapUtils` – Gemeinsame Logik für Tilemap-Interaktion und -Auswahl.
  - `HistoryManager` – Rückgängig/Wiederholen-Verwaltung für Editor-Operationen.
  - `HoverManager`, `GridManager` – Visuelle Hilfsmittel für Hover-Effekte und Rasterüberlagerungen.
  - `Translator`, `ConfigManager` – Lokalisierung und persistente Konfiguration.

---

## 📦 Installation

### Option 1 — Installer (empfohlen)

Laden Sie die neueste Version von [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases) herunter:

| Installer | Python | Betriebssystem |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | Enthalten (keine Installation nötig) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | Enthalten (keine Installation nötig) | Windows 7 / 8 / 8.1 |

Einfach den Installer ausführen und die App starten — kein Python oder pip erforderlich.

---

### Option 2 — Aus dem Quellcode ausführen

#### Anforderungen

| Umgebung | Python | Qt-Backend | Betriebssystem |
|---|---|---|---|
| **Modern** | 3.10+ | PySide6 (auto) | Windows 10/11, macOS 11+, Linux |
| **Legacy** | 3.8 / 3.9 | PySide2 5.15.2 (auto) | Windows 7 / 8 / 8.1 |

Die Anwendung erkennt automatisch, welches Qt-Backend basierend auf Ihrer Python-Version verwendet werden soll — keine manuelle Konfiguration erforderlich.

#### Abhängigkeiten

```bash
pip install -r requirements.txt
```

`requirements.txt` installiert automatisch das richtige Qt-Backend:
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

Weitere Abhängigkeiten: `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ Unterstützung für Legacy-Systeme (Windows 7 / 8 / 8.1)

Die vollständige grafische Oberfläche läuft auf Windows 7 und höher. Verwenden Sie **Python 3.8** und `requirements.txt` installiert automatisch **PySide2 5.15.2**.

Alternativ steht der **Mehrsprachige Kommandozeilen-Assistent** (`GBA_Studio_Wizard.bat`) für Stapelkonvertierungen ohne die grafische Oberfläche zur Verfügung und funktioniert auf jeder Windows-Version mit Python 3.8+:

1. Navigieren Sie zum Stammverzeichnis des Projekts.
2. Führen Sie **`GBA_Studio_Wizard.bat`** aus.
3. Wählen Sie Ihre Sprache (18 Sprachen unterstützt).
4. Folgen Sie den Schritt-für-Schritt-Anweisungen zur Konvertierung Ihres Bildes.

---

## 🚀 Erste Schritte

1. **Repository klonen**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Virtuelle Umgebung erstellen und aktivieren** (optional, aber empfohlen)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Unter Windows: .venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren**

   ```bash
   pip install -r requirements.txt
   ```

4. **Anwendung starten**

   ```bash
   python main.py
   ```

---

## 🧭 Grundlegende Verwendung

1. **Bild öffnen**
   - Gehen Sie zu **Datei → Bild öffnen** oder drücken Sie `Ctrl+O`.
   - Wählen Sie das Bild aus, das Sie in einen GBA-Hintergrund konvertieren möchten.

2. **Konvertierung konfigurieren**
   - Wählen Sie den **Hintergrundmodus** (**Textmodus** oder **Rotation/Scaling**).
   - Wählen Sie die Palette(n) oder Tilemap (nur für **Textmodus 4bpp**).
   - Legen Sie die Farbe fest, die als transparent verwendet werden soll.
   - Passen Sie die Ausgabegröße und andere Parameter an.
   - Klicken Sie auf **Konvertieren** und die Anwendung erledigt den Rest.

3. **Tiles bearbeiten**
   - Wechseln Sie zum Tab **Tiles bearbeiten**.
   - Verwenden Sie die Tilemap-Ansicht zum Zeichnen und Ändern einzelner Tiles.
   - Wählen Sie ganze Bereiche aus, um Tile-Gruppen zu kopieren, auszuschneiden, einzufügen oder zu drehen.
   - Synchronisieren Sie Änderungen in Echtzeit für sofortige Ergebnisse.
   - Passen Sie den **Zoom**-Grad für perfekte Präzision an.
   - Tiles optimieren/deoptimieren, um Speicherplatz zu sparen oder Hardware-Kompatibilität zu gewährleisten.
   - Assets zwischen den Formaten **4bpp** und **8bpp** konvertieren.
   - Nahtlos zwischen **Textmodus** und **Rotation/Scaling** wechseln.

4. **Paletten bearbeiten**
   - Gehen Sie zum Tab **Paletten bearbeiten**.
   - Ändern Sie Farben im Palettenraster und passen Sie sie mit dem Farbeditor an.
   - Wählen Sie bestimmte Bereiche oder alle Tiles einer Palette aus, um sie zu ersetzen oder mit einer anderen zu tauschen.

5. **Hintergrundvorschau**
   - Wechseln Sie zum Tab **Vorschau** für eine originalgetreue Darstellung, wie es auf einem echten GBA aussehen wird.
   - Überprüfen Sie, ob Ihre Tile- und Palettenkonfigurationen perfekt zusammenarbeiten.

6. **Assets exportieren**
   - Gehen Sie zu **Datei → Dateien exportieren** oder drücken Sie `Ctrl+E`.
   - Exportieren Sie Tilesets, Tilemaps und Paletten in Formaten, die für Ihre GBA-Entwicklungs-Toolchain bereit sind.
   - Exportieren Sie einzelne Assets bei Bedarf separat über ihre jeweiligen Menüs.

---

## 🔄 Rückgängig/Wiederholen

Die Anwendung verfolgt Ihre Bearbeitungsaktionen mit einem **Verlaufsmanager**:

- **Rückgängig** – macht die letzte Operation rückgängig.
- **Wiederholen** – stellt eine rückgängig gemachte Operation wieder her.

Das Verlaufssystem hält einen Puffer mit aktuellen Zuständen, einschließlich Tile-Bearbeitungen, Palettenänderungen und Tilemap-Operationen.

---

## ⚙️ Konfiguration und Lokalisierung

### Konfiguration

Die Anwendung verwendet einen Konfigurationsmanager zum Speichern von Einstellungen wie:

- Zuletzt verwendete Sprache
- Zuletzt verwendete Zoom-Stufe
- Ob die letzte Ausgabe beim Start geladen werden soll
- Andere Oberflächen- und Editor-Einstellungen

Die Konfiguration wird beim Start geladen und auf die Oberfläche und Menüs angewendet.

### Lokalisierung

Eine `Translator`-Komponente verwaltet die Oberflächentexte:

- Die Standardsprache wird über die Einstellungen konfiguriert.
- Übersetzungsdateien können hinzugefügt oder bearbeitet werden, um weitere Sprachen zu unterstützen.
- Oberflächentexte (Menüs, Dialoge, Beschriftungen) werden durch den Übersetzer geleitet.

---

## 🤝 Mitwirken

Beiträge sind willkommen! Wenn Sie helfen möchten:

1. Forken Sie dieses Repository.
2. Erstellen Sie einen Feature-Branch:
   ```bash
   git checkout -b feature/mein-neues-feature
   ```
3. Bestätigen Sie Ihre Änderungen:
   ```bash
   git commit -am "Mein neues Feature hinzufügen"
   ```
4. Pushen Sie den Branch:
   ```bash
   git push origin feature/mein-neues-feature
   ```
5. Öffnen Sie einen Pull Request mit einer Beschreibung Ihrer Änderungen.

Bitte halten Sie Ihren Code konsistent mit dem vorhandenen Stil und fügen Sie wenn möglich Tests hinzu.

---

## 📄 Lizenz

Dieses Projekt ist unter der **GNU General Public License v3.0 (GPL-3.0)** lizenziert.  
Weitere Details finden Sie in der Datei [LICENSE](LICENSE).

---

## 🙏 Danksagungen

- Dank an die GBA-Homebrew- und ROM-Hacking-Communities für ihre Dokumentation und Werkzeuge.
- Inspiriert von klassischen Pixel-Art-Editoren und GBA-Entwicklungshilfsprogrammen.

---

## 📩 Kontakt und Support

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Wenn Sie dieses Tool nützlich finden und seine Entwicklung unterstützen möchten, erwägen Sie, mir einen Kaffee zu spendieren!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
