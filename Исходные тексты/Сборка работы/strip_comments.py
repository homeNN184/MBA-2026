import zipfile,re,sys,shutil,os
def strip(path):
    tmp=path+'.tmp'
    zi=zipfile.ZipFile(path); zo=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
    for it in zi.infolist():
        n=it.filename; data=zi.read(n)
        if re.match(r'word/comments(Extended|Ids|Extensible)?\.xml$',n): continue
        if n=='word/_rels/document.xml.rels':
            s=data.decode('utf8'); s=re.sub(r'<Relationship [^>]*comments[^>]*/>','',s); data=s.encode('utf8')
        elif n=='[Content_Types].xml':
            s=data.decode('utf8'); s=re.sub(r'<Override [^>]*comments[^>]*/>','',s); data=s.encode('utf8')
        elif n.startswith('word/') and n.endswith('.xml') and b'comment' in data:
            s=data.decode('utf8')
            s=re.sub(r'<w:commentRangeStart [^>]*/>|<w:commentRangeEnd [^>]*/>','',s)
            s=re.sub(r'<w:r>(?:(?!</w:r>).)*?<w:commentReference [^>]*/>(?:(?!</w:r>).)*?</w:r>','',s,flags=re.S)
            s=re.sub(r'<w:commentReference [^>]*/>','',s)
            data=s.encode('utf8')
        zo.writestr(it,data)
    zo.close(); zi.close(); shutil.move(tmp,path)
for p in sys.argv[1:]: strip(p); print('ok',os.path.basename(p))
