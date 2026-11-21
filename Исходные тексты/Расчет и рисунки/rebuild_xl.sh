set -e
cd /home/claude/work/model
python3 analysis.py > /tmp/an.log 2>&1
python3 build_xlsx.py
rm -rf recalc && mkdir recalc && soffice --headless --calc --convert-to xlsx --outdir recalc TRL_model.xlsx >/dev/null 2>&1
python3 verify_xl.py recalc/TRL_model.xlsx
cp recalc/TRL_model.xlsx final_calc.xlsx
rm -rf /tmp/xo && mkdir -p /tmp/xo && cp final_calc.xlsx "/tmp/xo/Модель ЧДД (формулы).xlsx"
cp "/tmp/xo/Модель ЧДД (формулы).xlsx" /home/claude/work/out/
