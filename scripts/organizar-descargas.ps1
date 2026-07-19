<#
.SYNOPSIS
    Organiza la carpeta de Descargas: clasifica por tipo, aísla duplicados y temporales.
.DESCRIPTION
    - No borra de forma permanente: los temporales y duplicados van a la Papelera de reciclaje.
    - Clasifica el resto por tipo en subcarpetas.
    - Registra cada accion en un log.
.PARAMETER Path
    Carpeta a organizar. Por defecto ~\Downloads.
.PARAMETER DryRun
    Modo simulacion: muestra lo que haria sin mover nada.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File organizar-descargas.ps1 -DryRun
    powershell -ExecutionPolicy Bypass -File organizar-descargas.ps1
#>
param(
    [string]$Path = "$HOME\Downloads",
    [switch]$DryRun
)

# --- Reglas: extension -> carpeta destino ---
$Reglas = @{
    '.pdf'='Documentos'; '.doc'='Documentos'; '.docx'='Documentos'; '.odt'='Documentos';
    '.txt'='Documentos'; '.rtf'='Documentos'; '.xls'='Documentos'; '.xlsx'='Documentos';
    '.csv'='Documentos'; '.ppt'='Documentos'; '.pptx'='Documentos';
    '.jpg'='Imagenes'; '.jpeg'='Imagenes'; '.png'='Imagenes'; '.gif'='Imagenes';
    '.heic'='Imagenes'; '.webp'='Imagenes'; '.svg'='Imagenes'; '.bmp'='Imagenes'; '.tiff'='Imagenes';
    '.mp4'='Videos'; '.mov'='Videos'; '.mkv'='Videos'; '.avi'='Videos'; '.wmv'='Videos';
    '.mp3'='Audio'; '.wav'='Audio'; '.m4a'='Audio'; '.flac'='Audio'; '.aac'='Audio';
    '.exe'='Instaladores'; '.msi'='Instaladores'; '.msix'='Instaladores';
    '.zip'='Comprimidos'; '.rar'='Comprimidos'; '.7z'='Comprimidos'; '.tar'='Comprimidos'; '.gz'='Comprimidos';
    '.py'='Codigo'; '.js'='Codigo'; '.ts'='Codigo'; '.sql'='Codigo'; '.json'='Codigo'; '.html'='Codigo'; '.css'='Codigo'
}
$TempExt = @('.tmp','.crdownload','.part','.partial','.download')
$Basura  = @('Thumbs.db','desktop.ini','.DS_Store')

if (-not (Test-Path $Path)) { Write-Error "No existe la carpeta: $Path"; exit 1 }

$log = Join-Path $Path ("_organizacion_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))
$prefijo = if ($DryRun) { "[SIMULACION] " } else { "" }
function Registrar($msg) { $linea = "$prefijo$msg"; Write-Host $linea; if (-not $DryRun) { Add-Content -Path $log -Value $linea } }

Add-Type -AssemblyName Microsoft.VisualBasic
function Enviar-Papelera($archivo) {
    if ($DryRun) { return }
    [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
        $archivo, 'OnlyErrorDialogs', 'SendToRecycleBin')
}

Registrar "=== Organizando $Path ==="

$archivos = Get-ChildItem -Path $Path -File | Where-Object { $_.Name -notlike '_organizacion_*.log' }

# 1) Basura y temporales -> Papelera
foreach ($f in $archivos) {
    if ($TempExt -contains $f.Extension.ToLower() -or $Basura -contains $f.Name) {
        Registrar "Papelera (temporal/basura): $($f.Name)"
        Enviar-Papelera $f.FullName
    }
}

# 2) Duplicados exactos por hash -> Papelera (se conserva la primera copia)
$vistos = @{}
$archivos = Get-ChildItem -Path $Path -File | Where-Object { $_.Name -notlike '_organizacion_*.log' }
foreach ($f in $archivos) {
    if ($TempExt -contains $f.Extension.ToLower() -or $Basura -contains $f.Name) { continue }
    $h = (Get-FileHash $f.FullName -Algorithm SHA256).Hash
    if ($vistos.ContainsKey($h)) {
        Registrar "Papelera (duplicado de '$($vistos[$h])'): $($f.Name)"
        Enviar-Papelera $f.FullName
    } else {
        $vistos[$h] = $f.Name
    }
}

# 3) Clasificar el resto por tipo
$archivos = Get-ChildItem -Path $Path -File | Where-Object { $_.Name -notlike '_organizacion_*.log' }
foreach ($f in $archivos) {
    $destinoNombre = if ($Reglas.ContainsKey($f.Extension.ToLower())) { $Reglas[$f.Extension.ToLower()] } else { '_Para_revisar' }
    $destino = Join-Path $Path $destinoNombre
    if (-not $DryRun -and -not (Test-Path $destino)) { New-Item -ItemType Directory -Path $destino | Out-Null }
    $final = Join-Path $destino $f.Name
    # evitar sobrescritura
    $i = 1
    while ((Test-Path $final) -and -not $DryRun) {
        $final = Join-Path $destino ("{0}_{1}{2}" -f $f.BaseName, $i, $f.Extension); $i++
    }
    Registrar "Mover -> $destinoNombre\: $($f.Name)"
    if (-not $DryRun) { Move-Item -Path $f.FullName -Destination $final }
}

Registrar "=== Hecho. Revisa la carpeta _Para_revisar y vacia la Papelera cuando estes seguro. ==="
if (-not $DryRun) { Write-Host "Log guardado en: $log" }
