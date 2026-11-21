import json,sys
from openpyxl import load_workbook
R=json.load(open('results.json')); S=json.load(open('stage1.json')); lay=json.load(open('xl_layout.json'))
wb=load_workbook(sys.argv[1] if len(sys.argv)>1 else 'recalc/TRL_model.xlsx',data_only=True)
mx=0
def cmp(name,a,b):
    global mx
    d=abs(a-b); mx=max(mx,d)
    if d>1e-6: print("DIFF",name,a,b)
wc=wb['Чувств_ставка']
for r,s in zip((16,17,18),('TRL7','TRL6','TRL5')): cmp('switch '+s,wc.cell(r,2).value,R['switch'][s])
wu=wb['Устойчивость']
for i,s in enumerate(('TRL7','TRL6','TRL5')):
    cmp('m* '+s,wu.cell(4+i,2).value,S['res'][s]['mstar']); cmp('w1 '+s,wu.cell(4+i,4).value,S['res'][s]['worst']); print('resid',s,wu.cell(4+i,3).value)
we=wb['Точки входа']; EP=R['entry']
for i,d in enumerate(EP['opts']):
    r=4+i
    cmp('npv',we.cell(r,2).value,d['npv']); cmp('worst',we.cell(r,7).value,d['worst']); cmp('m',we.cell(r,8).value,d['m'])
    cmp('total',we.cell(r,17).value,d['total'])
pos=lay['EPOS']
for i,(k,v) in enumerate(EP['wsets'].items()):
    for j,t in enumerate(v['tot']): cmp('wset '+k,we.cell(pos['rs']+2+i,8+j).value,t)
    if we.cell(pos['rs']+2+i,12).value!=v['best']: print('best diff',k)
for i,g in enumerate(EP['w_rob_grid']):
    for j,t in enumerate(g['tot']): cmp('rob',we.cell(pos['rg']+2+i,2+j).value,t)
cmp('wsw',we.cell(pos['rgl']+1,2).value,EP['w_switch'])
wp=wb['Пороги']; X=S['thr56_X']
for r,v in zip(range(3,13),[S['thr56_rule']['dNPV0'],S['thr56_rule']['E_loss6'],X['El5_other'],X['X'],X['L6'],X['c6'],X['d6'],S['events']['TRL5']['6'][0],S['events']['TRL5']['6'][0]*X['L6'],X['X']/X['L6']]): cmp('thr%d'%r,wp.cell(r,2).value,v)
print("max",mx)
