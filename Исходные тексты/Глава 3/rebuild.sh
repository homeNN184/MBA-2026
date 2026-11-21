set -e
cd /home/claude/work/ch3
python3 build_md.py && python3 render_eq.py >/dev/null && python3 build_docx.py full.docx --noapp >/dev/null && python3 build_docx.py full_pdf.docx --pdf --noapp >/dev/null && soffice --headless --convert-to pdf full_pdf.docx >/dev/null 2>&1
python3 - <<'PY'
import subprocess
out=subprocess.run(['pdftotext','-layout','full_pdf.pdf','-'],capture_output=True,text=True).stdout
pages=out.split('\f'); print('pages',len(pages)-1)
for i,p in enumerate(pages,1):
    if 'Перечень приложений' in p: print('apps list page',i)
    if 'Выводы по главе 3' in p: print('conclusions',i)
PY
