# -*- coding: utf-8 -*-

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