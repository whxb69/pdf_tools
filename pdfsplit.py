import PyPDF2
import os
import time
import traceback

start = time.clock()

f = open('outline.ml', 'w', encoding='utf-8')
nameSplit = 'ProblemSolvingAndProgramDesignInC new.pdf'


def getlaveNum(strTmp):
    for i in range(len(strTmp)):
        if '\t' != strTmp[i]:
            return i + 1


def setsub(indexs, level):
    # 递归方式遍历目录 生成目录树
    sub = []
    for i, index in enumerate(indexs):
        clevel = getlaveNum(index)
        if clevel == level + 1:  # 深度增加 递归进入子树
            value, page = index.split('@')
            sub.append([value, page, setsub(indexs[i + 1:], level + 1)])
        elif clevel > level + 1:  # 深度增加大于1 跳过 继续寻找同级目录
            continue
        else:  # 深度不变 无子树直接跳出
            break
    return sub


def settree(indexs):
    '''

    :param indexs: list -> 整个章节标题页码 value:[\t title,page]
    :return: list -> [titel,page,subtree] subtree同为[title,page,subtitle] 为子项subtree为[]
    '''
    res = []
    for i, index in enumerate(indexs):
        level = getlaveNum(index)
        value, page = index.split('@')

        if level == 1:
            subtree = setsub(indexs[i + 1:], level)
            res.append([value, page, subtree])
    return res


def addtag(pdf, filei=None, offset=0):
    # print('*起始页为书籍目录第一页在pdf中对应的页码')

    if os.path.splitext(pdf)[1] == '.pdf':
        # 对当前pdf检测 是否已有目录 是否有匹配目录文件
        filep = pdf
        title = os.path.splitext(pdf)[0]
        print('当前pdf为 ' + title)
        pdfobj = open(filep, 'rb')
        reader = PyPDF2.PdfFileReader(pdfobj)
        outline = reader.outlines
        if outline:
            return '当前书籍已有目录！'
            # print(outline)

        # 识别并读取目录文件
        if not filei:
            filei = title + '.ml'
        if not os.path.exists(filei):
            return '未找到匹配的目录文件'

        fi = open(filei, 'r', encoding='utf-8')
        indexs = fi.readlines()

        # 建立目录树
        tree = settree(indexs)

        # 设置偏置页数
        # offset = input('请输入起始页：')
        writer = PyPDF2.PdfFileWriter()
        for i in range(0, reader.numPages):
            writer.addPage(reader.getPage(i))

        def addmarks(tree, parent):
            for value, page, sub in tree:
                cur = writer.addBookmark(value, int(page) + int(offset) - 1, parent)
                if sub != []:
                    addmarks(sub, cur)

        # 添加目录 设置信号量 失败不储存
        save = 0
        try:
            addmarks(tree, None)
            save = 1
        except:
            print(traceback.print_exc())
            save = 0
            return (title + ' 失败')

        if save == 1:
            if '.pdf' in title:
                title = title.split('.pdf')[0]
            if 'result\\' in title:
                title = title.replace('result\\', '')
            try:
                if os.path.exists('result\\' + title + '_ml.pdf'):
                    os.remove('result\\' + title + '_ml.pdf')
                #最终写结果
                with open('result\\' + nameResult + '\\' + title + '.pdf', 'wb') as fout:
                    writer.write(fout)
                print(title + ' 完成')
            except:
                print('请检查文件是否未关闭并重试')
            time.sleep(1)
        pdfobj.close()


def main(pdfdir):
    # pdfdir = '(Lecture Notes in Computer Science 3418 _ Theoretical Computer Science and General Issues) Ulrik Brandes, Thomas Erlebach (auth.), Ulrik Brandes, Thomas Erlebach (eds.) - Network Analysis_ Methodologi.pdf'
    # file = '怎样解题 new.pdf'
    pdfobj = open(pdfdir, 'rb')
    reader = PyPDF2.PdfFileReader(pdfobj)
    lines = reader.outlines
    get_data(reader, lines)
    pdfsplit(reader)


def pdfsplit(reader):
    # TODO:2.重建pdf文件3.重建同时按目录加书签
    idx = outline_split()
    for chp in idx:
        # 重置目录 将全局页码换为章节页码
        oldir = r'outline\\%s.ml' % chp
        fo = open(oldir, 'r', encoding='utf-8')
        lines = fo.readlines()
        fo.close()
        title, page = lines[0].split('@')
        offset = int(page) - 1
        fo = open(oldir, 'w', encoding='utf-8')
        for line in lines:
            line = newline(offset, line)
            print(line)
            fo.write(line + '\n')
        fo.close()

        # 重写pdf
        start = int(idx[chp].split('@')[1])
        if len(idx[chp].split('@')) < 3:
            end = reader.getNumPages() + 1
        else:
            end = int(idx[chp].split('@')[2]) + 1
        pdf_writer = PyPDF2.PdfFileWriter()
        for index in range(start, end):
            pdf_writer.addPage(reader.getPage(index - 1))

        for x in ['<','>' ,'/' ,'\\' ,'|', ':' ,'"' ,'*' ,'?']:
            if x in title:
                title = title.replace(x,' ')
        with open('result\\' + title + '.pdf', 'wb') as outfile:
            pdf_writer.write(outfile)

        # 添加新目录
        pdf = 'result\\' + title + '.pdf'  # 目标pdf
        ml = 'outline\\' + str(chp) + '.ml'  # 目录文件
        addtag(pdf, ml)
        # 删除中间文件
        os.remove('result\\' + title + '.pdf')


def outline_split():
    f.close()
    fm = open('outline.ml', 'r', encoding='utf-8')
    lines = fm.readlines()
    idx = {}
    temp = []
    num = 0
    for index, line in enumerate(lines):
        if index != (len(lines) - 1):
            if '\t' not in lines[index + 1]:
                temp.append(line)
                title, start = temp[0].split('@')
                temp = ''.join(temp)
                num += 1
                idx[num] = title + '@' + start  # 用数字存储标题 有的标题无法存为文件名
                fc = open('outline\\' + str(num) + '.ml', 'w', encoding='utf-8')
                fc.write(temp)
                fc.close()
                temp = []
            else:
                temp.append(line)
        else:
            temp.append(line)
            title, start = temp[0].split('@')
            temp = ''.join(temp)
            num += 1
            idx[num] = title + '@' + start
            fc = open('outline\\' + str(num) + '.ml', 'w', encoding='utf-8')
            fc.write(temp)
            fc.close()
    for index, item in enumerate(idx):
        if index != len(idx) - 1:
            end = idx[index + 2].split('@')[1]
            end = int(end) - 1
            idx[index + 1] = idx[index + 1].strip() + '@' + str(end)

    return idx


def newline(offset, line):
    title, page = line.split('@')
    page = int(page) - offset

    return title + '@' + str(page)


def get_data(reader, datas, deep=0):
    for index, item in enumerate(datas):
        if not isinstance(item, list):  # 不是列表 无子目录
            if deep > 0 and index > 0 and isinstance(datas[index - 1], list):
                deep -= 1  # 刚从子目录跳出
            title = item.title.strip()
            page = reader.getDestinationPageNumber(item) + 1
            tab = '\t' * deep
            # print('%s%s@%d' % (tab, title, page))
            f.write('%s%s@%d\n' % (tab, title, page))
        else:  # 是列表 有子目录
            deep += 1
            get_data(reader, item, deep)


def getResult(strNameSplit):
    if ' ' in strNameSplit:
        tmp = strNameSplit.split(' ')
    else:
        tmp = strNameSplit.split('.')
    return tmp[0]


if __name__ == '__main__':
    nameResult = getResult(nameSplit)
    if not os.path.isdir('result'):
        os.makedirs('result')
    if not os.path.isdir('result\\' + nameResult):
        os.makedirs('result\\' + nameResult)
    if not os.path.isdir('outline'):
        os.makedirs('outline')
    main(nameSplit)
    elapsed = (time.clock() - start)
    print("Time used:", elapsed)
