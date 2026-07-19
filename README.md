# Organización de la carpeta de Descargas

Guía práctica + scripts listos para usar para **revisar tipos de archivo, aplicar una
estructura de carpetas lógica, eliminar duplicados/basura y automatizar la organización
futura**. Cubre **Windows, macOS y Linux**.

> Principio de seguridad: los scripts de este repo **no borran nada de forma permanente**.
> Los archivos se mueven a la **Papelera** o a una carpeta de cuarentena `_Para_revisar`,
> y cada acción queda en un **registro (log)**. Tú decides el borrado definitivo.

---

## 1. Diagnóstico rápido: ¿qué tienes en Descargas?

Antes de mover nada, conviene ver el panorama (qué tipos y cuánto pesan).

**Windows (PowerShell):**
```powershell
Get-ChildItem "$HOME\Downloads" -File |
  Group-Object Extension |
  Select-Object Name, Count, @{n='MB';e={[math]::Round(($_.Group|Measure-Object Length -Sum).Sum/1MB,1)}} |
  Sort-Object MB -Descending | Format-Table -Auto
```

**macOS / Linux (bash):**
```bash
cd ~/Downloads && find . -maxdepth 1 -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
du -sh ~/Downloads          # tamaño total
```

---

## 2. Estructura de carpetas propuesta

Una estructura por **tipo + intención**, plana (máx. 2 niveles) para que sea fácil de mantener:

```
Descargas/
├── Documentos/        # PDF, DOCX, XLSX, PPTX, TXT, ODT...
├── Imagenes/          # JPG, PNG, HEIC, WEBP, SVG, GIF...
├── Videos/            # MP4, MOV, MKV, AVI...
├── Audio/             # MP3, WAV, M4A...
├── Instaladores/      # EXE, MSI, DMG, PKG, DEB, AppImage...
├── Comprimidos/       # ZIP, RAR, 7Z, TAR, GZ...
├── Codigo/            # ZIP de proyectos, .py, .js, .sql, .json...
├── _Para_revisar/     # duplicados y dudosos (cuarentena, NO borrar aún)
└── _Archivo/          # cosas que quieres conservar pero sacar de en medio
```

**Recomendación para tu caso (administración de fincas):** dentro de `Documentos/` añade
subcarpetas por comunidad o por tipo de gestión, p. ej. `Documentos/Facturas`,
`Documentos/Actas`, `Documentos/Presupuestos`. Los scripts admiten reglas personalizadas
(ver sección 5).

---

## 3. Prioridad de limpieza (qué eliminar primero)

Ataca en este orden, de mayor a menor seguridad:

1. **Temporales y basura evidente** — `.tmp`, `.crdownload`, `.part`, `.partial`,
   descargas a medias, `Thumbs.db`, `.DS_Store`. Casi siempre seguros de eliminar.
2. **Duplicados exactos** — mismo contenido (hash idéntico). Se conserva **una** copia y
   el resto va a `_Para_revisar`. Detecta también los típicos `archivo (1).pdf`,
   `archivo (2).pdf`.
3. **Instaladores ya usados** — `.exe`, `.msi`, `.dmg` de programas que ya instalaste.
   Ocupan mucho y rara vez se reutilizan.
4. **Archivos antiguos** — nada tocado en > 6–12 meses: revisa si aún los necesitas.
5. **Comprimidos ya extraídos** — el `.zip` cuya carpeta ya existe descomprimida.

Los scripts marcan 1 y 2 automáticamente (a Papelera / cuarentena) y **listan** 3–5 para
que decidas tú.

---

## 4. Pasos concretos (hazlo una vez)

1. **Copia de seguridad rápida** antes de la primera pasada:
   comprime Descargas en un ZIP o cópiala a un disco externo/nube.
2. **Ejecuta en modo simulación** (`-DryRun` / `--dry-run`): no mueve nada, solo muestra
   lo que haría. Revisa el resultado.
   > Nota: en simulación un mismo archivo puede aparecer en varias líneas (como duplicado
   > *y* como movimiento), porque nada se mueve realmente entre etapas. En modo real no
   > pasa: cada etapa mueve antes de la siguiente.
3. **Ejecuta en modo real**: organiza por tipo, aísla duplicados y temporales.
4. **Revisa `_Para_revisar`** con calma y vacía la Papelera cuando estés seguro.
5. **Programa la automatización** (sección 6) para que se mantenga solo.

---

## 5. Scripts incluidos en este repo

| Script | Sistema | Qué hace |
|--------|---------|----------|
| `scripts/organizar-descargas.ps1` | Windows | Clasifica por tipo, detecta duplicados por hash, temporales a Papelera, log. |
| `scripts/organizar-descargas.sh`  | macOS / Linux | Igual, en bash. Usa `~/.local/share/Trash` (Linux) o Papelera de macOS. |
| `scripts/reglas.example.json`     | Todos | Reglas de clasificación editables (extensión → carpeta). |

Uso básico:

```powershell
# Windows — primero simula, luego ejecuta
powershell -ExecutionPolicy Bypass -File scripts\organizar-descargas.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File scripts\organizar-descargas.ps1
```

```bash
# macOS / Linux — primero simula, luego ejecuta
bash scripts/organizar-descargas.sh --dry-run
bash scripts/organizar-descargas.sh
```

---

## 6. Automatizar la organización futura

### Windows — Programador de tareas
Ejecuta el script cada día a una hora fija:
```powershell
$acc = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$HOME\carpetaslocales\scripts\organizar-descargas.ps1`""
$trg = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "Organizar Descargas" -Action $acc -Trigger $trg -Description "Ordena la carpeta de Descargas"
```

### macOS — Carpetas inteligentes / launchd / Hazel
- **Sin instalar nada:** app *Automator* → *Acción de carpeta* sobre Descargas.
- **Programado:** un `launchd` `.plist` que ejecute el `.sh` cada X horas.
- **Recomendado (de pago, potentísimo):** **Hazel** — reglas visuales "si extensión = PDF,
  mover a Documentos", detección de duplicados y limpieza por antigüedad, en tiempo real.

### Linux — systemd timer
```ini
# ~/.config/systemd/user/organizar-descargas.timer
[Unit]
Description=Organizar Descargas a diario
[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true
[Install]
WantedBy=timers.target
```
Con su correspondiente `.service` que lance el `.sh`. Activar con
`systemctl --user enable --now organizar-descargas.timer`.

---

## 7. Herramientas y atajos recomendados

**Multiplataforma**
- **[organize-tool](https://github.com/tfeldmann/organize)** (Python): motor de reglas en YAML,
  ideal para automatizar clasificación y limpieza. `pip install organize-tool`.
- **[Czkawka](https://github.com/qarmin/czkawka)**: buscador de duplicados, imágenes similares
  y archivos vacíos. Gratuito y muy rápido.
- **[dupeGuru](https://dupeguru.voltaicideas.net/)**: duplicados por contenido, con vista previa.

**Windows**
- **File Juggler** o **DropIt**: reglas automáticas de ordenación de carpetas.
- Atajo: `Win + E` (Explorador), ordenar por *Tipo* o *Fecha* para revisión manual rápida.

**macOS**
- **Hazel** (el estándar de oro para esto), **Gemini 2** (duplicados).
- Atajo: en Finder, `Cmd + J` → activar "Ordenar por" → Tipo/Fecha.

**Linux**
- **organize-tool**, **Czkawka**, o `rmlint` para duplicados por línea de comandos.

---

## 8. Buenas prácticas para no volver al caos

- **Descargas es zona de tránsito, no de almacén.** Vacíala con frecuencia.
- Guarda lo importante en su sitio final (Documentos, nube) **el mismo día**.
- Deja la automatización corriendo a diario: el desorden no se acumula.
- Revisa `_Para_revisar` una vez a la semana; borra la Papelera al confirmar.
