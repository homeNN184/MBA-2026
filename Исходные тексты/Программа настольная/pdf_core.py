# -*- coding: utf-8 -*-
# Автор и разработчик: Postautov_K_V
"""Сборка PDF без внешних библиотек.

Модуль пишет файл PDF средствами стандартной библиотеки Python. Текст выводится
шрифтом TrueType, который встраивается в документ, поэтому кириллица отображается
одинаково на любом компьютере. Набор примитивов ограничен тем, что нужно отчету,
а именно текстом, линиями, прямоугольниками и ломаными.
"""
import os
import struct
import zlib

A4 = (595.28, 841.89)          # портрет, пункты
A4L = (841.89, 595.28)         # альбом

FONT_DIRS = [
    "C:/Windows/Fonts", "C:/WINDOWS/Fonts",
    "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/TTF", "/Library/Fonts", "/System/Library/Fonts/Supplemental",
]
FONT_REG = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
FONT_BLD = ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]


def find_font(names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


class TTF(object):
    """Чтение таблиц шрифта TrueType, которые нужны для встраивания."""

    def __init__(self, path):
        with open(path, "rb") as fh:
            self.data = fh.read()
        self.tables = {}
        num = struct.unpack(">H", self.data[4:6])[0]
        for i in range(num):
            o = 12 + i * 16
            tag = self.data[o:o + 4].decode("latin-1")
            off, ln = struct.unpack(">II", self.data[o + 8:o + 16])
            self.tables[tag] = (off, ln)
        off = self.tables["head"][0]
        self.upem = struct.unpack(">H", self.data[off + 18:off + 20])[0]
        self.bbox = struct.unpack(">hhhh", self.data[off + 36:off + 44])
        self.loc_fmt = struct.unpack(">h", self.data[off + 50:off + 52])[0]
        off = self.tables["hhea"][0]
        self.ascent, self.descent = struct.unpack(">hh", self.data[off + 4:off + 8])
        self.n_hm = struct.unpack(">H", self.data[off + 34:off + 36])[0]
        off = self.tables["maxp"][0]
        self.n_glyphs = struct.unpack(">H", self.data[off + 4:off + 6])[0]
        self._hmtx()
        self._cmap()

    def _hmtx(self):
        off = self.tables["hmtx"][0]
        self.adv = []
        last = 0
        for i in range(self.n_hm):
            last = struct.unpack(">H", self.data[off + i * 4:off + i * 4 + 2])[0]
            self.adv.append(last)
        while len(self.adv) < self.n_glyphs:
            self.adv.append(last)

    def _cmap(self):
        off = self.tables["cmap"][0]
        n = struct.unpack(">H", self.data[off + 2:off + 4])[0]
        self.cmap = {}
        subs = []
        for i in range(n):
            o = off + 4 + i * 8
            pid, eid, so = struct.unpack(">HHI", self.data[o:o + 8])
            if (pid, eid) in ((3, 1), (3, 10), (0, 3), (0, 4), (0, 6)):
                subs.append((pid, eid, off + so))
        # формат 4 разбирается ниже, формат 12 отдельной веткой
        sub = None
        for pid, eid, a in subs:
            if struct.unpack(">H", self.data[a:a + 2])[0] == 4:
                sub = a
                break
        if sub is None:
            for pid, eid, a in subs:
                if struct.unpack(">H", self.data[a:a + 2])[0] == 12:
                    self._cmap12(a)
                    return
            return
        segx2 = struct.unpack(">H", self.data[sub + 6:sub + 8])[0]
        seg = segx2 // 2
        base = sub + 14
        end = struct.unpack(">%dH" % seg, self.data[base:base + segx2])
        base += segx2 + 2
        sta = struct.unpack(">%dH" % seg, self.data[base:base + segx2])
        base += segx2
        delta = struct.unpack(">%dh" % seg, self.data[base:base + segx2])
        base += segx2
        ro_off = base
        ro = struct.unpack(">%dH" % seg, self.data[base:base + segx2])
        for i in range(seg):
            for c in range(sta[i], min(end[i], 0xFFFF) + 1):
                if c == 0xFFFF:
                    continue
                if ro[i] == 0:
                    g = (c + delta[i]) & 0xFFFF
                else:
                    p = ro_off + i * 2 + ro[i] + (c - sta[i]) * 2
                    if p + 2 > len(self.data):
                        continue
                    g = struct.unpack(">H", self.data[p:p + 2])[0]
                    if g:
                        g = (g + delta[i]) & 0xFFFF
                if g:
                    self.cmap[c] = g

    def _cmap12(self, a):
        n = struct.unpack(">I", self.data[a + 12:a + 16])[0]
        for i in range(n):
            o = a + 16 + i * 12
            s0, e0, g0 = struct.unpack(">III", self.data[o:o + 12])
            if e0 - s0 > 0x10FFFF:
                continue
            for c in range(s0, min(e0, 0xFFFF) + 1):
                self.cmap[c] = g0 + (c - s0)

    def gid(self, ch):
        return self.cmap.get(ord(ch), 0)

    def width(self, ch):
        g = self.gid(ch)
        a = self.adv[g] if g < len(self.adv) else 0
        return a * 1000.0 / self.upem


class PDF(object):
    """Документ PDF. Страницы добавляются вызовом page()."""

    def __init__(self, size=A4, margin=36.0):
        self.size = size
        self.margin = margin
        self.pages = []
        self.buf = []
        self.fonts = {}
        for key, names in (("R", FONT_REG), ("B", FONT_BLD)):
            p = find_font(names)
            if p is None:
                raise RuntimeError("Не найден шрифт TrueType для сборки отчета")
            self.fonts[key] = TTF(p)
        self.y = 0.0

    # ---------------------------------------------------------------- страницы
    def page(self, size=None):
        if self.buf:
            self.pages.append(("".join(self.buf), self._cur_size))
        self.buf = []
        self._cur_size = size or self.size
        self.y = self._cur_size[1] - self.margin
        return self._cur_size

    def close_page(self):
        if self.buf:
            self.pages.append(("".join(self.buf), self._cur_size))
            self.buf = []

    @property
    def W(self):
        return self._cur_size[0]

    @property
    def H(self):
        return self._cur_size[1]

    # ---------------------------------------------------------------- примитивы
    @staticmethod
    def _c(col):
        col = col.lstrip("#")
        return tuple(int(col[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def rect(self, x, y, w, h, fill=None, stroke=None, lw=0.5):
        if fill:
            r, g, b = self._c(fill)
            self.buf.append("%.3f %.3f %.3f rg\n" % (r, g, b))
        if stroke:
            r, g, b = self._c(stroke)
            self.buf.append("%.3f %.3f %.3f RG\n%.2f w\n" % (r, g, b, lw))
        op = "B" if (fill and stroke) else ("f" if fill else "S")
        self.buf.append("%.2f %.2f %.2f %.2f re %s\n" % (x, y, w, h, op))

    def line(self, x0, y0, x1, y1, col="#000000", lw=0.5, dash=None):
        r, g, b = self._c(col)
        self.buf.append("%.3f %.3f %.3f RG\n%.2f w\n" % (r, g, b, lw))
        self.buf.append("[%s] 0 d\n" % (" ".join("%.1f" % d for d in dash) if dash else ""))
        self.buf.append("%.2f %.2f m %.2f %.2f l S\n[] 0 d\n" % (x0, y0, x1, y1))

    def poly(self, pts, col="#000000", lw=1.0, close=False, fill=None):
        if not pts:
            return
        if fill:
            r, g, b = self._c(fill)
            self.buf.append("%.3f %.3f %.3f rg\n" % (r, g, b))
        r, g, b = self._c(col)
        self.buf.append("%.3f %.3f %.3f RG\n%.2f w\n" % (r, g, b, lw))
        self.buf.append("%.2f %.2f m " % pts[0])
        for p in pts[1:]:
            self.buf.append("%.2f %.2f l " % p)
        if close:
            self.buf.append("h ")
        self.buf.append(("B" if fill else "S") + "\n")

    def text_width(self, s, size, bold=False):
        f = self.fonts["B" if bold else "R"]
        return sum(f.width(ch) for ch in s) * size / 1000.0

    def text(self, x, y, s, size=9.0, col="#1c1c1a", bold=False, align="l"):
        if s is None:
            s = ""
        s = str(s)
        if not s:
            return
        key = "B" if bold else "R"
        f = self.fonts[key]
        w = self.text_width(s, size, bold)
        if align == "c":
            x -= w / 2.0
        elif align == "r":
            x -= w
        hexs = "".join("%04X" % f.gid(ch) for ch in s)
        r, g, b = self._c(col)
        self.buf.append("BT /F%s %.2f Tf %.3f %.3f %.3f rg %.2f %.2f Td <%s> Tj ET\n"
                        % (key, size, r, g, b, x, y, hexs))

    def wrap(self, s, width, size, bold=False):
        """Разбиение строки по ширине."""
        out, cur = [], ""
        words = []
        for word in str(s).split():
            # слово шире колонки переносится по символам
            while self.text_width(word, size, bold) > width and len(word) > 1:
                k = 1
                while k < len(word) and self.text_width(word[:k + 1], size, bold) <= width:
                    k += 1
                words.append(word[:k])
                word = word[k:]
            words.append(word)
        for word in words:
            t = (cur + " " + word).strip()
            if self.text_width(t, size, bold) <= width or not cur:
                cur = t
            else:
                out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out

    # ---------------------------------------------------------------- сохранение
    def save(self, path):
        self.close_page()
        objs = []

        def add(body):
            objs.append(body)
            return len(objs)

        font_ids = {}
        for key in ("R", "B"):
            f = self.fonts[key]
            raw = zlib.compress(f.data)
            ff = add(b"<< /Length %d /Length1 %d /Filter /FlateDecode >>\nstream\n"
                     % (len(raw), len(f.data)) + raw + b"\nendstream")
            k = 1000.0 / f.upem
            desc = ("<< /Type /FontDescriptor /FontName /EmbF%s /Flags 32 "
                    "/FontBBox [%d %d %d %d] /ItalicAngle 0 /Ascent %d /Descent %d "
                    "/CapHeight %d /StemV %d /FontFile2 %d 0 R >>"
                    % (key, int(f.bbox[0] * k), int(f.bbox[1] * k), int(f.bbox[2] * k),
                       int(f.bbox[3] * k), int(f.ascent * k), int(f.descent * k),
                       int(f.ascent * k * 0.7), 120 if key == "B" else 80, ff))
            dsc = add(desc.encode("latin-1"))
            ws = []
            for g in range(f.n_glyphs):
                a = f.adv[g] if g < len(f.adv) else 0
                ws.append(int(round(a * k)))
            wstr = "[0 [%s]]" % " ".join(str(v) for v in ws)
            cid = add(("<< /Type /Font /Subtype /CIDFontType2 /BaseFont /EmbF%s "
                       "/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
                       "/FontDescriptor %d 0 R /DW 500 /W %s /CIDToGIDMap /Identity >>"
                       % (key, dsc, wstr)).encode("latin-1"))
            font_ids[key] = add(("<< /Type /Font /Subtype /Type0 /BaseFont /EmbF%s "
                                 "/Encoding /Identity-H /DescendantFonts [%d 0 R] >>"
                                 % (key, cid)).encode("latin-1"))

        res = add(("<< /Font << /FR %d 0 R /FB %d 0 R >> >>"
                   % (font_ids["R"], font_ids["B"])).encode("latin-1"))

        page_ids, kids = [], []
        pages_obj = len(objs) + 1 + 2 * len(self.pages)
        for content, size in self.pages:
            raw = zlib.compress(content.encode("latin-1"))
            cs = add(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(raw) + raw + b"\nendstream")
            pid = add(("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] "
                       "/Resources %d 0 R /Contents %d 0 R >>"
                       % (pages_obj, size[0], size[1], res, cs)).encode("latin-1"))
            page_ids.append(pid)
            kids.append("%d 0 R" % pid)
        pg = add(("<< /Type /Pages /Kids [%s] /Count %d >>"
                  % (" ".join(kids), len(kids))).encode("latin-1"))
        info = add("<< /Author (Postautov_K_V) /Creator (Postautov_K_V) "
                   "/Producer (Postautov_K_V) >>".encode("latin-1"))
        root = add(("<< /Type /Catalog /Pages %d 0 R >>" % pg).encode("latin-1"))

        out = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
        pos, offsets = len(out[0]), []
        for i, body in enumerate(objs):
            offsets.append(pos)
            b = b"%d 0 obj\n" % (i + 1) + body + b"\nendobj\n"
            out.append(b)
            pos += len(b)
        xref = pos
        out.append(b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1))
        for o in offsets:
            out.append(b"%010d 00000 n \n" % o)
        out.append(b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                   % (len(objs) + 1, root, info, xref))
        with open(path, "wb") as fh:
            fh.write(b"".join(out))
        return path
