# Ruta del entorno virtual
$venvPath = ".\AppWeb\AppWeb\venv"

# Verificar si el entorno virtual ya existe
if (Test-Path $venvPath) {
    Write-Host "El entorno virtual ya existe. Activandolo..."
    & "$venvPath\Scripts\Activate.ps1"
} else {
    # Crear el entorno virtual si no existe
    Write-Host "El entorno virtual no existe. Creandolo en la carpeta 'AppWeb'..."
    python -m venv $venvPath

    # Activar el entorno virtual después de crearlo
    Write-Host "Activando entorno virtual recién creado..."
    & "$venvPath\Scripts\Activate.ps1"
}

# Siempre instalar dependencias de Django desde requirements.txt si existe
Write-Host "Instalando dependencias de Django..."
if (Test-Path ".\AppWeb\requirements.txt") {
    pip install -r ".\AppWeb\requirements.txt"
} else {
    Write-Host "No se encontro el archivo requirements.txt"
}
cd .\AppWeb
# Instalar dependencias de npm en la carpeta "AppWeb"

Write-Host "Instalacion completada. ¡Ya estas listo para trabajar!"
