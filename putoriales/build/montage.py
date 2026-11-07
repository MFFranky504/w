import sys,glob
from PIL import Image
files=sorted(glob.glob(sys.argv[1]+'/*.jpg'))[:int(sys.argv[3]) if len(sys.argv)>3 else 12]
n=len(files);cols=min(n,6);rows=(n+cols-1)//cols
w,h=270,480
im=Image.new('RGB',(w*cols,h*rows))
for i,f in enumerate(files):
    im.paste(Image.open(f).resize((w,h)),((i%cols)*w,(i//cols)*h))
im.save(sys.argv[2])
