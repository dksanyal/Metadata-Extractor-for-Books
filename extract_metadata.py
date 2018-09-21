# -*- coding: utf-8 -*-

# AUTHOR: Sk. Simran Akhtar.
# DATE: 21-Sep-2018.
# This work is funded by the NDLI project sponsored by MHRD, Govt. of India. If you use these scripts, we request you to kindly cite the following paper:
# Akhtar, Sk. Simran, et al. "A metadata extractor for books in a digital library." International Conference on Asian Digital Libraries (ICADL). Springer, 2018.

import os
import subprocess
import sys

folder=sys.argv[1]
out_dir=sys.argv[2]
files=os.scandir(folder)

subprocess.call(["mkdir","tmp"])

count=0
for x in files:
    if x.name.endswith(".pdf"):
        count=count+1
        
        
        y=x.name.split(".")[0]+".xml"
        
        
        subprocess.call(["pdftohtml","-i","-nomerge","-xml",folder+x.name,"tmp/"+y])
        
        fold=x.name.rstrip(".pdf")
        subprocess.call(["mkdir","tmp/"+fold])
        p=0
        while True:
            command1=subprocess.call(["convert","-density","300","-colorspace", "Gray","-threshold","55%",folder+x.name+"["+str(p)+"]","-depth","8","-strip","-background","white","-alpha","off","tmp/"+fold+"/"+fold+"_"+str(p)+".tiff"])
            command2=subprocess.call(["tesseract","tmp/"+fold+"/"+fold+"_"+str(p)+".tiff","--oem","1","tmp/"+fold+"/"+fold+"_"+str(p),"hocr"])
            command3=subprocess.call(["rm","tmp/"+fold+"/"+fold+"_"+str(p)+".tiff"])
            
            print(x.name+"["+str(p)+"]"+"done")
            p+=1
            if command1 is not 0 or command2 is not 0:
                break
        
        z="tmp/"+x.name.split(".")[0]+".txt"
        subprocess.run("pdfinfo "+folder+x.name+" > "+z, shell=True, check=True)
        
        subprocess.call(["python",'metadata.py',y,"tmp/",out_dir,"tmp/","tmp/"])
        
        print(x.name+" processed    count:",count,"     ",y)
		
subprocess.call(["rm","-r","tmp"])
