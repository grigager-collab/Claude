# какие товары VA заводим: всё мужское, кроме льна и тайвека и того, что уже на сайте; женское — по скринам
import json, sys
V=json.load(open('va_all.json')); split=json.load(open('men_split.json'))
byid={r['id']:r for r in V}
men=[i for i in split['off']]
men.remove(next(r['id'] for r in V if r['g']=='men' and r['art']=='21260503'))   # на сайте как «Олимпийка с принтом Ватаным» (артикул в Tilda ошибочно 21260505)
men.append(next(r['id'] for r in V if r['g']=='men' and r['art']=='21260505'))   # шорты Milky way: совпали с сайтом только по ошибочному артикулу
# «Костюм повседневный Space» 21260214 — тот же «Костюм с шёлком Ватаным», что на сайте (Григорий, 01.11): не заводим
W_ARTS=['24180230/02','24180240/02','24180242','24180241','25190501/02','24180240','24180243','26190101','26210505/02','26210401/01','26210505','26210401','26210101/01','26210102']
women=[next(r['id'] for r in V if r['g']=='women' and r['art']==a) for a in W_ARTS]
order=[r['id'] for r in V]
men.sort(key=order.index)
json.dump(dict(men=men, women=women), open('selection.json','w'))
print('мужское', len(men), '| женское', len(women))
for i in women: print('  ж', byid[i]['art'], byid[i]['name'], byid[i]['price'], byid[i]['color'])
