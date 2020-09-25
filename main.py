import sqlite3
import os
import fitz
import shutil
from PIL import Image


def pdf2png(filename):
    input_path = '.\\Books\\' + filename
    output_path = '.\\Books_temp\\' + filename[:-4] + '\\'

    pdf = fitz.open(input_path)

    for page in range(pdf.pageCount):
        p = pdf[page]
        rotate = int(0)

        zoom_x = 1384 / 612
        zoom_y = 1800 / 792

        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = p.getPixmap(matrix=mat, alpha=False)

        pix.writePNG(output_path + 'book_%s.png' % page)

    return pdf.pageCount


def note2png(filename):
    pathlist = os.listdir('.\\WriteNote\\')
    for path in pathlist:
        if path[:-32] == filename[:-4]:
            resource_path = '.\\WriteNote\\' + path + '\\'
        else:
            continue

        database = sqlite3.connect(resource_path + 'resources.vfs')
        cursor = database.cursor()
        # 索引
        cursor.execute('select storage_uri, space_uri from files')
        index = cursor.fetchall()
        # 大小
        cursor.execute('select offset, size from spaces')
        size = cursor.fetchall()
        cursor.close()
        database.close()

        size = {x[0]: x[1] for x in size}
        index = {int(x[0].split('/')[-1]): x[1].split('/')[-1].split('-') for x in index}
        # print(size)
        # print(index)
        with open(resource_path + 'writeNotes.bin', 'rb') as note:
            note_bin = note.read()
            for i in index.keys():
                png = open('.\\Books_temp\\' + filename[:-4] + '\\' + 'note_%s.png' % i, 'wb')
                for ii in index[i]:
                    png.write(note_bin[int(ii):int(ii) + size[int(ii)]])
                png.close()


def png_combine(filename, pages):
    temp_path = '.\\Books_temp\\' + filename[:-4] + '\\'
    for i in range(pages):
        book = temp_path + 'book_%s.png' % i
        note = temp_path + 'note_%s.png' % i
        if os.path.exists(note):
            print(book)
            print(note)
            img1 = Image.open(book)
            # img1 = img1.crop((0, 71, 1383, 1871))
            img1 = img1.convert('RGBA')
            img2 = Image.open(note)
            img2 = img2.crop((0, 71, 1383, 1871))
            img2 = img2.convert('RGBA')
            r, g, b, alpha = img2.split()
            alpha = alpha.point(lambda i: i > 0 and 204)
            img = Image.composite(img2, img1, alpha)
            img.save(temp_path + "book_note_%s.png" % i)
        else:
            shutil.copy(book, temp_path + "book_note_%s.png" % i)


def png2pdf(filename, pages):
    temp_path = '.\\Books_temp\\' + filename[:-4] + '\\'
    output_path = '.\\Books_output\\'
    index = []
    for f in os.listdir(temp_path):
        if f[:10] == 'book_note_':
            index.append(int(f[10:-4]))
    # print(index)
    index.sort()
    index = [temp_path + 'book_note_' + str(x) + '.png' for x in index]
    # print(index)
    output = fitz.open()
    for png in index:
        pdf_bytes = fitz.open(png).convertToPDF()
        png_pdf = fitz.open("pdf", pdf_bytes)
        output.insertPDF(png_pdf)
    if os.path.exists(output_path + filename):
        os.remove(output_path + filename)
    output.save(output_path + filename)
    output.close()


if __name__ == "__main__":
    for book in os.listdir('.\\Books'):
        try:
            os.mkdir('.\\Books_temp\\' + book[:-4])
        except:
            pass
        p = pdf2png(book)
        note2png(book)
        png_combine(book, p)
        png2pdf(book, p)
        temp_path = '.\\Books_temp\\' + book[:-4] + '\\'
        shutil.rmtree(temp_path)
        os.remove('.\\Books\\' + book)
        print('%s with notes finished' % book)

