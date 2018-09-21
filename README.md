# Metadata-Extractor-for-Books
Rule-based python script to extract metadata from NCERT books

SUMMARY

We developed a Python script to extract metadata from NCERT books. In the basic flow, the PDF file of the book is first converted to XML (using pdftohtml), then analyzed (by looking at spatial cues and text patterns) for specific metadata. DDC is inferred using ACT-DL service on the Web. If the title turns out to be an empty string, the PDF file is assumed to be an image from which text extraction must be preceded by OCR. So it is sent to an alternate flow where the PDF is OCR'ed using Tesseract (legacy mode; no LSTM). The resulting hOCR files are then pushed into the basic flow.


INPUT & OUTPUT

The software takes a set of PDF files (each containing front matter of a book) stored in a directory and stores metadata generated from them in a directory. Metadata for each book is organized according to NDLI schema and available as a JSON file.


HOW TO RUN (COMMANDLINE)

To use the software, keep your PDF files in a directory INDIR. Suppose you want the output JSON files to be output in directory OUTDIR. Assume these directories are created under the current directory. So, extract the file INOUT.zip and put INDIR, OUTDIR and the Python scripts in the same parent directory and excecute the following commandline:
python extract_metadata.py  ./INDIR/  ./OUTDIR/


DEPENDENCIES

The code uses the following external libraries/tools: 
Linux utilities:  pdfinfo, pdftohtml 
Image processing / OCR libraries: Tesseract, ImageMagick,
Python libraries: re, xlrd, json, sys, stringdist, bs4, requests, OrderedDict(collections), io, os, subprocess.


TEST CONFIGURATION

The code was tested using the following configuration:
1. Linux: Ubuntu 18.04
2. Python 3.6.5
3. GCC 7.3.0 on Linux
