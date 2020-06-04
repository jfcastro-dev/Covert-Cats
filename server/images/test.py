from steg import steg_img

'''
Because of the library we're using,
new.png will always be the output image encode.
hiddentext.txt will be output on decode.
after loading them up in the program, we simply
just delete the files client side so no artifacts of
our communication exist.
'''

def encodeFile(msg_path,img_path):
    encoded=steg_img.IMG(payload_path=msg_path,image_path=img_path)
    encoded.hide()

def decodeFile(img_path):
    decoded=steg_img.IMG(image_path=img_path)
    decoded.extract()

decodeFile('EXlqF0vXYAIam0P.png')