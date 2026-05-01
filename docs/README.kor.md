<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio**는 **Game Boy Advance (GBA) 배경**을 만들고 편집하기 위한 데스크톱 애플리케이션입니다. 이미지를 GBA 호환 타일셋과 타일맵으로 변환하고, 타일과 팔레트를 시각적으로 편집하며, GBA 프로젝트에 바로 사용할 수 있는 에셋을 내보낼 수 있습니다.

> ⚠️ 이 애플리케이션은 GBA 배경을 정밀하게 제어해야 하는 개발자, ROM 해커, 픽셀 아티스트를 위해 설계되었습니다.

---

## 🌐 번역

이 README는 다음 언어로 제공됩니다:

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ 기능

- **이미지에서 GBA로 변환**
  - 표준 이미지를 GBA 호환 타일셋과 타일맵으로 변환합니다.
  - 출력 크기와 색상 깊이(4bpp 및 8bpp)를 설정합니다.
  - 내보내기 전에 결과를 미리 봅니다.

- **타일 편집**
  - 타일의 시각적 선택 및 편집.
  - 타일맵 그리드에서 인터랙티브 드로잉 도구.
  - 픽셀 단위 편집을 위한 100%에서 800%까지의 줌 레벨.

- **팔레트 편집**
  - 팔레트당 최대 256색 편집.
  - 팔레트 변경 사항을 미리보기 및 타일과 동기화.
  - 개별 색상 재정렬, 교체 또는 조정.

- **미리보기 탭**
  - GBA와 유사한 화면에서 최종 배경이 어떻게 보일지 시각화.
  - 타일 및 팔레트 구성을 빠르게 검증.

- **실행 취소/다시 실행 기록**
  - 편집 기록의 완전한 추적.
  - 넓은 기록 버퍼를 가진 실행 취소 및 다시 실행 작업.

- **구성 가능한 인터페이스 및 상태 표시줄**
  - 타일 선택, 타일맵 좌표, 팔레트 ID, 대칭 상태, 줌 레벨이 포함된 상세 상태 표시줄.
  - 탭별 컨텍스트 도구 모음(미리보기, 타일, 팔레트).

- **다국어 지원**
  - 설정을 통한 언어 선택이 있는 내부 번역 시스템(Translator).
  - 인터페이스에서 여러 언어를 지원하도록 설계.

---

## 🖼️ 스크린샷

<p align="center"><img width="896" height="590" src="../assets/readme/kor_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="793" height="676" src="../assets/readme/kor_preview.png" alt="Image" /></p>

<p align="center"><img width="793" height="676" src="../assets/readme/kor_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="793" height="676" src="../assets/readme/kor_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ 아키텍처 설명

GBA Background Studio는 **Python**과 **PySide6 / PySide2** (하이브리드)로 구축되었으며, 모듈식 인터페이스 디자인을 따릅니다:

- **메인 윈도우 (`GBABackgroundStudio`)**
  - 애플리케이션 상태(현재 BPP, 줌 레벨, 타일 및 팔레트 선택)를 관리합니다.
  - 메인 탭과 커스텀 상태 표시줄을 호스팅합니다.
  - 구성을 로드하고 적용합니다(마지막 출력 세션 포함).

- **탭**
  - `PreviewTab` – GBA 스타일 배경 미리보기.
  - `EditTilesTab` – 타일 및 타일맵 편집 도구.
  - `EditPalettesTab` – 팔레트 편집기 및 색상 조작 도구.

- **인터페이스 컴포넌트 및 유틸리티**
  - `MenuBar` – 파일 작업(이미지 열기, 파일 내보내기, 종료) 및 편집기 작업.
  - `CustomGraphicsView` – 타일 기반 인터랙션이 있는 확장된 `QGraphicsView`.
  - `TilemapUtils` – 타일맵 인터랙션 및 선택을 위한 공유 로직.
  - `HistoryManager` – 편집기 작업을 위한 실행 취소/다시 실행 관리.
  - `HoverManager`, `GridManager` – 호버 효과 및 그리드 오버레이를 위한 시각적 도우미.
  - `Translator`, `ConfigManager` – 로컬라이제이션 및 영구 구성.

---

## 📦 설치

### 옵션 1 — 설치 프로그램 (권장)

[GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases)에서 최신 버전을 다운로드하세요:

| 설치 프로그램 | Python | 운영 체제 |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | 내장 (별도 설치 불필요) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | 내장 (별도 설치 불필요) | Windows 7 / 8 / 8.1 |

설치 프로그램을 실행하고 앱을 시작하기만 하면 됩니다 — Python이나 pip가 필요 없습니다.

---

### 옵션 2 — 소스에서 실행

#### 요구 사항

| 환경 | Python | Qt 백엔드 | 운영 체제 |
|---|---|---|---|
| **최신** | 3.10+ | PySide6 (자동) | Windows 10/11, macOS 11+, Linux |
| **레거시** | 3.8 / 3.9 | PySide2 5.15.2 (자동) | Windows 7 / 8 / 8.1 |

애플리케이션은 Python 버전에 따라 사용할 Qt 백엔드를 자동으로 감지합니다 — 수동 설정이 필요 없습니다.

#### 종속성

```bash
pip install -r requirements.txt
```

`requirements.txt`는 올바른 Qt 백엔드를 자동으로 설치합니다:
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

기타 종속성: `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ 레거시 시스템 지원 (Windows 7 / 8 / 8.1)

전체 그래픽 인터페이스는 Windows 7 이상에서 실행됩니다. **Python 3.8**을 사용하면 `requirements.txt`가 자동으로 **PySide2 5.15.2**를 설치합니다.

또한 **다국어 명령줄 마법사** (`GBA_Studio_Wizard.bat`)는 GUI 없이 일괄 변환에 사용할 수 있으며, Python 3.8+이 설치된 모든 Windows 버전에서 작동합니다:

1. 프로젝트 루트 디렉토리로 이동합니다.
2. **`GBA_Studio_Wizard.bat`**를 실행합니다.
3. 언어를 선택합니다 (18개 언어 지원).
4. 단계별 지침에 따라 이미지를 변환합니다.

---

## 🚀 시작하기

1. **저장소 클론**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **가상 환경 생성 및 활성화** (선택 사항이지만 권장)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows에서: .venv\Scripts\activate
   ```

3. **의존성 설치**

   ```bash
   pip install -r requirements.txt
   ```

4. **애플리케이션 실행**

   ```bash
   python main.py
   ```

---

## 🧭 기본 사용법

1. **이미지 열기**
   - **파일 → 이미지 열기**로 이동하거나 `Ctrl+O`를 누릅니다.
   - GBA 배경으로 변환할 이미지를 선택합니다.

2. **변환 구성**
   - **BG 모드** (**텍스트 모드** 또는 **회전/스케일**)를 선택합니다.
   - 사용할 팔레트 또는 타일맵을 선택합니다 (**텍스트 모드 4bpp** 전용).
   - 투명으로 사용할 색상을 설정합니다.
   - 출력 크기 및 기타 필요한 매개변수를 조정합니다.
   - **변환**을 클릭하면 애플리케이션이 나머지를 처리합니다.

3. **타일 편집**
   - **타일 편집** 탭으로 전환합니다.
   - 타일맵 뷰를 사용하여 개별 타일을 그리고 수정합니다.
   - 타일 그룹을 복사, 잘라내기, 붙여넣기 또는 회전하기 위해 전체 영역을 선택합니다.
   - 즉각적인 결과를 보기 위해 실시간으로 변경 사항을 동기화합니다.
   - 완벽한 정밀도를 위해 **줌** 레벨을 조정합니다.
   - 공간을 절약하거나 하드웨어 호환성을 보장하기 위해 타일 최적화/최적화 해제합니다.
   - **4bpp**와 **8bpp** 형식 간에 에셋을 변환합니다.
   - **텍스트 모드**와 **회전/스케일** 간에 원활하게 전환합니다.

4. **팔레트 편집**
   - **팔레트 편집** 탭으로 이동합니다.
   - 팔레트 그리드에서 색상을 수정하고 색상 편집기로 조정합니다.
   - 팔레트에 속하는 특정 영역 또는 모든 타일을 선택하여 다른 것으로 교체하거나 교환합니다.

5. **배경 미리보기**
   - 실제 GBA에서 어떻게 보일지 충실하게 표현하기 위해 **미리보기** 탭으로 전환합니다.
   - 타일 및 팔레트 구성이 완벽하게 함께 작동하는지 확인합니다.

6. **에셋 내보내기**
   - **파일 → 파일 내보내기**로 이동하거나 `Ctrl+E`를 누릅니다.
   - GBA 개발 툴체인에 통합할 준비가 된 형식으로 타일셋, 타일맵, 팔레트를 내보냅니다.
   - 필요한 경우 각 메뉴에서 개별 에셋을 별도로 내보냅니다.

---

## 🔄 실행 취소/다시 실행

애플리케이션은 **기록 관리자**를 사용하여 편집 작업을 추적합니다:

- **실행 취소** – 마지막 작업을 되돌립니다.
- **다시 실행** – 취소된 작업을 다시 적용합니다.

기록 시스템은 타일 편집, 팔레트 변경, 타일맵 작업을 포함한 최근 상태의 버퍼를 유지합니다.

---

## ⚙️ 구성 및 로컬라이제이션

### 구성

애플리케이션은 다음과 같은 설정을 저장하기 위해 구성 관리자를 사용합니다:

- 마지막으로 사용한 언어
- 마지막으로 사용한 줌 레벨
- 시작 시 마지막 출력을 로드할지 여부
- 기타 인터페이스 및 편집기 기본 설정

구성은 시작 시 로드되어 인터페이스와 메뉴에 적용됩니다.

### 로컬라이제이션

`Translator` 컴포넌트가 인터페이스 텍스트를 관리합니다:

- 기본 언어는 설정을 통해 구성됩니다.
- 더 많은 언어를 지원하기 위해 번역 파일을 추가하거나 편집할 수 있습니다.
- 인터페이스 텍스트(메뉴, 대화 상자, 레이블)는 번역기를 통해 처리됩니다.

---

## 🤝 기여

기여를 환영합니다! 도움을 주고 싶다면:

1. 이 저장소를 포크합니다.
2. 기능 브랜치를 만듭니다:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 변경 사항을 커밋합니다:
   ```bash
   git commit -am "새 기능 추가"
   ```
4. 브랜치를 푸시합니다:
   ```bash
   git push origin feature/my-new-feature
   ```
5. 변경 사항을 설명하는 Pull Request를 엽니다.

기존 스타일과 일관성을 유지하고 가능한 경우 테스트를 포함해 주세요.

---

## 📄 라이선스

이 프로젝트는 **GNU General Public License v3.0 (GPL-3.0)** 하에 라이선스가 부여됩니다.  
자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 감사의 말

- 문서와 도구를 제공해 준 GBA 홈브루 및 ROM 해킹 커뮤니티에 감사드립니다.
- 클래식 픽셀 아트 편집기와 GBA 개발 유틸리티에서 영감을 받았습니다.

---

## 📩 연락처 및 지원

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

이 도구가 유용하다고 생각하고 개발을 지원하고 싶다면, 커피 한 잔 사주는 것을 고려해 주세요!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
