# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 10:51:30 2018

@author: Sravani
"""
import re
import term_frequency as tf
#term_frequency file has implementations of build_document_index and build_word_index
from porterStemmer import PorterStemmer
from nltk.corpus import stopwords

global p
p=PorterStemmer()
global stopWords
stopWords = set(stopwords.words('english'))
           
global index_to_word
global word_index
global whole_list
whole_list=set(range(1,1401))

#this method creates a dictionary of form
#   key: word id
#   dict[word_id]=[list of document_id]

def sort(term_frequency_list):
    sorted_list={}
    for item in term_frequency_list:
        if item[0] not in sorted_list:
            sorted_list[item[0]]=[]
            sorted_list[item[0]].append(item[1])# ex: {1:{1:2}}
            
        else:
            sorted_list[item[0]].append(item[1])
    return sorted_list


def and_operation(x,y):
    global term_and_document_list,word_index
    if x ==[]:
        x_tmp=set(x)
    else:
        if type(x)==str:
            if x in word_index:
                tmp=term_and_document_list[word_index[x]]
            else:
                tmp=set()
            x_tmp=set(tmp)
        else:
            x_tmp=set(x)
    if y ==[]:
        y_tmp=set(y)
    else:
        if type(y)==str:
            if y in word_index:
                tmp=term_and_document_list[word_index[y]]
            else:
                tmp=set()
            y_tmp=set(tmp)
        else:
            y_tmp=set(y)
    return x_tmp.intersection(y_tmp)
     

def or_operation(x,y):
    global term_and_document_list,word_index
    if x ==[]:
        x_tmp=set(x)
    else:
        if type(x)==str:
            if x in word_index:
                tmp=term_and_document_list[word_index[x]]
            else:
                tmp=set()
            x_tmp=set(tmp)
        else:
            x_tmp=set(x)
    if y ==[]:
        y_tmp=set(y)
    else:
        if type(y)==str:
            if y in word_index:
                tmp=term_and_document_list[word_index[y]]
            else:
                tmp=set()
            y_tmp=set(tmp)
        else:
            y_tmp=set(y)
    
    return x_tmp.union(y_tmp)

def not_operation(x):
    global term_and_document_list,word_index
    if type(x)==str:
        if x in word_index:
                temp=term_and_document_list[word_index[x]]
        else:
            temp=set()
    else:
        temp=set(x)
    return whole_list.difference(temp)

def stem_query(msg):
    global p
    processed_query=[]
    msg_list=msg.strip().split(' ')
    for word in msg_list:
        #if word has an and,or,not,(,) add it to the processed query list
        if word == 'and' or word == 'or' or word == 'not' or word == '(' or word == ')':
            processed_query.append(word)
            continue
        else:
            if word in stopWords:
                continue
            else:
                processed_query.append(p.stem(word, 0,len(word)-1))
    processed_query=' '.join(processed_query)  
    return processed_query  

def query_processing(message):    
    #creating space before and after braces for easy splitting
    message=message.strip()
    message=re.sub(r"(\S)\(", r'\1 (', message)
    message=re.sub(r"\((\S)", r'( \1', message)
    message=re.sub(r"(\S)\)", r'\1 )', message)
    message=re.sub(r"\)(\S)", r') \1', message)
    msg=message.split(' ')
    operand_stack=[]
    operator_stack=[]
    #print(msg)
    if len(msg)==1:
        if msg[0] in word_index:
            return term_and_document_list[word_index[msg[0]]]
    else:
        i=0
        while i <len(msg):
            if msg[i] not in ['and','or','not','(',')']:
                operand_stack.append(msg[i])
                i+=1
            elif msg[i] in ['and','or']:
                operator_stack.append(msg[i])
                i+=1
            elif msg[i]=='not':
                if msg[i+1] not in ['(',')']:
                    operand_stack.append(not_operation(msg[i+1]))
                    i=i+2
                    
                else:
                    substr=message[message.find("(")+1:message.find(")")]
                    operand_stack.append(not_operation(query_processing(substr)))
                    i=msg.index(')')+1
            
            elif msg[i] in ['(',')']:
                substr=message[message[i].find("(")+1:message.find(")")]
                operand_stack.append(query_processing(substr))
                i=msg.index(')')+1
        
        while len(operator_stack)!=0:
            opr=operator_stack.pop()
            if opr=='and':
                x=operand_stack.pop()
                y=operand_stack.pop()
                operand_stack.append(and_operation(x,y))
            if opr=='or':
                x=operand_stack.pop()
                y=operand_stack.pop()
                operand_stack.append(or_operation(x,y))
            if opr=='not':
                x=operand_stack.pop()
                operand_stack.append(not_operation(x))
        return list(operand_stack.pop())
        
    
        
        
    


def index_to_word(index):
    index_to_word={}
    for key in index:
        #print(word_index[key])
        index_to_word[index[key]]=key  
    return index_to_word

def print_results(results):
    count=0
    totalCount=0
    for item in results:
        totalCount+=1
        print("\n********************************************")
        print("Original Query:",results[item]['query'])
        print("Processed Query:",results[item]['query_processed'])
        print("Document Ids:\n",results[item]['document_ids'])
        if(results[item]['document_ids']==[]):
            count+=1
            
    print("\nNumber of empty lists:",count)
    print("\nTotal Number of queries:",totalCount)

#driver code
document_dictionary=tf.build_document_index("cran.all.1400")
word_index,term_frequency_list=tf.build_word_index(document_dictionary)
#arrange the term_frequency_list into dict[word_id]=[list of document_id]
global term_and_document_list
term_and_document_list=sort(term_frequency_list)
index_to_word=index_to_word(word_index)

query_list=['user',\
            'various and user',\
            'attack or not user and various',\
            'attack or not (user and vary)',]

for item in query_list:
    print('\n')
    print("Original Query:",item)
    qry=stem_query(item)
    print("After stemming:",qry)
    print("Document List:",query_processing(qry))
            

