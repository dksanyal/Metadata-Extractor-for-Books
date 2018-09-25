# Metadata-Extractor-for-Books
Rule-based python script to extract metadata from NCERT books


We developed a Python script to extract metadata from NCERT books. In the basic flow, the PDF file of the book is first converted to XML (using pdftohtml), then analyzed (by looking at spatial cues and text patterns) for specific metadata. DDC is inferred using ACT-DL service on the Web. If the title turns out to be an empty string, the PDF file is assumed to be an image from which text extraction must be preceded by OCR. So it is sent to an alternate flow where the PDF is OCR'ed using Tesseract (legacy mode; no LSTM). The resulting hOCR files are then pushed into the basic flow.


HOW TO CITE
-----------
If you use these scripts, kindly cite the following paper:

Akhtar, Sk. Simran, Debarshi Kumar Sanyal, Samiran Chattopadhyay, Plaban Kumar Bhowmick, and Partha Pratim Das. "A metadata extractor for books in a digital library." International Conference on Asian Digital Libraries (ICADL). Springer, 2018.

This work is funded by the NDLI project sponsored by MHRD, Govt. of India. The scripts are written and tested by Sk. Simran Akhtar (4th year student (2015-2019), Department of Information Technology, Jadavpur University).


CODE / HOW TO RUN
-----------------
The software takes a set of PDF files (each containing front matter of a book) stored in a directory, generates metadata from them, and stores the metadata in a directory. Metadata for each book is organized according to NDLI schema and available as a JSON file.

Here is an example use case. Extract the file testcase.zip and put INDIR, OUTDIR and the Python scripts in the same parent directory. INDIR contains input PDF files. The generated JSON files will go to OUTDIR (it is preloaded with the JSON files we got by running the tool). Excecute the following commandline:

python ./extract_metadata.py  ./INDIR/  ./OUTDIR/

(The above script calls metadata.py which first runs basic flow using basic.py and if needed, follows it up with alternate flow. The evaluate.py script is used to evaluate the performance of metadata extraction with respect to manually curated golden metadata.)

DEPENDENCIES: The code uses the following external libraries/tools:

Linux utilities:  pdfinfo, pdftohtml 

Image processing / OCR libraries: Tesseract, ImageMagick,

Python libraries: re, xlrd, json, sys, stringdist, bs4, requests, OrderedDict(collections), io, os, subprocess.



TEST CONFIGURATION
------------------

The code was tested using the following configuration:

1. Linux: Ubuntu 18.04

2. Python 3.6.5

3. GCC 7.3.0 on Linux
