# -*- coding: UTF-8 -*-

def save(filename, contents):
    fh = open(filename, 'w', encoding='utf-8')
    fh.write(contents)
    fh.close()


def saveimg(filename, contents):
    fh = open(filename, 'wb')
    fh.write(contents)
    fh.close()


def sfnext(url):
    import re,urllib
    html=urllib.request.urlopen(url).read().decode("utf-8")
    xyz1 =re.search('class="btn normal">下一章</a>', html, flags=0).span()
    xyz1=xyz1[0]
    xyz=html[:xyz1]
    xyz=xyz[-40:]
    xyz2=re.search('=',xyz,flags=0).span()
    xyz2=xyz2[1]
    xyz=xyz[xyz2:]
    xyz=xyz[1:][:-2]
    xyz="http://book.sfacg.com"+xyz
    return xyz


def sflast(url):
    import re,urllib
    html=urllib.request.urlopen(urllib.request.Request(url)).read().decode("utf-8")
    syz1 = re.search('class="btn normal">上一章</a>', html, flags=0	).span()
    syz1=syz1[0]
    syz=html[:syz1]
    syz=syz[-200:]
    syz2=re.search('<a href=',syz,flags=0).span()
    syz2=syz2[1]
    syz=syz[syz2:]
    syz=syz[1:][:-2]
    syz="http://book.sfacg.com"+syz
    return syz


def sf(url, book_dir, cookies, headers, use_ocr = True, merge_total = True):
    import requests
    import os
    print("Use OCR:", use_ocr)
    html_file=requests.get(url, headers=headers, cookies=cookies)
    html=html_file.text
    # get total article
    All_num_1 = re.search('<div class="article" id="article">', html, flags=0).span()
    All_num_1 = All_num_1[1]
    all = html[All_num_1:]
    All_num_2 = re.search('<!-- 按钮 -->', all, flags=0).span()
    All_num_2 = All_num_2[0]
    all = all[:All_num_2]
    # get inside article
    Inside_num_1 = re.search('<div class="article-hd">', all, flags=0).span()[1]
    Inside = all[Inside_num_1:]
    Inside_num_2 = re.search('</div>', Inside, flags=0).span()[0]
    Inside = Inside[:Inside_num_2]

    
    # get title
    Title_num_1 = re.search('<h1 class="article-title">', Inside, flags=0).span()[1]
    Title = Inside[Title_num_1:]
    Title_num_2 = re.search('</h1>', Title, flags=0).span()[0]
    Title = Title[:Title_num_2]
    title_without_md = Title
    
    # get author
    Author_num_1 = re.search('作者', Inside, flags=0).span()[1]
    Author = Inside[Author_num_1:]
    Author_num_2 = re.search('</span>', Author, flags=0).span()[0]
    Author = Author[:Author_num_2]

    # get update time
    UPDate_time_1 = re.search('更新时间', Inside, flags=0).span()[1]
    UPDate_time = Inside[UPDate_time_1:]
    UPDate_time_2 = re.search('</span>', UPDate_time, flags=0).span()[0]
    UPDate_time = UPDate_time[:UPDate_time_2]

    # get word count
    Count_num_1 = re.search('字数', Inside, flags=0).span()[1]
    Count_num = Inside[Count_num_1:]
    Count_num_2 = re.search('</span>', Count_num, flags=0).span()[0]
    Count_num = Count_num[:Count_num_2]
    


    # shrink chapters
    idx_loc = re.search('<div class="article-content font16" id="ChapterBody" data-class="font16">', all, flags=0).span()[1]
    # print(idx_loc)
    data_no_proc = all[idx_loc:][:re.search('</div>', all[idx_loc:], flags=0).span()[0]]
    # print(data_no_proc)
    data_proc = re.sub("</p>", "\n", data_no_proc, count=0, flags=0) + " "
    data_proc = re.sub("<p>", "\t", data_proc, count=0, flags=0).replace('\r\n', '')
    data_proc = re.sub("<br>", "", data_proc, count=0, flags=0)
    # print(data_proc)
    
    # image wget for normal articles
    for idx in range(5):
        # print(re.search("<img src='", data_proc,flags=0))
        image_url = re.search("<img src='", data_proc,flags=0)
        if image_url == None: break
        image_url = image_url.span()
        input()
        image_url=image_url[1]
        data_cropped=data_proc[image_url:]
        
        idx_end=re.search("' />", data_cropped, flags=0).span()[0]
        image_link="https://book.sfacg.com/"+data_cropped[:idx_end]
        print("文章内图像:"+image_link)
        image_http="<img src='"+image_link+"' />"
        os.system('wget -P {}img/ '.format(book_dir)+image_link)
        data_proc=data_proc.replace(image_http, '![img{}](img/'.format(idx+1)+image_link[-40:]+')\n')

    # detect vip image
    vip_image_url=re.search("<img id='vipImage' src='/ajax/ashx/common.ashx?",data_proc)
    if vip_image_url != None: 

        # print(vip_image_url)
        idx_loc = vip_image_url.span()[1]
        # print(idx_loc)
        idx_end=re.search("' />",data_proc[idx_loc:]).span()[0]
        ashx_request = data_proc[idx_loc:][:idx_end]
        picurl='https://book.sfacg.com/ajax/ashx/common.ashx'+ashx_request 

        # get VIP pictures
        picurl.replace("&quick=true","")
        vip_image_http="<img id='vipImage' src='/ajax/ashx/common.ashx"+ashx_request+"' />"
        request_get=requests.get(picurl, headers=headers, cookies=cookies).content
        saveimg("{}vimg/{}.gif".format(book_dir, title_without_md), request_get)

        # convert downloaded gif to jpg
        gif2jpg("{}vimg/{}.gif".format(book_dir, title_without_md))
        os.system("rm \"{}vimg/{}.gif\"".format(book_dir, title_without_md))
        data_proc = data_proc.replace(vip_image_http, '![vimg]({}vimg/{}.jpg)\n'.format(book_dir, title_without_md))
        if use_ocr:
            print("\nImage recognizing...")
            text = image_ocr_recg("{}vimg/{}.jpg".format(book_dir, title_without_md))
            data_proc = data_proc.replace('![vimg]({}vimg/{}.jpg)'.format(book_dir, title_without_md), text)
            # print(text)
    
    if merge_total:
        book_name = book_dir.split("/")[-2]
        if (os.path.exists("{}{}.txt".format(book_dir, book_name)) == False):
            
            file = open("{}{}.txt".format(book_dir, book_name), "w")
            data = "《{}》\n".format(book_name)
            data += "作者: {}\n".format(Author)
            data += "\n"*12 + "="*40 + "\n"
            file.write(data)
            file.close()
        else:
            file = open("{}{}.txt".format(book_dir, book_name), "a+")
            data = Title + "\n" + "="*30
            data += "\n{}\n".format(data_proc)
            file.write(data)
            file.close()
    # make markdown file and save
    Title = "# " + Title
    Author = "\n"+"## 作者" + Author
    UPDate_time = "\n"+"#### 更新时间" + UPDate_time
    Count_num = "\n"+"#### 字数" + Count_num
    return_data = Title+Author+UPDate_time+Count_num+"\n***\n"
    return_data = return_data+"&nbsp;"+data_proc
    
    save("{}{}.md".format(book_dir, title_without_md), return_data)
    return return_data



def image_ocr_recg(image_path, line_size=38, line_cropped_size=17, save_path=""):
    image = Image.open(image_path)
    img_size = image.size
    cropped = Image.new("RGB", (img_size[0], img_size[1]//line_size*line_cropped_size))
    ocr = CnOcr(det_model_name="densenet_lite_136-gru")
    out_txt = ""
    for line in range(1, img_size[1]//line_size+1):
        imgc = image.crop((0,line_size*line-line_cropped_size,img_size[0],line_size*line))
        
        # check a line has tab or new_line
        head = imgc.crop((10,0,10+line_cropped_size,line_cropped_size)).convert("L").getextrema()
        tail = imgc.crop((img_size[0]-10-line_cropped_size,0,img_size[0]-10,line_cropped_size)).convert("L").getextrema()

        tab = True if head[0] == head[1] else False
        new_line = True if tail[0] == tail[1] else False

        # save cropped photos
        cropped.paste(imgc, (0, line*line_cropped_size))
        
        # ocr a line in article and fix wrong recognize
        # imgc.save("temp.jpg")
        result = ocr.ocr_for_single_line(np.array(imgc))
        if len(result) > 0:
            text = result['text'].replace("」","，")
            if tab: text = "\t"+text
            if new_line: text = text+"\n"
            out_txt += text
            # print(text)
        # input()
        
    if save_path != "":
        cropped.save(save_path)
    return out_txt

def gif2jpg(infile:str):
    try:
        image = Image.open(infile)
    except IOError:
        print("Cant load", infile)
        sys.exit(1)
    idx = 0
    palette = image.getpalette()
    try:
        while True:
            if idx == 1:
                break
            image.putpalette(palette)
            new_image = Image.new("RGB", image.size)
            new_image.paste(image)
            new_image.save(infile.replace(".gif", ".jpg"))
            idx += 1
            # image.seek(image.tell() + 1)
    except EOFError:
        pass # end of sequence

def manual(url, book_dir, cookies, headers, use_ocr):
    while True:
        print(sf(url, book_dir, cookies, headers, use_ocr))
        tj = input("是否继续? ,下一章输入n,上一章输入l,重输链接输入r ")
        if tj == "n":
            url=sfnext(url)
        if tj == "l":
            url=sflast(url)
        if tj == "r":
            url=input("请输入SF文章链接:")


def auto(url, book_dir, cookies, headers, use_ocr):
    while True:
        print(sf(url, book_dir, cookies, headers, use_ocr))
        url=sfnext(url)


import re
import os
import sys
from pathlib import Path
import uncurl

from cnocr import CnOcr
from PIL import Image
import numpy as np



if __name__ == '__main__':

    import requests

    input("请先确认是否已经将curl写入request.txt文件 (o゜▽゜)o☆")
    # Get cookies and headers from curl
    file = open('request.txt','r')
    curl = file.read().replace("\\","").replace("\n","")
    # request = uncurl.parse(curl)
    request_context = uncurl.parse_context(curl)
    url = request_context.url
    cookies = dict(request_context.cookies)
    headers = dict(request_context.headers)
    mode=input("模式选择:手动模式输入[m] 自动模式输入[a] [default:a]")
    use_ocr = False if input("是否使用OCR? [y/n] [default:y]").lower() == "n" else True

    html_file=requests.get(url, headers=headers, cookies=cookies)
    html=html_file.text
    # get total article
    idx_loc = re.search('class="item bold">', html, flags=0).span()
    if len(idx_loc) < 2:
        print("未检测到符合格式的网页请求，请确认输入的cURL是否对应某本书的某一章节")
        exit()
    idx_loc = idx_loc[1]
    book_name = html[idx_loc:]
    idx_end = re.search('</a>', book_name, flags=0).span()
    idx_end = idx_end[0]
    book_name = book_name[:idx_end]
    print(book_name)
    # book_name = "魔女的复仇黑童话"
    book_dir = "./{}/".format(book_name)
    Path(book_dir).mkdir(parents=True, exist_ok=True)
    # create img directories
    Path(book_dir+"img/").mkdir(parents=True, exist_ok=True)
    Path(book_dir+"vimg/").mkdir(parents=True, exist_ok=True)
    if mode == "m":
        manual(url, book_dir, cookies, headers, use_ocr)
    else:
        auto(url, book_dir, cookies, headers, use_ocr)
