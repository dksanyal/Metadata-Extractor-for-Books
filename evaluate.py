from __future__ import division
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from xlrd import open_workbook
import json
import re
import string
import stringdist


def evaluateMetadata(folder, golden):
    jsonfiles = [f for f in os.listdir(folder) if f.endswith('.json')]
    number_of_files=len(jsonfiles)+1  #add 1 for use in range(1, number_of_files)

    rb = open_workbook(golden)
    sheet1 = rb.sheet_by_index(0)
    database = [[sheet1.cell_value(r, c) for c in range(sheet1.ncols)] for r in range(sheet1.nrows)]     #golden_database
    data = ""

    def fbase(index):
        return database[row][index]
    def fdata(index):
        return data[index]

    #title
    title=0
    title_extracted=0
    title_extracted_correctly=0
    title_NLD=0
    for i in range(1,number_of_files):
            row = i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            #print(filename)
            try:
                with open(filename) as f:
                    data = json.load(f)
                    try:
                       X=fbase(50).lower().strip()
                    except:
                       X = ""
                    try:
                       Y="".join(fdata("dc.title")).lower().strip()
                    except:
                       Y=""
                    for p in string.punctuation+"–"+"—":
                       p="\\"+str(p)
                       X=re.sub(p," ",re.sub("\s+"," ",X)).strip()
                       Y=re.sub(p," ",re.sub("\s+"," ",Y)).strip()
                    if  X != "":
                       title+=1
                    if  Y != "":
                       title_extracted += 1
                    if X != "" and Y != "" and stringdist.levenshtein_norm(str(X).lower(),str(Y).lower())<=.1:
                       title_NLD+=1
                    if X != "" and X==Y:
                       title_extracted_correctly += 1
            except:
                data=""
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
    title=[title_precision,NLD_precision,recall,NLD_recall,F1,NLD_F1]


    #abstract
    description=0
    description_extracted=0
    description_extracted_correctly=0
    description_NLD=0
    i=0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            try: 
              with open(filename) as f:
                  data = json.load(f)
                  X=fbase(16).lower()

                  Y="".join(fdata("dc.description.abstract")).lower()
                  for p in string.punctuation:
                      p="\\"+str(p)
                      X=re.sub(p," ",re.sub("\s+"," ",X)).strip()
                      Y=re.sub(p," ",re.sub("\s+"," ",Y)).strip()
                  if X != "":
                     description+=1
                  if Y != "":
                     description_extracted+=1
                  if X != "" and stringdist.levenshtein_norm(str(X),str(Y))<=.1:
                     description_NLD+=1
                  if X != "" and X==Y:
                     description_extracted_correctly+=1
            except:
              pass
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

    abstract=[description_precision,NLD_precision,recall,NLD_recall,F1,NLD_F1]

    #editor
    editor=0
    editor_extracted=0
    edit_precision=0.0
    edit_recall=0.0
    n=0
    NLD_precision=0
    NLD_recall=0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            try:
              with open(filename) as f:
                 data = json.load(f)
                 X=str(fbase(5)).strip()
                 if X != "":
                     editor+=1
                 try:
                     Y="".join(fdata("dc.contributor.editor")).strip()
                 except:
                     Y=""
                 X_list=X.split("||")
                 Y_list=Y.split("||")
                 Common=list(set(X_list) & set(Y_list))

                 if(len(Y_list) != 0):
                     edit_precision+=len(Common)/len(Y_list)
                 if(len(X_list) != 0):
                     edit_recall+=len(Common)/len(X_list)

                 #NLD_similarity calculation
                 common_len=0
                 check_list=Y_list.copy()
                 for i in range(len(X_list)):
                     for j in range(len(Y_list)):
                         if X_list[i]!='' and Y_list[j]!='':
                            if stringdist.levenshtein_norm(str(X_list[i]),str(Y_list[j]))<=.1:
                               Y_list[j] = '' #added
                               common_len+=1
                               break
                 Y_list=check_list.copy()
                 if len(Y_list) != 0:
                    NLD_precision+=common_len/len(Y_list)
                 if len(X_list) != 0:
                    NLD_recall+=common_len/len(X_list)
                 if Y != "":
                    editor_extracted+=1
            except:
              pass
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
    editor=[edit_precision,NLD_precision,edit_recall,NLD_recall,edit_F1,NLD_F1]



    #illustrator
    illustrator=0
    illustrator_extracted=0
    i=0
    illus_precision=0.0
    illus_recall=0.0
    NLD_precision=0.0
    NLD_recall=0.0
    n=0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            with open(filename) as f:
              try:
                data = json.load(f)
                X=fbase(6)
                Y="".join(fdata("dc.contributor.illustrator"))

                X_list=X.split("||")
                Y_list=Y.split("||")

                Common=list(set(X_list) & set(Y_list))
                if(len(Y_list) != 0):
                    illus_precision+=len(Common)/len(Y_list)
                if(len(X_list) != 0):
                    illus_recall+=len(Common)/len(X_list)

                #NLD_similarity calculation
                common_len=0
                check_list=Y_list.copy()
                for i in range(len(X_list)):
                   for j in range(len(Y_list)):
                       if X_list[i]!='' and Y_list[j]!='':
                          if stringdist.levenshtein_norm(str(X_list[i]),str(Y_list[j]))<=.1:
                             common_len+=1
                             Y_list[j] = '' #added
                             break
                Y_list=check_list.copy()
                if len(Y_list)!=0:
                    NLD_precision+=common_len/len(Y_list)
                if(len(X_list)!=0):
                    NLD_recall+=common_len/len(X_list)

                if X != "":
                    illustrator+=1
                if Y != "":
                    illustrator_extracted+=1
              except:
                pass
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
    illustrator=[illus_precision,NLD_precision,illus_recall,NLD_recall,illus_F1,NLD_F1]

    #isbn
    isbn=0
    isbn_extracted=0
    isbn_extracted_correctly=0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            with open(filename) as f:
              try:
                data = json.load(f)
                X=database[i][22]
                Y="".join(fdata("dc.identifier.isbn"))
                if X != "":
                   isbn+=1
                if Y != "":
                   isbn_extracted+=1
                if X != "" and str(int(X))==str(Y):
                   isbn_extracted_correctly+=1
              except:
                pass
    isbn_precision=isbn_extracted_correctly/isbn_extracted
    recall=isbn_extracted_correctly/isbn
    try:
        F1=2.0*isbn_precision*recall/(isbn_precision+recall)
    except:
        F1=0.0
    isbn=[isbn_precision,recall,F1]

    #copyright
    copyright=0
    copyright_extracted=0
    copyright_extracted_correctly=0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            with open(filename) as f:
              try:
                data = json.load(f)
                X=int(fbase(7))
                Y=fdata("dc.date.copyright")
                if X != "":
                   copyright+=1
                if Y != "":
                   copyright_extracted+=1
                if X != "" and str(int(X))==str(Y):
                   copyright_extracted_correctly+=1
              except:
                pass
    copyright_precision=copyright_extracted_correctly/copyright_extracted
    recall=copyright_extracted_correctly/copyright
    try:
        F1=2.0*copyright_precision*recall/(copyright_precision+recall)
    except:
        F1=0.0
    copyright=[copyright_precision,recall,F1]


    #education Level
    Educational_level=0
    Educational_level_extracted=0
    Educational_level_extracted_correctly=0
    i=0
    for i in range(1,number_of_files):
        #i+=1
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            try:
              with open(filename) as f:
                 data = json.load(f)
                 X=fbase(57).lstrip('"')
                 Y=fdata("dcterm.educationlevel")
                 X=str(X).lower()
                 Y=str(Y).lower()
                 if X != "":
                   Educational_level+=1
                 if Y != "":
                   Educational_level_extracted+=1
                 if X is not None and X==Y:
                   Educational_level_extracted_correctly+=1
            except:
              pass
    Educational_level_precision=Educational_level_extracted_correctly/Educational_level_extracted
    recall=Educational_level_extracted_correctly/Educational_level
    try:
        F1=2.0*Educational_level_precision*recall/(Educational_level_precision+recall)
    except:
        F1=0.0
    education_level=[Educational_level_precision,recall,F1]


    #DDC 
    DDC=0
    DDC_extracted=0
    i=1
    ddc_precision=0.0
    ddc_recall=0.0
    for i in range(1,number_of_files):
            row=i
            filename=folder+"/"+"metadata_"+database[i][0]+".json"
            try:
              with open(filename, 'r') as f:
                 data = json.load(f)
                 X=fbase(43).lstrip('"')
                 Y=fdata("dc.subject.ddc")
                 X=str(X).lower()
                 Y=str(Y).lower()

                 X=re.findall("{.*?}",X)[0]
                 Y=re.findall("{.*?}",Y)[0]
                 X_list=re.findall(r"'\d+': '.*?'",X)
                 Y_list=re.findall(r"'\d+': '.*?'",Y)


                 Common=list(set(X_list) &  set(Y_list))

                 #print ("DDC: " + str(X_list) +  str(Y_list))
                 #print("Len of common, X_list, Y_list = " + str(len(Common)) + str(len(X_list)) + str(len(Y_list)))
                 if(len(Y_list)!=0):
                     ddc_precision += len(Common)/len(Y_list)
                 if(len(X_list)!=0):
                     ddc_recall += len(Common)/len(X_list)
                 if len(X_list) != 0:
                     DDC += 1
                 if len(Y_list) != 0:
                     DDC_extracted += 1
            except:
                 pass
    ddc_precision/=DDC_extracted
    ddc_recall/=DDC
    try:
        ddc_F1=2.0/(1.0/ddc_precision+1.0/ddc_recall)
    except:
        ddc_F1=0.0
    ddc=[ddc_precision,ddc_recall,ddc_F1]


    #Contents
    content=0
    content_extracted=0
    content_extracted_correctly=0
    cont_precision=0.0
    cont_recall=0.0
    n=0
    for i in range(1,number_of_files):
          row=i
          filename=folder+"/"+"metadata_"+database[i][0]+".json"
          try:  
            with open(filename) as f:
                data = json.load(f)
                X=fbase(14)
                Y=fdata("dc.description.toc")
                X=str(X).lower()
                Y=str(Y).lower()
                X=re.sub("x\d+","",X)
                for p in string.punctuation+"–"+"—"+"‘":
                    if p is not ",":
                       p="\\"+str(p)
                       X=re.sub(p," ",str(X).lower().strip())
                       Y=re.sub(p," ",str(Y).lower().strip())
                X=re.sub("\s+"," ",X)
                Y=re.sub("\s+"," ",Y)

                X_list=X.split(',')
                Y_list=Y.split(',')
                X_list_1 = list()
                Y_list_1 = list()
                for elem in X_list:
                    elem = elem.strip()
                    X_list_1.append(elem)

                for elem in Y_list:
                    elem = elem.strip()
                    Y_list_1.append(elem)

                X_list = X_list_1
                Y_list = Y_list_1

                #print("FINAL CONTENTS ***-------------------------> (X, Y):") 
                #print(X_list)
                #print(Y_list)
                Common=list(set(X_list) & set(Y_list))
                #print("LEN CONTENTS: Common: " + str(len(Common)) + ", X_list:" + str(len(X_list)) + ", Y_list: " + str(len(Y_list)))
                if(Y != ''):
                    cont_precision+=len(Common)/len(Y_list)
                if(X != ''):
                    cont_recall+=len(Common)/len(X_list)
                if X != '':
                    content+=1
                if Y != '':
                    content_extracted+=1
                if X is not None and str(X)==str(Y):
                    content_extracted_correctly+=1
          except:
            pass

    #print("Content extracted exactly correct = " + str(content_extracted_correctly) + ", total extracted TOCs = " + str(content_extracted) + ", total TOCs = " + str(content))
    #print("Content precision total = " + str(cont_precision) + ", Content recall total = " + str(cont_recall))
    cont_precision/=content_extracted
    cont_recall/=content
    try:
        cont_F1=2.0*cont_precision*cont_recall/(cont_precision+cont_recall)
    except:
        cont_F1=0.0
    content=[cont_precision,cont_recall,cont_F1]
    #print("Contents eval: " + str(content))

    perfMatrix1=np.array([title,abstract,editor,illustrator],np.float)
    perfMatrix2=np.array([content,isbn,copyright,education_level,ddc],np.float)
    #Return the matrices    
    d = dict()
    d['matrix1'] = perfMatrix1
    d['matrix2'] = perfMatrix2
    d['error']   = False
    return d

    


#def cmpOutputGolden()
