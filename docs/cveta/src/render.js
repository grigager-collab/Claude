const launch=require('../pw.js');const path=require('path');
(async()=>{
 const b=await launch();
 const p=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:2});
 await p.goto('file://'+path.resolve('slides.html'),{waitUntil:'networkidle',timeout:60000});
 await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
 console.log('шрифты:', await p.evaluate(()=>['Tenor Sans','Raleway'].map(f=>f+'='+document.fonts.check('20px "'+f+'"')).join(' ')));
 // переполнение: что-то вылезло за низ слайда?
 console.log(await p.evaluate(()=>[...document.querySelectorAll('.slide')].map(s=>{const r=s.getBoundingClientRect();let max=0;s.querySelectorAll('*').forEach(e=>{const q=e.getBoundingClientRect();if(q.height>0)max=Math.max(max,q.bottom-r.top)});return s.id+': низ содержимого '+Math.round(max)+' из 1350'}).join(' | ')));
 for (const id of ['s1','s2','s3','s4']){
   await p.locator('#'+id).screenshot({path:`out_${id}.jpg`,type:'jpeg',quality:92});
 }
 await b.close();
})();
