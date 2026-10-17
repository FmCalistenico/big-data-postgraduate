# Revisión de rutas del curso

La carpeta base es `/mnt/c/Users/TUPTC/bigdata`; el clon de `main` está en `big-data-postgraduate/`, el entorno en `.venv/` y los ejercicios en `kit/` dentro del repositorio.

Se revisaron documentación Markdown, fuentes JSON, README, scripts Python y notebooks versionados. Las guías vigentes inician cada bloque de navegación en la carpeta base y continúan con rutas relativas. La URL de GitHub conserva el nombre del repositorio.

Los scripts de `kit/` localizan los archivos por su propia ubicación. Se corrigieron los argumentos relativos de PQRS para que no dependan del directorio de lanzamiento. Los notebooks actuales también localizan el kit al abrirse desde la carpeta base, la raíz del repositorio, `kit/` o `kit/Notebooks/`.

Los archivos de `historico/pedidos/` y los cuatro notebooks originales de `supersalud/` se revisaron como material archivado. Conservan rutas históricas de Colab y Google Drive y no se certifican como ejecutables WSL; la ruta vigente es `kit/Notebooks/`. No se reemplazan rutas de outputs antiguos ni enlaces de descarga por rutas del curso.

La verificación local comprueba enlaces, sintaxis y resolución de rutas desde distintos directorios. No sustituye una instalación real en Windows/WSL.
