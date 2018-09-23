# -*- coding: utf-8 -*-
import roman
import re
from bs4 import BeautifulSoup
import json
import sys
import requests
import string
from io import open
from collections import OrderedDict
import subprocess

name=sys.argv[1]
fold=sys.argv[2]
folder=sys.argv[3]
json_fold=sys.argv[4]
pdf_info_dir=sys.argv[5]
hocr_dir=sys.argv[6]

#name="aeen1ps.xml"
#fold="xml_database/"
#json_fold="JSON/"
#pdf_info_dir="Pdfinfo-database/"
#hocr_dir="hOCR/"

url=fold+name+".xml"
metadata=OrderedDict()

soup=BeautifulSoup(open(fold+name+".xml",encoding='utf-8',errors='ignore'), "lxml")
json_output=open(json_fold+"metadata_"+name+".json",'w+',encoding='utf-8',errors='ignore')


with open(url, 'r',encoding='utf-8',errors='ignore') as myfile:
    data=myfile.read()
content_pages=[]
content_page_list=[]


from hunspell import Hunspell
h=Hunspell()

#Structure Multiline Metadata 
def remove_n(text):
    if type(text)==type([]):
        text=text[0]
    text=text.rstrip("\n")
    text=text.strip(" : ").strip(": ").strip(":").strip("^ ")
    pos=re.search("\n",text)
    count=0
    if True:
        while pos is not None:
            if len(text)==pos.span()[1]:
                break
            count+=1
            text_size=len(text)
            pos=pos.span()
            
            if re.match("\d",text[pos[1]]) is not None:
                pos=re.compile("\n").search(text,pos[1]+1)
                continue 
            
            check=re.search("and",text[pos[0]-4:pos[0]])
            if check is not None:
                text=text[:pos[0]]+" "+text[pos[1]:]
            check=re.search("and",text[pos[1]:pos[1]+4])
            if check is not None:
                text=text[:pos[0]]+" "+text[pos[1]:]
            if len(text)==text_size:
                if text[pos[0]-1]==":" or text[pos[1]-2]==":"and text[pos[0]-1]==" " :
                    text=text[:pos[0]-1]+":"+text[pos[1]:]
                elif text[pos[1]]<='z' and text[pos[1]]>='a':
                    text=text[:pos[0]]+" "+text[pos[1]:]
            
            pos=re.compile("\n").search(text,pos[1]+1)
        #text=re.sub("\s{2,100}"," ",text)
        text=text.split("\n")
        if len(text)>1:
            return text
        elif len(text)==1: 
            return text[0]
        else:
            return ""
    else:
        #text=re.sub("\s{2,100}"," ",text)
        text=text.split("\n")
        return text

#Remove single extra characters
def remove_extra(text):
    words=text.split()
    if len(words)==1:
        text=""
    if len(words)>2:
        text=words[0]+" "+words[1]
    return text

#check content format
def content_format_check(pages,num,i):
    x=False
    if re.search(r'[\divx]+',pages[num][i][4]) is not None:
        x=True
    if i>1:
        if re.search(r'\d+',pages[num][i-1][4]) is not None:
            x=True
    if i>2:   
        if re.search(r'\d+',pages[num][i-2][4]) is not None:
            x=True
    if i>3:   
        if re.search(r'\d+',pages[num][i-3][4]) is not None:
            x=True
    return x

#extract text from pages removing noises
def page_text(pages,num):
    x=''
    for i in range(len(pages[num])):
        if content_format_check(pages,num,i) is True and pages[num][i][4] is not '':
            x=x+pages[num][i][4]+"\n"
    x=re.sub('__','',x)
    x=re.sub('<b>','',x)
    x=re.sub('<i>','',x)
    x=re.sub('</b>','',x)
    x=re.sub('</i>','',x)
    return x
  
#extract text from the cover page    
def page_text_1(pages,num):
    x=''
    for i in range(len(pages[num])):
        x=x+pages[num][i][4]+"\n"
    return x    


#handle unstructured text        
def Sort(all_texts):
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if abs(all_texts[i][0]-all_texts[j][0])<15:
                all_texts[i][0]=all_texts[j][0]
    for i in range(1,len(all_texts)):           
        if all_texts[i][0] == all_texts[i-1][0] and all_texts[i][2]<all_texts[i-1][3] and all_texts[i][4]==all_texts[i-1][4] :
            all_texts[i-1][4]=""
    for i in range(1,len(all_texts)): 
        #all_texts[i][4]=''.join([k if ord(k) < 128 else ' ' for k in all_texts[i][4]])          
        if all_texts[i][2]>1200 or all_texts[i][2]<0 or all_texts[i][0]>1050 or all_texts[i][0]<100 :
            all_texts[i][4]=""
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if all_texts[i][0]<all_texts[j][0] or all_texts[i][0] == all_texts[j][0] and all_texts[i][2]<all_texts[j][2] :
                text=all_texts[i]
                all_texts[i]=all_texts[j]
                all_texts[j]=text

    return all_texts

#structure cover page
def Sort_1st_page(all_texts):
    for i in range(len(all_texts)):
        #all_texts[i][4]=''.join([k if ord(k) < 128 else ' ' for k in all_texts[i][4]])                     
        if all_texts[i][2]>1200 or all_texts[i][2]<0 or all_texts[i][0]>750 or all_texts[i][0]<50:
            all_texts[i][4]=""
    
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if abs(all_texts[i][0]-all_texts[j][0])<20:
                all_texts[i][0]=all_texts[j][0]
    for i in range(len(all_texts)):
        for j in range(i+1,len(all_texts)):       
            if abs(all_texts[i][0] - all_texts[j][0])<20 and all_texts[j][2]<all_texts[i][3]-3 and all_texts[i][4] is not "":
                all_texts[j][4]=""
    return all_texts

#structure 2nd page containing publication information 
def Sort_2nd_page(all_texts): 
    for i in range(len(all_texts)):           
        #all_texts[i][4]=''.join([k if ord(k) < 128 else ' ' for k in all_texts[i][4]])          
        if all_texts[i][0]>1200 or all_texts[i][2]<0 or all_texts[i][2]>750:
            all_texts[i][4]=""           
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if all_texts[i][2]>320:
                all_texts[i][0]=all_texts[i][0]+2000
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if abs(all_texts[i][0]-all_texts[j][0])<10:
                all_texts[i][0]=all_texts[j][0]
            if all_texts[i][0] == all_texts[j][0] and all_texts[i][2]<all_texts[j][2] :
                text=all_texts[i]
                all_texts[i]=all_texts[j]
                all_texts[j]=text
            if all_texts[i][0]<all_texts[j][0]:
                text=all_texts[i]
                all_texts[i]=all_texts[j]
                all_texts[j]=text
    for i in range(len(all_texts)):
        for j in range(len(all_texts)):
            if abs(all_texts[i][0]-all_texts[j][0])<10:
                all_texts[i][0]=all_texts[j][0]
    
    for i in range(len(all_texts)):
        for j in range(i+1,len(all_texts)):       
            if abs(all_texts[i][0] - all_texts[j][0])<10 and all_texts[j][2]<all_texts[i][3]-3 :
                all_texts[j][4]=""

    return all_texts


#Handle multiline metdata  
def Fuse_text(num):
    page_start=re.compile( '<page .*number="'+str(num)+'".*>').search(data).span()[1]
    page_end=re.compile("</page>").search(data,page_start).span()[0]
    texts=re.compile("<text.*</text>").findall(data,page_start,page_end)
    
    all_texts=[[]]
    for text in texts:
        curr_text=[]
        tops=re.search('top="\d*"',text).span()
        top=int(text[tops[0]:tops[1]].strip('top="').rstrip('"'))
    
        lefts=re.search('left="\-?\d*"',text)
        if lefts is not None:
            left=int(text[lefts.span()[0]:lefts.span()[1]].strip('left="').rstrip('"'))
        else:
            left=0
    
        texs=re.search('>.+<',text).span()
        tex=text[texs[0]:texs[1]].strip('>').rstrip('<').replace('<i>','').replace('</i>','').replace('<b>','').replace('</b>','')
    
        
        heights=re.search('height="\d*"',text).span()
        height=int(text[heights[0]:heights[1]].strip('height="').rstrip('"'))
        
        bottom=top+height
        
        widths=re.search('width="\d*"',text)
        if widths is not None:
            width=int(text[widths.span()[0]:widths.span()[1]].strip('width="').rstrip('"'))
        else:
            width=0  
        right=left+width
        
        
        
        curr_text.append(top)
        curr_text.append(bottom)
        curr_text.append(left)
        curr_text.append(right)
        curr_text.append(tex)
        all_texts.append(curr_text)
    all_texts.pop(0)        
    
    if num==1:
        all_texts=Sort_1st_page(all_texts)
    
    new_text=[[]]
    
    i=0
    
    while i <len(all_texts):
        curr_text=all_texts[i]
        j=1
        try:
            while i+j<len(all_texts) and abs(all_texts[i][1]-all_texts[i+j][1])<15:
                if abs(all_texts[i+j][2]-all_texts[i+j-1][3])<3 or abs(all_texts[i+j][3]-all_texts[i+j-1][2])<3:
                    curr_text[4]=curr_text[4]+all_texts[i+j][4]
                else:
                    if len(all_texts[i+j][4])>1 or len(all_texts[i+j][4])>1 and all_texts[i+j][4]<='Z' and all_texts[i+j][4]>='A': 
                        curr_text[4]=curr_text[4]+" "+all_texts[i+j][4]
                j=j+1
        except:
            break
        i=i+j
        if curr_text[4] is not "" and len(curr_text[4]) >2 :
                new_text.append(curr_text)
    new_text.pop(0)
    if num is 1:
        new_text=Sort_1st_page(new_text)
    elif num==2 or num==3:
        new_text=Sort_2nd_page(new_text)
    return new_text
        


def Fuse(num):
    page_start=re.compile('<page .*number="'+str(num)+'".*>').search(data).span()[1]
    page_end=re.compile("</page>").search(data,page_start).span()[0]
    
    try:
        texts=re.compile("<text.*</text>").findall(data,page_start,page_end)
        if texts is None:
            return []
        all_texts=[[]]
        for text in texts:
            curr_text=[]
            tops=re.search('top="\d*"',text).span()
            top=int(text[tops[0]:tops[1]].strip('top="').rstrip('"'))
            
            lefts=re.search('left="\-?\d*"',text).span()
            left=int(text[lefts[0]:lefts[1]].strip('left="').rstrip('"'))
            
    
            texs=re.search('>.+<',text).span()
            tex=text[texs[0]:texs[1]].strip('>').rstrip('<').replace('<i>','').replace('</i>','').replace('<b>','').replace('</b>','')
    
        
            heights=re.search('height="\d*"',text).span()
            height=int(text[heights[0]:heights[1]].strip('height="').rstrip('"'))
        
            bottom=top+height
            
            widths=re.search('width="\d*"',text).span()
            width=int(text[widths[0]:widths[1]].strip('width="').rstrip('"'))
            
            right=left+width
        
        
        
            curr_text.append(top)
            curr_text.append(bottom)
            curr_text.append(left)
            curr_text.append(right)
            curr_text.append(tex)
            all_texts.append(curr_text)
        all_texts.pop(0)        
        
        new_text=[[]]
        i=0
        all_texts=Sort(all_texts)
        while i <len(all_texts):
            curr_text=all_texts[i]
            j=1
            try:
                while i+j<len(all_texts) and abs(all_texts[i][1]-all_texts[i+j][1])<15:
                    if abs(all_texts[i+j][2]-all_texts[i+j-1][3])<3 or abs(all_texts[i+j][3]-all_texts[i+j-1][2])<3 :
                        curr_text[4]=curr_text[4]+all_texts[i+j][4]
                    else:
                        curr_text[4]=curr_text[4]+" "+all_texts[i+j][4]
                    j=j+1
            except:
                break
            i=i+j
            if curr_text[4] is not "" and len(curr_text[4]) >2 :
                new_text.append(curr_text)
        new_text.pop(0)
        return new_text
    except:
        return []

#find content start page
def find_content(pages):
    page_no=0
    keywords=['\s*CONTENTS','C O N T E N T S','TABLE OF CONTENTS','THEME','What is inside this book?','Foreword']
    #keywords=['\s*CONTENTS','TABLE OF CONTENTS','THEME','What is inside this book?','Foreword']    
    for x in keywords:
        for i in range(1,len(pages)):
            for j in range(0,min(15,len(pages[i]))):
                if re.search(x,pages[i][j][4],re.IGNORECASE) is not None:
                    page_no=i
                    seq,patt,page_no=Content_pattern_check(pages,page_no)
                    if page_no is not 0:
                        return seq,patt,page_no
                    else:
                        continue
    return 0,"",0

#ensure if content pattern exists in the chosen content start page
def Content_pattern_check(pages,page_no):        
    Pattern=''
    patterns=['\s*Unit\s*[\dIVXivx]+','\s*Chapter\s*\-?\d+','\s*C\s*H\s*A\s*[PT]\s*[TP]\s*E\s*R\s*\d+','\s*CHAPTER\s*\d+','\s*Chap\s*\d+','\s*CHAP\s*\d+','\s*Theme[\s\d]+','\s*Theme[\s\d]+','\s*Section\s*[\divxIVX]+','\d+\.[(\d+)\.]*','PART\s*[\divxIVX]+','\s*[\divxIVX]+\.','\s*\d+\)','\s*\(\d+\)']
    for pattern in patterns:
        for i in range(len(pages[page_no])):
            if len(pages[page_no])==1:
                continue
            if re.match(pattern,pages[page_no][i][4]):
                Pattern=pattern
                break
        if Pattern is not '':
            break
    if Pattern is '':
        return 0,Pattern,0
    new_pattern=re.compile(Pattern).findall(page_text(pages,page_no))[-1]
    seq1=re.findall(r'\d+',new_pattern)
    if len(seq1) is not 0:
        seq2=str(int(seq1[0])+1)
    else:
        seq1=re.findall(r'[ivxIVX]+',new_pattern)[0]
        if seq1=="i":
            seq1="I"
        seq2=roman.toRoman(roman.fromRoman(seq1)+1)
    return seq2,Pattern,page_no
    
#check subsequent pages for similar content pattern recursively
def check_pattern(page_no,pattern,seq,pages):
    if True:
        if len(pages)==page_no:
            return
        if page_text(pages,page_no) is '' :
            return
        if re.search(pattern,page_text(pages,page_no)) is None:
            return
        if re.search('\d+',re.findall(pattern,page_text(pages,page_no),re.IGNORECASE)[0]) is None:
            return
        if re.search(pattern,page_text(pages,page_no),re.IGNORECASE) is not None and str(seq)==re.findall('\d+',re.findall(pattern,page_text(pages,page_no),re.IGNORECASE)[0])[0] or re.search('^\d+\.\d+(\.\d+)* ',page_text(pages,page_no)) is not None:
            content_pages.append(page_text(pages,page_no))
            content_page_list.append(pages[page_no])
            Pattern=re.findall(pattern,page_text(pages,page_no))[-1]
            seq=int(re.findall(r'\d+',Pattern)[0])
            check_pattern(page_no+1,pattern,seq+1,pages)
        
#Generate HOCR files for alternate flow
def hocr_convert():
    subprocess.call(["mkdir","tmp/"+name])
    p=0
    while True:
        command1=subprocess.call(["convert","-density","300","-colorspace", "Gray","-threshold","55%",folder+name+".pdf["+str(p)+"]","-depth","8","-strip","-background","white","-alpha","off","tmp/"+name+"/"+name+"_"+str(p)+".tiff"])
        command2=subprocess.call(["tesseract","tmp/"+name+"/"+name+"_"+str(p)+".tiff","tmp/"+name+"/"+name+"_"+str(p),"--oem","3","-l","eng","hocr"])
        subprocess.call(["rm","tmp/"+name+"/"+name+"_"+str(p)+".tiff"])
        
        print(name+".pdf["+str(p)+"]"+"done")
        p+=1
        if command1 is not 0 or command2 is not 0:
            break

        
#Alternative Flow
def alter():
    try:
        url=hocr_dir+name+"/"+name.strip(".xml")+"_0"+".hocr"
        with open(url, 'r',encoding='utf-8',errors='ignore') as myfile:
            data=myfile.read()
        
        texts=[]
        word_text=""
        line_text=""
        p_text=""
        X_text=""
        
        c_areas=re.findall("<div.*?class='ocr_carea'.*?</div>",data,re.DOTALL)
        if len(c_areas)>0:    
            for i in range(len(c_areas)):
                text_i=[]
                pars=re.findall("<p.*?class='ocr_par'.*?</p>",c_areas[i],re.DOTALL)
                if(len(pars)>0):
                    p_text=""
                    for j in range(len(pars)):
                        text_j=[]
                        lines=re.findall("<span.*?class='ocr_line'.*?</span>\n",pars[j],re.DOTALL)
                        if(len(lines)>0):
                            line_text=""
                            for k in range(len(lines)):
                                text_k=[]
                                words=re.findall("<span class='ocrx_word'.*?</span>",lines[k],re.DOTALL)
                                if len(words)>0:
                                    word_text=""
                                    
                                    for l in range(len(words)):
                                        #print(words[l])
                                        x=re.findall(r">.*?</span>",words[l],re.DOTALL)
                                        if len(x)>0:
                                            x=re.sub("</span","",x[0].strip(">"))
                                        bbox=re.findall(r"title='bbox \d+ \d+ \d+ \d+",words[l],re.DOTALL)[0].strip("title='bbox ")
                                        bbox=bbox.split()
                                        text=[]
                                        if len(bbox)>0:
                                            text.append(bbox[1])
                                            text.append(bbox[3])
                                            text.append(bbox[0])
                                            text.append(bbox[2])
                                            text.append(x)
                                            
                                        if int(text[0])<2000:
                                            text_k.append(text)
                                            x=re.sub(u"\u2018","'",x)
                                            if h.spell(x) or len(h.suggest(x))is 0:
                                                word_text+=" "+x
                                            else:
                                                word_text+=" "+h.suggest(x)[0]
                                            word_text=word_text.strip()
                                text_j.append(text_k)
                                line_text+="\n"+word_text
                                line_text=line_text
                        text_i.append(text_j)
                        p_text+="\n\n"+line_text
                        p_text=p_text.strip()
                texts.append(text_i)
                X_text+="\n\n\n"+p_text
                X_text=X_text.strip("\n\n\n")
        titles=X_text
        desc=re.search("(T\s?E\s?X\s?T\s?.*C\s?l\s?a\s?s\s?s\s*[IVX]+\s*(\(.*?\))?)|(Supplementary.*Class\s*[IVX]+\s*(\(.*\))?)",titles,re.DOTALL|re.IGNORECASE)
        if desc is not None:
            desc=desc.span()
            des=titles[desc[0]:desc[1]]
            title=titles[:desc[0]]+titles[desc[1]:]
        else:
            des=""
            title=titles
        yyy=re.sub("[\n\s]+"," ",title)
        des=re.sub("[\n\s]+"," ",des)
        xxx=""
        for i in yyy.split():
            if (h.spell(i)==True and len(str(i))>1) or (i[0]<='9' and i[0]>='0') or i=='a' or i=='A' or i=='i' or i=='I' :
                xxx=xxx+i+" "
        title=xxx
        Class=re.findall(r"Class\s*[IVX]+",des,re.IGNORECASE)
        if len(Class)>0:
            Class=re.sub('^Class\s*',"",Class[0],flags=re.IGNORECASE)
        elif len(re.findall(r"Class\s*[\dIVX]+",des,re.IGNORECASE))>0:
            Class=re.sub('^Class\s*',"",re.findall(r"Class\s*[\dIVX]+",des,re.IGNORECASE)[0],flags=re.IGNORECASE)
        else:
            Class='XIII'  
            
        return title,des,Class
    except:
        return "","","XII"

def check_title(yyy):
    #alternate flow triggering part
    check=True
    title_xxx=yyy
    for p in string.punctuation+"–"+"—"+":":
            p="\\"+str(p)
            title_xxx=re.sub(p," ",title_xxx)
    p=False
    for i in re.sub("part","",re.sub("book","",title_xxx.lower())).split():
        if h.spell(i)==True and len(str(i))>1:
            p=True
            break
    if p is False:
        check=False
    #invoking the alternate flow
    title_xxx=re.sub("[(Book)(book)(part)(one)(two)(three)(four)(five)(six)(seven)(eight)\d\sIVX]+","",title_xxx,re.IGNORECASE)
    if title_xxx=="" or check==False:
        return False
    else:
        return True

#main section
pages=[[[]]]

num_page=len(re.compile(r'<page.*?</page>',re.DOTALL).findall(data))
for i in range(1,5):
    pages.append(Fuse_text(i)) 
    
subject_test_text=""  
Class=""    
if True:
    text=page_text_1(pages,1)
    
    #pattern analysis
    text_list=re.findall(r".*",text)
    title=text_list[0]
    desc=''
    for i in range(1,len(text_list)):
        if text_list[i] is not title and text_list[i] is not "":    
            desc=desc+text_list[i]+"\n"
    
    titles=title+" "+desc
    desc=re.search("(T\s?E\s?X\s?T\s?.*C\s?l\s?a\s?s\s?s\s*[IVX]+\s*(\(.*?\))?)|(Supplementary.*Class\s*[IVX]+\s*(\(.*\))?)",titles,re.DOTALL|re.IGNORECASE)
    if desc is not None:
        desc=desc.span()
        des=titles[desc[0]:desc[1]]
        title=titles[:desc[0]]+titles[desc[1]:]
    else:
        
        des=""
        title=titles
    subject_test_text+=title
    title=title.split("\n")
    xyz=""
    if len(title)>0:
        for i in range(len(title)):
            if re.search("book in",title[i],re.IGNORECASE) is None:
                xyz+=title[i]+"\n"
            else:
                des=title[i]
    title=xyz
    yyy=remove_n(title)
    
    if type(yyy)==type([]):
        zzz=yyy[0]
        for i in range(1,len(yyy)):
            zzz+=" "+yyy[i]
        yyy=zzz
    x=re.findall("Book\s*[(one)(two)(three)(four)(five)(six)(seven)(eight)\dIVX]+",yyy,re.IGNORECASE)
    if len(x)>0:
        x=x[0]
        yyy=re.sub(x,"",yyy)
        yyy=yyy+":"+x
    
    
    Class=re.findall(r"Class\s*[IVX]+",text,re.IGNORECASE)
    if len(Class)>0:
        Class=re.sub('^Class\s*',"",Class[0],flags=re.IGNORECASE)
    elif len(re.findall(r"Class\s*[\dIVX]+",des,re.IGNORECASE))>0:
        Class=re.sub('^Class\s*',"",re.findall(r"Class\s*[\dIVX]+",des,re.IGNORECASE)[0],flags=re.IGNORECASE)
    else:
        Class='XIII'
    
    if check_title(yyy) is False:
        hocr_convert()
        alt=alter()
        yyy=alt[0]
        if des=="":
            des=alt[1]
            Class=alt[2]
    
    metadata['dc.title']=yyy.strip()
    metadata['dc.description.abstract']=remove_n(des) 
    
    if Class!='XIII':
        metadata["dcterm.educationlevel"]=Class
    else:
        metadata["dcterm.educationlevel"]=""
    
    #page_2 processing
    #Publication Dates
    publication_date=OrderedDict()
    text=page_text_1(pages,2)
    if re.search("ISBN",text) is None:
        text=page_text_1(pages,3)
    if re.search("ISBN",text) is None:
        text=page_text_1(pages,4)
    output=re.findall(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*(Kartika|Phalguna|Magha|Agrahayana|Asvina|Vaishakha|Pausa|Chaitra|Jyaistha|Asadha|Shravana|Bhadra)?(\s+\d{4})?",text)
    first=''
    if len(output)>0:
        for i in output[0]:
            first=first+i
    publication_date['dc.date.firstPublication']=remove_n(first)
    
    reprint=''
    for i in range(1,len(output)):
        for j in output[i]:
            reprint=reprint+j
        reprint=reprint+"\n"
    publication_date['dc.date.reprint']=remove_n(reprint)

    #ISBN
    try:
        isbn=re.findall(r"ISBN\s+[\d\-X]+.*(\n.*[\d\-X]+.*)+",text)
        if len(isbn)>0:
            isbn=isbn[0]
        else:
            isbn=re.findall(r"ISBN[\s\d\-X]+",text)[0]
        isbn=re.findall(r"[\d\-X]{8,20}",isbn)[-1]
        isbn=remove_n(isbn)
        if type(isbn)==type([]):
            isbn=isbn[0]
        isbn=re.sub("\-","",isbn)
        metadata["dc.identifier.isbn"]=isbn
        
    except:
        metadata["dc.identifier.isbn"]=""
         
    #Copyright Year
    if True:
        year=""
        id=re.compile(r'©.*\d+',re.DOTALL).findall(soup.get_text())
        if len(id)>0:
            year=re.findall(r'\d+',id[0])[0]
        
        else:
            id=re.compile(r'[©(copyright)(all rights reserved)].*?\d{4}',re.DOTALL).findall(soup.get_text())
            if len(id)>0:
                year=re.findall(r'\d+',id[0])[0]
            
        metadata["dc.date.copyright"]=remove_n(year)
    
    #Editor Information
    try:
        publisher=re.findall(r"Head,\s*Publication.*",text)[0]
        editor_text=""
        editors=re.findall(r"Editor.*",text,re.IGNORECASE)
        for i in range(len(editors)):
            editor=re.sub("Editor\s*:?\s*","",editors[i]).strip(" : ").strip(": ")
            editor=editor.split()[-1]+","+editor.split()[0]
            editor=remove_n(editor)
            if i is not 0:
                editor_text+="||"+editor
            else:
                editor_text+=editor
        
        metadata["dc.contributor.editor"]=editor_text
        
    except:
        metadata["dc.contributor.editor"]=""

    new_page=[]
    p=2
    found=False
    for p in range(2,len(pages)):   
        for i in range(len(pages[p])):
            if re.search("Publication\s*Team",pages[p][i][4]) is not None:
                    found=True
            if found==True:
                    new_page.append(pages[p][i])
        if(found==True):
            break            
            
    
    found=0
    found_top=1000000
    found_left=1000000
    for i in range(len(new_page)):
            if re.search("Cover.*[(and),] Illustrations",new_page[i][4],re.IGNORECASE) is not None:
                if new_page[i][0]<found_top or new_page[i][0]==found_top and new_page[i][2]<found_left:
                    found_top=new_page[i][0]
                    found_left=new_page[i][2]
                    found=i
    for i in range(len(new_page)):
        if re.search('Cover[\w\s]*[(and),] Layout',new_page[i][4],re.IGNORECASE) is not None:
            if new_page[i][0]<found_top or new_page[i][0]==found_top and new_page[i][2]<found_left:
                found_top=new_page[i][0]
                found_left=new_page[i][2]
                found=i
    for i in range(len(new_page)):
        if re.search('Cover',new_page[i][4],re.IGNORECASE) is not None:
            if new_page[i][0]<found_top or new_page[i][0]==found_top and new_page[i][2]<found_left:
                found_top=new_page[i][0]
                found_left=new_page[i][2]
                found=i
    for i in range(len(new_page)):
        if re.search('Layout',new_page[i][4],re.IGNORECASE) is not None:
            if new_page[i][0]<found_top or new_page[i][0]==found_top and new_page[i][2]<found_left:
                found_top=new_page[i][0]
                found_left=new_page[i][2]
                found=i
    for i in range(len(new_page)):
        if re.search('Illus\w+ns?',new_page[i][4],re.IGNORECASE) is not None:
            if new_page[i][0]<found_top or new_page[i][0]==found_top and new_page[i][2]<found_left:
                found_top=new_page[i][0]
                found_left=new_page[i][2]
                found=i
    if found>0:
        new_text=[]
        for i in range(found,len(new_page)):
            new_text.append(new_page[i])
        illus_text=""
        test=False
        for i in range(len(new_text)):
            if test==True:
                break
            illus_tex=re.sub("Cover.*[(and),] Illustrations","",new_text[i][4],re.IGNORECASE)
            illus_tex=re.sub("Cover[\w\s]*[(and),\s]*[Ll]*ayout\s?","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("Cover","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("\.\s",".",illus_tex,re.IGNORECASE)
            illus_tex=re.sub(".*Layout","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("Illustrations?\s?","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("Illustrator","",illus_tex,re.IGNORECASE)
            illus_tex=illus_tex.strip(" ").rstrip(" ")
            if re.search("Cartography",illus_tex,re.IGNORECASE):
                illus_tex=""
            if re.search("Cartographic\s*Designs?",illus_tex,re.IGNORECASE):
                illus_tex=""
            if re.search("Cartoon",illus_tex,re.IGNORECASE):
                illus_tex=""
            if re.search("Sketches",illus_tex,re.IGNORECASE):
                illus_tex=""
            illus_tex=re.sub(",?New\s*Delhi.*","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("with.*","",illus_tex,re.IGNORECASE)
            if re.search("Centre.*",illus_tex,re.IGNORECASE):
                test=True
                illus_tex=re.sub("Centre.*","",illus_tex,re.IGNORECASE)
            if re.search("offices.*",illus_tex,re.IGNORECASE) or re.search("Printed.*",illus_tex,re.IGNORECASE):
                test=True
                illus_tex=""
            illus_tex=re.sub("assist.*","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub("\(.*\)","",illus_tex,re.IGNORECASE)
            illus_tex=re.sub(":","",illus_tex,re.IGNORECASE)
            if len(illus_tex)>1:
                xx=illus_tex.split("and")
                if(len(xx)>1):
                    for j in xx:
                        yy=j.split(',')
                        if len(yy)>1:
                            for k in yy:
                                if len(k)>1:
                                    illus_text+=remove_extra(k.rstrip(" ").strip(" "))+"||"
                        else:
                            if len(j)>1:
                                illus_text+=remove_extra(j.rstrip(" ").strip(" "))+"||"
                elif len(illus_tex.split(','))>1:
                    yy=illus_tex.split(',')
                    if len(yy)>1:
                        for k in yy:
                            if len(k)>1:
                                illus_text+=remove_extra(k.rstrip(" ").strip(" "))+"||"
                    else:
                        if len(j)>1:
                            illus_text+=illus_tex.rstrip(" ").strip(" ")+"||"
                    
                    
                else:
                    if len(illus_tex)>1:
                        illus_text+=remove_extra(illus_tex.rstrip(" ").strip(" "))+"||"
        illus_text=illus_text
        if re.search("||",illus_text) is not None:
            illus_tex=illus_text.split("||")
            illus_text=""
            for i in range(len(illus_tex)):
                if re.search(" ",illus_tex[i]):
                    x=re.search("\s+",illus_tex[i]).span()
                    p=illus_tex[i][x[1]:]+","+illus_tex[i][:x[0]]
                    illus_text+=p+"||"
            illus_text=illus_text.rstrip("||")
        new_list=illus_text.split("||")
        new_set=sorted(set(new_list))
        illus_text="||".join(new_set)    
        metadata["dc.contributor.illustrator"]=illus_text            
    else:
        metadata["dc.contributor.illustrator"]=""



#PDF INFO PART
pdfinfo=open(pdf_info_dir+name+".txt", 'r',encoding='utf-8',errors='ignore').read()
creationDate=re.findall("CreationDate:.*",pdfinfo)[0].strip("CreationDate:")
Num_page=re.findall("Pages:.*",pdfinfo)[0].strip("Pages:")
Num_page=re.findall("\d+",Num_page)[0]
page_size=re.findall("Page size:.*",pdfinfo)[0].strip("Page size:\s*")
File_size=re.findall("File size:.*",pdfinfo)[0].strip("File size:\s*")
version=re.findall("PDF version:.*",pdfinfo)[0].strip("PDF version:\s*") 
metadata["dc.date.created"]=creationDate
metadata["dc.date.publication"]=publication_date
extent=OrderedDict()
#extent["File type"]="PDF "+version
extent["PageCount"]=Num_page
extent["size_in_Bytes"]=File_size
#extent["pageSize"]=page_size
metadata['dc.format.extent']=extent





pages=[[[]]]
num_page=len(re.compile(r'<page.*?</page>',re.DOTALL).findall(data))
if num_page>24:
    num_page=24
for i in range(1,num_page+1):
    pages.append(Fuse(i))    
if True:
    seq,pattern,page_no=find_content(pages)
    if page_no>0:
        content_page_list.append(pages[page_no])
        content_pages.append(page_text(pages,page_no))
        if page_no+1 <=num_page:
            check_pattern(page_no+1,pattern,seq,pages)



#structure content properly for representation
content_text='' 
for i in content_pages:
    content_text+=i+"\n"

content_text=re.sub("’","'",content_text)
content_text=re.sub("\u2013","'",content_text)
content_text=re.sub("•","",content_text)

teacher_note=re.search("Teacher's Notes",content_text,re.IGNORECASE)
if teacher_note is not None:
    content_text= content_text[:teacher_note.span()[0]]
CONTENT=OrderedDict()
end1=0
content_text=re.sub('“','"',content_text)
content_text=re.sub('”','"',content_text)

while end1<len(content_text):
    start=re.compile(pattern,re.IGNORECASE).search(content_text,end1)    
    if start is None:
        break
    start1=start.span()[0]
    start2=start.span()[1]
    pattern_text=content_text[start1:start2].strip("\n")
    end=re.compile(pattern).search(content_text,start2)
    if end is not None:    
        end1=end.span()[0]
        end2=end.span()[1]
    else:
        end1=len(content_text)-1
        end2=len(content_text)
    content_line=content_text[start2+1:end1]
    try:
        page_no=re.findall(r"\d+\s{0,2}\–?\-?\s{0,2}\d*\n?",content_line)[0]
    except:
        page_no=""
    content_line_text=re.sub(page_no,'',content_line)
    content_line=OrderedDict()
    page_no=re.sub("–","-",page_no)
    try:
        seq=re.findall("\d+",pattern_text)[0]
    except:
        seq=""
    content_line_texts=remove_n(content_line_text)
    if type(['a','b'])==type(content_line_texts):
        for i in range(len(content_line_texts)):
            if len(re.sub("\n","",re.sub("\d+","",content_line_texts[0])))>1:
                if i is 0:
                    CONTENT[pattern_text+": "+seq+"."+str(i+1)+" "+re.sub("\n","",re.sub("\d+","",content_line_texts[i]))]=re.sub("\n.*","",page_no)
                elif i>0:
                    CONTENT[seq+"."+str(i+1)+" "+re.sub("\n","",re.sub("\d+","",content_line_texts[i]))]=re.sub("\n.*","",page_no)
            else:
                if i is 1:
                    CONTENT[pattern_text+": "+seq+"."+str(i)+" "+re.sub("\n","",re.sub("\d+","",content_line_texts[i]))]=re.sub("\n.*","",page_no)
                elif i>1:
                    CONTENT[seq+"."+str(i)+" "+re.sub("\n","",re.sub("\d+","",content_line_texts[i]))]=re.sub("\n.*","",page_no)
    else:
        CONTENT[pattern_text+": "+re.sub("\n","",re.sub("\d+","",content_line_text))]=re.sub("\n.*","",page_no)
    subject_test_text+=re.sub("\d","",content_line_text)
metadata['dc.description.toc']=CONTENT


#DDC classification
URL="http://clfapi.base-search.net/classify"
PARAMS=OrderedDict()
PARAMS['text'] = subject_test_text
PARAMS['language']="en"
PARAMS["format"]="xml"

xml_response=requests.get(url=URL,params = PARAMS).text
xml_response=re.sub("\n","",xml_response)

level1=re.findall('<result level="1">.*?</result>',xml_response)
level2=re.findall('<result level="2">.*?</result>',xml_response)
level3=re.findall('<result level="3">.*?</result>',xml_response)

if len(level1)>0:
    level1=level1[0]
else:
    level1=""
if len(level2)>0:
    level2=level2[0]
else:
    level2=""
if len(level3)>0:
    level3=level3[0]
else:
    level3=""
    
level1_DDC=re.findall('<DDC number="\d+".*?/>',level1)
level2_DDC=re.findall('<DDC number="\d+".*?/>',level2)        
level3_DDC=re.findall('<DDC number="\d+".*?/>',level3) 

levels=[level1_DDC,level2_DDC,level3_DDC]
subject=OrderedDict()
subjects=OrderedDict()
for i in range(len(levels)):
    subject=OrderedDict()
    for j in levels[i]:
        
        try:
            if float(re.findall('confidence="\d\.\d+"',j)[0].strip('confidence="').rstrip('"'))>0.15:
                ddc_number=re.findall('number="\d+"',j)[0].strip('number="').rstrip('"').ljust(3,'0')
                ddc_heading=re.findall('heading=".*?"',j)[0]
                ddc_heading=re.sub('"','',ddc_heading)
                ddc_heading=re.sub('heading=','',ddc_heading)
                subject[ddc_number]=ddc_heading
        except:
            continue
    subjects["level"+str(i+1)]=subject
metadata["dc.subject.ddc"]=subjects

#fill up other metadata
metadata["dc.description.searchVisibility"]="TRUE"
metadata["dc.format.mimetype"]="application/pdf"
metadata["dc.type"]="text"
metadata["dc.language"]="eng"
metadata["dc.contributor.advisosr"]=""
metadata["dc.contributor.author"]=""
metadata["dc.identifier.uri"]=""
metadata["dc.publisher.date"]=""
metadata["dc.publisher.place"]=""
metadata["dc.relation.referenences"]=""
metadata["dc.relation.haspart[]"]=""
metadata["dc.relation.ispartof"]=""
metadata["dc.relation.ispartofseries"]=""
metadata["dc.relation.requires[]"]="PDFviewer Plugin"
metadata["dc.rights.accessrights"]="Open"
metadata["dc.source.uri"]="http://www.ncert.nic.in/"
metadata["dc.source"]="NCERT"
metadata["dc.subject.prerequisitetopic[]"]=""
metadata["dc.title.alternative"]=""
metadata["lrmi.educationalAlignment.educationLevel"]=Class
metadata["lrmi.educationalAlignment.educationalFramework"]="Central Board of Secondary Education (CBSE)"
metadata["lrmi.educationalAlignment.educationLevel"]=Class
metadata["lrmi.educationalRole[]"]="student"
metadata["lrmi.educationalUse[]"]="reading"
metadata["lrmi.interactivityType[]"]="expositive"
metadata["lrmi.learningResourceType[]"]="book"

Class=roman.fromRoman(Class)
low=Class+3
high=Class+7
if Class<13:
    metadata["lrmi.typicalAgeRange[]"]=str(low)+"-"+str(high)
else:
    metadata["lrmi.typicalAgeRange[]"]=""


json.dump(metadata,json_output,indent=4)

json_output.close()
   