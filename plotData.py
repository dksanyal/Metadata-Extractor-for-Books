import zipfile
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from xlrd import open_workbook
import json
import re
import string
import stringdist
import evaluate as evalFile

#NUM_ATTRIBUTES_C1 = 4
#NUM_ATTRIBUTES_C2 = 5
X_LABEL_C1 = ['Title', 'Abstract', 'Editor', 'Illustrator']
X_LABEL_C2 = ['Contents', 'ISBN', 'Copyright-Yr', 'Edu-Lvl', 'DDC']
Y_TYPES_C1 = ['Precision', 'NLD_precision', 'Recall', 'NLD_recall', 'F1_score', 'NLD_F1_score']
Y_TYPES_C2 = ['Precision', 'Recall', 'F1_score']
COLORS_C1  = ['#63B8FF', '#00FF00', '#8B4C39', '#FFA500', '#FF3030', '#121212']
COLORS_C2  = ['#63B8FF', '#8B4C39', '#FF3030']

#Extract commandline parameters
def config_params():
    error = False
    try:
        output = sys.argv[1]
    except:
        output = ''
        error  = True       
 
    try:
        golden = sys.argv[2]
    except:
        golden = ''
        error  = True

    d=dict()
    d['output']=output
    d['golden']=golden
    d['wdir'] = './'
    d['error'] = error
    return d

#Extract the output files
def prepare_input(inpaths):
    error = False
    folders = set()

    #Get the input parameters    
    directory_to_extract_to = inpaths['wdir']
    output = inpaths['output']

    #Unzip the golden folder
    if (output != '' and os.path.isfile(output)):	
        zip_ref = zipfile.ZipFile(output, 'r')
        try:
            zip_ref.extractall(directory_to_extract_to) #extract files
            output_files = zip_ref.namelist() #extracted files
            for filename in output_files:
                folder = os.path.dirname(filename)
                folders.add(folder)
        except:
            print("ERROR: Could not extract generated files for evaluation.")
            error = True
        finally:
            zip_ref.close()
    else:
        print("ERROR: No generated files provided")
        error = True

    #Put the outputs in a dict and send
    d = dict()
    d['files'] = folders
    d['error'] = error
    return d

#Generate the evaluation results as two matrices for a given output folder.
#(Note a folder may corr. to BASIC or BASIC+ADV flow.)
#Matrix 1: 'Title', 'Abstract', 'Editor', 'Illustrator'
#Matrix 2: 'Contents', 'ISBN', 'Copyright-Year', 'Edu-Level', 'DDC'
#Matrix dim: Metadata attributes (rows) x measures (columns)

def gen_stats(folder,golden):
    #e = dict()
    print("Generating P, R, F1 for all metadata fields")
    e= evalFile.evaluateMetadata(folder, golden)
    return e

def plot_bars(df, yaxis, palette, fileprefix):
    #Plot the dataframe.
    #plt.clf()
    axes=df.plot(x='Attribute', y=yaxis, kind="bar",width=0.8,rot=0,grid=True, color=palette)   #shrink width to make space for legend
    #set numerical annotation for bars
    for p in axes.patches:
        axes.annotate(np.round(p.get_height(),decimals=3), (p.get_x()+p.get_width()/2, p.get_height()*1.085), ha='center', va='center',rotation=90,size=8)
    
    ax=plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    plt.xticks(size=8)
    plt.ylim(0,1.19)
    plt.axes().xaxis.grid(False)
    plt.axes().yaxis.grid(linestyle='--',linewidth=0.2)
    plt.legend(loc='center left', bbox_to_anchor=(1.0,0.5))   #make legend appear outside the bars

    plt.title(fileprefix)
    plt.savefig(fileprefix+".png", bbox_inches="tight")
    return False


def gen_plots(m1, m2, chartprefix):
    error = False
    
    #Now change each matrix to a dataframe. Add the names of each column.
    df = pd.DataFrame(m1, columns=Y_TYPES_C1)
    #Put metadata attribute name in column 1 of the dataframe.
    df['Attribute'] = X_LABEL_C1
    #Plot the dataframe.
    fileprefix = chartprefix + "-I"
    plot_bars(df, Y_TYPES_C1, COLORS_C1, fileprefix)

    #Plot the remaining attributes
    df = pd.DataFrame(m2, columns=Y_TYPES_C2)
    df['Attribute'] = X_LABEL_C2
    fileprefix = chartprefix + "-II"
    plot_bars(df, Y_TYPES_C2, COLORS_C2, fileprefix)
    return error 


#main function    
def main():
    result = config_params()
    golden=result['golden']
    err = result['error']
    
    if(err == True):
        print("Insufficient inputs. Use: python3 <scriptname> <outputzip_filename> <goldenXL_filename>")
        exit(-1)
    else:
        result = prepare_input(result)  #Extract generated files
        folders = result['files']    
        err = result['error']
        if(err == True):
            print("Failed to parse inputs")
            exit(-1)              #Generated files not found
        else:
            print("Got these folders: " + str(folders))
            for folder in folders:   #One folder for basic flow, one folder for alternate+basic flow
                result = gen_stats(folder,golden)   #Measure (P, R, F1)
                err         = result['error']

                if(err == True):
                    print("Performance assessment failed.")
                    exit(-1)              #Could not measure performance
                else:
                    err = gen_plots(result['matrix1'], result['matrix2'], str(folder)) #Plot data
                    if(err == True): 
                        print("Plot generation failed")
                        exit(-1)                   #Could not generate plot


#Call the main
if __name__ == '__main__':
    main()

