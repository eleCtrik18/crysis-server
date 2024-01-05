from pathlib import Path
from weasyprint import HTML


def html_to_pdf(html_file, output_path):
    html = Path(html_file).read_text()
    htmldoc = HTML(string=html, base_url="")
    out = htmldoc.write_pdf()
    Path(output_path).write_bytes(out)
    return output_path
