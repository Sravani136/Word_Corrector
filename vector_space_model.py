# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 21:00:16 2018

@author: Sravani
"""

import re
import term_frequency as tf
#term_frequency file has implementations of build_document_index and build_word_index
from porterStemmer import PorterStemmer
from nltk.corpus import stopwords
import math
import os

global p
p=PorterStemmer()
global stopWords
stopWords = set(stopwords.words('english'))
           
global index_to_word
global word_index
global whole_list
whole_list=set(range(1,1401))
global results


def sort(term_frequency_list):
    sorted_list={}
    for item in term_frequency_list:
        if item[0] not in sorted_list:
            sorted_list[item[0]]=[]
            sorted_list[item[0]].append(item[1])# ex: {1:{1:2}}
            
        else:
            sorted_list[item[0]].append(item[1])
    return sorted_list

def stem_query(msg):
    global p
    processed_query=[]
    msg_list=msg.strip().split(' ')
    for word in msg_list:
        #if word has an and,or,not,(,) add it to the processed query list
        if word in stopWords:
            continue
        else:
            processed_query.append(p.stem(word, 0,len(word)-1))
    processed_query=' '.join(processed_query)  
    return processed_query 

def vector_space_model(qry):
    qry=qry.split(' ')
    
    docList=set()
    wq=0
    for word in qry:
        if word in word_index:
            idx=word_index[word]
            #print(term_and_document_list[idx])
            x=set(term_and_document_list[idx])
            docList=docList.union(x)
            wq+=term_weight_dict[idx]**2
    wq=math.sqrt(wq)
    #print(docList)
    #print(type(docList))
    doc_list=set(docList)        
    doc_list=list(doc_list)  
    #print(doc_list)      
    ranking={}
    error=[]
    #print(doc_list)
    for docs in doc_list:
        wd=doc_weight[docs]
        ranking[docs]=0
        for word in qry:
            if word in word_index:
                word=word_index[word]
                try:
                    #ranking[docs]+=(1/(doc_weight[docs]*term_weight_dict[word]))*(Tf_dict[word][docs]*term_weight_dict[word])
                    ranking[docs]+=(Tf_dict[word][docs]*term_weight_dict[word])
            
                except ZeroDivisionError:
                    docs+=1
            
    for doc in ranking:
        ranking[doc]=(1/(wd*wq))*ranking[doc]
        
        
    #tmp={k: v for k, v in ranking.items() if v>0.5} 
    #print(tmp)
    #temp=sorted(ranking, key=ranking.get, reverse=True)
    temp=sorted(ranking, key=ranking.get, reverse=True)
    #y=sorted(ranking, key=ranking.get, reverse=True)
    #print(y)
    #temp=[num for num in temp if num>0.8]
    return  temp

def get_relevant_docs(filename):
    global results
    doc_list={}
    f=open(filename,'r')
    for line in f:
        temp=line.strip().split(' ')
        if(temp[2] not in[-1,4,5]):
            if int(temp[0]) not in doc_list:
                doc_list[int(temp[0])]=[int(temp[1])]
            else:
                doc_list[int(temp[0])].append(int(temp[1]))
                
    return doc_list    

def queries_results(filename,relevant_docs):
    #retrieve queries from the file
    content=''
    with open(filename) as file:
        for num, line in enumerate(file, 1):
            content+=line
    query_dict={}#ex: query_dict[query_id]={'query':original query
    #                                       'query_processed':query after stemming in the for of and,or,not
    #                                       'document_ids':list of documents in which the query is present
    #                                       }
    count=0
    content=content.split(".I ")
    for item in content:
        if item!="":
            item=item.split(".W")
            count+=1
            #key=int(item[0].strip())
            key=count
            query=re.sub('[^a-z^A-Z()\ \']+', " ", item[1].strip()).lower()
            if key not in query_dict: 
                query_dict[key]={}
                query_dict[key]['query']=query
                query_dict[key]['query_processed']=stem_query(query)
                query_dict[key]['document_ids']=vector_space_model(query_dict[key]['query_processed'])
                
                x=set(query_dict[key]['document_ids']) #from this algo
                y=set(relevant_docs[key]) #from cranqrel
                common=x.intersection(y)
                query_dict[key]['precision']=len(common)/len(x)*100
                query_dict[key]['recall']=len(common)/len(y)*100
                
    return query_dict  

def index_to_word(index):
    index_to_word={}
    for key in index:
        #print(word_index[key])
        index_to_word[index[key]]=key  
    return index_to_word

def print_results(results):
    count=0
    totalCount=0
    print("\nWriting query results and precisions,recall values to file \'results.txt' ...")
    
    try:
        os.remove("results.txt")
    except OSError:
        pass

    with open("results.txt", 'a') as f:
    
        for item in results:
            totalCount+=1
            f.writelines("\n\n********************************Query#"+str(item)+"****************************************\n")
            f.writelines("\n"+results[item]['query'])
            #f.writelines("\nProcessed Query:"+results[item]['query_processed'])
            f.writelines("\n\nNumber of documents retrieved:"+str(len(results[item]['document_ids'])))
            f.writelines("\n\nDocument Ids as per ranking:\n"+str(results[item]['document_ids']))
            f.writelines("\n\nPrecision:"+str(results[item]['precision']))
            f.writelines("\nRecall:"+str(results[item]['recall']))
            if(results[item]['document_ids']==[]):
                count+=1
            
         
    print("\nTotal Number of queries:",totalCount)

def build_term_weight(term_frequency_list,index_to_word):
    #retrieving term_frequencies (# of times the word occured in all the documents)
    term_weight={}
    for i in range(1,len(index_to_word)+1):
        term_weight[i]=0
    
    for item in term_frequency_list:
        term_weight[item[0]]+=item[2]
        
    for item in term_weight:
        term_weight[item]=math.log(1+(len(document_dictionary)/term_weight[item]))
        
    return term_weight
    
def build_Tf_dict(term_frequency_list,index_to_word):
    Tf_dict={}
    for i in range(1,len(index_to_word)+1):
        Tf_dict[i]={}
        for j in range(1,len(document_dictionary)+1):
            Tf_dict[i][j]=0
        
    for item in term_frequency_list:
        Tf_dict[item[0]][item[1]]=1+math.log(item[2])
        
    return Tf_dict
            
def build_doc_weight(Tf_dict):
    doc_wt={}
    for i in range(1,len(document_dictionary)+1):
        doc_wt[i]=0
        
    for i in range(1,len(Tf_dict)+1):
        for j in range(1,len(document_dictionary)+1):
            doc_wt[j]+=(Tf_dict[i][j])**2
            
    for item in doc_wt:
        doc_wt[item]=math.sqrt(doc_wt[item])
    
    return doc_wt
        

########################################################################
#driver code
########################################################################
print("\nReading documents...")

document_dictionary=tf.build_document_index("cran.all.1400")
word_index,term_frequency_list=tf.build_word_index(document_dictionary)

#arrange the term_frequency_list into dict[word_id]=[list of document_id]
term_and_document_list=sort(term_frequency_list)#rearranges to the for 1:'aerodynam'   2:'agree'
index_to_word=index_to_word(word_index)
print("\nBuilding models...")
term_weight_dict=build_term_weight(term_frequency_list,index_to_word)
Tf_dict=build_Tf_dict(term_frequency_list,index_to_word)
doc_weight=build_doc_weight(Tf_dict)
print("\nReading queries...")
#vector_space_model('aerodynam')
relevant_docs=get_relevant_docs("cranqrel")
results=queries_results("cran.qry",relevant_docs)
print_results(results)



