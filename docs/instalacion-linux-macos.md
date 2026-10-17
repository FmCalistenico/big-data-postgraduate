# Instalación inicial en Linux y macOS

[Índice](../README.md) · [Windows/WSL](instalacion-wsl.md) · [Datos y ejecución](entorno.md) · [Notebooks](../kit/Notebooks/README.md)

Esta guía prepara el mismo entorno del curso de forma nativa: Python 3.12, un `.venv` base CPU, JDK 21, Spark y Jupyter, con las versiones de bibliotecas fijadas en el repositorio. No hace falta instalar WSL en Linux ni en macOS. Los comandos se ejecutan en la terminal con Bash o Zsh; para Fish, abrir primero una sesión Bash.

## 1. Identificar el equipo e instalar herramientas

Planificar 16 GB de RAM y 20 GB libres para entorno, datos y temporales. Son estimaciones de capacidad, no una medición de instalación. Con 8 GB comenzar con las muestras incluidas y Spark `local[2]`.

### Linux

Comprobar distribución y arquitectura:

```bash
cat /etc/os-release
uname -m
```

En Ubuntu 24.04/26.04 o Debian con JDK 21 disponible en sus repositorios:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates unzip build-essential openjdk-21-jdk
```

Si `apt` no encuentra JDK 21, comprobar la versión y los repositorios oficiales de la distribución antes de continuar; no añadir repositorios de otra distribución. En Ubuntu puede ser necesario habilitar el componente oficial `universe`.

En Fedora, usar su gestor en lugar de `apt`:

```bash
sudo dnf install -y git curl ca-certificates unzip gcc gcc-c++ make java-21-openjdk-devel
```

[JDK 21 en Ubuntu](https://packages.ubuntu.com/noble-updates/openjdk-21-jdk) · [JDK 21 en Fedora](https://packages.fedoraproject.org/pkgs/java-21-openjdk/java-21-openjdk-devel/).

Para otras distribuciones, instalar los equivalentes de Git, curl y **JDK 21 completo** con su gestor oficial. `javac` debe estar disponible, no solamente `java`.

### macOS

Comprobar sistema y arquitectura:

```bash
sw_vers
uname -m
```

En el menú Apple → **Acerca de esta Mac**, revisar el campo **Chip** o **Procesador** y contrastarlo con `uname -m`:

| Equipo | Arquitectura nativa | Homebrew habitual | JDK requerido |
|---|---|---|---|
| Apple Silicon M1, M2, M3 o M4 (incluidas sus variantes) | `arm64` | `/opt/homebrew` | Temurin 21 para ARM64/aarch64 |
| Mac con procesador Intel | `x86_64` | `/usr/local` | Temurin 21 para x64 |

Si el equipo tiene chip Apple pero `uname -m` devuelve `x86_64`, la terminal se está ejecutando mediante Rosetta. Cerrar la terminal, desactivar **Abrir usando Rosetta** en la información de la aplicación, si aparece, y abrirla de nuevo. En Apple Silicon usar la terminal y Homebrew nativos para mantener Python, Java y las bibliotecas en la misma arquitectura.

Instalar las herramientas de línea de comandos de Apple si aún no están disponibles:

```bash
xcode-select --install
```

Esperar a que termine el instalador. Si ya están instaladas, continuar. Instalar Homebrew siguiendo sus [instrucciones oficiales](https://docs.brew.sh/Installation), que también indican las versiones de macOS y arquitecturas admitidas. Si `brew --version` ya funciona, omitir su instalación:

```bash
curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o /tmp/instalar-homebrew-bigdata.sh
/bin/bash /tmp/instalar-homebrew-bigdata.sh
```

Ejecutar los comandos de **Next steps** que muestre el instalador para añadir Homebrew al PATH de las siguientes sesiones. Para habilitarlo también en la sesión actual, ejecutar **solo uno** de estos bloques según el equipo:

**Apple Silicon M1–M4:**

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel:**

```bash
eval "$(/usr/local/bin/brew shellenv)"
```

Instalar Git y el **JDK Java 21 completo de Eclipse Temurin**. El comando es el mismo en ambos equipos; Homebrew selecciona el instalador de la arquitectura correspondiente:

```bash
brew --version
brew --prefix
brew install git
brew install --cask temurin@21
/usr/libexec/java_home -V
```

No usar `sudo brew`; el instalador del paquete Temurin puede solicitar la contraseña de administrador. `java_home -V` debe listar un JDK 21. El paso 5 configura cuál se usará en el curso. Consultar el [paquete oficial Temurin 21](https://formulae.brew.sh/cask/temurin@21) y el [soporte de Homebrew](https://docs.brew.sh/Installation) para la versión de macOS del equipo.

## 2. Crear la carpeta base y clonar main

Los pasos restantes son comunes a Linux y macOS salvo la configuración de Java. La carpeta base será `~/bigdata`, dentro del directorio personal. No crear `/mnt/c/Users/TUPTC/` en estos sistemas.

```bash
git --version
mkdir -p "$HOME/bigdata"
cd "$HOME/bigdata"
git clone --branch main https://github.com/eshernan/big-data-postgraduate.git
cd big-data-postgraduate
pwd
git branch --show-current
git status --short
```

La rama debe ser `main`. Si el repositorio ya existe, omitir `git clone` y entrar en esa copia; no clonar dentro de otra copia existente. `pwd` permite conocer la ruta absoluta que se usará en los notebooks.

```text
~/bigdata/                         # carpeta base
└── big-data-postgraduate/         # clon de main
    ├── .venv/                    # entorno local de este sistema
    ├── kit/
    │   ├── Notebooks/
    │   ├── data/
    │   └── salidas/
    ├── ejercicios/
    └── soluciones/
```

## 3. Instalar Python 3.12 y crear el entorno

Usar `uv` para obtener Python 3.12 sin reemplazar el Python del sistema. Si ya está instalado, comprobar `uv --version` y omitir la descarga del instalador.

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/instalar-uv-bigdata.sh
sh /tmp/instalar-uv-bigdata.sh
source "$HOME/.local/bin/env"
uv --version
uv python install 3.12
cd "$HOME/bigdata"
cd big-data-postgraduate
if [ ! -e .venv ]; then
    uv venv --python 3.12 --seed .venv
fi
source .venv/bin/activate
python --version
python -c 'import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())'
```

Debe aparecer Python `3.12.x` y un ejecutable dentro de la carpeta `.venv` de este repositorio. Si el entorno ya existe y corresponde a este sistema, activarlo sin recrearlo. No copiar un virtualenv de Windows, de otro equipo o de otra arquitectura.

[Instalador de uv](https://docs.astral.sh/uv/getting-started/installation/) · [Python con uv](https://docs.astral.sh/uv/guides/install-python/) · [Entornos virtuales](https://docs.astral.sh/uv/pip/environments/).

El bloque anterior conserva un entorno existente. Si la comprobación de Python falla o la carpeta pertenece a otro sistema, no instalar paquetes encima; seguir la [reconstrucción del entorno](entornos-virtuales.md#5-retomar-o-reconstruir). La única ampliación con entorno separado es GPU; las clases ordinarias siguen usando `.venv`.

## 4. Instalar bibliotecas y registrar el kernel

Desde la raíz, con `.venv` activo:

```bash
python -m pip install -r kit/requirements.txt -r kit/requirements_pqrs.txt -r kit/requirements_notebooks.txt
python -m pip check
python -m ipykernel install --sys-prefix --name bigdata-native --display-name "BigData · Linux/macOS · Python 3.12"
python -c "import pandas, numpy, pyarrow, duckdb, polars, geopandas, pyogrio, shapely, pyproj, rasterio, matplotlib; print('Bibliotecas disponibles')"
python -c "import duckdb; print(duckdb.sql('SELECT 2 + 2').fetchone())"
```

La consulta debe devolver `(4,)` y `pip check` no debe reportar incompatibilidades. Los archivos de requisitos son la referencia de versiones. No sustituirlos por instalaciones sin versión ni usar `sudo pip`. GeoPandas, Rasterio y Matplotlib cubren los ejercicios de mapas dentro de Jupyter; no se necesita QGIS.

La instalación anterior es **CPU**. En Linux, la [ampliación opcional de Polars GPU](polars-gpu.md) exige preparar primero controlador NVIDIA y CUDA Toolkit compatibles; después se utiliza `.venv-gpu`. En macOS Intel y Apple Silicon se mantiene CPU, sin instalar requisitos NVIDIA.

## 5. Configurar JDK 21 y Spark

Ejecutar **solo el bloque de Java que corresponda al sistema**. Los bloques crean el archivo de configuración del curso `~/.config/bigdata/entorno.sh`; si ya contiene ajustes propios, revisarlo e integrarlos antes de reemplazarlo.

### Java en Linux

```bash
javac -version
readlink -f "$(command -v javac)"
```

Debe mostrarse `javac 21...`. Si hay varias versiones, seleccionar JDK 21 con `sudo update-alternatives --config javac` y `sudo update-alternatives --config java` en Ubuntu/Debian, o `sudo alternatives --config javac` y `sudo alternatives --config java` en Fedora. Verificar de nuevo antes de guardar:

```bash
mkdir -p "$HOME/.config/bigdata"
cat > "$HOME/.config/bigdata/entorno.sh" <<'ENV'
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f /usr/bin/javac)")")"
export PATH="$JAVA_HOME/bin:$PATH"
ENV
source "$HOME/.config/bigdata/entorno.sh"
```

Estos gestores instalan el enlace `/usr/bin/javac`. En otra distribución o con un JDK instalado manualmente, sustituir el cálculo por la ruta real del JDK 21 que contiene `bin/java` y `bin/javac`.

### Java en macOS

Después de instalar `temurin@21`, seleccionar Java 21 con la herramienta de macOS. Este bloque sirve tanto para **Apple Silicon M1–M4** como para **Intel**:

```bash
/usr/libexec/java_home -v 21
mkdir -p "$HOME/.config/bigdata"
cat > "$HOME/.config/bigdata/entorno.sh" <<'ENV'
export JAVA_HOME="$(/usr/libexec/java_home -v 21)"
export PATH="$JAVA_HOME/bin:$PATH"
ENV
source "$HOME/.config/bigdata/entorno.sh"
java -version
javac -version
file "$JAVA_HOME/bin/java"
```

`java` y `javac` deben indicar **21**. `file` debe mostrar `arm64` en Apple Silicon o `x86_64` en Intel. Temurin se registra en `/Library/Java/JavaVirtualMachines`; no hace falta crear enlaces manuales. Si hay varios JDK 21, revisar `/usr/libexec/java_home -V` y, si es necesario, asignar a `JAVA_HOME` la ruta exacta de Temurin 21 de la arquitectura correcta. Si no aparece ningún JDK 21, completar la instalación antes de seguir.

Si anteriormente se configuró `openjdk@21`, sustituir el valor anterior de `JAVA_HOME` en el archivo del curso por el bloque anterior y reiniciar Jupyter y su kernel. No es necesario desinstalar otros JDK para seleccionar Java 21.

### Spark en ambos sistemas

```bash
cd "$HOME/bigdata"
cd big-data-postgraduate
source .venv/bin/activate
source "$HOME/.config/bigdata/entorno.sh"
printf '%s\n' "$JAVA_HOME"
java -version
javac -version
python -m pip install -r kit/requirements_spark.txt
python -m pip check
export PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"
```

`java` y `javac` deben indicar 21. PySpark se instala en `.venv`; no hace falta instalar otra distribución de Spark mediante Homebrew o descargar un clúster. [Requisitos e instalación de PySpark 4.0.1](https://spark.apache.org/docs/4.0.1/api/python/getting_started/install.html).

Prueba mínima de JVM, sesión local y trabajador Python:

```bash
python - <<'PYSPARK'
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[2]").appName("VerificacionCurso").getOrCreate()
try:
    assert spark.range(5).count() == 5
    assert spark.sparkContext.parallelize([1, 2, 3], 2).map(lambda x: x + 1).collect() == [2, 3, 4]
    print("Spark y trabajador Python: correctos")
finally:
    spark.stop()
PYSPARK
```

Esta prueba no reemplaza los talleres E07/E11 con sus datasets. Cargar el archivo de entorno en cada sesión, como en el paso 9; no es obligatorio modificar `.bashrc` ni `.zshrc`.

## 6. Adaptar las rutas visibles de los notebooks

Los notebooks iniciales muestran una ruta WSL que el estudiante puede editar. Ejecutar `pwd` en la raíz del repositorio y copiar su resultado en la primera celda. Por ejemplo:

```python
# Ejemplo Linux: sustituir ana por el usuario real.
repositorio = "/home/ana/bigdata/big-data-postgraduate"
```

```python
# Ejemplo macOS: sustituir ana por el usuario real.
repositorio = "/Users/ana/bigdata/big-data-postgraduate"
```

En las plantillas PD01–PD03 la variable se llama `REPO`: asignarle la misma ruta real. No escribir literalmente `$HOME` o `~` dentro de estas cadenas Python: una cadena normal no los expande. Mantener los nombres de las subcarpetas y archivos que aparecen después de esa variable.

En las instrucciones de los talleres, sustituir el inicio `cd /mnt/c/Users/TUPTC/bigdata` por `cd "$HOME/bigdata"`; el siguiente `cd big-data-postgraduate` se mantiene. Los comandos relativos dentro de `kit/` son iguales. Si una instrucción pide el kernel WSL, elegir aquí **BigData · Linux/macOS · Python 3.12**.

## 7. Abrir Jupyter y empezar con pandas

Desde la raíz se pueden abrir tanto `kit/Notebooks/` como `ejercicios/` y `soluciones/`:

```bash
cd "$HOME/bigdata"
cd big-data-postgraduate
source .venv/bin/activate
source "$HOME/.config/bigdata/entorno.sh"
export PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Copiar en el navegador del mismo equipo la URL que imprime Jupyter, con su puerto y token reales. Abrir `kit/Notebooks/01_Perfil_PQRS.ipynb`, seleccionar el kernel registrado y adaptar la ruta antes de ejecutar celda por celda. Las tres muestras PQRS ya están incluidas; para prepararlas o verificarlas, desde `kit/` ejecutar `python 00_datos.py --descargar pqrs` y `python 00_datos.py --verificar pqrs`. En las clases iniciales, realizar directamente las operaciones pandas; no sustituir el notebook por un comando que produzca todo el perfil.

P02 escribe Parquet; P03 requiere ese producto y DIVIPOLA. Los detalles están en el [índice de notebooks](../kit/Notebooks/README.md). Detener Jupyter con `Ctrl+C` y confirmar cuando se solicite.

## 8. Preparar los datos y los mapas

Para AGROSAVIA, EVA y DIVIPOLA, desde una terminal con el entorno activo:

```bash
cd "$HOME/bigdata"
cd big-data-postgraduate
source .venv/bin/activate
cd kit
python 00_datos.py --listar
python 00_datos.py --descargar agrosavia eva divipola
```

Consultar [datos y ejecución](entorno.md) para verificar huellas, descargar NASA/CHIRPS y preparar las fuentes geoespaciales. Los ZIP DANE se descargan por navegador cuando el portal requiere ese procedimiento y se copian a `kit/data/raw/` con los nombres del manifiesto. En Linux/macOS no usar las rutas del Explorador de Windows.

Los notebooks E08/E09/E11 generan sus mapas con GeoPandas, Rasterio y Matplotlib. Usar las muestras antes de descargar los CSV PQRS completos. Los datos originales y las salidas se excluyen de Git.

## 9. Retomar y actualizar el curso

```bash
cd "$HOME/bigdata"
cd big-data-postgraduate
git status --short
# Solo si no hay trabajo local pendiente de conservar:
git switch main
git pull --ff-only origin main
source .venv/bin/activate
source "$HOME/.config/bigdata/entorno.sh"
export PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Si hay modificaciones propias, conservarlas antes de actualizar; no usar un reset para resolverlas. Si una actualización cambia los requisitos, volver a ejecutar la instalación de dependencias y `pip check`. No recrear el entorno en cada sesión. Si `pull --ff-only` detecta historiales divergentes, detenerse y revisar, especialmente en clones anteriores a la corrección de autoría.

## Problemas frecuentes y alcance de validación

| Síntoma | Comprobación |
|---|---|
| `brew` o `uv` no se encuentra | Completar el PATH indicado por su instalador; abrir otra terminal o cargar el archivo de entorno correspondiente. |
| Python incorrecto o `ModuleNotFoundError` | Activar `.venv`, revisar `python -c 'import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())'` y seleccionar el kernel del curso. |
| Error al instalar una rueda binaria | Revisar Python 3.12, arquitectura y versión del sistema; no mezclar paquetes Intel y ARM ni cambiar versiones fijadas sin revisar compatibilidad. |
| `JAVA_GATEWAY_EXITED` | Revisar JDK 21, JAVA_HOME, `java -version` y `javac -version`; cargar el entorno antes de iniciar Jupyter. |
| Spark no resuelve el nombre local del equipo | Revisar hostname/red; para la prueba local puede usarse `export SPARK_LOCAL_IP=127.0.0.1` antes de iniciar Spark. |
| Trabajador Spark usa otro Python | Exportar `PYSPARK_PYTHON="$VIRTUAL_ENV/bin/python"` con `.venv` activo y reiniciar la sesión/kernel. |
| `FileNotFoundError` en el notebook | Revisar `repositorio` o `REPO`, el nombre del archivo y que las fuentes estén descargadas. |
| Puerto Jupyter ocupado | Usar el puerto que informe Jupyter o iniciar con `--port=8889`. |

Se revisaron documentación oficial, enlaces y sintaxis de los comandos. Las pruebas previas de notebooks en macOS no equivalen a ejecutar esta instalación desde cero. **La instalación limpia completa en Linux y macOS queda pendiente de prueba**; no se certifican todas las distribuciones, versiones de macOS o arquitecturas.
