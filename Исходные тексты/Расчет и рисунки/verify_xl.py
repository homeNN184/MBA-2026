import json, sys, subprocess, shutil, os
from openpyxl import load_workbook
R=json.load(open('results.json')); lay=json.load(open('xl_layout.json'))
Y0=lay['Y0']
cols={'inn':'C','pilot':'D','inv':'E','rework':'F','capex':'G','rev':'H','opex':'I','to':'J','tr':'K','kr':'L','toir':'M','ebitda':'N','am':'O','rnd':'P','base':'Q','loss_open':'R','loss_add':'S','limit':'T','loss_use':'U','loss_close':'V','taxable':'W','tax':'X','cf_op':'Y','cf':'Z','cum':'AA','df':'AB','pv':'AC','cumd':'AD','pv_capex':'AE','pv_op':'AF'}
def check(path):
    wb=load_workbook(path,data_only=True)
    mx=0;worst=None
    for s,c in (('BASE','БАЗ'),('TRL7','И7'),('TRL6','И6'),('TRL5','И5')):
        ws=wb['Год_'+c]
        for r in R['scn'][s]['rows']:
            for k,col in cols.items():
                v=ws['%s%d'%(col,Y0+r['n']-1)].value
                d=abs((v or 0)-(r[k]+(r.get('t7x',0) if k=='rework' else 0)))
                if d>mx: mx=d; worst=(s,r['n'],k,v,r[k])
    # ставка
    ws=wb['Чувств_ставка']; mr=0
    for i,d in enumerate(R['sens_rate']):
        for j,s in enumerate(('BASE','TRL7','TRL6','TRL5')):
            mr=max(mr,abs(ws.cell(4+i,2+j).value-d['npv'][s]))
        for j,s in enumerate(('TRL7','TRL6','TRL5')):
            mr=max(mr,abs(ws.cell(4+i,6+j).value-d['R'][s]))
    # события
    wv=wb['События']; me=0
    for s in ('TRL7','TRL6','TRL5'):
        e=lay['EVT'][s]; cc=e['cols']
        items=sorted(R['scn'][s]['out']['items'],key=lambda it:it['combo'])
        from openpyxl.utils import column_index_from_string as ci
        for i,it in enumerate(items):
            r=e['first']+i
            me=max(me,abs(wv['%s%d'%(cc['p'],r)].value-it['prob']),abs(wv['%s%d'%(cc['c'],r)].value-it['cost']),abs(wv['%s%d'%(cc['d'],r)].value-it['delay']),abs(wv['%s%d'%(cc['r'],r)].value-it['rem']),abs(wv['%s%d'%(cc['l'],r)].value-it['loss']))
        tot=e['tot']
        me=max(me,abs(wv['%s%d'%(cc['n'],tot)].value-R['scn'][s]['out']['E_npv']),abs(wv['%s%d'%(cc['p'],tot)].value-1))
    return mx,worst,mr,me
if __name__=='__main__':
    print(check(sys.argv[1]))
