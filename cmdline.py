import pymupdf  # PyMuPDF
import os

class Cmdline:
    def __init__(self, args) -> None:
        self.args = args
        self.input_pdf = ""
        self.output_pdf = ""

    def get_num_pages(self):
        """Print the total number of pages in the input PDF."""

    def split_pdf(self):
        """Split the input PDF into multiple PDFs based on page ranges.
        args.split is a list where each element is a list of zero‑based page indices.
        The output_path is treated as a directory; files are named part_1.pdf, part_2.pdf, …
        """

    def del_range(self):
        """Delete the specified pages from the input PDF and write the result to output_path.
        args.delete is a list of lists of zero‑based page numbers. We flatten it.
        """

    def add_pdf(self):
        """Add pages from another PDF into the source PDF.
        The insert PDF is provided via the positional argument `insert`.
        Insertion point is defined by either `--after` or `--before` (1‑based).
        The result is written to output_path.
        """

    def crop_half(self):
        """Crop specified pages in half (left and right) and duplicate each as two pages.
        args.crop_half provides page ranges (zero‑based). For each page we create two pages:
        one with the left half of the original media box and one with the right half.
        The result is saved to output_path.
        """
