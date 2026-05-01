<p align="center"><img width="1868" height="560" src="assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** is a desktop application for creating and editing **Game Boy Advance (GBA) backgrounds**. It allows you to convert images into GBA-compatible tilesets and tilemaps, edit tiles and palettes visually, and export ready-to-use assets for your GBA projects.

> ⚠️ This application is designed for developers, ROM hackers, and pixel artists who need fine-grained control over GBA backgrounds.

---

## 🌐 Translations

This README is available in the following languages:

<p align="center">
  <a href="README.md">English</a> | <a href="docs/README.spa.md">Español</a> | <a href="docs/README.brp.md">Português (BR)</a> | <a href="docs/README.fra.md">Français</a> | <a href="docs/README.deu.md">Deutsch</a> | <a href="docs/README.ita.md">Italiano</a> | <a href="docs/README.por.md">Português</a> | <a href="docs/README.nld.md">Nederlands</a> | <a href="docs/README.pol.md">Polski</a><br>
  <a href="docs/README.tur.md">Türkçe</a> | <a href="docs/README.vie.md">Tiếng Việt</a> | <a href="docs/README.ind.md">Bahasa Indonesia</a> | <a href="docs/README.hin.md">हिन्दी</a> | <a href="docs/README.rus.md">Русский</a> | <a href="docs/README.jpn.md">日本語</a> | <a href="docs/README.zhs.md">简体中文</a> | <a href="docs/README.zht.md">繁體中文</a> | <a href="docs/README.kor.md">한국어</a>
</p>

---

## ✨ Features

- **Image to GBA conversion**
  - Convert standard images into GBA-friendly tilesets and tilemaps.
  - Configure output size and color depth (4bpp and 8bpp).
  - Preview the result before exporting.

- **Tileset editing**
  - Visual tile selection and editing.
  - Interactive drawing tools on the tilemap grid.
  - Zoom levels from \(100\%\) to \(800\%\) for pixel-perfect editing.

- **Palette editing**
  - Edit up to 256 colors per palette.
  - Synchronize palette changes with previews and tiles.
  - Reorder, replace, or tweak individual colors.

- **Preview tab**
  - See how your final background will look on a GBA-like screen.
  - Quickly validate tile and palette configurations.

- **Undo / Redo history**
  - Comprehensive history tracking for edits.
  - Undo and redo operations with a large history buffer.

- **Configurable UI & status bar**
  - Detailed status bar with tile selection, tilemap coordinates, palette ID, flip state, and zoom level.
  - Context-sensitive toolbar per tab (preview, tiles, palettes).

- **Multi-language support**
  - Internal translation system (Translator) with language selection via configuration.
  - Designed to support multiple languages in the UI.

---

## 🖼️ Screenshots

<p align="center"><img width="896" height="590" src="assets/readme/eng_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="812" height="676" src="assets/readme/eng_preview.png" alt="Image" /></p>

<p align="center"><img width="812" height="676" src="assets/readme/eng_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="812" height="676" src="assets/readme/eng_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Architecture Overview

GBA Background Studio is built with **Python** and **PySide6 / PySide2** (hybrid), and follows a modular UI design:

- **Main window (`GBABackgroundStudio`)**
  - Manages application state (current BPP, zoom level, tile and palette selection).
  - Hosts the main tabs and the custom status bar.
  - Loads and applies configuration (including last session output).

- **Tabs**
  - `PreviewTab` – GBA-style preview of the background.
  - `EditTilesTab` – Tile and tilemap editing tools.
  - `EditPalettesTab` – Palette editor and color manipulation tools.

- **UI components & utilities**
  - `MenuBar` – File operations (open image, export files, exit) and editor actions.
  - `CustomGraphicsView` – Extended `QGraphicsView` with tile-based interaction (hover, drawing, selection, paste preview).
  - `TilemapUtils` – Shared logic for tilemap interaction and selection.
  - `HistoryManager` – Undo/redo management for editor operations.
  - `HoverManager`, `GridManager` – Visual helpers for hover effects and grid overlays.
  - `Translator`, `ConfigManager` – Localization and persistent configuration.

---

## 📦 Installation

### Option 1 — Installer (recommended)

Download the latest release from [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases):

| Installer | Python | OS |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | Bundled (no install needed) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | Bundled (no install needed) | Windows 7 / 8 / 8.1 |

Just run the installer and launch the app — no Python or pip required.

---

### Option 2 — Run from source

#### Requirements

| Environment | Python | Qt Backend | OS |
|---|---|---|---|
| **Modern** | 3.10+ | PySide6 (auto) | Windows 10/11, macOS 11+, Linux |
| **Legacy** | 3.8 / 3.9 | PySide2 5.15.2 (auto) | Windows 7 / 8 / 8.1 |

The application automatically detects which Qt backend to use based on your Python version — no manual configuration needed.

#### Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` automatically installs the correct Qt backend:
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

Other dependencies: `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ Legacy OS Support (Windows 7 / 8 / 8.1)

The full graphical interface runs on Windows 7 and later. Use **Python 3.8** and the `requirements.txt` will automatically install **PySide2 5.15.2**.

Alternatively, the **Multi-language CLI Wizard** (`GBA_Studio_Wizard.bat`) is available for batch conversions without the GUI, and works on any Windows version with Python 3.8+:

1. Navigate to the project root.
2. Run **`GBA_Studio_Wizard.bat`**.
3. Select your language (18 languages supported).
4. Follow the step-by-step instructions to convert your image.

---

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Create and activate a virtual environment** (optional but recommended)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

---

## 🧭 Basic Usage

1. **Open an Image**
   - Go to **File → Open Image** or press `Ctrl+O`.
   - Select the image you want to convert into a GBA background.

2. **Configure Conversion**
   - Select the **BG Mode** (**Text Mode** or **Rotation/Scaling Mode**).
   - Choose the palette(s) or Tilemap to use (only for **4bpp Text Mode**).
   - Set the color to be used as transparent.
   - Adjust the output size and other necessary parameters.
   - Click **Convert**, and the app will handle the rest for you.

3. **Edit Tiles**
   - Switch to the **Edit Tiles** tab.
   - Use the tilemap view to draw and modify individual tiles.
   - Select entire areas to copy, cut, paste, or rotate groups of tiles.
   - Synchronize changes in real-time to see instant results.
   - Adjust the **Zoom** level for perfect precision.
   - Optimize or Deoptimize tilesets to save space or ensure hardware compatibility.
   - Convert assets between **4bpp** and **8bpp** formats.
   - Switch between **Text Mode** and **Rotation/Scaling Mode** seamlessly.

4. **Edit Palettes**
   - Go to the **Edit Palettes** tab.
   - Modify colors in the palette grid and fine-tune them using the color editor.
   - Select specific areas or all tiles belonging to a palette to replace or swap them with another.

5. **Preview the Background**
   - Switch to the **Preview** tab for a high-fidelity representation of how it will look on an actual GBA.
   - Verify that your tile and palette configurations work perfectly together.

6. **Export Assets**
   - Go to **File → Export Files** or press `Ctrl+E`.
   - Export tilesets, tilemaps, and palettes in formats ready to be integrated into your GBA development toolchain.
   - Export individual assets separately from their respective menus if needed.

---

## 🔄 Undo / Redo

The application tracks your editing actions using a **history manager**:

- **Undo** – revert the last operation.
- **Redo** – re-apply an operation that was undone.

The history system keeps a buffer of recent states, including tile edits, palette changes, and tilemap operations.

---

## ⚙️ Configuration & Localization

### Configuration

The app uses a configuration manager to store settings such as:

- Last used language
- Last used zoom level
- Whether to load the last output on startup
- Other UI and editor preferences

The configuration is loaded on startup and applied to the UI and menus.

### Localization

A `Translator` component handles the UI text:

- Default language is configured through the settings.
- Translation files can be added or edited to support more languages.
- UI texts (menus, dialogs, labels) are passed through the translator.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to help:

1. Fork this repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -am "Add my new feature"
   ```
4. Push the branch:
   ```bash
   git push origin feature/my-new-feature
   ```
5. Open a Pull Request describing your changes.

Please keep your code consistent with the existing style and include tests when possible.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for more details.

---

## 🙏 Acknowledgments

- Thanks to the GBA homebrew and ROM hacking communities for their documentation and tools.
- Inspired by classic pixel art editors and GBA development utilities.

---

## 📩 Contact & Support

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

If you find this tool useful and would like to support its development, consider buying me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
