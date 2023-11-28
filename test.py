import glob
from imageplustxt import add_text_to_image


add_text_to_image("assets/images/nota.png","assets/images/nota_nova.png","JN",(255,255,255),"bibl/image_plus_text/imageplustxt/fonts/LDFComicSans.ttf")
l = glob.glob("assets/images/door/*")
print(l)