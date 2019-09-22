import PyPDF2


def main():
    file = '(The Morgan Kaufmann Series in Computer Graphics) Michael F. Cohen, John R. Wallace - Radiosity and Realistic Image Synthesis -Morgan Kaufmann (1993).pdf'
    # file = '怎样解题 new.pdf'
    pdfobj = open(file, 'rb')
    reader = PyPDF2.PdfFileReader(pdfobj)
    lines = reader.outlines
    get_data(reader, lines)


def get_data(reader, datas, deep=0):
    for index, item in enumerate(datas):
        if not isinstance(item, list):
            if deep > 0 and isinstance(datas[index - 1], list):
                deep -= 1
            title = item.title
            page = reader.getDestinationPageNumber(item) + 1
            tab = '\t' * deep
            print('%s%s\t%d' % (tab, title, page))
        else:
            deep += 1
            get_data(reader, item, deep)


if __name__ == '__main__':
    main()
