# -*- coding: utf-8 -*-
"""Сборка браузерной программы в один файл."""
import io, os
d = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: io.open(os.path.join(d, n), encoding="utf-8").read()
out = rd("shell_head.html") + rd("core.js") + rd("shell_glue.js") + rd("app.js") + rd("shell_tail.html")
io.open(os.path.join(d, "Модель интеграции (браузер).html"), "w", encoding="utf-8").write(out)
print("готово, %d байт" % len(out.encode("utf-8")))
_FILES_AUTHOR = [os.path.join(d, "Модель интеграции (браузер).html")]

# служебные свойства: автор и разработчик
import subprocess as _sp, sys as _sys
_sp.call([_sys.executable, "/home/claude/work/setauthor.py"] + _FILES_AUTHOR)
