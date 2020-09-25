import sqlite3
import os
import fitz
import shutil
from PIL import Image


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
        try:
            with open(resource_path + 'writeNotes.bin', 'rb') as note:
                note_bin = note.read()
                for i in index.keys():
                    png = open('.\\Books_temp\\' + filename[:-4] + '\\' + 'note_%s.png' % i, 'wb')
                    for ii in index[i]:
                        png.write(note_bin[int(ii):int(ii) + size[int(ii)]])
                    png.close()
        except FileNotFoundError:
            print('%s has no notes!' % filename)


def png_attach(filename):
    pdf_path = '.\\Books\\' + filename
    pdf = fitz.open(pdf_path)
    for p in range(pdf.pageCount):
        notepath1 = '.\\Books_temp\\' + book[:-4] + '\\' 'note_%s.png' % p
        notepath2 = '.\\Books_temp\\' + book[:-4] + '\\' 'note_%s_.png' % p
        try:
            noteimg = Image.open(notepath1)
        except FileNotFoundError:
            continue
        noteimg = noteimg.crop((0, 71, 1383, 1871))
        noteimg.save(notepath2)

        targetpage = pdf[p]
        targetpage.insertImage(fitz.Rect(0, 0, 612, 792), filename=notepath2)
    
    pdf.save('.\\Books_output\\' + filename)



if __name__ == "__main__":
    for book in os.listdir('.\\Books'):
        if book[-4:] == '.txt':
            continue
        try:
            os.mkdir('.\\Books_temp\\' + book[:-4])
        except:
            pass

        note2png(book)
        png_attach(book)
        temp_path = '.\\Books_temp\\' + book[:-4] + '\\'
        shutil.rmtree(temp_path)
        os.remove('.\\Books\\' + book)
        print('%s with notes finished' % book)
