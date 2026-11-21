# -*- coding: utf-8 -*-
"""Пиктограммы в плоском стиле для схем презентации."""
import math
from matplotlib.patches import Polygon, Circle, Rectangle, FancyBboxPatch, Wedge


def _ln(ax, x1, y1, x2, y2, c, lw, z=6):
    ax.plot([x1, x2], [y1, y2], color=c, lw=lw, solid_capstyle="round", zorder=z)


def lamp(ax, x, y, s, c, lw=1.7):
    """Идея, уровень готовности TRL1. Лучи не выходят за пределы круга узла."""
    ax.add_patch(Circle((x, y + 0.13 * s), 0.29 * s, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x - 0.15 * s, y - 0.23 * s, x + 0.15 * s, y - 0.23 * s, c, lw)
    _ln(ax, x - 0.10 * s, y - 0.37 * s, x + 0.10 * s, y - 0.37 * s, c, lw)
    _ln(ax, x - 0.10 * s, y - 0.17 * s, x - 0.10 * s, y - 0.23 * s, c, lw * 0.8)
    _ln(ax, x + 0.10 * s, y - 0.17 * s, x + 0.10 * s, y - 0.23 * s, c, lw * 0.8)
    for a in (25, 65, 90, 115, 155):
        r = math.radians(a)
        _ln(ax, x + 0.40 * s * math.cos(r), y + 0.13 * s + 0.40 * s * math.sin(r),
            x + 0.56 * s * math.cos(r), y + 0.13 * s + 0.56 * s * math.sin(r), c, lw * 0.8)


def flask(ax, x, y, s, c, lw=1.7):
    """Испытания и подтверждение характеристик."""
    _ln(ax, x - 0.16 * s, y + 0.62 * s, x - 0.16 * s, y + 0.10 * s, c, lw)
    _ln(ax, x + 0.16 * s, y + 0.62 * s, x + 0.16 * s, y + 0.10 * s, c, lw)
    _ln(ax, x - 0.28 * s, y + 0.62 * s, x + 0.28 * s, y + 0.62 * s, c, lw)
    ax.add_patch(Polygon([[x - 0.16 * s, y + 0.10 * s], [x - 0.52 * s, y - 0.56 * s],
                          [x + 0.52 * s, y - 0.56 * s], [x + 0.16 * s, y + 0.10 * s]],
                         closed=True, fc="none", ec=c, lw=lw, zorder=6))
    ax.add_patch(Polygon([[x - 0.37 * s, y - 0.28 * s], [x - 0.52 * s, y - 0.56 * s],
                          [x + 0.52 * s, y - 0.56 * s], [x + 0.37 * s, y - 0.28 * s]],
                         closed=True, fc=c, ec="none", alpha=0.3, zorder=6))


def _gear(ax, x, y, r, teeth, c, lw, fill=False):
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.82
        pts.append([x + rr * math.cos(a), y + rr * math.sin(a)])
    ax.add_patch(Polygon(pts, closed=True, fc=c if fill else "none", ec=c, lw=lw, zorder=6))
    ax.add_patch(Circle((x, y), r * 0.32, fc="white", ec=c, lw=lw * 0.8, zorder=7))


def gears(ax, x, y, s, c, lw=1.6):
    """Готовое оборудование, уровень готовности TRL9."""
    _gear(ax, x - 0.16 * s, y + 0.11 * s, 0.44 * s, 11, c, lw)
    _gear(ax, x + 0.34 * s, y - 0.26 * s, 0.27 * s, 9, c, lw)


def doc(ax, x, y, s, c, lw=1.7):
    """Проектная документация."""
    ax.add_patch(Polygon([[x - 0.38 * s, y - 0.62 * s], [x - 0.38 * s, y + 0.62 * s],
                          [x + 0.18 * s, y + 0.62 * s], [x + 0.40 * s, y + 0.38 * s],
                          [x + 0.40 * s, y - 0.62 * s]],
                         closed=True, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x + 0.18 * s, y + 0.62 * s, x + 0.18 * s, y + 0.38 * s, c, lw * 0.8)
    _ln(ax, x + 0.18 * s, y + 0.38 * s, x + 0.40 * s, y + 0.38 * s, c, lw * 0.8)
    for k in range(3):
        _ln(ax, x - 0.22 * s, y + 0.10 * s - k * 0.24 * s,
            x + 0.24 * s, y + 0.10 * s - k * 0.24 * s, c, lw * 0.8)


def draft(ax, x, y, s, c, lw=1.7):
    """Рабочая документация. Лист с чертежом вместо строк текста."""
    ax.add_patch(Polygon([[x - 0.38 * s, y - 0.62 * s], [x - 0.38 * s, y + 0.62 * s],
                          [x + 0.18 * s, y + 0.62 * s], [x + 0.40 * s, y + 0.38 * s],
                          [x + 0.40 * s, y - 0.62 * s]],
                         closed=True, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x + 0.18 * s, y + 0.62 * s, x + 0.18 * s, y + 0.38 * s, c, lw * 0.8)
    _ln(ax, x + 0.18 * s, y + 0.38 * s, x + 0.40 * s, y + 0.38 * s, c, lw * 0.8)
    ax.add_patch(Rectangle((x - 0.22 * s, y - 0.14 * s), 0.30 * s, 0.30 * s,
                           fc="none", ec=c, lw=lw * 0.8, zorder=6))
    _ln(ax, x + 0.08 * s, y + 0.16 * s, x + 0.24 * s, y + 0.16 * s, c, lw * 0.8)
    _ln(ax, x + 0.24 * s, y + 0.16 * s, x + 0.24 * s, y - 0.14 * s, c, lw * 0.8)
    _ln(ax, x - 0.24 * s, y - 0.34 * s, x + 0.26 * s, y - 0.34 * s, c, lw * 0.7)
    _ln(ax, x - 0.24 * s, y - 0.28 * s, x - 0.24 * s, y - 0.40 * s, c, lw * 0.7)
    _ln(ax, x + 0.26 * s, y - 0.28 * s, x + 0.26 * s, y - 0.40 * s, c, lw * 0.7)


def stamp(ax, x, y, s, c, lw=1.7):
    """Экспертиза и согласование."""
    ax.add_patch(Circle((x, y + 0.10 * s), 0.44 * s, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x - 0.20 * s, y + 0.12 * s, x - 0.04 * s, y - 0.06 * s, c, lw)
    _ln(ax, x - 0.04 * s, y - 0.06 * s, x + 0.24 * s, y + 0.32 * s, c, lw)
    _ln(ax, x - 0.52 * s, y - 0.52 * s, x + 0.52 * s, y - 0.52 * s, c, lw)


def crane(ax, x, y, s, c, lw=1.7):
    """Строительно-монтажные работы."""
    _ln(ax, x - 0.10 * s, y - 0.52 * s, x - 0.10 * s, y + 0.52 * s, c, lw)
    _ln(ax, x - 0.42 * s, y + 0.52 * s, x + 0.46 * s, y + 0.52 * s, c, lw)
    _ln(ax, x + 0.30 * s, y + 0.52 * s, x + 0.30 * s, y + 0.12 * s, c, lw * 0.8)
    ax.add_patch(Rectangle((x + 0.14 * s, y - 0.16 * s), 0.31 * s, 0.28 * s,
                           fc="none", ec=c, lw=lw * 0.8, zorder=6))
    _ln(ax, x - 0.42 * s, y - 0.52 * s, x + 0.22 * s, y - 0.52 * s, c, lw)
    _ln(ax, x - 0.10 * s, y + 0.18 * s, x - 0.36 * s, y + 0.52 * s, c, lw * 0.7)


def building(ax, x, y, s, c, lw=1.7):
    """Объект введен в эксплуатацию. Флаг не выходит за пределы круга узла."""
    ax.add_patch(Rectangle((x - 0.42 * s, y - 0.52 * s), 0.84 * s, 0.78 * s,
                           fc="none", ec=c, lw=lw, zorder=6))
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((x - 0.27 * s + i * 0.31 * s, y - 0.34 * s + j * 0.29 * s),
                                   0.18 * s, 0.18 * s, fc=c, ec="none", alpha=0.45, zorder=7))
    _ln(ax, x, y + 0.26 * s, x, y + 0.60 * s, c, lw)
    ax.add_patch(Polygon([[x, y + 0.60 * s], [x + 0.32 * s, y + 0.49 * s], [x, y + 0.38 * s]],
                         closed=True, fc=c, ec="none", zorder=7))


def check(ax, x, y, s, c, lw=2.0):
    """Контрольная точка, подтверждение."""
    ax.add_patch(Circle((x, y), 0.52 * s, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x - 0.24 * s, y + 0.02 * s, x - 0.06 * s, y - 0.20 * s, c, lw)
    _ln(ax, x - 0.06 * s, y - 0.20 * s, x + 0.26 * s, y + 0.24 * s, c, lw)


def target(ax, x, y, s, c, lw=1.7):
    """Цель работы."""
    ax.add_patch(Circle((x, y), 0.56 * s, fc="none", ec=c, lw=lw, zorder=6))
    ax.add_patch(Circle((x, y), 0.34 * s, fc="none", ec=c, lw=lw * 0.85, zorder=6))
    ax.add_patch(Circle((x, y), 0.12 * s, fc=c, ec="none", zorder=7))


def books(ax, x, y, s, c, lw=1.7):
    """Нормативная и методическая база."""
    for k, dy in enumerate((-0.42, -0.08, 0.26)):
        ax.add_patch(Rectangle((x - 0.46 * s + k * 0.04 * s, y + dy * s),
                               0.86 * s, 0.26 * s, fc="none", ec=c, lw=lw * 0.9, zorder=6))
        _ln(ax, x - 0.34 * s + k * 0.04 * s, y + (dy + 0.13) * s,
            x - 0.02 * s + k * 0.04 * s, y + (dy + 0.13) * s, c, lw * 0.7)


def search(ax, x, y, s, c, lw=1.7):
    """Анализ организации работ."""
    ax.add_patch(Circle((x - 0.10 * s, y + 0.14 * s), 0.38 * s, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x + 0.16 * s, y - 0.12 * s, x + 0.44 * s, y - 0.44 * s, c, lw * 1.3)
    _ln(ax, x - 0.26 * s, y + 0.14 * s, x + 0.06 * s, y + 0.14 * s, c, lw * 0.7)
    _ln(ax, x - 0.10 * s, y - 0.02 * s, x - 0.10 * s, y + 0.30 * s, c, lw * 0.7)


def chartup(ax, x, y, s, c, lw=1.7):
    """Экономическая модель и расчет."""
    _ln(ax, x - 0.44 * s, y + 0.48 * s, x - 0.44 * s, y - 0.44 * s, c, lw)
    _ln(ax, x - 0.44 * s, y - 0.44 * s, x + 0.48 * s, y - 0.44 * s, c, lw)
    for k, h in enumerate((0.22, 0.42, 0.66)):
        ax.add_patch(Rectangle((x - 0.30 * s + k * 0.26 * s, y - 0.44 * s),
                               0.17 * s, h * s, fc=c, ec="none", alpha=0.35, zorder=6))
    pts = [(-0.30, -0.10), (-0.04, 0.06), (0.22, 0.30)]
    for a, b in zip(pts[:-1], pts[1:]):
        _ln(ax, x + a[0] * s, y + a[1] * s, x + b[0] * s, y + b[1] * s, c, lw)
    ax.add_patch(Polygon([[x + 0.22 * s, y + 0.30 * s], [x + 0.10 * s, y + 0.28 * s],
                          [x + 0.20 * s, y + 0.16 * s]], closed=True, fc=c, ec="none", zorder=7))


def warn(ax, x, y, s, c, lw=1.7):
    """Риск переделок."""
    ax.add_patch(Polygon([[x, y + 0.56 * s], [x + 0.58 * s, y - 0.46 * s],
                          [x - 0.58 * s, y - 0.46 * s]],
                         closed=True, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x, y + 0.26 * s, x, y - 0.10 * s, c, lw)
    _ln(ax, x, y - 0.24 * s, x, y - 0.28 * s, c, lw * 1.2)


def minus(ax, x, y, s, c, lw=2.0):
    """Слабая сторона, недостающий элемент."""
    ax.add_patch(Circle((x, y), 0.52 * s, fc="none", ec=c, lw=lw, zorder=6))
    _ln(ax, x - 0.26 * s, y, x + 0.26 * s, y, c, lw)
