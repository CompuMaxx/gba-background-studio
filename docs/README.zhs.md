<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** 是一款用于创建和编辑 **Game Boy Advance (GBA) 背景**的桌面应用程序。它允许将图像转换为 GBA 兼容的图块集和图块映射，可视化编辑图块和调色板，并导出可在 GBA 项目中直接使用的资源。

> ⚠️ 此应用程序专为需要精确控制 GBA 背景的开发者、ROM 黑客和像素艺术家设计。

---

## 🌐 翻译

此 README 提供以下语言版本：

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 功能特性

- **图像转 GBA**
  - 将标准图像转换为 GBA 兼容的图块集和图块映射。
  - 配置输出尺寸和颜色深度（4bpp 和 8bpp）。
  - 导出前预览结果。

- **编辑图块**
  - 图块的可视化选择和编辑。
  - 图块映射网格上的交互式绘图工具。
  - 100% 至 800% 的缩放级别，支持逐像素编辑。

- **编辑调色板**
  - 每个调色板最多编辑 256 种颜色。
  - 将调色板更改与预览和图块同步。
  - 重新排列、替换或调整单个颜色。

- **预览选项卡**
  - 在类似 GBA 的屏幕上可视化最终背景的外观。
  - 快速验证图块和调色板配置。

- **撤销/重做历史**
  - 完整的编辑历史跟踪。
  - 具有大型历史缓冲区的撤销和重做操作。

- **可配置的界面和状态栏**
  - 详细的状态栏，包含图块选择、图块映射坐标、调色板 ID、翻转状态和缩放级别。
  - 每个选项卡的上下文工具栏（预览、图块、调色板）。

- **多语言支持**
  - 内部翻译系统（Translator），通过设置选择语言。
  - 设计为支持界面中的多种语言。

---

## 🖼️ 截图

<p align="center"><img width="896" height="590" src="../assets/readme/zhs_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zhs_preview.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zhs_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="796" height="676" src="../assets/readme/zhs_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ 架构说明

GBA Background Studio 使用 **Python** 和 **PySide6 / PySide2**（混合）构建，遵循模块化界面设计：

- **主窗口（`GBABackgroundStudio`）**
  - 管理应用程序状态（当前 BPP、缩放级别、图块和调色板选择）。
  - 承载主选项卡和自定义状态栏。
  - 加载并应用配置（包括最后一次输出会话）。

- **选项卡**
  - `PreviewTab` – GBA 风格的背景预览。
  - `EditTilesTab` – 图块和图块映射编辑工具。
  - `EditPalettesTab` – 调色板编辑器和颜色操作工具。

- **界面组件和实用程序**
  - `MenuBar` – 文件操作（打开图像、导出文件、退出）和编辑器操作。
  - `CustomGraphicsView` – 具有基于图块交互的扩展 `QGraphicsView`。
  - `TilemapUtils` – 图块映射交互和选择的共享逻辑。
  - `HistoryManager` – 编辑器操作的撤销/重做管理。
  - `HoverManager`、`GridManager` – 悬停效果和网格叠加的视觉辅助工具。
  - `Translator`、`ConfigManager` – 本地化和持久配置。

---

## 📦 安装

### 选项 1 — 安装程序（推荐）

从 [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases) 下载最新版本：

| 安装程序 | Python | 操作系统 |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | 已内置（无需安装） | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | 已内置（无需安装） | Windows 7 / 8 / 8.1 |

只需运行安装程序并启动应用 — 无需 Python 或 pip。

---

### 选项 2 — 从源码运行

#### 要求

| 环境 | Python | Qt 后端 | 操作系统 |
|---|---|---|---|
| **现代** | 3.10+ | PySide6 (自动) | Windows 10/11, macOS 11+, Linux |
| **旧版** | 3.8 / 3.9 | PySide2 5.15.2 (自动) | Windows 7 / 8 / 8.1 |

应用程序根据您的 Python 版本自动检测使用哪个 Qt 后端 — 无需手动配置。

#### 依赖项

```bash
pip install -r requirements.txt
```

`requirements.txt` 自动安装正确的 Qt 后端：
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

其他依赖项：`Pillow`、`numpy`、`scipy`、`scikit-learn`、`opencv-python`、`certifi`。

---

### 🏛️ 旧版系统支持（Windows 7 / 8 / 8.1）

完整图形界面可在 Windows 7 及更高版本上运行。使用 **Python 3.8**，`requirements.txt` 将自动安装 **PySide2 5.15.2**。

此外，**多语言命令行向导** (`GBA_Studio_Wizard.bat`) 可用于无 GUI 的批量转换，适用于安装了 Python 3.8+ 的任何 Windows 版本：

1. 导航到项目根目录。
2. 运行 **`GBA_Studio_Wizard.bat`**。
3. 选择您的语言（支持 18 种语言）。
4. 按照分步说明转换您的图像。

---

## 🚀 快速开始

1. **克隆仓库**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **创建并激活虚拟环境**（可选但推荐）

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # 在 Windows 上：.venv\Scripts\activate
   ```

3. **安装依赖项**

   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用程序**

   ```bash
   python main.py
   ```

---

## 🧭 基本使用

1. **打开图像**
   - 转到**文件 → 打开图像**或按 `Ctrl+O`。
   - 选择要转换为 GBA 背景的图像。

2. **配置转换**
   - 选择**背景模式**（**文本模式**或**旋转/缩放**）。
   - 选择要使用的调色板或图块映射（仅适用于**文本模式 4bpp**）。
   - 设置将用作透明的颜色。
   - 调整输出尺寸和其他必要参数。
   - 点击**转换**，应用程序将处理其余部分。

3. **编辑图块**
   - 切换到**编辑图块**选项卡。
   - 使用图块映射视图绘制和修改单个图块。
   - 选择整个区域以复制、剪切、粘贴或旋转图块组。
   - 实时同步更改以查看即时结果。
   - 调整**缩放**级别以获得完美精度。
   - 优化/取消优化图块以节省空间或确保硬件兼容性。
   - 在 **4bpp** 和 **8bpp** 格式之间转换资源。
   - 在**文本模式**和**旋转/缩放**之间无缝切换。

4. **编辑调色板**
   - 转到**编辑调色板**选项卡。
   - 在调色板网格中修改颜色，并使用颜色编辑器进行调整。
   - 选择特定区域或属于某个调色板的所有图块，以替换或与另一个调色板交换。

5. **背景预览**
   - 切换到**预览**选项卡，以忠实呈现在真实 GBA 上的外观。
   - 验证图块和调色板配置是否完美协同工作。

6. **导出资源**
   - 转到**文件 → 导出文件**或按 `Ctrl+E`。
   - 以可集成到 GBA 开发工具链的格式导出图块集、图块映射和调色板。
   - 如有需要，从各自的菜单单独导出各个资源。

---

## 🔄 撤销/重做

应用程序使用**历史管理器**跟踪您的编辑操作：

- **撤销** – 撤销最后一次操作。
- **重做** – 重新应用已撤销的操作。

历史系统维护最近状态的缓冲区，包括图块编辑、调色板更改和图块映射操作。

---

## ⚙️ 配置和本地化

### 配置

应用程序使用配置管理器存储以下设置：

- 最后使用的语言
- 最后使用的缩放级别
- 启动时是否加载最后的输出
- 其他界面和编辑器偏好设置

配置在启动时加载并应用于界面和菜单。

### 本地化

`Translator` 组件管理界面文本：

- 默认语言通过设置配置。
- 可以添加或编辑翻译文件以支持更多语言。
- 界面文本（菜单、对话框、标签）通过翻译器处理。

---

## 🤝 贡献

欢迎贡献！如果您想提供帮助：

1. Fork 此仓库。
2. 创建功能分支：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 提交您的更改：
   ```bash
   git commit -am "添加我的新功能"
   ```
4. 推送分支：
   ```bash
   git push origin feature/my-new-feature
   ```
5. 打开描述您更改的 Pull Request。

请保持代码与现有风格一致，并在可能的情况下包含测试。

---

## 📄 许可证

本项目在 **GNU General Public License v3.0 (GPL-3.0)** 下授权。  
有关更多详细信息，请参阅 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 感谢 GBA homebrew 和 ROM 黑客社区提供的文档和工具。
- 受经典像素艺术编辑器和 GBA 开发实用程序的启发。

---

## 📩 联系和支持

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

如果您觉得这个工具有用并想支持其开发，请考虑请我喝杯咖啡！

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
