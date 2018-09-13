# Metadata-Extractor-for-Books
Rule-based python script to extract metadata from NCERT books

We developed a Python script to extract metadata from NCERT books. In the basic flow, the PDF file of the book is first converted to XML (using pdftohtml), then analyzed (by looking at spatial cues and text patterns) for specific metadata. DDC is inferred using ACT-DL service on the Web. If the title turns out to be an empty string, the PDF file is assumed to be an image from which text extraction must be preceded by OCR. So it is sent to an alternate flow where the PDF is OCR'ed using Tesseract (legacy mode; no LSTM). The resulting hOCR files are now pushed into the basic flow.

