from PIL import Image
import glob, os

for infile in glob.glob('*'):
    im = Image.open(infile)

    file = os.path.splitext(infile)
    filename = file[0] + "." + "png"
    needsSaving = False

    if im.format <> "PNG":
        #print infile, im.format
        needsSaving = True

    if im.size != (48,48):
        print infile, im.size
        im = im.resize((48,48), Image.ANTIALIAS)
        needsSaving = True

    if needsSaving:
        im.save(filename, "PNG")



