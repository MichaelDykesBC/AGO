from PyPDF2 import PdfFileReader

#pdfpath = r'C:\Users\Mike\Desktop\21_PECC SitRep_Nov 16_2021_#2_FINAL[1].pdf'
pdfpath = r'C:\Users\Mike\Desktop\21_PECC SitRep_July05_2021_#105_FINAL[1].pdf'
#pdfpath = r'C:\Users\Mike\Desktop\21_PECC SitRep_Sept 10_2021_#170 FINAL[1].pdf'

file = open(pdfpath, 'rb')

# creating a pdf reader object
fileReader = PdfFileReader(file)
page = fileReader.getPage(0)
page_text = page.extractText()

print(page_text.rsplit("\n"))
#page_text.rsplit("ObjectID ",1)[1].rsplit("\n", -1)[0]