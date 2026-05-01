<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** は、**Game Boy Advance (GBA) の背景**を作成・編集するためのデスクトップアプリケーションです。画像をGBA互換のタイルセットとタイルマップに変換し、タイルとパレットを視覚的に編集し、GBAプロジェクトで使用できるアセットをエクスポートすることができます。

> ⚠️ このアプリケーションは、GBA背景を精密に制御する必要がある開発者、ROMハッカー、ピクセルアーティスト向けに設計されています。

---

## 🌐 翻訳

このREADMEは以下の言語で利用可能です：

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 機能

- **画像からGBAへの変換**
  - 標準画像をGBA互換のタイルセットとタイルマップに変換します。
  - 出力サイズと色深度（4bppおよび8bpp）を設定します。
  - エクスポート前に結果をプレビューします。

- **タイル編集**
  - タイルの視覚的な選択と編集。
  - タイルマップグリッド上のインタラクティブな描画ツール。
  - ピクセル単位の編集のための100%から800%のズームレベル。

- **パレット編集**
  - パレットごとに最大256色を編集。
  - パレットの変更をプレビューとタイルに同期。
  - 個々の色の並べ替え、置換、または調整。

- **プレビュータブ**
  - GBAに似た画面で最終的な背景がどのように見えるかを視覚化。
  - タイルとパレットの設定を素早く検証。

- **元に戻す/やり直し履歴**
  - 編集履歴の完全な追跡。
  - 広い履歴バッファを持つ元に戻す・やり直し操作。

- **設定可能なインターフェースとステータスバー**
  - タイル選択、タイルマップ座標、パレットID、反転状態、ズームレベルを含む詳細なステータスバー。
  - タブごとのコンテキストツールバー（プレビュー、タイル、パレット）。

- **多言語サポート**
  - 設定による言語選択を持つ内部翻訳システム（Translator）。
  - インターフェースで複数の言語をサポートするように設計。

---

## 🖼️ スクリーンショット

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/4e231a96-c5bd-4a1f-ab93-89d38e3f534c" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/5788d3cd-098e-4303-bd1e-cc5c79776fd5" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/09a37f4a-9c62-4491-b063-e2f7f7ba1992" /></p>

<p align="center"><img width="842" height="676" alt="Image" src="https://github.com/user-attachments/assets/94afe102-34a7-47f8-b5ec-31b48e719c60" /></p>

---

## 🏗️ アーキテクチャの説明

GBA Background Studioは**Python**と**PySide6**で構築されており、モジュラーインターフェースデザインに従っています：

- **メインウィンドウ（`GBABackgroundStudio`）**
  - アプリケーションの状態（現在のBPP、ズームレベル、タイルとパレットの選択）を管理。
  - メインタブとカスタムステータスバーをホスト。
  - 設定を読み込んで適用（最後の出力セッションを含む）。

- **タブ**
  - `PreviewTab` – GBAスタイルの背景プレビュー。
  - `EditTilesTab` – タイルとタイルマップの編集ツール。
  - `EditPalettesTab` – パレットエディタと色操作ツール。

- **インターフェースコンポーネントとユーティリティ**
  - `MenuBar` – ファイル操作（画像を開く、ファイルをエクスポート、終了）とエディタアクション。
  - `CustomGraphicsView` – タイルベースのインタラクションを持つ拡張`QGraphicsView`。
  - `TilemapUtils` – タイルマップのインタラクションと選択のための共有ロジック。
  - `HistoryManager` – エディタ操作の元に戻す/やり直し管理。
  - `HoverManager`、`GridManager` – ホバー効果とグリッドオーバーレイのビジュアルヘルパー。
  - `Translator`、`ConfigManager` – ローカライゼーションと永続的な設定。

---

## 📦 インストール

### 要件
- **Python** (3.12以上推奨)
- **Pip** (Pythonパッケージマネージャー)
- **PySide6のOSサポート:**
  - **Windows:** Windows 10 (バージョン 1809) 以降
  - **macOS:** macOS 11 (Big Sur) 以降
  - **Linux:** glibc 2.28以降を搭載した最新のディストリビューション

### 依存関係
主な依存関係は以下の通りです：
- `PySide6` (Qt for Python) - *注：上記のOSバージョンが必要です。*
- `Pillow` (PIL) 画像処理用

以下のコマンドで依存関係をインストールできます：
```bash
pip install -r requirements.txt
```

---

### 🏛️ レガシーOSのサポート (Windows 7 / 8 / 8.1)
**PySide6**（GUIフレームワーク）をサポートしていない旧バージョンのWindowsを使用している場合でも、**多言語コマンドラインウィザード**を介してコア変換エンジンを使用できます。

レガシー用の依存関係は以下のコマンドでインストールできます：
```bash
pip install -r requirements-legacy.txt
```

これにより、グラフィカルインターフェースなしで、母国語のステップバイステップガイドに従って画像をGBAアセットに変換できます。

1. プロジェクトのルートディレクトリに移動します。
2. **`GBA_Studio_Wizard.bat`** ファイルを実行します。
3. 言語を選択します（18言語対応）。
4. 指示に従って画像をドラッグ＆ドロップし、GBA出力を設定します。

---

## 🚀 はじめに

1. **リポジトリをクローン**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **仮想環境を作成して有効化**（オプションですが推奨）

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windowsの場合: .venv\Scripts\activate
   ```

3. **依存関係をインストール**

   ```bash
   pip install -r requirements.txt
   ```

4. **アプリケーションを実行**

   ```bash
   python main.py
   ```

---

## 🧭 基本的な使い方

1. **画像を開く**
   - **ファイル → 画像を開く** に移動するか、`Ctrl+O` を押します。
   - GBA背景に変換したい画像を選択します。

2. **変換を設定**
   - **BGモード**（**テキストモード** または **回転/スケーリング**）を選択します。
   - 使用するパレットまたはタイルマップを選択します（**テキストモード4bpp** のみ）。
   - 透明として使用する色を設定します。
   - 出力サイズとその他の必要なパラメータを調整します。
   - **変換** をクリックすると、アプリケーションが残りを処理します。

3. **タイル編集**
   - **タイル編集** タブに切り替えます。
   - タイルマップビューを使用して個々のタイルを描画・変更します。
   - タイルグループをコピー、カット、ペースト、または回転するために完全な領域を選択します。
   - リアルタイムで変更を同期して即座に結果を確認します。
   - 完璧な精度のために **ズーム** レベルを調整します。
   - タイルを最適化/最適化を解除してスペースを節約するか、ハードウェア互換性を確保します。
   - **4bpp** と **8bpp** フォーマット間でアセットを変換します。
   - **テキストモード** と **回転/スケーリング** をシームレスに切り替えます。

4. **パレット編集**
   - **パレット編集** タブに移動します。
   - パレットグリッドの色を変更し、カラーエディタで調整します。
   - パレットに属する特定の領域またはすべてのタイルを選択して、別のものと置換または交換します。

5. **背景プレビュー**
   - 実際のGBAでどのように見えるかの忠実な表現のために **プレビュー** タブに切り替えます。
   - タイルとパレットの設定が完璧に連携していることを確認します。

6. **アセットをエクスポート**
   - **ファイル → ファイルをエクスポート** に移動するか、`Ctrl+E` を押します。
   - タイルセット、タイルマップ、パレットをGBA開発ツールチェーンに統合できる形式でエクスポートします。
   - 必要に応じて、それぞれのメニューから個々のアセットを別々にエクスポートします。

---

## 🔄 元に戻す/やり直し

アプリケーションは **履歴マネージャー** を使用して編集アクションを追跡します：

- **元に戻す** – 最後の操作を元に戻します。
- **やり直し** – 元に戻した操作を再適用します。

履歴システムは、タイル編集、パレット変更、タイルマップ操作を含む最近の状態のバッファを維持します。

---

## ⚙️ 設定とローカライゼーション

### 設定

アプリケーションは以下のような設定を保存するために設定マネージャーを使用します：

- 最後に使用した言語
- 最後に使用したズームレベル
- 起動時に最後の出力を読み込むかどうか
- その他のインターフェースとエディタの設定

設定は起動時に読み込まれ、インターフェースとメニューに適用されます。

### ローカライゼーション

`Translator` コンポーネントがインターフェーステキストを管理します：

- デフォルト言語は設定を通じて設定されます。
- 翻訳ファイルを追加または編集して、より多くの言語をサポートできます。
- インターフェーステキスト（メニュー、ダイアログ、ラベル）は翻訳者を通じて処理されます。

---

## 🤝 貢献

貢献を歓迎します！ 協力したい場合：

1. このリポジトリをフォークします。
2. フィーチャーブランチを作成します：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 変更をコミットします：
   ```bash
   git commit -am "新機能を追加"
   ```
4. ブランチをプッシュします：
   ```bash
   git push origin feature/my-new-feature
   ```
5. 変更を説明するPull Requestを開きます。

既存のスタイルと一致するようにコードを維持し、可能な場合はテストを含めてください。

---

## 📄 ライセンス

このプロジェクトは **GNU General Public License v3.0 (GPL-3.0)** の下でライセンスされています。  
詳細については [LICENSE](LICENSE) ファイルを参照してください。

---

## 🙏 謝辞

- ドキュメントとツールを提供してくれたGBAホームブルーおよびROMハッキングコミュニティに感謝します。
- クラシックなピクセルアートエディタとGBA開発ユーティリティからインスピレーションを受けています。

---

## 📩 連絡先とサポート

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

このツールが役に立つと感じ、その開発をサポートしたい場合は、コーヒーをご馳走することをご検討ください！

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
