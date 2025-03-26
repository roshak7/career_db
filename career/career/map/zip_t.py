import zipfile, io
i = open('E:\\dev\\career-backend\\media\\img\\none.jpg', 'rb').read()

# with zipfile.ZipFile('E:\\dev\\career-backend\\media\\Python.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zipf.write('E:\\dev\\career-backend\\media\\img\\none.jpg', '\\img\\none.jpg')
#     zipf.write('E:\\dev\\career-backend\\media\\img\\1.jpg', '\\img\\1.jpg')
#     zipf.close()
o = io.StringIO()

text1 = """JSON 1 ..."""
# jdata_file_1 = io.StringIO(text1)
# jdata_file_1 = io.BytesIO(text1)

text2 = """JSON 2 ..."""
# jdata_file_2 = io.StringIO(text2)


# zf = zipfile.ZipFile(o, mode='w')
with zipfile.ZipFile('E:\\dev\\career-backend\\media\\Python.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.writestr('\\json\\json1.json',text1)
    zipf.writestr('\\json\\json2.json',text2)
    # zipf.
    # zipf.write(jdata_file_2, 'file_2.json')

# with zipfile.ZipFile('E:\\dev\\career-backend\\media\\Python.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zipf.write('E:\\dev\\career-backend\\media\\img\\none.jpg', '\\img\\none.jpg')
#     zipf.write('E:\\dev\\career-backend\\media\\img\\1.jpg', '\\img\\1.jpg')
    zipf.close()

# zf.writestr('id_card\\none.jpg', i)
# zf.close()
# o.seek(0)
# response = HttpResponse(o.read())
# o.close()
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = "attachment; filename=\"picture.zip\""
