import PyPDF2
import os
import traceback
import time

'''
针对扫描版pdf添加目录
需要有目录文件，使用\t制表符组织目录
目录和扫描版页码有偏差手动设置起始页码
'''
def setsub(indexs, level):
    #递归方式遍历目录 生成目录树
    sub = []
    for i, index in enumerate(indexs):
        clevel = len(index.split('\t'))
        if clevel == level + 1:
            value, page = index.split('@')
            sub.append([value, page, setsub(indexs[i+1:], level+1)])
        elif clevel > level + 1:
            continue
        else:
            break
    return sub

def settree(indexs):
    res = []
    for i, index in enumerate(indexs):
        level = len(index.split('\t'))
        value, page = index.split('@')
        subtree = setsub(indexs[i+1:], level)
        if level == 1:
            res.append([value, page, subtree])
    return res


def main1():
    print('*起始页为书籍目录第一页在pdf中对应的页码')
    all = os.listdir(os.getcwd())

    for file in all:
        if os.path.splitext(file)[1] == '.pdf':
            #对当前pdf检测 是否已有目录 是否有匹配目录文件
            filep = file
            title = os.path.splitext(file)[0]
            print('当前书籍为 '+title)
            pdfobj = open(filep, 'rb')
            reader = PyPDF2.PdfFileReader(pdfobj)
            outline = reader.outlines
            if outline != []:
                print('当前书籍已有目录！')
                # print(outline)
                time.sleep(1)
                continue

            #识别并读取目录文件
            filei = title + '.ml'
            if not os.path.exists(filei):
                print('未找到匹配的目录文件')
                continue
            fi = open(filei, 'r', encoding='utf-8')
            indexs = fi.readlines()

            #建立目录树
            tree = settree(indexs)

            #设置偏置页数
            offset = input('请输入起始页：')
            writer = PyPDF2.PdfFileWriter()
            for i in range(0, reader.numPages):
                writer.addPage(reader.getPage(i))

            def addmarks(tree, parent):
                for value, page, sub in tree:
                    cur = writer.addBookmark(value, int(page)+int(offset)-2, parent)
                    if sub != []:
                        addmarks(sub, cur)

            #添加目录 设置信号量 失败不储存
            save = 0
            try:
                addmarks(tree, None)
                save = 1
            except:
                print(traceback.print_exc())
                save = 0
                print(title + ' 失败')
                break

            if save == 1:
                try:
                    if os.path.exists('result\\' + title + ' new.pdf'):
                        os.remove('result\\' + title + ' new.pdf')
                    with open('result\\' + title + ' new.pdf', 'wb') as fout:
                        writer.write(fout)
                    print(title + ' 完成')
                except:
                    print('请检查文件是否未关闭并重试')
                time.sleep(1)

if __name__ == '__main__':
    main1()
