from django.shortcuts import render
from django.urls import reverse
from django.http import Http404, HttpResponse
from django import forms

from PIL import Image
import numpy as np
import functools, zipfile, os, hashlib, random

# Create your views here.
def download_file(filename, aimname):
    file = open(filename, 'rb')  
    response = HttpResponse(file)  
    response['Content-Type'] = 'application/octet-stream'  
    response['Content-Disposition'] = 'attachment; filename = %s'.format(aimname)   
    return response 

def text_embed(request):
    if request.method == 'POST':
        if request.POST['select_fun'] == "Extract info":
            return extract_info(request)
        else:
            return embedding_info(request)

    return render(request, 'lab/text_embed.html')

def embedding_info(request):
    if request.method == 'POST':
        text = request.POST['text']
        text = '#$#' + text
        text += '#%#' #作为结束标记
        
        img = request.FILES.get('beforeimg', None)

        accept_format = ['png', 'jpg', 'peg', 'bmp'] #peg -> jpeg
        if img.name[-3:] not in accept_format:
            raise Http404
        
        im = np.array(Image.open(img))        
        rows, columns, colors = im.shape
        embed = []
        for c in text:
            bin_sign = (bin(ord(c))[2:]).zfill(16)
            for i in range(16):
                embed.append(int(bin_sign[i]))
        
        count = 0
        for row in range(rows):
            for col in range(columns):
                for color in range(colors):
                    if count < len(embed):
                        im[row][col][color] = im[row][col][color] // 2 * 2 + embed[count]
                        count += 1

        # 这里将图片路径换成绝对路径，否则报错
        Image.fromarray(im).save('media/lab/Text_embed.png')

        return download_file('media/lab/Text_embed.png', 'Text_embed.png')

    content = {'text':'', 'selected':"Embedding info"}
    return render(request, 'lab/text_embed.html', content)
    

def extract_info(request):
    if request.method == 'POST':
        img = request.FILES.get('afterimg', None)

        # if not img.name.endswith('.png'):
        #     raise Http404
        
        accept_format = ['png', 'jpg', 'peg', 'bmp'] #peg -> jpeg
        if img.name[-3:] not in accept_format:
            raise Http404

        im = np.array(Image.open(img))
        rows, columns, colors = im.shape
        text = ""
        extract = np.array([], dtype = int)

        count = 0
        for row in range(rows):
            for col in range(columns):
                for color in range(colors):
                    extract = np.append(extract, im[row][col][color] % 2)
                    count += 1
                    if count % 16 == 0:
                        bcode = functools.reduce(lambda x, y: str(x) + str(y), extract)
                        cur_char = chr(int(bcode, 2))
                        text += cur_char
                        if len(text) == 3 and text != '#$#':
                            content = { 'text':'非标准格式文件，无法解密', 'selected':'Extract info'}
                            return render(request, 'lab/text_embed.html', content)
                        if cur_char == '#' and text[-3:] == '#%#':
                            content = { 'text':text[3:-3] }
                            return render(request, 'lab/text_embed.html', content)
                        extract = np.array([], dtype=int)

    return render(request, 'lab/text_embed.html')

def hash_verify(request):
    if request.method == 'POST':
        file = request.FILES.get('file', None)

        with open('media/lab/'+file.name, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)

        content = {}
        algorithm_names = ['md5', 'sha1', 'sha256', 'sha512']

        for name in algorithm_names:
            algorithm = hashlib.new(name)

            # read 1M one time
            read_size = 1024*1024
            with open('media/lab/'+file.name, 'rb') as f:
                while True:
                    b = f.read(read_size)
                    if b:
                        algorithm.update(b)
                    else:
                        break

            content[name] = algorithm.hexdigest()

        os.remove('media/lab/'+file.name)
        return render(request, 'lab/hash_verify.html', content)

    return render(request, 'lab/hash_verify.html')

def download_hash_verify(request):
    return download_file('media/lab/hash_verify.zip', 'hash_verify.zip')

# 将256灰度映射到70个字符上
ascii_char = list(r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

def get_char(r, g, b, alpha = 256):
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    unit = (256.0 + 1) / length
    return ascii_char[int(gray/unit)]

# 检查长宽是否在可接受范围内以及输入时候正确
def check_wh(src, default):
    try :
        src = int(src)
    except:
        src = default
    else:
        src = default if src not in list(range(10, 150)) else src
    return src

def character_image(request):
    if request.method == 'POST':
        img = request.FILES.get('img', None)
        imgformat = request.POST['format']
        
        accept_format = ['png', 'jpg', 'peg', 'bmp'] #peg -> jpeg
        if img.name[-3:] not in accept_format:
            raise Http404

        im = Image.open(img)
        w, h = im.size

        height = request.POST['height']
        height = check_wh(height, 80)
        try:
            autowidth = request.POST['autowidth']
        except Exception as e:
            width = request.POST['width']
            width = check_wh(width, 120)
        else:
            width = w * height // h
        
        im = im.resize((width, height), Image.NEAREST)

        txt = ""

        for i in range(height):
            for j in range(width):
                txt += get_char(*im.getpixel((j, i)))
            txt += '\n'

        with open('media/lab/character_image.txt', 'w') as f_obj:
            f_obj.write(txt)
             
        return download_file('media/lab/character_image.txt', 'character_image.txt')

    return render(request, 'lab/character_image.html')