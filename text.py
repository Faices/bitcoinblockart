import fitz
from svglib import svglib
from reportlab.graphics import renderPDF

# Convert svg to pdf in memory with svglib+reportlab
# directly rendering to png does not support transparency nor scaling
drawing = svglib.svg2rlg(path="images/block_772813.svg")
pdf = renderPDF.drawToString(drawing)

# Open pdf with fitz (pyMuPdf) to convert to PNG
doc = fitz.Document(stream=pdf)
pix = doc.load_page(0).get_pixmap(alpha=False, dpi=300)
pix.save("output.png")