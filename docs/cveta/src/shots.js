const launch=require('../pw.js');const fs=require('fs');
const D=JSON.parse(fs.readFileSync('colors/data.json'));
const sw=slug=>D[slug].og.replace('/-/resize/504x/','/-/resize/240x240/-/format/webp/');
const ORDER=[['olimpiyka-hlopkovaya-chernyy','Чёрный'],['olimpiyka-hlopkovaya-siniy','Синий'],['olimpiyka-hlopkovaya-ocean-siniy','Ocean'],['olimpiyka-hlopkovaya-volcano-korichnevyy','Volcano']];
(async()=>{
 const b=await launch();
 const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:2});
 await ctx.addCookies([{name:'t2y_cc',value:'all',domain:'2young4u.ru',path:'/'}]);
 const p=await ctx.newPage();
 const meta={};
 async function load(){ await p.goto('https://2young4u.ru/p/olimpiyka-hlopkovaya-volcano-korichnevyy?nc='+Date.now(),{waitUntil:'load',timeout:90000}); await p.waitForTimeout(4000); }
 async function shot(name){
   const r=await p.evaluate(()=>{const c=document.querySelector('.t760');
     const t=c.querySelector('.js-product-name').getBoundingClientRect(), btn=c.querySelector('.t760__btn-wrapper').getBoundingClientRect();
     const items=[...c.querySelectorAll('.t-product__option[data-edition-option-id="Цвет"] .t-product__option-item')].map(l=>{const q=l.querySelector('.t-product__option-checkmark').getBoundingClientRect();return [q.x,q.y,q.width,q.height]});
     return {x:t.x-24,y:t.y-24,w:btn.right-t.x+48+70,h:btn.bottom-t.y+48,items};});
   r.w=Math.min(r.w,1440-r.x);
   await p.screenshot({path:`colors/img/${name}.png`,clip:{x:r.x,y:r.y,width:r.w,height:r.h}});
   meta[name]={w:r.w,h:r.h,items:r.items.map(([x,y,w,h])=>[x-r.x,y-r.y,w,h])};
 }
 await load(); await shot('col_now');
 // четыре квадратика: клоны штатного, порядок постоянный, активный — Volcano
 for (const [name,title] of [['col_four',null],['col_one_product','Олимпийка хлопковая']]){
   await load();
   await p.evaluate(({order,urls,title})=>{
     const form=document.querySelector('.t760 .t-product__option[data-edition-option-id="Цвет"] form');
     const cur=form.querySelector('label');
     order.forEach(([slug,label],i)=>{
       if(slug==='olimpiyka-hlopkovaya-volcano-korichnevyy') return;
       const n=cur.cloneNode(true); n.classList.remove('t-product__option-item_active');
       const inp=n.querySelector('input'); inp.checked=false; inp.value=label;
       const m=n.querySelector('.t-product__option-checkmark'); m.style.backgroundImage=`url("${urls[slug]}")`;
       n.querySelector('.t-product__option-title').textContent=label;
       form.insertBefore(n,cur);
     });
     if(title) document.querySelector('.t760 .js-product-name').textContent=title;
   },{order:ORDER,urls:Object.fromEntries(ORDER.map(([s])=>[s,sw(s)])),title});
   await p.waitForTimeout(2500);
   await shot(title?'col_one_product':'col_four');
 }
 fs.writeFileSync('colors/img/meta.json',JSON.stringify(meta,null,1));
 console.log(JSON.stringify(meta));
 // плитки каталога
 await p.goto('https://2young4u.ru/men/hoodies?nc='+Date.now(),{waitUntil:'load',timeout:90000}); await p.waitForTimeout(3000);
 for(let y=0;y<2500;y+=300){ await p.evaluate(y=>scrollTo(0,y),y); await p.waitForTimeout(300); }
 const tiles=await p.evaluate(()=>[...document.querySelectorAll('.t-catalog__card')].map(c=>{
   const im=c.querySelector('[data-original]'); const a=c.querySelector('a[href]');
   return {name:(c.querySelector('.t-catalog__card__title, .js-product-name')||{}).textContent?.trim(), price:(c.querySelector('.js-product-price')||{}).textContent?.trim(), img:im&&im.getAttribute('data-original'), href:a&&a.getAttribute('href')};}));
 fs.writeFileSync('colors/img/tiles.json',JSON.stringify(tiles,null,1));
 tiles.forEach(t=>console.log(t.name,'|',t.price,'|',t.href,'|',(t.img||'').slice(-50)));
 await b.close();
})();
