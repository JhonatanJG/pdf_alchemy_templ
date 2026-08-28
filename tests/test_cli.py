import sys
import fitz
from pathlib import Path


# Ensure the project root is in sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from pdf_alchemy_templ.cmdline import Cmdline
from pdf_alchemy_templ.parseargs import PDFArgumentParser

ASSET_PDF = Path(__file__).resolve().parent / "assets" / "test_alchemy.pdf"


def run_cmdline(args_list, capsys):
    """Helper to parse arguments, run Cmdline, and capture output."""
    parser = PDFArgumentParser()
    args = parser.parser.parse_args(args_list)
    app = Cmdline(args)
    # Dispatch based on args similar to main logic
    if args.total_pages:
        app.get_num_pages()
    elif args.split:
        app.split_pdf()
    elif args.delete:
        app.del_range()
    elif args.crop_half:
        app.crop_half()
    elif args.command == "add":
        app.add_pdf()
    else:
        print("No arguments used")
    return capsys.readouterr().out


def test_get_num_pages(capsys):
    out = run_cmdline(["-f", str(ASSET_PDF), "-o", "out", "-tp"], capsys)
    assert "Total pages" in out


def test_split_pdf(tmp_path, capsys):
    # Split first two pages and the rest
    out_dir = tmp_path / "split"
    out_dir.mkdir()
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_dir),
        "-s", "1-2", "3-4"
    ], capsys)
    # Expect two files part_1.pdf and part_2.pdf
    part1 = out_dir / "part_1.pdf"
    part2 = out_dir / "part_2.pdf"
    assert part1.is_file() and part2.is_file()
    # Verify page counts
    doc1 = fitz.open(part1)
    doc2 = fitz.open(part2)
    assert doc1.page_count == 2
    # remaining pages count may vary depending on original pdf length
    assert doc2.page_count >= 1
    doc1.close()
    doc2.close()


def test_del_range(tmp_path, capsys):
    out_pdf = tmp_path / "deleted.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "-d", "1-2"
    ], capsys)
    assert out_pdf.is_file()
    src_doc = fitz.open(ASSET_PDF)
    out_doc = fitz.open(out_pdf)
    assert out_doc.page_count == src_doc.page_count - 2
    src_doc.close()
    out_doc.close()


def test_add_pdf(tmp_path, capsys):
    # Create a small PDF to insert (1 page)
    insert_pdf = tmp_path / "insert.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(insert_pdf)
    doc.close()

    out_pdf = tmp_path / "added.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "add", str(insert_pdf),
        "--after", "1"
    ], capsys)
    assert out_pdf.is_file()
    src_doc = fitz.open(ASSET_PDF)
    out_doc = fitz.open(out_pdf)
    # Inserting 1 page after page 1 should increase total pages by 1
    assert out_doc.page_count == src_doc.page_count + 1
    src_doc.close()
    out_doc.close()


def test_crop_half(tmp_path, capsys):
    out_pdf = tmp_path / "cropped.pdf"
    # Crop first page only
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "-ch", "1"
    ], capsys)
    assert out_pdf.is_file()
    src_doc = fitz.open(ASSET_PDF)
    out_doc = fitz.open(out_pdf)
    # Original page count plus one extra page for the cropped one
    assert out_doc.page_count == src_doc.page_count + 1
    src_doc.close()
    out_doc.close()

# Don't modify above,
# Add your tests for the 2 new functionalities below


def _make_pdf_with_pages(path, texts):
    """Create a small PDF at `path` with one page per string in `texts`."""
    doc = fitz.open()
    for text in texts:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


# ---- add (insercion posicional) ----

def test_add_pdf_after_inserts_at_correct_index(tmp_path, capsys):
    """--after 3 debe insertar justo despues de la pagina 3 (indice 3, 0-based)."""
    insert_pdf = tmp_path / "insert.pdf"
    _make_pdf_with_pages(insert_pdf, ["INSERTED-MARKER"])

    out_pdf = tmp_path / "added_after.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "add", str(insert_pdf),
        "--after", "3"
    ], capsys)

    out_doc = fitz.open(out_pdf)
    # La pagina insertada queda en el indice 3
    assert "INSERTED-MARKER" in out_doc[3].get_text()
    # La pagina original 4 (antes en indice 3) se corrio al indice 4
    assert "Page 4 of 50" in out_doc[4].get_text()
    # Lo que va antes del punto de insercion queda intacto
    assert "Page 3 of 50" in out_doc[2].get_text()
    out_doc.close()


def test_add_pdf_before_inserts_at_correct_index(tmp_path, capsys):
    """--before 5 debe insertar justo antes de la pagina 5 (indice 4, 0-based)."""
    insert_pdf = tmp_path / "insert.pdf"
    _make_pdf_with_pages(insert_pdf, ["INSERTED-MARKER"])

    out_pdf = tmp_path / "added_before.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "add", str(insert_pdf),
        "--before", "5"
    ], capsys)

    out_doc = fitz.open(out_pdf)
    assert "INSERTED-MARKER" in out_doc[4].get_text()
    # La pagina original 5 (antes en indice 4) se corrio al indice 5
    assert "Page 5 of 50" in out_doc[5].get_text()
    # Lo anterior al punto de insercion no cambia
    assert "Page 4 of 50" in out_doc[3].get_text()
    out_doc.close()


def test_add_pdf_multi_page_insert_preserves_order(tmp_path, capsys):
    """Insertar un PDF de varias paginas debe mantener el orden interno de esas paginas."""
    insert_pdf = tmp_path / "insert_multi.pdf"
    _make_pdf_with_pages(insert_pdf, ["INSERT-A", "INSERT-B"])

    out_pdf = tmp_path / "added_multi.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "add", str(insert_pdf),
        "--after", "10"
    ], capsys)

    src_doc = fitz.open(ASSET_PDF)
    out_doc = fitz.open(out_pdf)
    assert out_doc.page_count == src_doc.page_count + 2
    assert "INSERT-A" in out_doc[10].get_text()
    assert "INSERT-B" in out_doc[11].get_text()
    # La pagina original 11 (antes en indice 10) ahora esta en el indice 12
    assert "Page 11 of 50" in out_doc[12].get_text()
    src_doc.close()
    out_doc.close()


# ---- crop_half (recorte en mitades) ----

def test_crop_half_splits_page_into_equal_halves(tmp_path, capsys):
    """Cada pagina recortada debe producir dos mitades del ancho correcto."""
    out_pdf = tmp_path / "cropped_single.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "-ch", "1"
    ], capsys)

    src_doc = fitz.open(ASSET_PDF)
    original_rect = src_doc[0].rect
    mid_x = (original_rect.x0 + original_rect.x1) / 2

    out_doc = fitz.open(out_pdf)
    left_page, right_page = out_doc[0], out_doc[1]

    # La posicion real del recorte vive en cropbox; rect siempre se
    # normaliza a partir de (0, 0) sin importar el cropbox aplicado.
    assert left_page.cropbox.x0 == original_rect.x0
    assert left_page.cropbox.x1 == mid_x
    assert right_page.cropbox.x0 == mid_x
    assert right_page.cropbox.x1 == original_rect.x1
    # Las dos mitades deben ser distintas entre si (regresion del bug
    # donde copy_page() comparte xref y ambas terminan con el mismo cropbox)
    assert left_page.cropbox != right_page.cropbox
    # El ancho de cada mitad debe ser la mitad del original
    assert left_page.rect.width == right_page.rect.width
    assert left_page.rect.width == mid_x - original_rect.x0
    # La altura no debe cambiar
    assert left_page.rect.height == original_rect.height
    assert right_page.rect.height == original_rect.height
    src_doc.close()
    out_doc.close()


def test_crop_half_preserves_surrounding_pages(tmp_path, capsys):
    """Recortar una pagina intermedia no debe alterar el contenido de las demas."""
    out_pdf = tmp_path / "cropped_middle.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "-ch", "3"
    ], capsys)

    out_doc = fitz.open(out_pdf)
    # Paginas antes del recorte quedan intactas
    assert "Page 1 of 50" in out_doc[0].get_text()
    assert "Page 2 of 50" in out_doc[1].get_text()
    # La pagina original 4 (antes en indice 3) se corrio un puesto por el recorte
    assert "Page 4 of 50" in out_doc[4].get_text()
    out_doc.close()


def test_crop_half_multiple_pages_range(tmp_path, capsys):
    """Recortar un rango de paginas debe aumentar el total en una por cada pagina recortada."""
    out_pdf = tmp_path / "cropped_range.pdf"
    run_cmdline([
        "-f", str(ASSET_PDF),
        "-o", str(out_pdf),
        "-ch", "1-3"
    ], capsys)

    src_doc = fitz.open(ASSET_PDF)
    out_doc = fitz.open(out_pdf)
    # 3 paginas recortadas -> 3 paginas extra
    assert out_doc.page_count == src_doc.page_count + 3
    # La pagina original 4 (antes en indice 3) se corrio 3 puestos
    assert "Page 4 of 50" in out_doc[6].get_text()
    src_doc.close()
    out_doc.close()
