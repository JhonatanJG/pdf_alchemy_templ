# PDF Alchemy

CLI en Python para manipular archivos PDF: consultar número de páginas, dividir,
eliminar páginas, insertar un PDF dentro de otro en una posición exacta y
recortar páginas en mitades.

**Fork** the project to your github account, this will have the associated
tests and template to start the project and finish implementation.

## Requisitos

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes y proyectos)
- PyMuPDF (`pymupdf`)

## Instalación

```bash
uv sync
```

## Ejecutar la herramienta

1. Inicializar el entorno virtual

```bash
uv venv
source .venv/bin/activate
```

2. Ejecutar el CLI

```bash
uv run main.py [opciones]
```

## Comandos

Todos los comandos requieren `-f/--file` (ruta del PDF de entrada) y
`-o/--output` (ruta o carpeta de salida).

| Comando | Descripción |
|---|---|
| `-tp`, `--total-pages` | Imprime el número total de páginas del PDF. |
| `-s`, `--split` | Divide el PDF en varios archivos según rangos de páginas (`--split 1-30 31-40`) o páginas individuales (`--split 1 4 6`). Genera `part_1.pdf`, `part_2.pdf`, ... en el directorio de salida. |
| `-d`, `--delete` | Elimina las páginas indicadas (rango o individuales) y guarda una copia sin ellas. |
| `-ch`, `--crop-half` | **Funcionalidad nueva.** Recorta cada página indicada en dos mitades (izquierda y derecha), generando dos páginas independientes por cada una. |
| `add <archivo>` | **Funcionalidad nueva.** Inserta el PDF `<archivo>` completo dentro del PDF de entrada, en la posición exacta indicada con `--after N` o `--before N` (ambos 1-based, mutuamente excluyentes). |

### Ejemplos

```bash
# Número total de páginas
uv run main.py -f documento.pdf -tp

# Dividir en dos partes
uv run main.py -f documento.pdf -o salida/ -s 1-10 11-20

# Eliminar las páginas 1 a 3
uv run main.py -f documento.pdf -o documento_sin_1_3.pdf -d 1-3

# Insertar anexo.pdf despues de la pagina 5
uv run main.py -f documento.pdf -o documento_con_anexo.pdf add anexo.pdf --after 5

# Insertar otrosi.pdf antes de la pagina 10
uv run main.py -f documento.pdf -o documento_con_otrosi.pdf add otrosi.pdf --before 10

# Recortar en mitades las paginas 1 a 3 (util para libros escaneados)
uv run main.py -f escaneado.pdf -o escaneado_paginado.pdf -ch 1-3
```

## Funcionalidades nuevas (propuesta del equipo)

A partir de la investigación de mercado (Smallpdf, iLovePDF, PDFtk) se
identificaron dos vacíos no cubiertos por las alternativas comerciales y se
implementaron en el prototipo:

### 1. Inserción de PDF en posición específica (`add`)

Permite insertar el contenido completo de un archivo PDF dentro de otro en una
posición exacta (antes o después de una página determinada), en lugar de
simplemente concatenar documentos al inicio o al final. Resuelve casos de uso
frecuentes en contextos administrativos y legales: añadir anexos, otrosíes o
capítulos nuevos en un punto intermedio de un documento ya existente.

- **Implementación:** `Cmdline.add_pdf()` en `cmdline.py`, usando
  `pymupdf.Document.insert_pdf(insert_doc, start_at=...)`.
- **Cómo funciona:** recibe el PDF de origen, el PDF a insertar y la posición
  (`--after N` o `--before N`, 1-based); calcula el índice 0-based
  correspondiente y llama a `insert_pdf` en ese punto; guarda el resultado en
  `output_path`.

### 2. Recorte de páginas en mitades (`crop_half`)

Divide cada página seleccionada en dos mitades (izquierda y derecha),
generando dos páginas independientes a partir de una sola. Útil para separar
documentos escaneados en formato de libro (dos páginas por hoja) en páginas
individuales legibles.

- **Implementación:** `Cmdline.crop_half()` en `cmdline.py`, usando
  `Page.set_cropbox()` sobre una copia de cada página original.
- **Cómo funciona:** por cada página indicada, calcula el punto medio del
  ancho, duplica la página y aplica un `cropbox` distinto a cada mitad (mitad
  izquierda / mitad derecha); guarda el resultado en `output_path`.

#### Reto técnico encontrado y solucionado

Durante las pruebas se detectó que `Document.copy_page()` crea una página que
**comparte el mismo xref** (referencia interna) con la página original, en
lugar de una copia independiente. Esto causaba que, al asignar el `cropbox`
de la segunda mitad, la primera mitad quedara sobrescrita con las mismas
coordenadas, perdiendo el contenido de la mitad izquierda. Se solucionó
usando `Document.fullcopy_page()`, que crea un xref nuevo e independiente
para la página duplicada, permitiendo que cada mitad conserve su propio
`cropbox`.

## Ejecutar las pruebas

```bash
uv run pytest -q
```

El repositorio incluye:

- Pruebas base para las funcionalidades originales (`total_pages`, `split`,
  `delete`) y sanity checks base para las 2 funcionalidades nuevas.
- Pruebas unitarias propias adicionales para `add` y `crop_half`
  (`tests/test_cli.py`, debajo del comentario `Add your tests for the 2 new
  functionalities below`), que validan no solo el conteo de páginas sino el
  contenido y la posición real de las páginas insertadas/recortadas:
  - `test_add_pdf_after_inserts_at_correct_index`
  - `test_add_pdf_before_inserts_at_correct_index`
  - `test_add_pdf_multi_page_insert_preserves_order`
  - `test_crop_half_splits_page_into_equal_halves`
  - `test_crop_half_preserves_surrounding_pages`
  - `test_crop_half_multiple_pages_range`

### Evidencia de pruebas pasando

```
$ uv run pytest -q
...........                                                             [100%]
11 passed in 0.38s
```

## Compilar a ejecutable independiente

```bash
uv pip install pyinstaller
uv run pyinstaller --onefile main.py
```

> Verás la nueva compilación bajo `dist/`
