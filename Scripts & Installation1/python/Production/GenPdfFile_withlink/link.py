#!/usr/bin/python3
import pdfrw
# pip install pdfrw
# required a file sample.pdf with link
# link file generated by cnc
def createLink():
  fh = open('link.txt')		  
  for link in fh:
    linkinfo = link.split("~")
    link = linkinfo[0].replace(" ", "").rstrip('\n')
    email = linkinfo[1].replace(" ", "").rstrip('\n')
    createNewPdf(link, email)

def createNewPdf(link, email):
  pdf = pdfrw.PdfReader("sample.pdf")  
  new_pdf = pdfrw.PdfWriter() 
  for page in pdf.pages:
    for annot in page.Annots or []:
      old_url = annot.A.URI      
      new_url = pdfrw.objects.pdfstring.PdfString("("+link+")")      
      annot.A.URI = new_url  
    new_pdf.addpage(page) 
  new_pdf.write(email+".pdf")

createLink()