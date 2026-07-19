<#
.SYNOPSIS
    Clasifica la carpeta de Descargas por el CONTENIDO del fichero, no solo por extension.
.DESCRIPTION
    - Lee el texto dentro de PDFs (si hay 'pdftotext' de poppler), TXT/CSV y el nombre del fichero.
    - Aplica reglas por palabras clave -> subcarpeta destino (Facturas, Actas, etc.).
    - Si no reconoce el contenido, cae en la clasificacion por tipo.
    - No borra nada. Modo simulacion con -DryRun.
.NOTES
    Para leer el contenido de los PDF instala poppler (incluye pdftotext.exe):
      winget install oschwartz10612.Poppler   (o descarga poppler-windows y anade su \bin al PATH)
    Sin poppler, los PDF se clasifican por su nombre de fichero.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File clasificar-por-contenido.ps1 -DryRun
    powershell -ExecutionPolicy Bypass -File clasificar-por-contenido.ps1
#>
param(
    [string]$Path = "$HOME\Downloads",
    [switch]$DryRun
)

if (-not (Test-Path $Path)) { Write-Error "No existe la carpeta: $Path"; exit 1 }

$log = Join-Path $Path ("_clasificacion_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))
$prefijo = if ($DryRun) { "[SIMULACION] " } else { "" }
function Registrar($msg) { $l = "$prefijo$msg"; Write-Host $l; if (-not $DryRun) { Add-Content -Path $log -Value $l } }

$tienePdftotext = [bool](Get-Command pdftotext -ErrorAction SilentlyContinue)
if (-not $tienePdftotext) { Registrar "AVISO: no se encontro 'pdftotext'; los PDF se clasifican solo por su nombre. Instala poppler para leer su contenido." }

# Reglas de CONTENIDO: primera coincidencia gana. Amplia libremente.
$ReglasContenido = @(
    @{ Carpeta='Documentos\Facturas';     Claves=@('factura','n. factura','nº factura','importe total','base imponible','iva') },
    @{ Carpeta='Documentos\Actas';        Claves=@('acta','junta de propietarios','orden del dia','se acuerda') },
    @{ Carpeta='Documentos\Presupuestos'; Claves=@('presupuesto','oferta economica','partida','mediciones','coste estimado') },
    @{ Carpeta='Documentos\Contratos';    Claves=@('contrato','arrendamiento','clausula','clausulado','firmante') },
    @{ Carpeta='Documentos\Seguros';      Claves=@('poliza','seguro','aseguradora','cobertura','siniestro','prima anual') },
    @{ Carpeta='Documentos\Impuestos';    Claves=@('modelo 3','modelo 1','agencia tributaria','impuesto','declaracion','liquidacion','irpf') },
    @{ Carpeta='Documentos\Nominas';      Claves=@('nomina','salario','retribucion','seguridad social','cotizacion') },
    @{ Carpeta='Documentos\Certificados'; Claves=@('certificado','certificado energetico','itv','inspeccion tecnica') },
    @{ Carpeta='Documentos\Recibos';      Claves=@('recibo','domiciliacion','cargo en cuenta','adeudo') },
    @{ Carpeta='Documentos\Bancos';       Claves=@('extracto','movimientos','saldo','cuenta corriente','banco') }
)

$ReglasTipo = @{
    '.pdf'='Documentos\Otros'; '.doc'='Documentos\Otros'; '.docx'='Documentos\Otros'; '.odt'='Documentos\Otros';
    '.txt'='Documentos\Otros'; '.rtf'='Documentos\Otros'; '.xls'='Documentos\Otros'; '.xlsx'='Documentos\Otros';
    '.csv'='Documentos\Otros'; '.ppt'='Documentos\Otros'; '.pptx'='Documentos\Otros';
    '.jpg'='Imagenes'; '.jpeg'='Imagenes'; '.png'='Imagenes'; '.gif'='Imagenes'; '.heic'='Imagenes'; '.webp'='Imagenes'; '.svg'='Imagenes';
    '.mp4'='Videos'; '.mov'='Videos'; '.mkv'='Videos'; '.avi'='Videos';
    '.mp3'='Audio'; '.wav'='Audio'; '.m4a'='Audio'; '.flac'='Audio';
    '.exe'='Instaladores'; '.msi'='Instaladores'; '.dmg'='Instaladores';
    '.zip'='Comprimidos'; '.rar'='Comprimidos'; '.7z'='Comprimidos';
    '.py'='Codigo'; '.js'='Codigo'; '.sql'='Codigo'; '.json'='Codigo'; '.html'='Codigo'
}

function Quitar-Acentos($s) {
    $s = $s.ToLower()
    $map = @{ 'á'='a';'é'='e';'í'='i';'ó'='o';'ú'='u';'à'='a';'è'='e';'ì'='i';'ò'='o';'ù'='u';'ä'='a';'ë'='e';'ï'='i';'ö'='o';'ü'='u';'ñ'='n' }
    foreach ($k in $map.Keys) { $s = $s -replace $k, $map[$k] }
    return $s
}

function Texto-De($file) {
    $contenido = ""
    switch ($file.Extension.ToLower()) {
        '.pdf'  { if ($tienePdftotext) { $contenido = (& pdftotext -q -l 3 $file.FullName - 2>$null) -join "`n" } }
        {$_ -in '.txt','.csv','.md','.log','.json'} {
            $contenido = Get-Content -Path $file.FullName -TotalCount 400 -ErrorAction SilentlyContinue | Out-String
        }
    }
    return (Quitar-Acentos("$($file.Name)`n$contenido"))
}

Registrar "=== Clasificando por contenido: $Path ==="

$archivos = Get-ChildItem -Path $Path -File | Where-Object { $_.Name -notlike '_clasificacion_*.log' -and $_.Name -notlike '_organizacion_*.log' }
foreach ($f in $archivos) {
    $txt = Texto-De $f
    $sub = $null; $motivo = 'contenido'
    foreach ($regla in $ReglasContenido) {
        foreach ($clave in $regla.Claves) {
            if ($txt.Contains($clave)) { $sub = $regla.Carpeta; break }
        }
        if ($sub) { break }
    }
    if (-not $sub) {
        $motivo = 'tipo'
        $sub = if ($ReglasTipo.ContainsKey($f.Extension.ToLower())) { $ReglasTipo[$f.Extension.ToLower()] } else { '_Para_revisar' }
    }

    $destino = Join-Path $Path $sub
    if (-not $DryRun -and -not (Test-Path $destino)) { New-Item -ItemType Directory -Path $destino -Force | Out-Null }
    $final = Join-Path $destino $f.Name
    $i = 1
    while ((Test-Path $final) -and -not $DryRun) {
        $final = Join-Path $destino ("{0}_{1}{2}" -f $f.BaseName, $i, $f.Extension); $i++
    }
    Registrar "[$motivo] $($f.Name)  ->  $sub\"
    if (-not $DryRun) { Move-Item -Path $f.FullName -Destination $final }
}

Registrar "=== Hecho. Revisa las subcarpetas y _Para_revisar. Nada se ha borrado. ==="
if (-not $DryRun) { Write-Host "Log guardado en: $log" }
