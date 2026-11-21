# -*- coding: utf-8 -*-
import re, subprocess, os, hashlib
md = open("ch3.md", encoding="utf-8").read()
blocks = re.findall(r"^\$\$(.*?)\$\$$", md, flags=re.S | re.M)
tpl = r"""\documentclass[border=4pt,varwidth=15cm]{standalone}
\usepackage{amsmath,amssymb}
\usepackage{fontspec}
\setmainfont{Liberation Serif}
\begin{document}
\fontsize{15}{18}\selectfont
\begin{math}\displaystyle %s\end{math}
\end{document}
"""
for i, b in enumerate(blocks, 1):
    tex = f"eq/e{i}.tex"
    open(tex, "w", encoding="utf-8").write(tpl % b.strip())
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory", "eq", tex], capture_output=True, text=True)
    if not os.path.exists(f"eq/e{i}.pdf"): print("FAIL", i, r.stdout[-400:])
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", f"eq/e{i}.pdf", f"eq/e{i}"], check=True)
print(len(blocks))
