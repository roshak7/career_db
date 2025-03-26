
# inputFile = "e:\\tmp\\1\\profile.xlsx"
# outputFile = "e:\\tmp\\1\\ToPDF.pdf"
# from openpyxl import load_workbook
# from fpdf import FPDF
#
# workbook = load_workbook(inputFile)
# sheet = workbook.active
# pdf = FPDF()
# pdf.add_page()
# for row in sheet.iter_rows():
#     for cell in row:
#         pdf.cell(40, 10, str(cell.value))
# pdf.output(outputFile)


import subprocess

# subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', 'e:\\tmp\\1\\profile.xlsx'])
subprocess.run(['unoconv', '-f', 'pdf', 'e:\\tmp\\1\\profile.xlsx'])
# unoconv -f pdf some-document.xls
# import uno