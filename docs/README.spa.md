<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** es una aplicación de escritorio para crear y editar **fondos de Game Boy Advance (GBA)**. Permite convertir imágenes en tilesets y tilemaps compatibles con GBA, editar tiles y paletas visualmente, y exportar assets listos para usar en tus proyectos GBA.

> ⚠️ Esta aplicación está diseñada para desarrolladores, ROM hackers y pixel artists que necesitan control preciso sobre los fondos de GBA.

---

## 🌐 Traducciones

Este README está disponible en los siguientes idiomas:

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Características

- **Conversión de imagen a GBA**
  - Convierte imágenes estándar en tilesets y tilemaps compatibles con GBA.
  - Configura el tamaño de salida y la profundidad de color (4bpp y 8bpp).
  - Vista previa del resultado antes de exportar.

- **Edición de Tileset**
  - Selección y edición visual de tiles.
  - Herramientas de dibujo interactivas sobre la cuadrícula del tilemap.
  - Niveles de zoom del 100% al 800% para edición pixel a pixel.

- **Edición de Paletas**
  - Edita hasta 256 colores por paleta.
  - Sincroniza los cambios de paleta con las vistas previas y los tiles.
  - Reordena, reemplaza o ajusta colores individuales.

- **Pestaña de Vista Previa**
  - Visualiza cómo quedará tu fondo final en una pantalla similar a la GBA.
  - Valida rápidamente las configuraciones de tiles y paletas.

- **Historial de Deshacer / Rehacer**
  - Seguimiento completo del historial de ediciones.
  - Operaciones de deshacer y rehacer con un amplio buffer de historial.

- **Interfaz y barra de estado configurables**
  - Barra de estado detallada con selección de tile, coordenadas del tilemap, ID de paleta, estado de volteo y nivel de zoom.
  - Barra de herramientas contextual por pestaña (vista previa, tiles, paletas).

- **Soporte multiidioma**
  - Sistema de traducción interno (Translator) con selección de idioma mediante configuración.
  - Diseñado para soportar múltiples idiomas en la interfaz.

---

## 🖼️ Capturas de Pantalla

<p align="center"><img width="896" height="590" src="../assets/readme/spa_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="856" height="676" src="../assets/readme/spa_preview.png" alt="Image" /></p>

<p align="center"><img width="856" height="676" src="../assets/readme/spa_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="856" height="676" src="../assets/readme/spa_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Descripción de la Arquitectura

GBA Background Studio está construido con **Python** y **PySide6 / PySide2** (híbrido), y sigue un diseño de interfaz modular:

- **Ventana principal (`GBABackgroundStudio`)**
  - Gestiona el estado de la aplicación (BPP actual, nivel de zoom, selección de tile y paleta).
  - Aloja las pestañas principales y la barra de estado personalizada.
  - Carga y aplica la configuración (incluyendo la última sesión de salida).

- **Pestañas**
  - `PreviewTab` – Vista previa del fondo al estilo GBA.
  - `EditTilesTab` – Herramientas de edición de tiles y tilemap.
  - `EditPalettesTab` – Editor de paletas y herramientas de manipulación de colores.

- **Componentes y utilidades de la interfaz**
  - `MenuBar` – Operaciones de archivo (abrir imagen, exportar archivos, salir) y acciones del editor.
  - `CustomGraphicsView` – `QGraphicsView` extendido con interacción basada en tiles (hover, dibujo, selección, vista previa de pegado).
  - `TilemapUtils` – Lógica compartida para la interacción y selección del tilemap.
  - `HistoryManager` – Gestión de deshacer/rehacer para operaciones del editor.
  - `HoverManager`, `GridManager` – Ayudas visuales para efectos de hover y superposiciones de cuadrícula.
  - `Translator`, `ConfigManager` – Localización y configuración persistente.

---

## 📦 Instalación

### Opción 1 — Instalador (recomendado)

Descarga la última versión desde [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases):

| Instalador | Python | SO |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | Incluido (no requiere instalación) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | Incluido (no requiere instalación) | Windows 7 / 8 / 8.1 |

Solo ejecuta el instalador y lanza la aplicación — no se necesita Python ni pip.

---

### Opción 2 — Ejecutar desde el código fuente

#### Requisitos

| Entorno | Python | Backend Qt | SO |
|---|---|---|---|
| **Moderno** | 3.10+ | PySide6 (auto) | Windows 10/11, macOS 11+, Linux |
| **Legacy** | 3.8 / 3.9 | PySide2 5.15.2 (auto) | Windows 7 / 8 / 8.1 |

La aplicación detecta automáticamente qué backend Qt usar según tu versión de Python — no se necesita configuración manual.

#### Dependencias

```bash
pip install -r requirements.txt
```

`requirements.txt` instala automáticamente el backend Qt correcto:
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

Otras dependencias: `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ Soporte para Sistemas Legacy (Windows 7 / 8 / 8.1)

La interfaz gráfica completa funciona en Windows 7 y versiones posteriores. Usa **Python 3.8** y `requirements.txt` instalará automáticamente **PySide2 5.15.2**.

Alternativamente, el **Asistente de Línea de Comandos Multilingüe** (`GBA_Studio_Wizard.bat`) está disponible para conversiones por lotes sin la interfaz gráfica, y funciona en cualquier versión de Windows con Python 3.8+:

1. Dirígete a la raíz del proyecto.
2. Ejecuta **`GBA_Studio_Wizard.bat`**.
3. Selecciona tu idioma (18 idiomas soportados).
4. Sigue las instrucciones paso a paso para convertir tu imagen.

---

## 🚀 Primeros Pasos

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Crea y activa un entorno virtual** (opcional pero recomendado)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   ```

3. **Instala las dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación**

   ```bash
   python main.py
   ```

---

## 🧭 Uso Básico

1. **Abrir una Imagen**
   - Ve a **Archivo → Abrir imagen** o presiona `Ctrl+O`.
   - Selecciona la imagen que deseas convertir en un fondo GBA.

2. **Configurar la Conversión**
   - Selecciona el **Modo de Fondo** (**Modo Texto** o **Modo Rotación/Escalado**).
   - Elige la(s) paleta(s) o Tilemap a usar (solo para **Modo Texto 4bpp**).
   - Establece el color que se usará como transparente.
   - Ajusta el tamaño de salida y otros parámetros necesarios.
   - Haz clic en **Convertir** y la aplicación se encargará del resto.

3. **Editar Tiles**
   - Cambia a la pestaña **Editar Tiles**.
   - Usa la vista del tilemap para dibujar y modificar tiles individuales.
   - Selecciona áreas completas para copiar, cortar, pegar o rotar grupos de tiles.
   - Sincroniza los cambios en tiempo real para ver resultados instantáneos.
   - Ajusta el nivel de **Zoom** para una precisión perfecta.
   - Optimiza o Desoptimiza tilesets para ahorrar espacio o garantizar compatibilidad con el hardware.
   - Convierte assets entre los formatos **4bpp** y **8bpp**.
   - Cambia entre **Modo Texto** y **Modo Rotación/Escalado** sin problemas.

4. **Editar Paletas**
   - Ve a la pestaña **Editar Paletas**.
   - Modifica los colores en la cuadrícula de paletas y ajústalos con el editor de colores.
   - Selecciona áreas específicas o todos los tiles pertenecientes a una paleta para reemplazarlos o intercambiarlos con otra.

5. **Vista Previa del Fondo**
   - Cambia a la pestaña **Vista Previa** para una representación fiel de cómo se verá en una GBA real.
   - Verifica que tus configuraciones de tiles y paletas funcionen perfectamente juntas.

6. **Exportar Assets**
   - Ve a **Archivo → Exportar archivos** o presiona `Ctrl+E`.
   - Exporta tilesets, tilemaps y paletas en formatos listos para ser integrados en tu cadena de herramientas de desarrollo GBA.
   - Exporta assets individuales por separado desde sus respectivos menús si es necesario.

---

## 🔄 Deshacer / Rehacer

La aplicación rastrea tus acciones de edición usando un **gestor de historial**:

- **Deshacer** – revierte la última operación.
- **Rehacer** – vuelve a aplicar una operación que fue deshecha.

El sistema de historial mantiene un buffer de estados recientes, incluyendo ediciones de tiles, cambios de paleta y operaciones de tilemap.

---

## ⚙️ Configuración y Localización

### Configuración

La aplicación usa un gestor de configuración para almacenar ajustes como:

- Último idioma utilizado
- Último nivel de zoom utilizado
- Si cargar la última salida al iniciar
- Otras preferencias de interfaz y editor

La configuración se carga al iniciar y se aplica a la interfaz y los menús.

### Localización

Un componente `Translator` gestiona los textos de la interfaz:

- El idioma predeterminado se configura a través de los ajustes.
- Los archivos de traducción pueden añadirse o editarse para soportar más idiomas.
- Los textos de la interfaz (menús, diálogos, etiquetas) pasan por el traductor.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si deseas ayudar:

1. Haz un fork de este repositorio.
2. Crea una rama de características:
   ```bash
   git checkout -b feature/mi-nueva-caracteristica
   ```
3. Confirma tus cambios:
   ```bash
   git commit -am "Añadir mi nueva característica"
   ```
4. Sube la rama:
   ```bash
   git push origin feature/mi-nueva-caracteristica
   ```
5. Abre un Pull Request describiendo tus cambios.

Por favor, mantén tu código consistente con el estilo existente e incluye pruebas cuando sea posible.

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia Pública General GNU v3.0 (GPL-3.0)**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- Gracias a las comunidades de homebrew y ROM hacking de GBA por su documentación y herramientas.
- Inspirado en editores clásicos de pixel art y utilidades de desarrollo para GBA.

---

## 📩 Contacto y Soporte

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Si encuentras esta herramienta útil y deseas apoyar su desarrollo, ¡considera invitarme un café!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
