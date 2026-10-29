# Отбор и пережатие фото Forest: 900×1200 (3:4), JPEG, без EXIF
import os,sys
from PIL import Image, ImageOps
SRC=sys.argv[1]; OUT=sys.argv[2]
D={
 '22270709':('22270709 дел футболка',['3_MAN_03','3_MOD_05.JPG','3_MOD_02.JPG','3_MOD_01.JPG','3_MOD_03.JPG','3_MOD_04.JPG']),
 '22270801':('22270801 олимп зел выш',['4_MAN_03.jpg','6_MOD_06.JPG','6_MOD_03.JPG','6_MOD_02.JPG','6_MOD_04.JPG','6_MOD_05.JPG']),
 '22270802':('22270802 брюки',['1_MAN_02.jpg','1_MOD_02.JPG','5_MOD_02.JPG','5_MOD_01.JPG','5_MOD_03.JPG','1_MOD_01.JPG']),
 '22270803':('22270811 кост Дикаприо зел выш',['3_MAN_03.jpg','5_MOD_08.JPG','5_MOD_05.JPG','5_MOD_04.JPG','5_MOD_06.JPG','5_MOD_07.JPG']),
 '22270811':('22270811 костюм Дикаприо зел выш',['5_MAN_03.jpg','5_MOD_08.JPG','5_MOD_09.JPG','5_MOD_05.JPG','5_MOD_04.JPG','5_MOD_02.JPG','5_MOD_01.JPG','5_MOD_06.JPG','5_MOD_07.JPG','5_MOD_03.JPG']),
 '22270812':('22270812 Кост стойка зел выш',['6_MAN_03.jpg','6_MOD_06.JPG','6_MOD_07.JPG','6_MOD_03.JPG','6_MOD_02.JPG','5_MOD_02.JPG','5_MOD_01.JPG','6_MOD_04.JPG','6_MOD_05.JPG','5_MOD_03.JPG']),
 '22270821':('22270821 тройка дикапр беж футб беж выш',['1_MAN_03','1_MOD_09.JPG','1_MOD_13.JPG','1_MOD_10.JPG','1_MOD_05.JPG','1_MOD_04.JPG','1_MOD_01.JPG','1_MOD_03.JPG','1_MOD_06.JPG','1_MOD_08.JPG','1_MOD_07.JPG','1_MOD_12.JPG']),
 '22270822':('22270822 комплект стойка беж фут беж выш',['2_MAN_02','2_MOD_09.JPG','2_MOD_08.JPG','2_MOD_03.JPG','2_MOD_02.JPG','1_MOD_01.JPG','1_MOD_03.JPG','2_MOD_04.JPG','2_MOD_05.JPG','2_MOD_10.JPG','1_MOD_02.JPG','2_MOD_06.JPG']),
}
for art,(folder,files) in D.items():
    os.makedirs(os.path.join(OUT,art),exist_ok=True)
    for i,f in enumerate(files,1):
        im=ImageOps.exif_transpose(Image.open(os.path.join(SRC,folder,[x for x in sorted(os.listdir(os.path.join(SRC,folder))) if x.startswith(f)][0]))).convert('RGB')
        im=ImageOps.fit(im,(900,1200),Image.LANCZOS) if im.size!=(900,1200) else im
        im.save(os.path.join(OUT,art,'%02d.jpg'%i),'JPEG',quality=86,optimize=True,progressive=True)
    print(art,len(files))
