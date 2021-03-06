#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#          Extract Bursts from TOPS of Sentinel-1                                # 
#                                                                                #
##################################################################################
#'''
import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict


def ras2jpg(input, strTitle):
    call_str = "convert " + input + ".ras " + input + ".jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 250 " + input + ".thumb.jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 500 " + input + ".bthumb.jpg"
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".thumb.jpg 14 " + strTitle
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".bthumb.jpg 24 " + strTitle
    os.system(call_str)

def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()

def usage():
    print '''
******************************************************************************************************
 
                     Extracting bursts from TOPS of Sentinel-1

   usage:
   
            BurstExt_TOPS_Gamma.py projectName Date FirtSW EndSW FirtBurst EndBursit 
      
      e.g.  BurstExt_TOPS_Gamma.py PacayaT163S1A 131021 2 3 6 9
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if (len(sys.argv) ==6 or len(sys.argv) ==7):
        projectName = sys.argv[1]
        Date = sys.argv[2]
        SW = sys.argv[3]
        EW = sys.argv[4]
        SB   = sys.argv[5]
        if (len(sys.argv) ==7 ):
            EB   = sys.argv[6]
    else:
        usage();sys.exit(1)
       
    
    
    scratchDir = os.getenv('SCRATCHDIR')    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    workDir = slcDir + '/' + Date
    templateContents=read_template(templateFile)
       
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']

    TOPPar1     = workDir + '/' + Date + '.IW1.slc.TOPS_par'   # bursts number in all of TOPS are same ? If not, should modify
    if (len(sys.argv) ==6):
        EB = UseGamma(TOPPar1 , 'read', 'number_of_bursts:')
    
    
    SLC1_tab = workDir + '/' + 'SLC_Tab1_' + SW + EW + '_' + SB + EB
    SLC2_tab = workDir + '/' + 'SLC_Tab2_' + SW + EW + '_' + SB + EB   
    BURST_tab = workDir + '/' + 'BURST_Tab_' + SW + EW + '_' + SB + EB   
    
    MslcImg = workDir + '/'+Date + '.'+ SW + EW + '_' + SB + EB  + '.slc'
    MslcPar = workDir + '/'+Date + '.'+ SW + EW + '_' + SB + EB  + '.slc.par'    
    
    MamprlksImg = workDir + '/'+Date + '.'+ SW + EW + '_' + SB + EB  + '_' + rlks + 'rlks' + '.amp'
    MamprlksPar = workDir + '/'+Date + '.'+ SW + EW + '_' + SB + EB  + '_' + rlks + 'rlks' + '.amp.par' 
    
    
    if os.path.isfile(SLC1_tab):
        os.remove(SLC1_tab)
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)     
    if os.path.isfile(BURST_tab):
        os.remove(BURST_tab)
        
    
    for kk in range(int(EW)-int(SW)+1):
        call_str = 'echo ' + workDir + '/' + Date+'.IW'+str(int(SW)+kk) + '.slc' + ' ' + workDir + '/'+ Date + '.IW'+str(int(SW)+kk) +'.slc.par' + ' ' + workDir + '/'+ Date+'.IW'+str(int(SW)+kk) + '.slc.TOPS_par >>' + SLC1_tab
        os.system(call_str)
        
        call_str = 'echo ' + workDir + '/'+ Date+ '_'+ SB + EB +'.IW'+str(int(SW)+kk)+ '.slc' + ' ' + workDir + '/' + Date + '_'+ SB + EB +'.IW'+ str(int(SW)+kk)+ '.slc.par' + ' ' + workDir + '/'+ Date+'_'+ SB + EB + '.IW'+str(int(SW)+kk)+ '.slc.TOPS_par >>' + SLC2_tab
        os.system(call_str)
        
        call_str = 'echo ' + SB + ' ' + EB + ' >>' + BURST_tab
        os.system(call_str)

    call_str = 'SLC_copy_S1_TOPS ' + SLC1_tab + ' ' + SLC2_tab + ' ' + BURST_tab 
    os.system(call_str)
        
    
    call_str = 'SLC_mosaic_S1_TOPS ' + SLC2_tab + ' ' + MslcImg + ' ' + MslcPar + ' ' + rlks + ' ' +azlks
    os.system(call_str)
    
    call_str = '$GAMMA_BIN/multi_look ' + MslcImg + ' ' + MslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
    os.system(call_str)
    
    nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')
    call_str = '$GAMMA_BIN/raspwr ' + MamprlksImg + ' ' + nWidth 
    os.system(call_str)  
    ras2jpg(MamprlksImg, MamprlksImg) 
    
    print "burst extraction: SWATH: %s, %s   BURSTs: %s, %s    S1 Date: %s    done! "  % ( SW, EW, SB, EB, Date )       
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
