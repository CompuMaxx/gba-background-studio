<p align="center"><img width="1868" height="560" src="../assets/readme/banner.png" alt="Image" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** è un'applicazione desktop per creare e modificare **sfondi per Game Boy Advance (GBA)**. Permette di convertire immagini in tileset e tilemap compatibili con GBA, modificare visivamente quadri e palette, ed esportare asset pronti all'uso per i tuoi progetti GBA.

> ⚠️ Questa applicazione è progettata per sviluppatori, ROM hacker e pixel artist che necessitano di un controllo preciso sugli sfondi GBA.

---

## 🌐 Traduzioni

Questo README è disponibile nelle seguenti lingue:

<p align="center">
  <a href="../README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jpn.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Caratteristiche

- **Conversione da immagine a GBA**
  - Converte immagini standard in tileset e tilemap compatibili con GBA.
  - Configura la dimensione di output e la profondità di colore (4bpp e 8bpp).
  - Anteprima del risultato prima dell'esportazione.

- **Modifica Quadri**
  - Selezione e modifica visiva dei quadri.
  - Strumenti di disegno interattivi sulla griglia della tilemap.
  - Livelli di zoom dal 100% all'800% per la modifica pixel per pixel.

- **Modifica Palette**
  - Modifica fino a 256 colori per palette.
  - Sincronizza le modifiche della palette con le anteprime e i quadri.
  - Riordina, sostituisce o regola i colori individuali.

- **Scheda Anteprima**
  - Visualizza come apparirà il tuo sfondo finale su uno schermo simile al GBA.
  - Valida rapidamente le configurazioni di quadri e palette.

- **Cronologia Annulla/Ripristina**
  - Tracciamento completo della cronologia delle modifiche.
  - Operazioni di annullamento e ripristino con un ampio buffer della cronologia.

- **Interfaccia e barra di stato configurabili**
  - Barra di stato dettagliata con selezione del quadro, coordinate della tilemap, ID palette, stato di specchiamento e livello di zoom.
  - Barra degli strumenti contestuale per scheda (anteprima, quadri, palette).

- **Supporto multilingua**
  - Sistema di traduzione interno (Translator) con selezione della lingua tramite impostazioni.
  - Progettato per supportare più lingue nell'interfaccia.

---

## 🖼️ Screenshot

<p align="center"><img width="896" height="590" src="../assets/readme/ita_conversion_interfaz.png" alt="Image" /></p>

<p align="center"><img width="956" height="676" src="../assets/readme/ita_preview.png" alt="Image" /></p>

<p align="center"><img width="956" height="676" src="../assets/readme/ita_edit_tiles.png" alt="Image" /></p>

<p align="center"><img width="956" height="676" src="../assets/readme/ita_edit_palettes.png" alt="Image" /></p>

---

## 🏗️ Descrizione dell'Architettura

GBA Background Studio è costruito con **Python** e **PySide6 / PySide2** (ibrido), seguendo un design dell'interfaccia modulare:

- **Finestra principale (`GBABackgroundStudio`)**
  - Gestisce lo stato dell'applicazione (BPP corrente, livello di zoom, selezione di quadro e palette).
  - Ospita le schede principali e la barra di stato personalizzata.
  - Carica e applica la configurazione (inclusa l'ultima sessione di output).

- **Schede**
  - `PreviewTab` – Anteprima dello sfondo in stile GBA.
  - `EditTilesTab` – Strumenti di modifica di quadri e tilemap.
  - `EditPalettesTab` – Editor di palette e strumenti di manipolazione dei colori.

- **Componenti e utilità dell'interfaccia**
  - `MenuBar` – Operazioni sui file (apri immagine, esporta file, esci) e azioni dell'editor.
  - `CustomGraphicsView` – `QGraphicsView` esteso con interazione basata sui quadri.
  - `TilemapUtils` – Logica condivisa per l'interazione e la selezione della tilemap.
  - `HistoryManager` – Gestione annulla/ripristina per le operazioni dell'editor.
  - `HoverManager`, `GridManager` – Aiuti visivi per effetti hover e sovrapposizioni della griglia.
  - `Translator`, `ConfigManager` – Localizzazione e configurazione persistente.

---

## 📦 Installazione

### Opzione 1 — Installer (consigliato)

Scarica l'ultima versione da [GitHub Releases](https://github.com/CompuMaxx/gba-background-studio/releases):

| Installer | Python | SO |
|---|---|---|
| `GBABackgroundStudio_Setup.exe` | Incluso (nessuna installazione richiesta) | Windows 10 / 11 |
| `GBABackgroundStudio_Legacy_Setup.exe` | Incluso (nessuna installazione richiesta) | Windows 7 / 8 / 8.1 |

Basta eseguire l'installer e avviare l'app — non è necessario Python o pip.

---

### Opzione 2 — Eseguire dal codice sorgente

#### Requisiti

| Ambiente | Python | Backend Qt | SO |
|---|---|---|---|
| **Moderno** | 3.10+ | PySide6 (auto) | Windows 10/11, macOS 11+, Linux |
| **Legacy** | 3.8 / 3.9 | PySide2 5.15.2 (auto) | Windows 7 / 8 / 8.1 |

L'applicazione rileva automaticamente quale backend Qt utilizzare in base alla versione di Python — nessuna configurazione manuale necessaria.

#### Dipendenze

```bash
pip install -r requirements.txt
```

`requirements.txt` installa automaticamente il backend Qt corretto:
- **Python ≥ 3.10** → `PySide6`
- **Python 3.8 / 3.9** → `PySide2 5.15.2`

Altre dipendenze: `Pillow`, `numpy`, `scipy`, `scikit-learn`, `opencv-python`, `certifi`.

---

### 🏛️ Supporto per Sistemi Legacy (Windows 7 / 8 / 8.1)

L'interfaccia grafica completa funziona su Windows 7 e versioni successive. Usa **Python 3.8** e `requirements.txt` installerà automaticamente **PySide2 5.15.2**.

In alternativa, il **Assistente da Riga di Comando Multilingue** (`GBA_Studio_Wizard.bat`) è disponibile per conversioni batch senza l'interfaccia grafica, e funziona su qualsiasi versione di Windows con Python 3.8+:

1. Naviga alla radice del progetto.
2. Esegui **`GBA_Studio_Wizard.bat`**.
3. Seleziona la tua lingua (18 lingue supportate).
4. Segui le istruzioni passo dopo passo per convertire la tua immagine.

---

## 🚀 Per Iniziare

1. **Clona il repository**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Crea e attiva un ambiente virtuale** (opzionale ma consigliato)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Su Windows: .venv\Scripts\activate
   ```

3. **Installa le dipendenze**

   ```bash
   pip install -r requirements.txt
   ```

4. **Avvia l'applicazione**

   ```bash
   python main.py
   ```

---

## 🧭 Utilizzo di Base

1. **Aprire un'Immagine**
   - Vai su **File → Apri Immagine** o premi `Ctrl+O`.
   - Seleziona l'immagine che vuoi convertire in uno sfondo GBA.

2. **Configurare la Conversione**
   - Seleziona la **Modalità BG** (**Modalità Testo** o **Rotazione/Scalatura**).
   - Scegli la/le palette o la Tilemap da usare (solo per **Modalità Testo 4bpp**).
   - Imposta il colore che verrà usato come trasparente.
   - Regola la dimensione di output e gli altri parametri necessari.
   - Clicca su **Converti** e l'applicazione si occuperà del resto.

3. **Modifica Quadri**
   - Passa alla scheda **Modifica Quadri**.
   - Usa la vista della tilemap per disegnare e modificare quadri individuali.
   - Seleziona aree intere per copiare, tagliare, incollare o ruotare gruppi di quadri.
   - Sincronizza le modifiche in tempo reale per vedere i risultati istantaneamente.
   - Regola il livello di **Zoom** per una precisione perfetta.
   - Ottimizza o Deottimizza Quadri per risparmiare spazio o garantire la compatibilità hardware.
   - Converti gli asset tra i formati **4bpp** e **8bpp**.
   - Passa tra **Modalità Testo** e **Rotazione/Scalatura** senza problemi.

4. **Modifica Palette**
   - Vai alla scheda **Modifica Palette**.
   - Modifica i colori nella griglia delle palette e regolali con l'editor dei colori.
   - Seleziona aree specifiche o tutti i quadri appartenenti a una palette per sostituirli o scambiarli con un'altra.

5. **Anteprima dello Sfondo**
   - Passa alla scheda **Anteprima** per una rappresentazione fedele di come apparirà su un GBA reale.
   - Verifica che le configurazioni di quadri e palette funzionino perfettamente insieme.

6. **Esportare gli Asset**
   - Vai su **File → Esporta File** o premi `Ctrl+E`.
   - Esporta tileset, tilemap e palette in formati pronti per essere integrati nella tua catena di strumenti di sviluppo GBA.
   - Esporta asset individuali separatamente dai rispettivi menu se necessario.

---

## 🔄 Annulla/Ripristina

L'applicazione traccia le tue azioni di modifica usando un **gestore della cronologia**:

- **Annulla** – annulla l'ultima operazione.
- **Ripristina** – riapplica un'operazione annullata.

Il sistema della cronologia mantiene un buffer di stati recenti, incluse le modifiche ai quadri, i cambiamenti di palette e le operazioni sulla tilemap.

---

## ⚙️ Configurazione e Localizzazione

### Configurazione

L'applicazione usa un gestore di configurazione per memorizzare impostazioni come:

- Ultima lingua utilizzata
- Ultimo livello di zoom utilizzato
- Se caricare l'ultimo output all'avvio
- Altre preferenze di interfaccia ed editor

La configurazione viene caricata all'avvio e applicata all'interfaccia e ai menu.

### Localizzazione

Un componente `Translator` gestisce i testi dell'interfaccia:

- La lingua predefinita è configurata tramite le impostazioni.
- I file di traduzione possono essere aggiunti o modificati per supportare più lingue.
- I testi dell'interfaccia (menu, dialoghi, etichette) passano attraverso il traduttore.

---

## 🤝 Contribuire

I contributi sono benvenuti! Se vuoi aiutare:

1. Fai un fork di questo repository.
2. Crea un branch di funzionalità:
   ```bash
   git checkout -b feature/mia-nuova-funzionalita
   ```
3. Conferma le tue modifiche:
   ```bash
   git commit -am "Aggiungere la mia nuova funzionalità"
   ```
4. Invia il branch:
   ```bash
   git push origin feature/mia-nuova-funzionalita
   ```
5. Apri una Pull Request descrivendo le tue modifiche.

Per favore, mantieni il tuo codice coerente con lo stile esistente e includi test quando possibile.

---

## 📄 Licenza

Questo progetto è concesso in licenza sotto la **GNU General Public License v3.0 (GPL-3.0)**.  
Consulta il file [LICENSE](LICENSE) per maggiori dettagli.

---

## 🙏 Ringraziamenti

- Grazie alle comunità homebrew e ROM hacking GBA per la loro documentazione e i loro strumenti.
- Ispirato dagli editor di pixel art classici e dalle utilità di sviluppo GBA.

---

## 📩 Contatto e Supporto

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Se trovi questo strumento utile e vuoi supportarne lo sviluppo, considera di offrirmi un caffè!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
