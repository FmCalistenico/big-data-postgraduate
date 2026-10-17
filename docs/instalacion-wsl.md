# Instalación del curso: Windows → WSL 2 → Ubuntu-26.04

[Índice](../README.md) · [Datos y ejecución](entorno.md) · [Notebooks](../kit/Notebooks/README.md)

Esta guía es la instalación de referencia para Windows. Para equipos Linux o macOS, seguir la [instalación nativa](instalacion-linux-macos.md). PowerShell se usa para instalar y administrar WSL; Python, Git, Java, bibliotecas, Jupyter y las prácticas se ejecutan **dentro de Ubuntu-26.04**. Las instrucciones antiguas de los anexos históricos no sustituyen esta guía.

## 1. Instalar WSL desde Windows

Usar Windows 11 o Windows 10 versión 2004/build 19041 o posterior con virtualización habilitada. Abrir **PowerShell como administrador** y ejecutar:

```powershell
wsl --install --no-distribution
```

Reiniciar Windows si se solicita. Volver a PowerShell y ejecutar:

```powershell
wsl --update
wsl --set-default-version 2
wsl --list --online
```

Localizar **Ubuntu-26.04** en la columna `NAME`. Instalar esa distribución por su nombre exacto:

```powershell
wsl --install --distribution Ubuntu-26.04
```

Si el listado no contiene `Ubuntu-26.04`, actualizar WSL y volver a consultar; no sustituirla silenciosamente por `Ubuntu` u otra versión. Si la descarga mediante Store falla, la alternativa oficial es `wsl --install --web-download --distribution Ubuntu-26.04`.

Comprobar la instalación y entrar:

```powershell
wsl --list --verbose
wsl --set-default Ubuntu-26.04
wsl --distribution Ubuntu-26.04
```

La columna `VERSION` debe mostrar `2`. Si muestra `1`, salir de Ubuntu y ejecutar en PowerShell `wsl --set-version Ubuntu-26.04 2`. En el primer inicio, crear el usuario y la contraseña de Ubuntu; al escribir la contraseña no aparecen caracteres. Ese usuario se utilizará durante todo el curso.

[Referencia: instalación y comandos WSL de Microsoft](https://learn.microsoft.com/en-us/windows/wsl/basic-commands) · [Instalación de Ubuntu en WSL](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/).

## 2. Entrar a la carpeta base y clonar

`TUPTC` es el usuario Windows del ejemplo: sustituirlo por el nombre real en todas las rutas `/mnt/c/Users/TUPTC/`. No reutilizar esta carpeta para crear un entorno Windows nativo; esa alternativa necesita otro clon.

**Todos los comandos siguientes son Bash, dentro de Ubuntu.** Confirmar la distribución y preparar la carpeta base del curso:

```bash
cat /etc/os-release
whoami
mkdir -p /mnt/c/Users/TUPTC/bigdata
cd /mnt/c/Users/TUPTC/bigdata
pwd
```

`VERSION_ID` debe indicar `26.04`; `pwd` debe mostrar `/mnt/c/Users/TUPTC/bigdata`. Conservar el usuario normal de Ubuntu creado en el paso anterior.

Instalar Git y las herramientas dentro de Ubuntu y pasar a la carpeta base `/mnt/c/Users/TUPTC/bigdata`. Comprobar que esa carpeta existe y es accesible antes de clonar:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates unzip build-essential openjdk-21-jdk
cd /mnt/c/Users/TUPTC/bigdata
git clone --branch main https://github.com/eshernan/big-data-postgraduate.git
cd big-data-postgraduate
git branch --show-current
git status --short
```

El clonado crea la subcarpeta `big-data-postgraduate` dentro de `bigdata`. Si ya existe el repositorio, omitir el clonado y entrar con `cd big-data-postgraduate`. La ruta del repositorio será `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate`. La guía clona siempre la rama principal **`main`**; `git branch --show-current` debe devolver `main`. No usar `sudo git clone`. El repositorio y su `.venv` se guardan en esa carpeta de Windows, pero Python, Java y todos los comandos se ejecutan desde Ubuntu en WSL.

## 3. Python 3.12 y entorno virtual dentro de Ubuntu

Ubuntu 26.04 incluye Python 3.14. El curso mantiene Python 3.12 para las versiones fijadas de pandas, NumPy, PyArrow y demás bibliotecas. Instalarlo mediante `uv`, sin reemplazar `/usr/bin/python3`:

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/instalar-uv-bigdata.sh
sh /tmp/instalar-uv-bigdata.sh
source "$HOME/.local/bin/env"
uv --version
uv python install 3.12
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
if [ ! -e .venv ]; then
    uv venv --python 3.12 --seed .venv
fi
source .venv/bin/activate
python --version
python -c 'import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())'
```

Debe aparecer Python `3.12.x` y un ejecutable dentro de `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate/.venv/`. Se crea **un entorno base CPU**, en la raíz del repositorio. No crear otro `.venv` dentro de `kit/`. Si ya existe el entorno, activar el existente en lugar de recrearlo.

[Ubuntu 26.04: versión de Python](https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/) · [Instalador oficial de uv](https://docs.astral.sh/uv/getting-started/installation/) · [Instalación de versiones de Python con uv](https://docs.astral.sh/uv/guides/install-python/).

El bloque anterior conserva un entorno existente. Si la comprobación de Python falla o la carpeta pertenece a otro sistema, no instalar paquetes encima; seguir la [reconstrucción del entorno](entornos-virtuales.md#5-retomar-o-reconstruir). La única ampliación con entorno separado es GPU; las clases ordinarias siguen usando `.venv`.

## 4. Instalar las bibliotecas y Jupyter

Desde la raíz del repositorio, con `.venv` activo:

```bash
python -m pip install -r kit/requirements.txt -r kit/requirements_pqrs.txt -r kit/requirements_notebooks.txt
python -m pip check
python -m ipykernel install --sys-prefix --name bigdata-wsl --display-name "BigData · WSL Ubuntu 26.04 · Python 3.12"
```

Los archivos de requisitos son la referencia de versiones. Usar siempre `python -m pip` del entorno activo, sin `sudo pip`. Cualquier biblioteca adicional que el docente autorice se instala en este mismo entorno y se registra en el archivo de requisitos correspondiente.

Comprobación de importaciones:

```bash
python -c "import pandas, numpy, pyarrow, duckdb, polars, rasterio, shapely, pyproj, geopandas, pyogrio, matplotlib; print('Bibliotecas disponibles')"
python -c "import duckdb; print(duckdb.sql('SELECT 2 + 2').fetchone())"
```

La consulta debe devolver `(4,)`.

La instalación anterior es **CPU**. La [ampliación opcional de Polars GPU](polars-gpu.md) se realiza aparte: controlador NVIDIA en Windows, CUDA Toolkit compatible dentro de WSL 2 y paquetes en `.venv-gpu`. No instalar el controlador Linux dentro de WSL ni ejecutar los requisitos GPU antes de preparar esos prerrequisitos.

## 5. Configurar Java y Spark

El paquete `openjdk-21-jdk` del paso 2 incluye `java` y `javac`. Guardar la configuración en un archivo del usuario y cargarlo desde Bash:

```bash
mkdir -p "$HOME/.config/bigdata"
cat > "$HOME/.config/bigdata/entorno.sh" <<'ENV'
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f /usr/bin/javac)")")"
export PATH="$JAVA_HOME/bin:$PATH"
ENV
grep -qxF 'source "$HOME/.config/bigdata/entorno.sh"' "$HOME/.bashrc" || echo 'source "$HOME/.config/bigdata/entorno.sh"' >> "$HOME/.bashrc"
source "$HOME/.config/bigdata/entorno.sh"
java -version
javac -version
python -m pip install -r kit/requirements_spark.txt
python -m pip check
export PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"
```

Prueba mínima, antes de procesar datos:

```bash
python - <<'PYSPARK'
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").appName("VerificacionWSL").getOrCreate()
assert spark.range(5).count() == 5
print("Spark local: correcto")
spark.stop()
PYSPARK
```

[Paquete JDK 21 para Ubuntu 26.04](https://packages.ubuntu.com/resolute/openjdk-21-jdk). Si `apt` no lo encuentra, comprobar que está habilitado el componente oficial `universe` de Ubuntu; no instalar un JDK de otra distribución.

Ejecutar los talleres E07/E11 después de preparar sus entradas; la prueba anterior solo comprueba el arranque. No instalar Java para Windows como sustituto del JDK de Ubuntu.

## 6. Abrir Jupyter y ejecutar la primera práctica

En Ubuntu, con el entorno activo:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate/kit
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Copiar en el navegador de Windows la URL `http://localhost:8888/lab?token=...` que muestre Jupyter, usando el puerto y token reales. Abrir `Notebooks/01_Perfil_PQRS.ipynb` y seleccionar **BigData · WSL Ubuntu 26.04 · Python 3.12**. El navegador se abre en Windows, pero el kernel ejecuta en Ubuntu. Detener Jupyter con `Ctrl+C` al terminar. [Acceso desde Windows mediante localhost](https://learn.microsoft.com/en-us/windows/wsl/networking).

Las tres muestras PQRS ya están en el clon; desde `kit/`, prepararlas con `python 00_datos.py --descargar pqrs` y comprobarlas con `python 00_datos.py --verificar pqrs`. NASA, los archivos agroambientales y los completos PQRS requieren las descargas de [la guía de datos](entorno.md); no iniciar el notebook de eventos hasta disponer de `kit/data/raw/nasa.json`.

## 7. Mapas en Jupyter con GeoPandas

Todos los ejercicios geoespaciales se ejecutan en el mismo `.venv`: GeoPandas y Pyogrio para vectores, Rasterio para ráster y Matplotlib para mapas. Las versiones están fijadas en `kit/requirements.txt`. Esta actividad no necesita una aplicación de escritorio ni WSLg.

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
python -m pip install -r kit/requirements.txt -r kit/requirements_notebooks.txt
python -m pip check
python -c "import geopandas, pyogrio, rasterio, matplotlib; print('Entorno geoespacial disponible')"
jupyter lab kit/Notebooks/
```

Abrir los notebooks E08, E09 y E11 del [índice](../kit/Notebooks/README.md). Los mapas se muestran en el navegador y se guardan en `kit/salidas/`. Instalar dentro de Ubuntu, sin `sudo pip`; mantener el kernel del curso. La prueba de importaciones no reemplaza la ejecución con los datasets.

[Instalación de GeoPandas](https://geopandas.org/en/stable/getting_started/install.html) · [Rasterio y mapas](https://rasterio.readthedocs.io/en/stable/topics/plotting.html).

## 8. Retomar el trabajo en otra sesión

En PowerShell:

```powershell
wsl --distribution Ubuntu-26.04
```

En Ubuntu:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
source "$HOME/.config/bigdata/entorno.sh"
export PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"
git status --short
# Si no hay cambios locales pendientes:
git switch main
git pull --ff-only origin main
cd kit
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Para abrir los archivos en el Explorador de Windows desde Ubuntu: `explorer.exe .`. Para copiar un ZIP descargado en Windows, usar la ruta `/mnt/c/Users/TUPTC/Downloads/archivo.zip` y colocarlo en `kit/data/raw/`; sustituir el nombre del archivo por el descargado.

## Recursos y problemas frecuentes

- Planificar 16 GB de RAM y 20 GB libres para entorno y datos; las cifras son presupuesto, no una medición de instalación. Con 8 GB trabajar primero con muestras y cerrar aplicaciones pesadas.
- `python` debe apuntar a `.venv/bin/python`; si muestra una ruta Windows o Python 3.14, activar de nuevo el entorno dentro de Ubuntu.
- Si falta una biblioteca, usar `python -m pip` en ese mismo entorno. No copiar virtualenvs de Windows o de otro sistema.
- Si Spark no arranca, comprobar `java`, `javac` y `JAVA_HOME` dentro de Ubuntu. Reiniciar el kernel después de cambiar variables de entorno.
- Si Ubuntu-26.04 no inicia por virtualización, revisar los requisitos WSL de Microsoft y habilitar virtualización del equipo según el fabricante.

La guía se contrastó con documentación oficial; **la instalación completa en un equipo Windows con Ubuntu-26.04 está pendiente de prueba**. Las validaciones previas de los ejercicios en macOS no certifican este entorno nuevo.

## Estructura de referencia

```text
/mnt/c/Users/TUPTC/bigdata/          # carpeta base
└── big-data-postgraduate/          # clon de main
    ├── .venv/                     # entorno de Ubuntu
    └── kit/
        ├── Notebooks/
        ├── data/
        └── salidas/
```
