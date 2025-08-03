import PyPDF2
reader = PyPDF2.PdfReader('pdf-extract\\game-of-thrones.pdf')
#read text
# page = reader.pages[0]
# print(page.extract_text())

#read images
page = reader.pages[0]
count = 0

for image_file_object in page.images:
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
        count += 1

        