from Tkinter import Tk, Canvas, Frame, Button, Entry, Text, Scrollbar
from Tkinter import BOTH, W, NW, SUNKEN, TOP, X, FLAT, LEFT, N, S, END, VERTICAL, NS
import os
import sys
import requests
import random
import docx
import PyPDF2
from tkFileDialog import askopenfilename
import tkFileDialog
import subprocess
import slate
import string

'''
	GUI AND LOGIC FOR OPENSTACK SEARCH

'''
class Example(Frame):
    '''
	Constructor for creating a frame
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    '''
	Browse the filename to be added to to Openstack Swift
    '''
    def browsefile(self):
        self.filename = askopenfilename()
        self.nm = self.filename.split("/")
        self.fnm = self.nm[len(self.nm)-1]
        self.e2.configure(state="normal")
        self.e2.update()
        self.e2.delete(0, 'end')  
        self.e2.insert("end", self.fnm)
        self.e2.configure(state="disabled")
        self.e2.update() 
 
    '''
	Add Data - To Openstack Swift
        Check For De-Duplication of Data
        - Display the Data When found duplicate data
        Check For Already Added File - same file 
        - Display the content of already Added file 

    '''
    def addData(self):
        file_ext=self.fnm.split('.') 
        result = requests.get('http://localhost:8983/solr/techproducts/select?q='+ str(self.fnm)+'&wt=json&fl=id')
        op = result.json()
        flag = False
        if op['response']['numFound'] == 0:
           un_id = random.randint(1, 1000)
           if file_ext[1] == 'txt':
              listdocs = requests.get('http://localhost:8983/solr/techproducts/select?q=*.'+ file_ext[1] +'&wt=json')
              listdict = listdocs.json()
              f = open(self.fnm,"r")
              lines = f.readlines()
              alllines = ""
              for j in range(0, len(lines)):
                  alllines += lines[j]
              for i in range(0, len(listdict['response']['docs'])):
                  if alllines.strip() == (listdict['response']['docs'][i]['content'][0]).strip():
                     name = str(listdict['response']['docs'][i]['resourcename']).split("/")
                     self.e3.delete('1.0', END)
                     self.e3.insert(END,"Cannot Add Duplicate Data. There is already a file with same contents\n File name : "+ str(name[len(name)-1]) + "\n")
                     self.e3.insert(END,"Here are the contents\n")
                     self.e3.insert(END,str(listdict['response']['docs'][i]['content'][0]).strip())
                     flag = True
           if file_ext[1] == 'pdf':
              listdocs = requests.get('http://localhost:8983/solr/techproducts/select?q=*.'+ file_ext[1] +'&wt=json')
              listdict = listdocs.json()
              with open(self.fnm) as f:
                   doc = slate.PDF(f)  
              alllines = ""     
              for i in range(0, len(doc)):
                  alllines += doc[i]         
              remove = string.punctuation + string.whitespace
              alllines = alllines.translate(None, remove) 
              for i in range(0, len(listdict['response']['docs'])):
                  alldocs = (listdict['response']['docs'][i]['content'][0]).encode("utf-8")
                  alldocs = alldocs.translate(None, remove)  
                  res = (alllines == alldocs)
                  if alllines == alldocs:
                     name = str(listdict['response']['docs'][i]['resourcename']).split("/")
                     self.e3.delete('1.0', END)
                     self.e3.insert(END,"Cannot Add Duplicate Data. There is already a file with same contents\n File name : "+ str(name[len(name)-1]) + "\n")
                     self.e3.insert(END,"Here are the contents\n")
                     self.e3.insert(END,str(listdict['response']['docs'][i]['content'][0]).strip())
                     flag = True
           if file_ext[1] == 'docx':
              listdocs = requests.get('http://localhost:8983/solr/techproducts/select?q=*.'+ file_ext[1] +'&wt=json')
              listdict = listdocs.json()
              document = docx.Document(self.fnm)
              alllines = ""
              for para in document.paragraphs:
                  dl = para.text.encode("utf-8")
                  alllines += dl
              remove = string.punctuation + string.whitespace
              alllines = alllines.translate(None, remove)
              for i in range(0, len(listdict['response']['docs'])):
                  alldocs = (listdict['response']['docs'][i]['content'][0]).encode("utf-8")
                  alldocs = alldocs.translate(None, remove)
                  res = (alllines == alldocs)
                  if alllines == alldocs:
                     name = str(listdict['response']['docs'][i]['resourcename']).split("/")
                     self.e3.delete('1.0', END)
                     self.e3.insert(END,"Cannot Add Duplicate Data. There is already a file with same contents\n File name : "+ str(name[len(name)-1]) + "\n")
                     self.e3.insert(END,"Here are the contents\n")
                     self.e3.insert(END,str(listdict['response']['docs'][i]['content'][0]).strip())
                     flag = True
           if flag == False:
              os.system('cp '+ str(self.fnm) + " /opt/solr/example/exampledocs/")
              os.system("/opt/solr/bin/post -c techproducts /opt/solr/example/exampledocs/" + str(self.fnm) + " -params \"literal.id=" + str(un_id) + "\"")
              self.e3.delete('1.0', END)
              self.e3.insert(END,"Indexing Done for the Upload .....\n")
              container = subprocess.check_output(["swift","list","-v","--os-username","admin","--os-password","ea12f4366a2a4253","--os-auth-url","http://localhost:5000/v2.0","--os-tenant-name","admin"])
              container = container.split("\n")
              os_name = os.environ['OS_USERNAME']
              os_password = os.environ['OS_PASSWORD']
              os_auth_url = os.environ['OS_AUTH_URL']
              os_tenant_name = os.environ['OS_TENANT_NAME']  
              response = os.system("swift upload -c -v --os-username "+ str(os_name) + " --os-password "+ str(os_password) + " --os-auth-url " + str(os_auth_url) + " --os-tenant-name "+ str(os_tenant_name) + " "+ str(container[0]) + " "+ str(self.fnm))
              if response == 0:
                 self.e3.insert(END,"File Uploaded Successfully to Openstack Swift\n")
        if op['response']['numFound'] > 0:
           answer = requests.get('http://localhost:8983/solr/techproducts/select?q='+ str(self.fnm)+'&wt=json&fl=content')
           details = answer.json()
           content_dict = details['response']['docs'][0]['content']
           self.e3.delete('1.0', END)
           self.e3.insert(END,"Cannot Add Data Again\n")
           self.e3.insert(END,"Data Already Added to Openstack Swift:\nHere are the contents\n")
           self.e3.insert(END,content_dict[0])
    
    '''
	Search The Openstack Swift Data with Search Query given by the user
    '''    
    def searchData(self):
        query = self.e1.get()
        qresult = requests.get('http://localhost:8983/solr/techproducts/browse?q='+ str(query)+'&wt=json')
        qop = qresult.json()
        if qop['response']['numFound'] == 0:
           self.e3.delete('1.0', END)
           self.e3.insert(END,"Sorry !! No Details found for the search query")
        if qop['response']['numFound'] > 0:
           length = len(qop['response']['docs'])
           self.e3.delete('1.0', END)
           for i in range(0, length):
               sname = str(qop['response']['docs'][i]['resourcename']).split("/")
               self.e3.insert(END,"Filename : " + str(sname[len(sname)-1]) + "\n")
               self.e3.insert(END,qop['response']['docs'][i]['content'][0])
           self.e3.insert(END,"Search Result Found "+ str(length) + " \n")

    '''
        Clear The Text Area 
    '''
    def clearText(self):
        self.e1.delete(0, 'end')
        self.e2.configure(state="normal")
        self.e2.update()
        self.e2.delete(0, 'end')
        self.e2.configure(state="disabled")
        self.e2.update()
        self.e3.delete('1.0', END) 

    '''
	GUI : Add Canvas
	      Add Buttons : Quit, Clear, Search, Browse, Add
              Add Text Area : Search, Add, Output
    '''
    def initUI(self):
        self.parent.title("Openstack Search")
        self.config(bg = '#F0F0F0')
        self.pack(fill = BOTH, expand = 1)
        #create canvas
        self.canvas1 = Canvas(self, relief = FLAT, background = "#D2D2D2",
                                            width = 1000, height = 500)
        self.canvas1.pack(side = TOP, anchor = NW, padx = 10, pady = 10)
        self.e1 = Entry(self.canvas1)
        self.e1.config(width=20)
        self.e2 = Entry(self.canvas1)
        self.e2.config(width=20)
        self.e2.config(state="disabled") 
        self.e1_window = self.canvas1.create_window(210,70,window = self.e1)
        self.e2_window = self.canvas1.create_window(210,120,window = self.e2)
        self.e3 = Text(self.canvas1,height=18)
        self.e3.grid(column=1,row=5, columnspan=5, rowspan=1, sticky='W')
        scrb=Scrollbar(self.canvas1,orient=VERTICAL,command=self.e3.yview)
        self.e3.configure(yscrollcommand=scrb.set)
        self.e3_window = self.canvas1.create_window(450,350,window = self.e3)
        
        self.button1 = Button(self, text = "Quit", command = self.quit, anchor = W)
        self.button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
        self.button1_window = self.canvas1.create_window(10, 10, anchor=NW, window=self.button1)
        self.button2 = Button(self, text = "Search", anchor = W)
        self.button2.configure(command=self.searchData)
        self.button2.configure(width = 10, activebackground = "#33B5F5", relief = FLAT)
        self.button2_window = self.canvas1.create_window(10, 60, anchor=NW, window=self.button2)
        self.button3 = Button(self, text = "Browse", command = self.browsefile, anchor = W)
        self.button3.configure(width = 10, activebackground = "#33B5D5", relief = FLAT)
        self.button3_window = self.canvas1.create_window(10, 110, anchor=NW, window=self.button3)
        self.button3 = Button(self, text = "Add", command = self.addData, anchor = W)
        self.button3.configure(width = 10, activebackground = "#33B5D5", relief = FLAT)
        self.button3_window = self.canvas1.create_window(10, 160, anchor=NW, window=self.button3)
        self.button4 = Button(self, text = "Clear", command = self.clearText, anchor = W)
        self.button4.configure(width = 10, activebackground = "#33B5D5", relief = FLAT)
        self.button4_window = self.canvas1.create_window(200, 10, anchor=NW, window=self.button4)
 
'''
	Main Function
'''
def main():
    root = Tk()
    root.geometry('800x600+10+50')
    app = Example(root)
    app.mainloop()

if __name__ == '__main__':
    main()
