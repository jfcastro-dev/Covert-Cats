from steg import steg_img
import sys
#RUN AS ROOT OR IT WILL NOT WORK

def decodeFile(img_path):
    decoded=steg_img.IMG(image_path=img_path)
    decoded.extract()

decodeFile(sys.argv[1])
