import glob
from bibl.image_plus_text.imgplustxt import add_text_to_image


add_text_to_image("assets/images/nota.png","assets/images/nota_nova.png","JN")
l = glob.glob("assets/images/door/*")
print(l)