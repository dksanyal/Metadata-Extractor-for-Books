from xlrd import open_workbook
import json
import re
import string
import sys
import stringdist
import os 
golden_data=sys.argv[1]
location=sys.argv[2]

number_of_files=len(os.listdir(location))+1
#golden_data="golden.xlsx"
#location="OUTDIR/"

rb = open_workbook(golden_data)
sheet1 = rb.sheet_by_index(0)
database = [[sheet1.cell_value(r, c) for c in range(sheet1.ncols)] for r in range(sheet1.nrows)]

def fbase(index):
    return database[row][index]
def fdata(index): 
    return data[index]

title=0
title_extracted=0
title_extracted_correctly=0
title_NLD=0
for i in range(1,number_of_files):
    if True:
        if i==number_of_files:
            break
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        try:
            f=open(filename)
            with open(filename) as f:
                data = json.load(f)
        except:
            data=""
        X=fbase(50).lower().strip()
        try:
            Y="".join(fdata("dc.title")).lower().strip()
        except:
            Y=""
        for p in string.punctuation+"–"+"—":
            p="\\"+str(p)
            X=re.sub(p," ",re.sub("\s+"," ",X)).strip()
            Y=re.sub(p," ",re.sub("\s+"," ",Y)).strip()
        
        if  X is not "":
            title+=1
        if  Y is not "":
            title_extracted+=1
        if X is not "" and Y is not "" and stringdist.levenshtein_norm(str(X).lower(),str(Y).lower())<=.1:
            title_NLD+=1
        if X is not "" and X==Y:
            title_extracted_correctly+=1
        continue
title_precision=title_extracted_correctly/title_extracted
NLD_precision=title_NLD/title_extracted
recall=title_extracted_correctly/title
NLD_recall=title_NLD/title
try:
    F1=2.0*title_precision*recall/(title_precision+recall)
except:
    F1=0.0
try:
    NLD_F1=2.0/(1.0/NLD_precision+1.0/NLD_recall)
except:
    NLD_F1=0.0
print("title_extracted:",title_extracted)    
print("title_extracted_correctly:",title_extracted_correctly)
print("title_precision: ",title_precision)
print("NLD_precision:",NLD_precision)
print("recall: ",recall)
print("NLD_recall: ",NLD_recall)
print("F1 score: ",F1)
print("NLD_F1 score: ",NLD_F1)
 
       


print("\ndescription")
description=0
description_extracted=0
description_extracted_correctly=0
description_NLD=0
i=0
for i in range(1,number_of_files):
    if True:
        row=i
        if i==number_of_files:
            break
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(16).lower()
        
        
        Y="".join(fdata("dc.description.abstract")).lower()
        for p in string.punctuation:
            p="\\"+str(p)
            X=re.sub(p," ",re.sub("\s+"," ",X)).strip()
            Y=re.sub(p," ",re.sub("\s+"," ",Y)).strip()
        
        if X is not "":
            description+=1
        if Y is not "":
            description_extracted+=1
        if X is not "" and stringdist.levenshtein_norm(str(X),str(Y))<=.1:
            description_NLD+=1
        if X is not "" and X==Y:
            description_extracted_correctly+=1
    else:
        continue
description_precision=description_extracted_correctly/description_extracted
NLD_precision=description_NLD/description_extracted
recall=description_extracted_correctly/description
NLD_recall=description_NLD/description
try:
    F1=2.0*description_precision*recall/(description_precision+recall)
except:
    F1=0.0
try:
    NLD_F1=2.0/(1.0/NLD_precision+1.0/NLD_recall)
except:
    NLD_F1=0.0
print("description_precision: ",description_precision)
print("NLD_precision:",NLD_precision)
print("recall: ",recall)
print("NLD_recall: ",NLD_recall) 
print("F1 score: ",F1)
print("NLD_F1 score: ",NLD_F1)


print("\neditor")
editor=0
editor_extracted=0
editor_extracted_correctly=0
editor_NLD=0
edit_precision=0.0
edit_recall=0.0
n=0
count=0
for i in range(1,number_of_files):
    try:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=str(fbase(5)).strip()
        if X is not "":
            editor+=1
        try:
            Y="".join(fdata("dc.contributor.editor")).strip()
        except:
            Y=""
        X_list=X.split("||")
        Y_list=Y.split("||")        
        Common=list(set(X_list) & set(Y_list))
        
        if(Y is not ''):
            edit_precision+=len(Common)/len(Y_list)
        edit_recall+=len(Common)/len(X_list)
        
        
        #NLD_similarity calculation
        common_len=0
        check_list=Y_list.copy()
        for i in range(len(X_list)):
            for j in range(len(Y_list)):
                if X_list[i]!='' and Y_list[j]!='':
                    if stringdist.levenshtein_norm(str(X_list[i]),str(Y_list[j]))<=.1:
                        common_len+=1
                        break
        Y_list=check_list.copy()
        if Y!='':
            NLD_precision+=common_len/len(Y_list)
        if(X!=''):
            NLD_recall+=common_len/len(X_list)
        
        if Y is not "":
            editor_extracted+=1
    except:
        continue
    
edit_precision/=editor_extracted
edit_recall/=editor
NLD_precision/=editor_extracted
NLD_recall/=editor
try:
    edit_F1=2.0*edit_precision*edit_recall/(edit_precision+edit_recall)
except:
    edit_F1=0.0

try:
    NLD_F1=2.0/(1.0/NLD_precision+1.0/NLD_recall)
except:
    NLD_F1=0.0
    
print("editor_precision: ",edit_precision)
print("NLD_precision:",NLD_precision)
print("recall: ",edit_recall)
print("NLD_recall: ",NLD_recall)
print("F1 score: ",edit_F1)
print("NLD_F1 score: ",NLD_F1)





print("\nillustrator")
illustrator=0
illustrator_extracted=0
illustrator_extracted_correctly=0

i=0
illus_precision=0.0
illus_recall=0.0

NLD_precision=0.0
NLD_recall=0.0
n=0
for i in range(1,number_of_files):
    if True:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(6)
        Y="".join(fdata("dc.contributor.illustrator"))
        
        X_list=X.split("||")
        Y_list=Y.split("||")
        
        Common=list(set(X_list) & set(Y_list))
        if(Y is not ''):
            illus_precision+=len(Common)/len(Y_list)
        if(X is not ''):
            illus_recall+=len(Common)/len(X_list)
        
        #NLD_similarity calculation
        common_len=0
        check_list=Y_list.copy()
        
        for i in range(len(X_list)):
            for j in range(len(Y_list)):
                if X_list[i]!='' and Y_list[j]!='':
                    if stringdist.levenshtein_norm(str(X_list[i]),str(Y_list[j]))<=.1:
                        common_len+=1
                        break
        Y_list=check_list.copy()
        if Y!='':
            NLD_precision+=common_len/len(Y_list)
        if(X!=''):
            NLD_recall+=common_len/len(X_list)
        
        if X is not "":
            illustrator+=1
        if Y is not "":
            illustrator_extracted+=1
    else:
        continue
    
illus_precision/=illustrator_extracted
illus_recall/=illustrator

NLD_precision/=illustrator_extracted
NLD_recall/=illustrator

try:
    illus_F1=2.0*illus_precision*illus_recall/(illus_precision+illus_recall)
except:
    illus_F1=0.0

try:
    NLD_F1=2.0/(1.0/NLD_precision+1.0/NLD_recall)
except:
    NLD_F1=0.0
print("illustrator_precision: ",illus_precision)
print("NLD_precision:",NLD_precision)
print("recall: ",illus_recall)
print("NLD_recall: ",NLD_recall)
print("F1 score: ",illus_F1)
print("NLD_F1 score: ",NLD_F1)



print("\nisbn")
isbn=0
isbn_extracted=0
isbn_extracted_correctly=0
for i in range(1,number_of_files):
    try:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=database[i][22]
        Y="".join(fdata("dc.identifier.isbn"))
        if X is not "":
            isbn+=1
        if Y is not "":
            isbn_extracted+=1
        if X is not "" and str(int(X))==str(Y):
            isbn_extracted_correctly+=1    
    except:
        continue
isbn_precision=isbn_extracted_correctly/isbn_extracted
recall=isbn_extracted_correctly/isbn
try:
    F1=2.0*isbn_precision*recall/(isbn_precision+recall)
except:
    F1=0.0
print("isbn_precision: ",isbn_precision)
print("recall: ",recall)
print("F1 score: ",F1)



print("\ncopyrights")
copyright=0
copyright_extracted=0
copyright_extracted_correctly=0
for i in range(1,number_of_files):
    try:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=int(fbase(7))
        Y=fdata("dc.date.copyright")
        if X is not "":
            copyright+=1
        if Y is not "":
            copyright_extracted+=1
        if X is not "" and str(int(X))==str(Y):
            copyright_extracted_correctly+=1            
    except:
        continue
copyright_precision=copyright_extracted_correctly/copyright_extracted
recall=copyright_extracted_correctly/copyright
try:
    F1=2.0*copyright_precision*recall/(copyright_precision+recall)
except:
    F1=0.0
print("copyright_precision: ",copyright_precision)
print("recall: ",recall)
print("F1 score: ",F1)



print("\nFormat info")
Format=0
Format_extracted=0
Format_extracted_correctly=0
for i in range(1,number_of_files):
    try:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(18).lstrip('"')
        Y=fdata("dc.format.extent")
        X=str(X).lower()
        Y=str(Y).lower()
        if X is not "":
            Format+=1
        if Y is not "":
            Format_extracted+=1
        if X is not "" and X==Y:
            Format_extracted_correctly+=1            
    except:
        continue
Format_precision=Format_extracted_correctly/Format_extracted
recall=Format_extracted_correctly/Format
try:
    F1=2.0*Format_precision*recall/(Format_precision+recall)
except:
    F1=0.0
print("Format_precision: ",Format_precision)
print("recall: ",recall)
print("F1 score: ",F1)



print("\n\nEducational_level info")
Educational_level=0
Educational_level_extracted=0
Educational_level_extracted_correctly=0
i=0
for i in range(1,number_of_files):
    i+=1
    try:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(57).lstrip('"')
        Y=fdata("dcterm.educationlevel")
        X=str(X).lower()
        Y=str(Y).lower()
        if X is not "":
            Educational_level+=1
        if Y is not "":
            Educational_level_extracted+=1
        if X is not None and X==Y:
            Educational_level_extracted_correctly+=1   
        
    except:
        continue
Educational_level_precision=Educational_level_extracted_correctly/Educational_level_extracted
recall=Educational_level_extracted_correctly/Educational_level
try:
    F1=2.0*Educational_level_precision*recall/(Educational_level_precision+recall)
except:
    F1=0.0
print("Educational_level_precision: ",Educational_level_precision)
print("recall: ",recall)
print("F1 score: ",F1)


print("\n\nDDC")
DDC=0
DDC_extracted=0
DDC_extracted_correctly=0
i=1

ddc_precision=0.0
ddc_recall=0.0
n=0
for i in range(1,number_of_files):
    if True:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(43).lstrip('"')
        Y=fdata("dc.subject.ddc")
        X=str(X).lower()
        Y=str(Y).lower()
        
        X=re.findall("{.*?}",X)[0]
        Y=re.findall("{.*?}",Y)[0]
        X_list=re.findall(r"'\d+': '.*?'",X)
        Y_list=re.findall(r"'\d+': '.*?'",Y)
        
        Common=list(set(X_list) & set(Y_list))
        
        if(len(Y_list)!=0):
            n+=1
            ddc_precision+=len(Common)/len(Y_list)
        if(len(X_list)!=0):
            ddc_recall+=len(Common)/len(X_list)
        
        if X is not "":
            DDC+=1
        if Y is not "":
            DDC_extracted+=1
    else:
        continue
recall=DDC_extracted_correctly/DDC
ddc_precision/=DDC_extracted
ddc_recall/=DDC    
try:
    ddc_F1=2.0/(1.0/ddc_precision+1.0/ddc_recall)
except:
    ddc_F1=0.0
print("DDC_precision: ",ddc_precision)
print("recall: ",ddc_recall)
print("F1 score: ",ddc_F1)



print("\nContents")
content=0
content_extracted=0
content_extracted_correctly=0
cont_precision=0.0
cont_recall=0.0
n=0
for i in range(1,number_of_files):
    if True:
        row=i
        filename=location+"metadata_"+database[i][0]+".json"
        f=open(filename)
        with open(filename) as f:
            data = json.load(f)
        X=fbase(14)
        Y=fdata("dc.description.toc")
        x=X
        y=Y
        X=str(X).lower()
        Y=str(Y).lower()
        
        X=re.sub("x\d+","",X)
        for p in string.punctuation+"–"+"—"+"‘":
            if p is not ":":
                p="\\"+str(p)
                X=re.sub(p," ",str(X).lower().strip())
                Y=re.sub(p," ",str(Y).lower().strip())
        X=re.sub("\s+"," ",X)
        Y=re.sub("\s+"," ",Y)
        
        
        X_list=X.split(":")
        Y_list=Y.split(":")
        
        Common=list(set(X_list) & set(Y_list))
        if(Y is not ''):
            cont_precision+=len(Common)/len(Y_list)
        if(X is not ''):
            cont_recall+=len(Common)/len(X_list)
        if X is not "":
            content+=1
        if Y is not "":
            content_extracted+=1            
        
        if X is not None and str(X)==str(Y):
            content_extracted_correctly+=1 
        
        
    else:
        continue
cont_precision/=content_extracted
cont_recall/=content
try:
    cont_F1=2.0*cont_precision*cont_recall/(cont_precision+cont_recall)
except:
    cont_F1=0.0


print("content_extracted_correctly:",content_extracted_correctly)
print("content_precision: ",cont_precision)
print("recall: ",cont_recall)
print("F1 score: ",cont_F1)
