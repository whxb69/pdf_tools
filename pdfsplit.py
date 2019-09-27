import PyPDF2
from pdftag import addtag
import os

f = open('outline.ml','w',encoding='utf-8')

def main(pdfdir):
    # pdfdir = '(Lecture Notes in Computer Science 3418 _ Theoretical Computer Science and General Issues) Ulrik Brandes, Thomas Erlebach (auth.), Ulrik Brandes, Thomas Erlebach (eds.) - Network Analysis_ Methodologi.pdf'
    # file = '怎样解题 new.pdf'
    pdfobj = open(pdfdir, 'rb')
    reader = PyPDF2.PdfFileReader(pdfobj)
    lines = reader.outlines
    get_data(reader, lines)
    pdfsplit(reader)

def pdfsplit(reader):
    #TODO:2.重建pdf文件3.重建同时按目录加书签
    idx = outline_split()
    for chp in idx:
        #重置目录   
        oldir = r'outline\\%s.ml'%chp
        fo = open(oldir,'r',encoding='utf-8')
        lines = fo.readlines()
        fo.close()
        title,page = lines[0].split('@')
        offset = int(page)-1
        fo = open(oldir,'w',encoding='utf-8')
        for line in lines:
            line = newline(offset, line)
            print(line)
            fo.write(line+'\n')
        fo.close()
        
        #重写pdf
        start = int(idx[chp].split('@')[1])
        if len(idx[chp].split('@'))<3:
            end = reader.getNumPages()+1
        else:
            end = int(idx[chp].split('@')[2])+1
        pdf_writer = PyPDF2.PdfFileWriter()
        for index in range(start,end):
            pdf_writer.addPage(reader.getPage(index-1))
        with open('result\\' + title + '.pdf', 'wb') as outfile:
            pdf_writer.write(outfile)
        
        #添加新目录
        pdf = 'result\\' + title + '.pdf'
        ml = 'outline\\'+str(chp)+'.ml'
        addtag(pdf,ml)
        #删除中间文件
        os.remove('result\\' + title + '.pdf')

        
def outline_split():
    f.close()
    fm = open('outline.ml','r',encoding='utf-8')
    lines = fm.readlines()
    idx = {}
    temp = []
    num = 0
    for index,line in enumerate(lines):
        if index != (len(lines)-1):
            if '\t' not in lines[index+1]:
                temp.append(line)
                title,start = temp[0].split('@')
                temp = ''.join(temp)
                num += 1
                idx[num] = title+'@'+start#用数字存储标题 有的标题无法存为文件名
                fc = open('outline\\' + str(num) +'.ml','w',encoding='utf-8')
                fc.write(temp)
                fc.close()
                temp = []
            else:
                temp.append(line)
        else:
            temp.append(line)
            title,start = temp[0].split('@')
            temp = ''.join(temp)
            num += 1
            idx[num] = title+'@'+start
            fc = open('outline\\' + str(num) +'.ml','w',encoding='utf-8')
            fc.write(temp)
            fc.close()
    for index,item in enumerate(idx):
        if index != len(idx)-1:
            end = idx[index+2].split('@')[1]
            end = int(end)-1
            idx[index+1] = idx[index+1].strip()+'@'+str(end)

    return idx

def newline(offset, line):
    title,page = line.split('@')
    page = int(page) - offset
    
    return title+ '@' +str(page)
    
def get_data(reader, datas, deep=0):
    for index, item in enumerate(datas):
        if not isinstance(item, list):#不是列表 无子目录
            if deep > 0 and index > 0 and isinstance(datas[index - 1], list):
                deep -= 1
            title = item.title
            page = reader.getDestinationPageNumber(item) + 1
            tab = '\t' * deep
            # print('%s%s@%d' % (tab, title, page))
            f.write('%s%s@%d\n' % (tab, title, page))
        else:#是列表 有子目录
            deep += 1
            get_data(reader, item, deep)

if __name__ == '__main__':
    if not os.path.isdir('result'):
        os.makedirs('result')
    if not os.path.isdir('outline'):
        os.makedirs('outline')
    main('Developer Library - X_ Inside Mac OS X System Overview-Fatbrain (2001).pdf')
    