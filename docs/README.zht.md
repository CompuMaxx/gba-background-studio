<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** 是一款用於建立和編輯 **Game Boy Advance (GBA) 背景**的桌面應用程式。它允許將圖像轉換為 GBA 相容的圖塊集和圖塊映射，可視化編輯圖塊和調色盤，並匯出可在 GBA 專案中直接使用的資源。

> ⚠️ 此應用程式專為需要精確控制 GBA 背景的開發者、ROM 駭客和像素藝術家設計。

---

## 🌐 翻譯

此 README 提供以下語言版本：

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 功能特性

- **圖像轉 GBA**
  - 將標準圖像轉換為 GBA 相容的圖塊集和圖塊映射。
  - 設定輸出尺寸和顏色深度（4bpp 和 8bpp）。
  - 匯出前預覽結果。

- **編輯圖塊**
  - 圖塊的可視化選擇和編輯。
  - 圖塊映射網格上的互動式繪圖工具。
  - 100% 至 800% 的縮放級別，支援逐像素編輯。

- **編輯調色盤**
  - 每個調色盤最多編輯 256 種顏色。
  - 將調色盤更改與預覽和圖塊同步。
  - 重新排列、替換或調整個別顏色。

- **預覽分頁**
  - 在類似 GBA 的螢幕上可視化最終背景的外觀。
  - 快速驗證圖塊和調色盤設定。

- **復原/重做歷史**
  - 完整的編輯歷史追蹤。
  - 具有大型歷史緩衝區的復原和重做操作。

- **可設定的介面和狀態列**
  - 詳細的狀態列，包含圖塊選擇、圖塊映射座標、調色盤 ID、翻轉狀態和縮放級別。
  - 每個分頁的上下文工具列（預覽、圖塊、調色盤）。

- **多語言支援**
  - 內部翻譯系統（Translator），透過設定選擇語言。
  - 設計為支援介面中的多種語言。

---

## 🖼️ 截圖

<p align="center"><img width="896" height="590" src="../assets/readme/zht_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zht_preview.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zht_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zht_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ 架構說明

GBA Background Studio 使用 **Python** 和 **PySide6 / PySide2**（混合）建構，遵循模組化介面設計：

- **主視窗（`GBABackgroundStudio`）**
  - 管理應用程式狀態（目前 BPP、縮放級別、圖塊和調色盤選擇）。
  - 承載主分頁和自訂狀態列。
  - 載入並套用設定（包括最後一次輸出工作階段）。

- **分頁**
  - `PreviewTab` – GBA 風格的背景預覽。
  - `EditTilesTab` – 圖塊和圖塊映射編輯工具。
  - `EditPalettesTab` – 調色盤編輯器和顏色操作工具。

- **介面元件和公用程式**
  - `MenuBar` – 檔案操作（開啟圖像、匯出檔案、結束）和編輯器操作。
  - `CustomGraphicsView` – 具有基於圖塊互動的擴充 `QGraphicsView`。
  - `TilemapUtils` – 圖塊映射互動和選擇的共用邏輯。
  - `HistoryManager` – 編輯器操作的復原/重做管理。
  - `HoverManager`、`GridManager` – 懸停效果和網格疊加的視覺輔助工具。
  - `Translator`、`ConfigManager` – 本地化和持久設定。

---

## 📦 安裝

### 選項 1 — 安裝程式（推薦）

從 [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases) 下載最新版本：

| 安裝程式 | Python | 作業系統 |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | 已內建（無需安裝） | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | 已內建（無需安裝） | Windows 7 / 8 / 8.1 |

只需執行安裝程式並啟動應用程式 — 無需 Python 或 pip。

---

### 選項 2 — 從原始碼執行

#### 要求

| 環境 | Python | Qt 後端 | 作業系統 |
|---|---|---|---|
| **現代** | 3.10+ | PySide6 (自動) | Windows 10/11, macOS 11+, Linux |
| **舊版** | 3.8 / 3.9 | PySide2 5.15.2 (自動) | Windows 7 / 8 / 8.1 |

應用程式根據您的 Python 版本自動偵測使用哪個 Qt 後端 — 無需手動設定。

#### 相依性

```bash
pip install -r requirements.txt
```

`requirements.txt` 自動安裝正確的 Qt 後端：
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

其他相依性：`Pillow`、`numpy`、`scipy`、`scikit-learn`、`opencv-python`、`certifi`。

---

### 🏛️ 舊版系統支援（Windows 7 / 8 / 8.1）

完整圖形介面可在 Windows 7 及更高版本上執行。使用 **Python 3.8**，`requirements.txt` 將自動安裝 **PySide2 5.15.2**。

此外，**多語言命令列精靈** (`GBA_Studio_Wizard.bat`) 可用於無 GUI 的批次轉換，適用於安裝了 Python 3.8+ 的任何 Windows 版本：

1. 導覽至專案根目錄。
2. 執行 **`GBA_Studio_Wizard.bat`**。
3. 選擇您的語言（支援 18 種語言）。
4. 按照逐步說明轉換您的圖像。

---

## 🚀 快速開始

1. **複製儲存庫**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **建立並啟用虛擬環境**（可選但建議）

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # 在 Windows 上：.venv\Scripts\activate
   ```

3. **安裝相依性**

   ```bash
   pip install -r requirements.txt
   ```

4. **執行應用程式**

   ```bash
   python main.py
   ```

---

## 🧭 基本使用

1. **開啟圖像**
   - 前往**檔案 → 開啟圖像**或按 `Ctrl+O`。
   - 選擇要轉換為 GBA 背景的圖像。

2. **設定轉換**
   - 選擇**背景模式**（**文字模式**或**旋轉/縮放**）。
   - 選擇要使用的調色盤或圖塊映射（僅適用於**文字模式 4bpp**）。
   - 設定將用作透明的顏色。
   - 調整輸出尺寸和其他必要參數。
   - 點擊**轉換**，應用程式將處理其餘部分。

3. **編輯圖塊**
   - 切換到**編輯圖塊**分頁。
   - 使用圖塊映射檢視繪製和修改個別圖塊。
   - 選擇整個區域以複製、剪下、貼上或旋轉圖塊群組。
   - 即時同步更改以查看即時結果。
   - 調整**縮放**級別以獲得完美精度。
   - 優化/取消優化圖塊以節省空間或確保硬體相容性。
   - 在 **4bpp** 和 **8bpp** 格式之間轉換資源。
   - 在**文字模式**和**旋轉/縮放**之間無縫切換。

4. **編輯調色盤**
   - 前往**編輯調色盤**分頁。
   - 在調色盤網格中修改顏色，並使用顏色編輯器進行調整。
   - 選擇特定區域或屬於某個調色盤的所有圖塊，以替換或與另一個調色盤交換。

5. **背景預覽**
   - 切換到**預覽**分頁，以忠實呈現在真實 GBA 上的外觀。
   - 驗證圖塊和調色盤設定是否完美協同運作。

6. **匯出資源**
   - 前往**檔案 → 匯出檔案**或按 `Ctrl+E`。
   - 以可整合到 GBA 開發工具鏈的格式匯出圖塊集、圖塊映射和調色盤。
   - 如有需要，從各自的選單單獨匯出各個資源。

---

## 🔄 復原/重做

應用程式使用**歷史管理員**追蹤您的編輯操作：

- **復原** – 復原最後一次操作。
- **重做** – 重新套用已復原的操作。

歷史系統維護最近狀態的緩衝區，包括圖塊編輯、調色盤更改和圖塊映射操作。

---

## ⚙️ 設定和本地化

### 設定

應用程式使用設定管理員儲存以下設定：

- 最後使用的語言
- 最後使用的縮放級別
- 啟動時是否載入最後的輸出
- 其他介面和編輯器偏好設定

設定在啟動時載入並套用於介面和選單。

### 本地化

`Translator` 元件管理介面文字：

- 預設語言透過設定設定。
- 可以新增或編輯翻譯檔案以支援更多語言。
- 介面文字（選單、對話框、標籤）透過翻譯器處理。

---

## 🤝 貢獻

歡迎貢獻！如果您想提供協助：

1. Fork 此儲存庫。
2. 建立功能分支：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -am "新增我的新功能"
   ```
4. 推送分支：
   ```bash
   git push origin feature/my-new-feature
   ```
5. 開啟描述您更改的 Pull Request。

請保持程式碼與現有風格一致，並在可能的情況下包含測試。

---

## 📄 授權

本專案在 **GNU General Public License v3.0 (GPL-3.0)** 下授權。  
有關更多詳細資訊，請參閱 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- 感謝 GBA homebrew 和 ROM 駭客社群提供的文件和工具。
- 受經典像素藝術編輯器和 GBA 開發公用程式的啟發。

---

## 📩 聯絡和支援

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

如果您覺得這個工具有用並想支援其開發，請考慮請我喝杯咖啡！

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
