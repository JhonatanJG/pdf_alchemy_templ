import pymupdf  # PyMuPDF
import os

class Cmdline:
    def __init__(self, args) -> None:
        self.args = args
        self.input_pdf = ""
        self.output_pdf = ""

    def get_num_pages(self):
        """Print the total number of pages in the input PDF."""
        doc = pymupdf.open(self.args.file_path)
        print(f"Total pages: {doc.page_count}")
        doc.close()

    def split_pdf(self):
        """Split the input PDF into multiple PDFs based on page ranges.
        args.split is a list where each element is a list of zero‑based page indices.
        The output_path is treated as a directory; files are named part_1.pdf, part_2.pdf, …
        """
        os.makedirs(self.args.output_path, exist_ok=True)
        src = pymupdf.open(self.args.file_path)

        for i, page_range in enumerate(self.args.split, start=1):
            new_doc = pymupdf.open()
            for p in page_range:
                new_doc.insert_pdf(src, from_page=p, to_page=p)
            out_file = os.path.join(self.args.output_path, f"part_{i}.pdf")
            new_doc.save(out_file)
            new_doc.close()

        src.close()

    def del_range(self):
        """Delete the specified pages from the input PDF and write the result to output_path.
        args.delete is a list of lists of zero‑based page numbers. We flatten it.
        """
        src = pymupdf.open(self.args.file_path)
        pages_to_delete = sorted({p for sub in self.args.delete for p in sub})
        src.delete_pages(pages_to_delete)
        src.save(self.args.output_path)
        src.close()

    def add_pdf(self):
        """Add pages from another PDF into the source PDF.
        The insert PDF is provided via the positional argument `insert`.
        Insertion point is defined by either `--after` or `--before` (1‑based).
        The result is written to output_path.
        """
        src = pymupdf.open(self.args.file_path)
        insert_doc = pymupdf.open(self.args.insert)

        if self.args.after is not None:
            # Insertar despues de la pagina N (1-based) = posicion N en 0-based
            start_at = self.args.after
        else:
            # Insertar antes de la pagina N (1-based) = posicion N-1 en 0-based
            start_at = self.args.before - 1

        src.insert_pdf(insert_doc, start_at=start_at)
        src.save(self.args.output_path)
        src.close()
        insert_doc.close()

    def crop_half(self):
        """Crop specified pages in half (left and right) and duplicate each as two pages.
        args.crop_half provides page ranges (zero‑based). For each page we create two pages:
        one with the left half of the original media box and one with the right half.
        The result is saved to output_path.
        """
        src = pymupdf.open(self.args.file_path)
        pages_to_crop = sorted({p for sub in self.args.crop_half for p in sub})

        offset = 0
        for p in pages_to_crop:
            idx = p + offset
            page = src[idx]
            rect = page.rect
            mid_x = (rect.x0 + rect.x1) / 2
            left_rect = pymupdf.Rect(rect.x0, rect.y0, mid_x, rect.y1)
            right_rect = pymupdf.Rect(mid_x, rect.y0, rect.x1, rect.y1)

            # Duplicamos la pagina justo despues de la original
            src.copy_page(idx, to=idx + 1)
            src[idx].set_cropbox(left_rect)
            src[idx + 1].set_cropbox(right_rect)
            offset += 1

        src.save(self.args.output_path)
        src.close()