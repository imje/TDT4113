from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFont


class Imager():
    _pixel_colors_ = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'white': (255, 255, 255),
                      'black': (0, 0, 0)}
    _image_dir_ = "images/"
    _image_ext_ = "jpeg"

    def __init__(self, fname=False, dir=None, ext=None, image=False, width=100, height=100, background='black',
                 mode='RGB'):
        self.init_file_info(fname, dir, ext)
        self.image = image  # A PIL image object
        self.xmax = width; self.ymax = height  # These can change if there's an input image or file
        self.mode = mode
        self.init_image(background=background)

    def init_file_info(self, fname=None, dir=None, ext=None):
        self.dir = dir if dir else self._image_dir_
        self.ext = ext if ext else self._image_ext_
        self.fid = self.gen_fid(fname) if fname else None

    def gen_fid(self, fname, dir=None, ext=None):
        dir = dir if dir else self.dir
        ext = ext if ext else self.ext
        return dir + fname + "." + ext

    def init_image(self, background='black'):
        if self.fid: self.load_image()
        if self.image:
            self.get_image_dims()
        else:
            self.image = self.gen_plain_image(self.xmax, self.ymax, background)

    # Load image from file
    def load_image(self):
        self.image = Image.open(self.fid)  # the image is actually loaded as needed (automatically by PIL)
        if self.image.mode != self.mode:
            self.image = self.image.convert(self.mode)

    # Save image to a file.  Only if fid has no extension is the type argument used.  When writing to a JPEG
    # file, use the extension JPEG, not JPG, which seems to cause some problems.
    def dump_image(self, fname, dir=None, ext=None):
        self.image.save(self.gen_fid(fname, dir=dir, ext=ext))

    def get_image(self):
        return self.image

    def set_image(self, im):
        self.image = im

    def display(self):
        self.image.show()

    def get_image_dims(self):
        self.xmax = self.image.size[0]
        self.ymax = self.image.size[1]

    def copy_image_dims(self, im2):
        im2.xmax = self.xmax;
        im2.ymax = self.ymax

    def gen_plain_image(self, x, y, color, mode=None):
        m = mode if mode else self.mode
        return Image.new(m, (x, y), self.get_color_rgb(color))

    def get_color_rgb(self, colorname):
        return Imager._pixel_colors_[colorname]

    # This returns a resized copy of the image
    def resize(self, new_width, new_height, image=False):
        image = image if image else self.image
        return Imager(image=image.resize((new_width, new_height)))

    def scale(self, xfactor, yfactor):
        return self.resize(round(xfactor * self.xmax), round(yfactor * self.ymax))

    def get_pixel(self, x, y):
        return self.image.getpixel((x, y))

    def set_pixel(self, x, y, rgb):
        self.image.putpixel((x, y), rgb)

    def combine_pixels(self, p1, p2, alpha=0.5):
        return tuple([round(alpha * p1[i] + (1 - alpha) * p2[i]) for i in range(3)])

    # The use of Image.eval applies the func to each BAND, independently, if image pixels are RGB tuples.
    def map_image(self, func, image=False):
        # "Apply func to each pixel of the image, returning a new image"
        image = image if image else self.image
        return Imager(image=Image.eval(image, func))  # Eval creates a new image, so no need for me to do a copy.

    # This applies the function to each RGB TUPLE, returning a new tuple to appear in the new image.  So func
    # must return a 3-tuple if the image has RGB pixels.

    def map_image2(self, func, image=False):
        im2 = image.copy() if image else self.image.copy()
        for i in range(self.xmax):
            for j in range(self.ymax):
                im2.putpixel((i, j), func(im2.getpixel((i, j))))
        return Imager(image=im2)

    # WTA = winner take all: The dominant color becomes the ONLY color in each pixel.  However, the winner must
    # dominate by having at least thresh fraction of the total.
    def map_color_wta(self, image=False, thresh=0.34):
        image = image if image else self.image

        def wta(p):
            s = sum(p);
            w = max(p)
            if s > 0 and w / s >= thresh:
                return tuple([(x if x == w else 0) for x in p])
            else:
                return (0, 0, 0)

        return self.map_image2(wta, image)

    # Note that grayscale uses the RGB triple to define shades of gray.
    def gen_grayscale(self, image=False):
        return self.scale_colors(image=image, degree=0)

    def scale_colors(self, image=False, degree=0.5):
        image = image if image else self.image
        return Imager(image=ImageEnhance.Color(image).enhance(degree))

    def paste(self, im2, x0=0, y0=0):
        self.get_image().paste(im2.get_image(), (x0, y0, x0 + im2.xmax, y0 + im2.ymax))

    def reformat(self, fname, dir=None, ext='jpeg', scalex=1.0, scaley=1.0):
        im = self.scale(scalex, scaley)
        im.dump_image(fname, dir=dir, ext=ext)

    ### Combining imagers in various ways.

    ## The two concatenate operations will handle images of different sizes
    def concat_vert(self, im2=False, background='black'):
        im2 = im2 if im2 else self  # concat with yourself if no other imager is given.
        im3 = Imager()
        im3.xmax = max(self.xmax, im2.xmax)
        im3.ymax = self.ymax + im2.ymax
        im3.image = im3.gen_plain_image(im3.xmax, im3.ymax, background)
        im3.paste(self, 0, 0)
        im3.paste(im2, 0, self.ymax)
        return im3

    def concat_horiz(self, im2=False, background='black'):
        im2 = im2 if im2 else self  # concat with yourself if no other imager is given.
        im3 = Imager()
        im3.ymax = max(self.ymax, im2.ymax)
        im3.xmax = self.xmax + im2.xmax
        im3.image = im3.gen_plain_image(im3.xmax, im3.ymax, background)
        im3.paste(self, 0, 0)
        im3.paste(im2, self.xmax, 0)
        return im3

    # This requires self and im2 to be of the same size
    def morph(self, im2, alpha=0.5):
        im3 = Imager(width=self.xmax, height=self.ymax)  # Creates a plain image
        for x in range(self.xmax):
            for y in range(self.ymax):
                rgb = self.combine_pixels(self.get_pixel(x, y), im2.get_pixel(x, y), alpha=alpha)
                im3.set_pixel(x, y, rgb)
        return im3

    def morph4(self, im2):
        im3 = self.morph(im2, alpha=0.66)
        im4 = self.morph(im2, alpha=0.33)
        return self.concat_horiz(im3).concat_vert(im4.concat_horiz(im2))

    def morphroll(self, im2, steps=3):
        delta_alpha = 1 / (1 + steps)
        roll = self
        for i in range(steps):
            alpha = (i + 1) * delta_alpha
            roll = roll.concat_horiz(self.morph(im2, 1 - alpha))
        roll = roll.concat_horiz(im2)
        return roll

    # Put a picture inside a picture inside a picture....
    def tunnel(self, levels=5, scale=0.75):
        if levels == 0:
            return self
        else:
            child = self.scale(scale, scale)  # child is a scaled copy of self
            child.tunnel(levels - 1, scale)
            dx = round((1 - scale) * self.xmax / 2);
            dy = round((1 - scale) * self.ymax / 2)
            self.paste(child, dx, dy)
            return self

    def mortun(self, im2, levels=5, scale=0.75):
        return self.tunnel(levels, scale).morph4(im2.tunnel(levels, scale))

# FRA ImageFilter
    def contour(self,image=False):
        image = image if image else self.image
        im = ImageFilter.CONTOUR
        return Imager(image = image.filter(im))

    def emboss(self,image=False):
        image = image if image else self.image
        im = ImageFilter.EMBOSS
        return Imager(image=image.filter(im))

    def blur(self,image=False):
        image = image if image else self.image
        im = ImageFilter.BLUR
        return Imager(image=image.filter(im))

#Fra ImageOps
    def inverter(self,image=False):
        image = image if image else self.image
        im = ImageOps.invert(image)
        return Imager(image=im)

    def solarize(self,image=False,threshold=128):
        image = image if image else self.image
        im = ImageOps.solarize(image,threshold)
        return Imager(image=im)


####**************** TESTS ************************

def ptest1(fid1='trump', fid2="pinocchio",steps=5,newsize=250):
    im1 = Imager(fid1); im2 = Imager(fid2)
    im1 = im1.resize(newsize,newsize); im2 = im2.resize(newsize,newsize)
    roll = im1.morphroll(im2,steps=steps)
    roll.display()
    return roll

def ptest2(fid1='einstein',outfid='tunnel',levels=3,newsize=250,scale=0.8):
    im1 = Imager(fid1);
    im1 = im1.resize(newsize,newsize);
    im2 = im1.tunnel(levels=levels,scale=scale)
    im2.display()
    im2.dump_image(outfid)
    return im2

def ptest3(fid1='pinocchio', fid2="donaldduck",newsize=250,levels=4,scale=0.75):
    im1 = Imager(fid1); im2 = Imager(fid2)
    im1 = im1.resize(newsize,newsize); im2 = im2.resize(newsize,newsize)
    box = im1.mortun(im2,levels=levels,scale=scale)
    box.display()
    return box

def ptestcontour(fid1='pinocchio'):
    im1 = Imager(fid1)
    im1 = Imager.contour(im1)
    im1.display()
    return im1

def ptestemboss(fid1='pinocchio'):
    im1 = Imager(fid1)
    im1 = Imager.emboss(im1)
    im1.display()
    return im1

def ptestblur(fid1='pinocchio'):
    im1 = Imager(fid1)
    im1 = Imager.blur(im1)
    im1.display()
    return im1

def ptestinverter(fid1='pinocchio'):
    im1 = Imager(fid1)
    im1 = Imager.inverter(im1)
    im1.display()
    return im1

def ptestsolarize(fid1='pinocchio'):
    im1 = Imager(fid1)
    im1 = Imager.solarize(im1)
    im1.display()
    return im1



def main1():
    bilde1=Imager('einstein')
    bilde2=Imager('minions')
    bilde3=Imager('campus')
    b1=bilde1.contour().blur().resize(500,500)
    b2=bilde2.inverter().tunnel().resize(500,500)
    b3=bilde3.emboss().resize(500,500)
    b4=b1.morph(b2,0.25)
    image=b3.morphroll(b4)
    image.display()
    return image

def main2():
    bilde1=Imager('campus')
    bilde2=Imager('library')
    bilde3=Imager('northernlights')
    b1 = bilde1.gen_grayscale().resize(500,500)
    b2 = bilde2.contour().resize(500,500)
    b3 = bilde3.inverter().blur().resize(500,500)
    b4 = b1.morph(b2,0.70)
    image = b3.morph(b4,0.30)
    image.display()



main2()

