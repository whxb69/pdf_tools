import PyPDF2
import os
import traceback
import time


'''
针对电子版生成的pdf添加目录
以pdf内容(如markdown)标题等级为依据
'''
def main():
    if not os.path.exists('result'):
        os.mkdir('result')
    all = os.listdir(os.getcwd())
    for file in all:
        if os.path.splitext(file)[1] == '.pdf':
            title = os.path.splitext(file)[0]
            pdfobj = open(file, 'rb')
            reader = PyPDF2.PdfFileReader(pdfobj)
            indexs = reader.outlines
            if indexs == []:
                temp = reader.resolvedObjects
                for k, v in temp.items():
                    if len(v) > 1:
                        for kk, vv in v.items():
                            if isinstance(vv, list):
                                indexs.append(dicformat({kk: vv}))
                            # print(kk,vv)
                    else:
                        if isinstance(v, list):
                            indexs.append({k: v})
                        # print(k,v)
            writer = PyPDF2.PdfFileWriter()
            # writer.setPageMode(r'/UseOutlines')
            for i in range(0, reader.numPages):
                writer.addPage(reader.getPage(i))

            save = 0
            for index in indexs:
                try:
                    page = reader.getObject(index['/Page'])['/StructParents']
                    value = index['/Title'][1:]
                    writer.addBookmark(value, page)
                    save = 1
                except:
                    save = 0
                    print(title + ' 失败')
                    break
            if save == 1:
                with open('result//' + title + ' new.pdf', 'wb') as fout:
                    writer.write(fout)
                print(title + ' 完成')

    os.startfile('result')
    os.system('pause')

def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def dicformat(indic):
    dic = {}
    value = indic[list(indic.keys())[0]]
    dic['/Title'] = list(indic.keys())[0]
    dic['/Page'] = value[0]
    dic['/Type'] = value[1]
    dic['/Left'] = value[2]
    dic['/Top'] = value[3]
    return dic

if __name__ == '__main__':
    main()