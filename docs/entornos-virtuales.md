# Entornos virtuales por plataforma

[Índice](../README.md) · [Windows con WSL](instalacion-wsl.md) · [Linux y macOS](instalacion-linux-macos.md) · [Polars GPU NVIDIA](polars-gpu.md)

El entorno **base CPU** se llama `.venv` y utiliza Python **3.12** en todas las plataformas. Git, Java y los controladores son herramientas del sistema; las bibliotecas Python se instalan dentro del entorno. El entorno no se copia ni se comparte entre Windows, WSL, Linux, macOS, equipos o arquitecturas.

La ampliación NVIDIA se documenta por separado y utiliza `.venv-gpu` en Linux/WSL 2. No es un prerrequisito del curso ni de la guía rápida de Polars.

## 1. Elegir dónde ejecutar

| Plataforma | Terminal y entorno | Alcance |
|---|---|---|
| Windows con WSL 2 | Bash de Ubuntu; `.venv/bin/python` | Ruta de referencia para el curso completo. GPU opcional con preparación específica. |
| Linux | Bash/Zsh; `.venv/bin/python` | Curso completo; GPU opcional en una combinación NVIDIA admitida. |
| macOS Apple Silicon | Terminal nativa ARM64; `.venv/bin/python` | Curso en CPU; Python, Java y paquetes deben ser ARM64. |
| macOS Intel | Terminal x86_64; `.venv/bin/python` | Curso en CPU, sujeto a disponibilidad de paquetes para la versión de macOS. |
| Windows nativo | PowerShell; `.venv\Scripts\python.exe` | Alternativa CPU para las guías de pandas, Polars y DuckDB. Para el curso completo y GPU, seguir WSL. |

Usar un clon distinto para Windows nativo y WSL, aunque ambos puedan ver el mismo disco. Un entorno creado por Windows no se activa mediante `source`, y uno de WSL no se activa mediante `Activate.ps1`.

## 2. Crear o activar en Linux, macOS y WSL

Instalar `uv` siguiendo la guía del sistema. Situarse en la raíz del clon, donde están `README.md` y `kit/`. Ejecutar en Bash/Zsh, después de salir de otro entorno con `deactivate` si estaba activo:

```bash
uv python install 3.12
if [ ! -e .venv ]; then
    uv venv --python 3.12 --seed .venv
fi
source .venv/bin/activate
python -c 'import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())'
python -m pip --version
python -m pip install -r kit/requirements.txt -r kit/requirements_pqrs.txt -r kit/requirements_notebooks.txt
python -m pip check
```

El `if` evita recrear el entorno en cada sesión. Si ya existe pero no corresponde a Python 3.12 y a este sistema, no instalar encima: conservarlo con otro nombre y crear uno correcto. No cambiar el Python del sistema ni ejecutar `sudo pip`.

Registrar el kernel con el nombre de la guía del sistema. Para Spark, instalar JDK 21 y `requirements_spark.txt` después, siguiendo esa misma guía. [Creación de entornos con uv](https://docs.astral.sh/uv/pip/environments/).

## 3. Alternativa CPU en Windows nativo

Esta ruta permite practicar las tres guías rápidas; no sustituye la preparación del curso en WSL. Abrir PowerShell, instalar `uv` si falta y volver a abrir la terminal para actualizar PATH:

```powershell
winget install --id=astral-sh.uv -e
```

Con Git instalado, clonar en una carpeta diferente de la usada por WSL:

```powershell
New-Item -ItemType Directory -Force "$HOME\bigdata-native" | Out-Null
Set-Location "$HOME\bigdata-native"
git clone --branch main https://github.com/eshernan/big-data-postgraduate.git
Set-Location big-data-postgraduate
```

Si el clon ya existe, omitir `git clone` y entrar en él. Crear el entorno solo cuando no exista:

```powershell
uv python install 3.12
if (-not (Test-Path .venv)) {
    uv venv --python 3.12 --seed .venv
}
.\.venv\Scripts\python.exe -c "import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())"
.\.venv\Scripts\python.exe -m pip install pandas==2.2.3 numpy==2.2.6 pyarrow==19.0.1 duckdb==1.4.1 -r kit/requirements_pqrs.txt -r kit/requirements_notebooks.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ipykernel install --sys-prefix --name bigdata-windows-cpu --display-name "BigData · Windows CPU · Python 3.12"
.\.venv\Scripts\python.exe -m jupyter lab
```

El uso del ejecutable explícito funciona sin activar scripts de PowerShell. Si la política del equipo lo permite, se puede activar con `.\.venv\Scripts\Activate.ps1` y usar `python`; si está bloqueado, mantener los comandos anteriores sin cambiar la política global. No instalar `requirements_gpu.txt` aquí. [Instalación oficial de uv en Windows](https://docs.astral.sh/uv/getting-started/installation/).

## 4. Verificar el intérprete y el kernel

Ejecutar también dentro del notebook:

```python
import sys
import platform

print(sys.executable)
print(sys.version)
print(platform.system(), platform.machine())
assert sys.version_info[:2] == (3, 12)
assert sys.prefix != sys.base_prefix
```

La ruta debe pertenecer a `.venv`, o a `.venv-gpu` únicamente para la ampliación NVIDIA. Instalar una biblioteca desde otra terminal no cambia el kernel activo. Tras instalar o cambiar dependencias, reiniciar el kernel. Usar `python -m pip` para vincular la instalación al intérprete seleccionado.

## 5. Retomar o reconstruir

En Bash/Zsh, desde la raíz:

```bash
source .venv/bin/activate
python -m pip check
```

En PowerShell se puede usar directamente `.\.venv\Scripts\python.exe`. No ejecutar nuevamente la creación del entorno en cada sesión. Si cambiaron los requisitos, reinstalarlos y ejecutar `pip check`.

Si se movió el repositorio o se cambió de sistema/arquitectura, reconstruir el entorno: cerrar Jupyter, desactivar, conservar la carpeta vieja con otro nombre, crear el entorno nuevo, reinstalar los requisitos y registrar el kernel otra vez. No copiar paquetes manualmente ni borrar entregas o datos al reconstruir. Las carpetas de entornos quedan fuera de Git.

**Alcance de revisión:** se comprueban instrucciones y sintaxis. La instalación limpia completa de todas las plataformas y la ruta GPU requieren pruebas en los equipos correspondientes; `pip check` por sí solo no certifica la ejecución.
