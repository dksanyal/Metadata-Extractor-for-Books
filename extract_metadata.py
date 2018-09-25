# -*- coding: utf-8 -*-

# AUTHOR: Sk. Simran Akhtar.
# DATE: 25-Sep-2018.
# This work is funded by the NDLI project sponsored by MHRD, Govt. of India. If you use these scripts, we request you to kindly cite the following paper:
# Akhtar, Sk. Simran, et al. "A metadata extractor for books in a digital library." International Conference on Asian Digital Libraries (ICADL). Springer, 2018.

import os
import subprocess
import sys

in_dir=sys.argv[1]
out_dir=sys.argv[2]
try:
	process=sys.argv[3]+".py"
except:
	process="metadata.py"
files=os.scandir(in_dir)

subprocess.call(["mkdir","tmp"])

count=0
for x in files:
    if x.name.endswith(".pdf"):
        count=count+1
        
        
        y=x.name.split(".")[0]
        
        subprocess.call(["pdftohtml","-i","-nomerge","-xml",in_dir+x.name,"tmp/"+y])
        
        
        z="tmp/"+x.name.split(".")[0]+".txt"
        subprocess.run("pdfinfo "+in_dir+x.name+" > "+z, shell=True, check=True)
        
        subprocess.call(["python",process,y,"tmp/",in_dir,out_dir,"tmp/","tmp/"])
        
        print(x.name+" processed    count:",count,"     ",y)
		
subprocess.call(["rm","-r","tmp"])
