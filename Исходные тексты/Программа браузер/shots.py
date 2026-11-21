# -*- coding: utf-8 -*-
"""Съемка экранов браузерной программы для приложения работы.

Снимки делаются в окне 2560 на 2800 точек. Для вкладок, содержимое которых
не помещается в окно, рабочая область прокручивается к нужной карточке.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/work/fig/prog"
JS = os.path.join(HERE, "_shots.js")

SHOTS = [
    ("p01a", "sum", 0, False),
    ("p01b", "sum", 1, False),
    ("p02a", "cal", 0, False),
    ("p02b", "cal", 1, False),
    ("p03a", "flow", 0, False),
    ("p04a", "sens", 0, False),
    ("p04b", "sens", 1, False),
    ("p05a", "mc", 0, True),
    ("p05b", "mc", 1, True),
    ("p05c", "mc", 3, True),
    ("p06a", "ev", 0, False),
    ("p06b", "ev", 1, False),
    ("p07a", "pick", 0, False),
    ("p08a", "chk", 0, False),
    ("p08b", "chk", 1, False),
    ("p09a", "rep", 0, False),
]

script = r"""
const { chromium } = require('playwright');
const SHOTS = %s;
const OUT = %s;
const FILE = %s;
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 2560, height: 2800 }, deviceScaleFactor: 1 });
  const errs = [];
  pg.on('pageerror', e => errs.push(String(e)));
  await pg.goto('file://' + FILE);
  await pg.waitForTimeout(900);
  await pg.evaluate(() => {
    const e = document.querySelector('#form input[data-key="use_crit"]');
    if (e) { e.checked = true; e.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await pg.click('#run');
  await pg.waitForTimeout(2500);
  let mcDone = false;
  for (const [name, tab, card, needMc] of SHOTS) {
    await pg.click('.tab[data-t="' + tab + '"]');
    await pg.waitForTimeout(500);
    if (needMc && !mcDone) {
      const btn = await pg.$('#view button');
      if (btn) { await btn.click(); await pg.waitForTimeout(16000); }
      mcDone = true;
      await pg.waitForTimeout(600);
    }
    await pg.evaluate(k => {
      const cards = document.querySelectorAll('#view .card');
      if (k > 0 && cards[k]) cards[k].scrollIntoView({ block: 'start' });
      else window.scrollTo(0, 0);
    }, card);
    await pg.waitForTimeout(500);
    await pg.screenshot({ path: OUT + '/' + name + '.png' });
    console.log(name);
  }
  if (errs.length) console.log('ошибки:', errs.slice(0, 3));
  await b.close();
})().then(() => process.exit(0));
"""

import json
open(JS, "w", encoding="utf-8").write(
    script % (json.dumps(SHOTS, ensure_ascii=False), json.dumps(OUT),
              json.dumps(os.path.join(HERE, "Модель интеграции (браузер).html"))))
subprocess.run(["node", JS], check=True)

from PIL import Image
for name, *_ in SHOTS:
    p = os.path.join(OUT, name + ".png")
    im = Image.open(p).convert("RGB")
    im.save(os.path.join(OUT, name + ".jpg"), quality=88, optimize=True)
print("снимков:", len(SHOTS))
