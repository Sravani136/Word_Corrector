# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 22:20:44 2018

@author: Sravani
"""
import re
from nltk.corpus import stopwords
from porterStemmer import PorterStemmer

def build_word_index(doc_dict):
    '''
    this method builds the word index dictionary
    '''
    dictionary={}
    stopWords = set(stopwords.words('english'))
    p=PorterStemmer() 
    global idx
    term_frequecy_list=[]
    def append_to_word_list(text,doc_index):
        global idx
        #text = " ".join(re.findall("[a-zA-Z]+", st)).lower()
        text=" ".join(re.findall("[a-zA-Z]+", text))
        text=set(text.split(" "))
        text=list(text)
        text.sort()
        temp_list=[]
        f_dt={}
        for word in text:
            if(word!=""):
                if word in stopWords:
                    continue
                else:
                    word=p.stem(word, 0,len(word)-1)
                    #update frequency of term
                    if word not in f_dt:
                        f_dt[word]=1
                    else:
                        f_dt[word]+=1
                    #check if word in dictionary and append it
                    if word not in dictionary:
                        dictionary[word]=idx
                        idx+=1
                    term_frequecy_list.append([dictionary[word],doc_index,f_dt[word]])    
                    #wordlist.append(word)
                    
    
    idx=1      
    for i in range(1,len(doc_dict)+1):
        if(doc_dict[i][1]!=''):
            append_to_word_list(doc_dict[i][1],i)
    
    return dictionary,term_frequecy_list

def build_document_index(filename):
    '''
    reads the file and builds an index for all the documents
    it returns a dictionary{document#,title of document,content of document}
    '''
    
    #f=open(path,"r")
    index=0
    content=''
    with open(filename) as file:
        for num, line in enumerate(file, 1):
            content+=line
    
    content=content.split(".I ")
    doc_dict={}
    
    for doc in content:
        if doc!='':
            index=int(doc.strip().split("\n")[0])
            doc_dict[index]=[]
            title=doc.split(".A")[0].split(".T\n")[1]
            doc_content=doc.split(".A")[1].split(".W\n")[1]
            if(title!=''):
                doc_dict[index].append(' '.join(title.split('\n')))
            else:
                doc_dict[index].append('')
            if(doc_content!=''):
                doc_dict[index].append(' '.join(doc_content.split('\n')))
            else:
                doc_dict[index].append('')
    
    return doc_dict
                
def print_results(word_index,term_frequency_list,document_dictionary):
    index_to_word={}
    doc_dict_lenght=len(document_dictionary)
    for key in word_index:
        index_to_word[word_index[key]]=key
    doc_num=1
    unique_word_count=0
    temp={}
    f=open("results.txt","+a")
    for item in term_frequency_list:
        if item[1]==doc_num:
            unique_word_count+=1
            temp[index_to_word[item[0]]]=item[2]
        
            
        else:
            
            print("\n********************************")
            print("Document Number:",doc_num)
            print("Number of Unique Terms:",unique_word_count)
            print("\n")
            for key in temp:
                print("Term:%s\tFrequency:%d"%(key,temp[key]))
            
            f.writelines("\n***************************************************************")
            f.writelines("\nDocument Number:"+str(doc_num))
            f.writelines("\nNumber of Unique Terms:"+str(unique_word_count))
            f.writelines("\n")
            for key in temp:
                f.writelines("\nTerm:"+str(key)+"\t\tFrequency:"+str(temp[key]))
            doc_num=item[1]
            unique_word_count=0
            temp={}
    print("\n********************************")
    print("Document Number:",doc_num)
    print("Number of Unique Terms:",unique_word_count)
    print("\n")
    for key in temp:
        print("Term:%s\tFrequency:%d"%(key,temp[key]))
    
    f.writelines("\n***************************************************************")
    f.writelines("\nDocument Number:"+str(doc_num))
    f.writelines("\nNumber of Unique Terms:"+str(unique_word_count))
    f.writelines("\n")
    for key in temp:
        f.writelines("\nTerm:"+str(key)+"\t\tFrequency:"+str(temp[key]))
            
    f.close()
            
        #print(item[0],index_to_word[item[0]])
        #break    
    


    


#print(word_index) 