#!/usr/bin/python3
# coding: utf-8

import re
from array import array
import csv
import requests
import sys
import os
import functools
from concurrent import futures
from urllib.parse import urlparse

app_dir = os.path.abspath(os.path.dirname(__file__))
static_path = os.path.join(app_dir, "static")
html_cache_path = os.path.join(app_dir, "html_cache")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

text_list = ["Vin_I.txt", "Vin_II.txt", "Vin_III.txt", "Vin_IV.txt", "Vin_V.txt",
             "DN_I.txt", "DN_II.txt", "DN_III.txt",
             "MN_I.txt", "MN_II.txt", "MN_III.txt",
             "AN_I.txt", "AN_II.txt", "AN_III.txt", "AN_IV.txt", "AN_V.txt",
             "SN_I.txt", "SN_II.txt", "SN_III.txt", "SN_IV.txt", "SN_V.txt",
             "Khp.txt", "Ud.txt", "It.txt", "Nidd_I.txt", "Nidd_II.txt", "Khp.txt",
             "Dhātuk.txt", "Yam_I.txt", "Yam_II.txt", "Kv.txt", "Pugg.txt", "Paṭis_I.txt", "Paṭis_II.txt",
             "Vibh.txt", "Dhs.txt", "Mil.txt", "Vism.txt"]

text_dict = {"Vin_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin1maou.htm",
             "Vin_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin2cuou.htm",
             "Vin_III.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin3s1ou.htm",
             "Vin_IV.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin4s2ou.htm",
             "Vin_V.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/1_vin/vin5paou.htm",
             "DN_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/1_digh/dighn1ou.htm",
             "DN_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/1_digh/dighn2ou.htm",
             "DN_III.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/1_digh/dighn3ou.htm",
             "MN_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/2_majjh/majjn1ou.htm",
             "MN_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/2_majjh/majjn2ou.htm",
             "MN_III.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/2_majjh/majjn3ou.htm",
             "AN_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/4_angu/angut1ou.htm",
             "AN_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/4_angu/angut2ou.htm",
             "AN_III.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/4_angu/angut3ou.htm",
             "AN_IV.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/4_angu/angut4ou.htm",
             "AN_V.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/4_angu/angut5ou.htm",
             "SN_I.txt":"http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu1ou.htm",
             "SN_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu2ou.htm",
             "SN_III.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu3ou.htm",
             "SN_IV.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu4ou.htm",
             "SN_V.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/3_samyu/samyu5ou.htm",
             "Ap.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/apadanou.htm",
             "Khp.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/khudp_ou.htm",
             "Dhp.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/dhampdou.htm",
             "Sn.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/sutnipou.htm",
             "Ud.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/udana_ou.htm",
             "It.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/itivutou.htm",
             "Vm.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/vimvatou.htm",
             "Pv.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/petvatou.htm",
             "Th.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/theragou.htm",
             "Thi.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/therigou.htm",
             "Nidd_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/nidde1ou.htm",
             "Nidd_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/nidde2ou.htm",
             "Bv.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/budvmsou.htm",
             "Cp.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/carpitou.htm",
             "Ja_1.txt":"http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak1ou.htm",
             "Ja_2.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak2ou.htm",
             "Ja_3.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak3ou.htm",
             "Ja_4.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak4ou.htm",
             "Ja_5.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak5ou.htm",
             "Ja_6.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/jatak6ou.htm",
             "Dhātuk.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/dhatukou.htm",
             "Yam_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/yamak_1ou.htm",
             "Yam_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/yamak_2ou.htm",
             "Kv.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/kathavou.htm",
             "Pugg.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/pugpan_ou.htm",
             "Paṭis_I.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/patis1ou.htm",
             "Paṭis_II.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/patis2ou.htm",
             "Vibh.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/vibhanou.htm",
             "Dhs.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/3_abh/dhamsgou.htm",
             "Mil.txt": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/2_parcan/milindou.htm",
             "Vism.txt":"http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/buvismou.htm",
             "Sp_1":"http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_1ou.htm",
             "Sp_2": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_2ou.htm",
             "Sp_3": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_3ou.htm",
             "Sp_4":"http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_4ou.htm",
             "Sp_5": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_5ou.htm",
             "Sp_6": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_6ou.htm",
             "Sp_7": "http://gretil.sub.uni-goettingen.de/gretil/2_pali/4_comm/samp_7ou.htm",
             }

def static_file_path(file_name):
    global static_path
    return os.path.join(static_path, file_name)

# html_cache_path にHTMLファイルがあればそれを利用する
# ダウンロードしたHTMLの改行コードは CRLF
# $ file html_cache/vin1maou.htm
# html_cache/vin1maou.htm: HTML document text, Unicode text, UTF-8 text, with very long lines (333), with CRLF line terminators
def download(url):
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    path = os.path.join(html_cache_path, file_name)

    if os.path.exists(path):
        # 改行コードを保ったまま開く
        with open(path, "r", encoding="utf-8", newline="") as f:
            result = f.read()
    else:
        response = requests.get(url)
        response.encoding = "utf-8"
        result = response.text
        # 改行コードを保ったまま保存する
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(result)
    return result

def write_text_file(file_name, content, newline=None):
    with open(static_file_path(file_name), "w", encoding="utf-8", newline=newline) as f:
        f.write(content)

def write_csv_file(file_name, data, oneline=False):
    with open(static_file_path(file_name), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if oneline:
            # 単一行のCSV
            writer.writerow(data)
        else:
            writer.writerows(data)

def write_bin_file(file_name, data):
    with open(static_file_path(file_name), "wb") as f:
        data.tofile(f)

def mainpart():
    print(static_path)
    print("### Start ###")
    print(" ")
    with futures.ThreadPoolExecutor() as executor:
        res = executor.map(text_requests, text_dict.items())
        list(res)
    print("\n\n#### All texts were installed" + ": Process 100 %"+  "*" * (100 // 5))#八百長

Sp_flag = 0
def text_requests(text_dict_item):
    global Sp_flag
    name, _ = text_dict_item
    if name == "Th.txt":
        Thera_make()
    elif name == "Thi.txt":
        Theri_make()
    elif name == "Ap.txt":
        Ap_create()
    elif name == "Sn.txt":
        Sn_create()
    elif name in {"Cp.txt", "Vm.txt", "Pv.txt", "Dhp.txt", "Bv.txt"}:
        text_name, extention = name.split(".")
        exec("{}_make()".format(text_name))
    elif name in ["Ja_{}.txt".format(i) for i in range(1, 7)]:
        text_name, extention = name.split(".")
        J_create(name, text_name[-1], text_name)
    elif name in ["Sp_{}".format(i) for i in range(1,8)]:
        if Sp_flag == 1:
            pass
        else:
            Sp_flag = 1
            Sp_create()
    else:
        text_create(name)


def process_print(func):
    @functools.wraps(func)
    def printer(*args, **kwargs):
        proc_per = ( len(os.listdir(static_path)) * 100 // 268 )
        if args:
            text_name = args[0].split(".")[0]
            txt_path = static_file_path(text_name + "_.txt")
            htm_path = static_file_path(text_name + "_.htm")
            if not(os.path.exists(txt_path)) and not(os.path.exists(htm_path)):
                print("\r#### Preparing {:14}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end = "")
                result = func(*args, **kwargs)               
                print("\r#### Done with {:14}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
                return result
            else:
                print("\r#### Pass {:19}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end = "")
        else:
            file_name = func.__name__.split("_")[0]
            txt_path = static_file_path(file_name + "_.txt")
            csv_path = static_file_path(file_name + "_.csv")
            htm_path = static_file_path(file_name + "_.htm")
            if not(os.path.exists(txt_path)) and not(os.path.exists(csv_path)) and not(os.path.exists(htm_path)):
                print("\r#### Preparing {:14}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
                result = func(*args, **kwargs)
                print("\r#### Done with {:14}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
                return result
            else:
                print("\r#### Pass {:19}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
    return printer

def htm_make(name, html):
    new_name = name.split(".")[0]
    new_name = new_name + "_.htm"
    new_html = add_page_section(html)
    write_text_file(new_name, new_html)

# ページ表記に section タグを追加する
# <section id ='223'>[page 223]</section>
def add_page_section(html):
    replace = """<section id ='""" + r"\2" + """'>""" + r"\1" + r"\2" + r"\3" + """</section>"""
    return re.sub(r"(\[page )(\d{1,4})(\])", replace, html)

import copy
def text_make(text):
    vin_ = download(text_dict[text])
    htm_make(text, copy.deepcopy(vin_))
    vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
    vin_ = re.sub(r"\r\n", "\n", vin_)#これが大事な一行になる
    if text in {"SN_II.txt", "SN_III.txt", "SN_IV.txt", "SN_V.txt"}:
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=CHAPTER)", "", vin_)
    elif text == "SN_I.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=<b>SN_1)", "", vin_)
    elif text == "Khp.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=Buddhaṃ)", "", vin_)
    elif text == "Nidd_I.txt":
        vin_ = re.sub(r"""(?<=page 001\])(.|\s)*?Part I""", "", vin_)
    elif text == "Nidd_II.txt":
        vin_ = re.sub(r"""(?<=page 001\])(.|\s)*?Vatthugāthā\.""", "", vin_)
    elif text == "J_1":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=JaNi)", "", vin_)
    elif text == "Paṭis_II.txt":
        vin_ = re.sub(r"""(?<=page 001\])(.|\s)*?INDRIYAKATHĀ</span><BR>""", "", vin_)
    elif text == "Dhs.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?{MĀTIKĀ\.}<br>", "", vin_)
    elif text == "Dhātuk.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?BUDDHASSA<BR>", "", vin_)
    elif text == "Mil.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?TASSA BHAGAVATO ARAHATO SAMMĀSAMBUDDHASSA\.<BR>", "", vin_)
    elif text == "Vism.txt":
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?NIDĀNĀDIKATHĀ<BR>", "", vin_)
    elif "&nbsp;" in text[:1000] or text in {"Yam_I.txt", "Yam_II.txt", "Pugg.txt", "Paṭis_I.txt"}:
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=\n(\w|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\w))", "", vin_)
    else:
        vin_ = re.sub(r"(?<=page 001\])(.|\s)*?(?=\n     \S)", "", vin_)
    vin_ = re.sub(r"\[page(.|\s)*?\]", "%", vin_)
    vin_ = re.sub(r"(?<=page 001])(.|\s)*?(?=\n\     \S)", "", vin_)
    vin_ = re.sub(r"<span class=\"red\">\d*?</span>", "", vin_)
    vin_ = re.sub(r"\((.|\s).*?\d\)", "", vin_)
    vin_ = re.sub(r"\[\d.*?\]", "", vin_)#カッコで括られたセクションの名前のようなところを削除したい
    vin_ = re.sub(r"\s+\d{1,3}\. .*?VAGGA\.", "", vin_)#Jataka の ~ vagga っていうのを消したい
    vin_ = re.sub(r"\s+\[.*?\](\<BR\>|\<br\>)", "", vin_)
    vin_ = re.sub(r"\s+VAGGA (I[VX]|V*?I{0,3})\..*?\.", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"\. \. \.", "@", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?\[.*?\](<BR>|<br>)", "", vin_)#Majjhimanikaya の数字のやつを消したい
    vin_ = re.sub(r"(?<=\n)\s+?(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\. \w*?\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?.*?, ((C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}))\.\s{0,1}(?=(<BR>\n|<br>\n))", "", vin_)
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|&lt;|&gt;|_{3,})", "", vin_)
    vin_ = re.sub(r"(<BR>|<br>)", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"\n%\n", "%", vin_)
    vin_ = re.sub(r"(\w)-%", r"\1"+"&", vin_)
    vin_ = re.sub(r"&{2,}", "&", vin_)#これ特に要らない気もするけど、とりあえず残す。
    vin_ = re.sub(r"(\w)\-\n", r"\1"+"#", vin_)# -改行 は # でとりあえず置き換えておく)
    vin_ = re.sub(r"\n", " \n", vin_)
    vin_ = re.sub(r"--", "@", vin_)#--pa--, --la-- が検索のときに入らないようにするだけ
    text_for_count = re.sub(r"%", " %", vin_)
    text_for_search = re.sub(r"[%&#\n]", "", text_for_count)
    return text_for_count, text_for_search



def bin_maker(text_for_count, text_name):
    line = 0
    page = 0
    j = 0
    page_list = array("I")#あるテキストインデックスにおいて、何ページ・何行目であるかが入る
    line_list = array("I")
    text_index = array("I")#すべての改行位置先頭のテキストインデックスが入る
    end = len(text_for_count) - 1
    for i in range(len(text_for_count) - 1):
        j = j + 1# j はテキストの index そのものを指す
        if i == len(text_for_count) - 1:
            break
        elif text_for_count[i] == "%" or text_for_count[i] == "&" or i == end:#ページ更新の儀式
            j = j - 1
            line = 1
            page += 1
            text_index.append(j)
            page_list.append(page)
            if i != end:
                line_list.append(line)
        elif text_for_count[i] == "\n" or text_for_count[i] == "#":#行更新の儀式
            line += 1
            j = j - 1
            text_index.append(j)
            line_list.append(line)
            page_list.append(page)
            
    index_bin = text_name + "_index_" + ".bin"
    write_bin_file(index_bin, text_index)

    line_bin = text_name + "_line_" + ".bin"
    write_bin_file(line_bin, line_list)

    page_bin = text_name + "_page_" + ".bin"
    write_bin_file(page_bin, page_list)

def Sp_make(text = "Sp"):
    Sp_raw = ""
    for i in range(1, 8):
        vin_ = download(text_dict["Sp_{}".format(i)])
        vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
        vin_ = re.sub(r"\r\n", "\n", vin_)
        if i == 1:
            htm_make("Sp_1", copy.deepcopy(vin_))
            vin_ = re.sub(r"(?<=page 001\])(.|\s)*?sammāsambuddhassa\.<br>", "", vin_)
        elif i == 2:
            htm_make("Sp_2", copy.deepcopy(vin_))
            start, end = re.search(r"(?<=\d\])(.|\s)*?II<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
#            vin_ = re.sub(r"(?<=\d\])(.|\s)*?II<br>", "", vin_)
        elif i == 3:
            htm_make("Sp_3", copy.deepcopy(vin_))
            start, end = re.search(r"(?<=\d\])(.|\s)*?SAṄGHĀDISESA I-XIII<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 4:
            htm_make("Sp_4", copy.deepcopy(vin_))
            start, end = re.search(r"""(?<=\d\])(.|\s)*?SAMBUDDHASSA\.<span class="red"><sup>1</sup></span><br>""", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
            vin_ += "%"#For page 950 is not exist.
        elif i == 5:
            htm_make("Sp_5", copy.deepcopy(vin_))
            start, end = re.search(r"(?<=\d\])(.|\s)*?SAMANTAPĀSĀDIKĀ<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 6:
            htm_make("Sp_6", copy.deepcopy(vin_))
            start, end = re.search(r"(?<=\d\])(.|\s)*?KAMMAKKHANDHAKA-VAṆṆANĀ<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 7:
            htm_make("Sp_7", copy.deepcopy(vin_))
            start, end = re.search(r"(?<=\d\])(.|\s)*?I<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        Sp_raw += vin_
    vin_ = Sp_raw; Sp_raw = ""
    vin_ = re.sub(r"\[page(.|\s)*?\]", "%", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", vin_)
    #ローマ数字＋タイトル的な部分を消したい
    vin_ = re.sub(r"\((.|\s).*?\d\)", "", vin_)
    vin_ = re.sub(r"\[\d.*?\]", "", vin_)#カッコで括られたセクションの名前のようなところを削除したい
    vin_ = re.sub(r"\s+\d{1,3}\. .*?VAGGA\.", "", vin_)#Jataka の ~ vagga っていうのを消したい
    vin_ = re.sub(r"\s+\[.*?\](\<BR\>|\<br\>)", "", vin_)
    vin_ = re.sub(r"\s+VAGGA (I[VX]|V*?I{0,3})\..*?\.", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"\. \. \.", "@", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?\[.*?\](<BR>|<br>)", "", vin_)#Majjhimanikaya の数字のやつを消したい
    vin_ = re.sub(r"(?<=\n)\s+?(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\. \w*?\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?.*?, ((C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}))\.\s{0,1}(?=(<BR>\n|<br>\n))", "", vin_)
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|&lt;|&gt;|_{3,})", "", vin_)
    vin_ = re.sub(r"(<BR>|<br>)", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"\n%\n", "%", vin_)
    vin_ = re.sub(r"(\w)-%", r"\1"+"&", vin_)
    vin_ = re.sub(r"&{2,}", "&", vin_)#これ特に要らない気もするけど、とりあえず残す。
    vin_ = re.sub(r"(\w)\-\n", r"\1"+"#", vin_)# -改行 は # でとりあえず置き換えておく)
    vin_ = re.sub(r"\n", " \n", vin_)
    vin_ = re.sub(r"--", "@", vin_)#--pa--, --la-- が検索のときに入らないようにするだけ
    text_for_count = re.sub(r"%", " %", vin_)
    text_for_search = re.sub(r"[%&#\n]", "", text_for_count)
    return text_for_count, text_for_search


def Jataka(text_for_search, text_number):
    pre_long = len(text_for_search)
    verse = []
    J_verse_start = array("I")
    J_verse_end = []
    Jataka = r"Ja\_(.|\s)*?\da?b? \|\|"
    A = re.finditer(Jataka, text_for_search)
    for text in A:
        J_verse_start.append(text.start())#keep startpoints of verses
        J_verse_end.append(text.end())
        verse.append([text.group(0)])
        verse_long = len(text_for_search[text.start(): text.end()])
        text_for_search = text_for_search[0: text.start()] + "."*verse_long + text_for_search[text.end():]
    new_Ja = "Ja_" + str(text_number) + "_.txt"
    write_text_file(new_Ja, text_for_search)

    new_bin = "J_" + str(text_number) + "_start_point_.bin"
    write_bin_file(new_bin, J_verse_start)

    new_verse = "J_" + str(text_number) + ".csv"
    write_csv_file(new_verse, verse)

def Sn_text_make(text = "Sn"):
    vin_ = download(text_dict["Sn.txt"])
    htm_make(text, copy.deepcopy(vin_))
    vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
    vin_ = re.sub(r"\r\n", "\n", vin_)#これが大事な一行になる
    vin_ = re.sub(r"(?<=\[page 001\])(.|\s)*?Uragasutta\.", "", vin_)
    vin_ = re.sub(r"\[page(.|\s)*?\]", "%", vin_)
     #全てのテキストごとに異なる最初の部分を処理
    vin_ = re.sub(r"\[F\._.*?\]", "", vin_)
    vin_ = re.sub(r"\s+?\d{1,2}.*?(sutta|\d\))\.", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", vin_)
    #ローマ数字＋タイトル的な部分を消したい
    vin_ = re.sub(r"(?<=\n)\s*?(I[VX]|V*?I{0,3})\..*?\.", "", vin_)
    vin_ = re.sub(r"\[\d.*?\]", "", vin_)#カッコで括られたセクションの名前のようなところを削除したい
    vin_ = re.sub(r"\s+\d{1,3}\. .*?VAGGA\.", "", vin_)
    vin_ = re.sub(r"\s+\[.*?\](\<BR\>|\<br\>)", "", vin_)
    vin_ = re.sub(r"\s+VAGGA (I[VX]|V*?I{0,3})\..*?\.", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|<b>|</b>|</span>|&nbsnbsp;|&nbsp;|&#8216;)", "", vin_)
    vin_ = re.sub(r"(<BR>|<br>)", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"\n%\n", "%", vin_)
    vin_ = re.sub(r"(\w)-%", r"\1"+"&", vin_)
    vin_ = re.sub(r"&{2,}", "&", vin_)#これ特に要らない気もするけど、とりあえず残す。
    vin_ = re.sub(r"(\w)-\n", r"\1"+"#", vin_)# -改行 は # でとりあえず置き換えておく)
    vin_ = re.sub(r"\n", " \n", vin_)
    text_for_count = re.sub(r"%", " %", vin_)
    text_for_search = re.sub(r"[%&#\n]", "", text_for_count)
    return text_for_count, text_for_search


def Sn(text_for_search):
    pre_long = len(text_for_search)
    verse = []
    J_verse_start = array("I")
    J_verse_end = []
    Jataka = r"\d{1,4}\. .*?\|\|.*?\|\|"
    A = re.finditer(Jataka, text_for_search)
    for text in A:
        J_verse_start.append(text.start())#韻文の開始位置を保存しておく
        J_verse_end.append(text.end())
        if text.group(0) != "":
            verse.append([text.group(0)])
        verse_long = len(text_for_search[text.start(): text.end()])
        text_for_search = text_for_search[0: text.start()] + "."*verse_long + text_for_search[text.end():]
    new_Ja = "Sn_.txt"
    write_text_file(new_Ja, text_for_search)

    new_bin = "Sn_verse_start_point.bin"
    write_bin_file(new_bin, J_verse_start)

    new_verse = "Sn_verse.csv"
    write_csv_file(new_verse, verse)

def Ap_make(text = "Ap"):
    vin_ = download(text_dict["Ap.txt"])
    htm_make(text, copy.deepcopy(vin_))
    vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
    vin_ = re.sub(r"\r\n", "\n", vin_)#これが大事な一行になる
    vin_ = re.sub(r"\[page(.|\s)*?\]", "%", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", vin_)
    vin_ = re.sub(r"\((.|\s).*?\d\)", "", vin_)
    vin_ = re.sub(r"\[\d.*?\]", "", vin_)#カッコで括られたセクションの名前のようなところを削除したい
    vin_ = re.sub(r"\s+\d{1,3}\. .*?VAGGA\.", "", vin_)#Jataka の ~ vagga っていうのを消したい
    vin_ = re.sub(r"\s+\[.*?\](\<BR\>|\<br\>)", "", vin_)
    vin_ = re.sub(r"\s+VAGGA (I[VX]|V*?I{0,3})\..*?\.", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"\. \. \.", "@", vin_)
    vin_ = re.sub(r"\*", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?\[.*?\](<BR>|<br>)", "", vin_)#Majjhimanikaya の数字のやつを消したい
    vin_ = re.sub(r"(?<=\n)\s+?(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin_ = re.sub(r"(?<=\n)\s+?(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\. \w*?\.\s{0,1}(?=(<BR>|<br>))", "", vin_)
    vin = re.sub(r"(?<=\n)\s+?.*?, ((C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}))\.\s{0,1}(?=(<BR>\n|<br>\n))", "", vin_)
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|&lt;|&gt;)", "", vin_)
    vin_ = re.sub(r"(\n\s{3,}.*?<BR>)(\n)(\S)", r"\1"+ "~\n" + r"\3", vin_)#apadanaは韻文単位で獲得したいため
    vin_ = re.sub(r"(?<=\n)_*?<BR>\n", "", vin_)
    vin_ = re.sub(r"(?<=\d) //", " //~", vin_)
    vin_ = re.sub(r"(<BR>|<br>)", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"\n%\n", "%", vin_)
    vin_ = re.sub(r"(\w)-%", r"\1"+"&", vin_)
    vin_ = re.sub(r"&{2,}", "&", vin_)#これ特に要らない気もするけど、とりあえず残す。
    vin_ = re.sub(r"(\w)\-\n", r"\1"+"#", vin_)# -改行 は # でとりあえず置き換えておく)
    vin_ = re.sub(r"\n", " \n", vin_)
    vin_ = re.sub(r"--", "@", vin_)#--pa--, --la-- が検索のときに入らないようにするだけ
    text_for_count = re.sub(r"%", " %", vin_)
    text_for_search = re.sub(r"[%&#\n]", "", text_for_count)
    return text_for_count, text_for_search


@process_print
def Theri_make(text = "Thi"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/therigou.htm"
    vin_ = download(url)
    text_body = re.sub(r"(\|\| Thī_)(.*?)( \|\|)", "<section id ='Thī_" + r"\2" + "'>" + r"\1"+r"\2"+r"\3" + "</section>", copy.deepcopy(vin_))

    write_text_file("Thi_.htm", text_body)

    vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
    vin_ = re.sub(r"\r\n", "\n", vin_)#これが大事な一行になる
    vin_ = re.sub(r"itthaṃ sudaṃ bhagavā Muttaṃ sikkhamānaṃ imāya<BR>\ngāthāya abhiṇhaṃ ovadati\. ||<BR>", "", vin_)
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"\[page(.|\s)*?\]", "%", vin_)#%page区切りは%で表す
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|</body>|</html>)", "", vin_)
    vin_ = re.sub(r"-<BR>\n", "", vin_)#Therigathaだとこれは必須になる
    vin_ = re.sub(r"%", "", vin_)
    vin_ = re.sub(r"^\s{2,}.*?$", "", vin_)
    vin_ = re.sub(r"(?<!\|)<BR>\n", "", vin_)#Therigathaだとこれは必須になる
    vin_ = re.sub(r"-\n", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"\r {1,}(?=|| Th)", "", vin_)
    vin_ = re.sub(r"\n\s{1,}\|\| Th", " || Th", vin_)
    vin_ = re.sub(r"(?<=\n)\s{2,}.*?\n", "", vin_)
    vin_ = re.sub(r"(?<=\n)gāthaṃ abhāsitthā ti\. \|\|\n", "", vin_)#Theriのみ使用
    vs = re.finditer(r"(\s|.)*? Thī_.*? \|\|", vin_)
    verse_set = []
    for v in vs:
        verse = v.group(0)
        verse = re.sub(r" \|\n", "|<BR>", verse)
        verse = re.sub(r"\n", "", verse)
        verse_set.append(verse)
    write_csv_file("Theri_.csv", verse_set, oneline=True)

@process_print
def Thera_make(text = "Th"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/theragou.htm"
    vin_ = download(url)
    vin_ = re.sub(r"\|\| 939 \|\|", "|| Th_939 ||", vin_)
    text_body = re.sub(r"(\|\| Th_)(.*?)( \|\|)", "<section id ='Th_" + r"\2" + "'>" + r"\1"+r"\2"+r"\3" + "</section>", copy.deepcopy(vin_))

    write_text_file("Th_.htm", text_body)

    vin_ = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", vin_)
    vin_ = re.sub(r"\r\n", "\n", vin_)#これが大事な一行になる
    vin_ = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", vin_)
    vin_ = re.sub(r"\[page(.|\s)*?\]", "", vin_)
    vin_ = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|</body>|</html>)", "", vin_)
    vin_ = re.sub(r"-<BR>\n", "", vin_)
    vin_ = re.sub(r"uddānaṃ:(.|\s).*?ti\.<BR>", "", vin_)
    vin_ = re.sub(r"( {4,})(.*?<BR>\n.*?)( {4,})(.*?\|\| Th_\*\d)", r"\2" + r"\4", vin_)
    vin_ = re.sub(r"-\n", "", vin_)
    vin_ = re.sub(r"\n{2,}", "\n", vin_)
    vin_ = re.sub(r"(?<=\n)abhāsittha\.<BR>", "", vin_)
    vin_ = re.sub(r"(?<=\n)abhāsitthā 'ti.<BR>", "", vin_)
    vin_ = re.sub(r"\n\s{1,}\|\| Th", " || Th", vin_)
    vin_ = re.sub(r"(?<=\n)\s{2,}.*?\n", "", vin_)
    vin_ = re.sub(r"(<BR>\n){2,}", "<BR>\n", vin_)# This code is needed for the typo of e-text itself
    vin_ = vin_[:-5] + " || Th_end ||"# To deal with the last verse
    vs = re.finditer(r"(\s|.)*? Th_.*? \|\|", vin_)
    verse_set = []
    for v in vs:
        verse = v.group(0)
        lines = verse.split("<BR>\n")#Delete nonsence line-changes; sometimes line-changes don't mean pada(s)-changes.
        changed_verse = ""
        for line in lines[1:]:
            if len(line) >= 30:
                changed_verse += line + " <BR>"
            else:
                changed_verse = changed_verse[:-4] + line + " <BR>"
        changed_verse = changed_verse[:-4]
        verse_set.append(changed_verse)
    write_csv_file("Thera_.csv", verse_set, oneline=True)

@process_print
def Cp_make(text = "Cp"):
    Cp_number = r"<b>Cp_.*</b>"
    Cp_vers = r"\d\s\|\|</b><BR>"
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/carpitou.htm"
    text = download(url)
    text_body = re.sub(r"(<b>)(Cp_.*?)(\.)(.*?)(</b>)", "<section id ='" + r"\2" + "_" + r"\4" + "'>" + r"\1"+r"\2"+r"\3"+r"\4"+r"\5" + "</section>", copy.deepcopy(text))

    write_text_file("Cp_.htm", text_body)

    Cp = re.finditer(Cp_number, text)
    Cp_list = [
        (Cp_index.start(), Cp_index.end()) 
        for Cp_index in Cp
        ]
    Cp_text = re.finditer(Cp_vers, text)
    Cp_text_list = [C.end() for C in Cp_text]
    result_list = [
        [text[Cp_list[j][0]: Cp_list[j][1]], text[Cp_list[j][1]+1: Cp_text_list[j]]] 
        for j in range(len(Cp_list))
        ]
    final_result = []
    for text in result_list:
        number = re.sub(r"(<b>|</b>)", "", text[0])
#        number = re.sub(r"_", " ", number)
        main = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", text[1])
        main = re.sub(r"(<sup>)(\d*)(</sup>)", "*"r"\2", main)
        main = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"red\">|</span>|<b>|</b>|&nbsp;|&#8216;|<BR>)", "", main)
        main = re.sub(r"\n", "<BR>", main)
        main.lstrip().rstrip()
        final_result.append([number, main])
    write_csv_file("Cp_.csv", final_result)

@process_print
def Vm_make(text = "Vv"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/vimvatou.htm"
    text = download(url)
    text_body = re.sub(r"(<b>)(Vv_.*?)(\d*?)(\[.*?\])(\.)(\d*?)(</b>)", "<section id='" + r"\2" + r"\3" + r"\4" + "_" + r"\6" + "'>".replace(".", "_") + r"\1"+r"\2"+r"\3"+r"\4"+r"\5"+r"\6"+r"\7" + "</section>" ,copy.deepcopy(text))

    write_text_file("Vm_.htm", text_body)

    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\[page.*?\].*?<BR>\n", "", text)
    text = re.sub(r"(?<=\n)\s*?<b>\d.*?<BR>\n", "", text)
#    text = re.sub(r"<b>.*?</b>", "", text)
    text = re.sub(r"<i>.*?</i>", "", text)
    text = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", text)
    start_point = re.finditer(r"<b>Vv.*?</b>", text)
    end_point = re.finditer(r"\d \|\|</b><BR>", text)
    start_points = [(n.start(), n.end()) for n in start_point]
    end_points = [n.end() for n in end_point]
    result = []
    for i in range(len(start_points)):
        number = text[start_points[i][0]: start_points[i][1]]
        main = text[start_points[i][1]+1: end_points[i]]
        number = number.replace("<b>", "").replace("</b>", "")
        main = re.sub(r"\[page.*?\].*?\n", "", main)
        main = re.sub(r"(<span class=\"red\"><sup>)(\d*)(</sup></span>)", "*"r"\2", main)
        main = re.sub(r"(<b>|</b>)", "", main)
        main = re.sub(r"<b>.*?</b>", "", main)
#        main = re.sub(r"<i>.*?</i>", "", main)
        main = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", main)
        main = re.sub(r"(<sup>)(\d*)(</sup>)", "*"r"\2", main)
        main = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"red\">|</span>|<b>|</b>|&nbsp;|&#8216;)", "", main)
        main = re.sub(r"^ ?.*?$", "", main)
        main = re.sub(r"(<BR>\n){2,}", "<BR>\n", main)
        if main[-4:] == "<BR>":
            main = main[:-4]
        result.append([number + "(Vv)", main.strip()])#(Vv, Vm のテキスト名をここに入力しておく)
    write_csv_file("Vm_.csv", result)

@process_print
def Pv_make(text = "Pv"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/petvatou.htm"
    text = download(url)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"(?<=48 Akkharukkhapetavatthu</b><BR>\r\n) ", "<b>Vv_IV,13[=48].1</b>", text)
    text_body = re.sub(r"(<b>)(Vv_.*?)(\d*?)(\[.*?\])(\.)(\d*?)(</b>)", "<section id='" + r"\2" + r"\3" + r"\4" + "_" + r"\6" + "'>" + r"\1"+r"\2"+r"\3"+r"\4"+r"\5"+r"\6"+r"\7" + "</section>" ,copy.deepcopy(text))

    write_text_file("Pv_.htm", text_body)

    text = re.sub(r"\[page.*?\].*?<BR>\n", "", text)
    text = re.sub(r"(?<=\n)\s*?<b>\d.*?<BR>\n", "", text)
#    text = re.sub(r"<b>.*?</b>", "", text)
    text = re.sub(r"<i>.*?</i>", "", text)
    start_point = re.finditer(r"<b>Vv.*?</b>", text)
    end_point = re.finditer(r"\d \|\|</b>.?<BR>", text)
    start_points = [(n.start(), n.end()) for n in start_point]
    end_points = [n.end() for n in end_point]
    result = []
    for i in range(len(start_points)):
        number = text[start_points[i][0]: start_points[i][1]]
        main = text[start_points[i][1]+1: end_points[i]]
        number = number.replace("<b>", "").replace("</b>", "")
        main = re.sub(r"(<span class=\"red\"><sup>)(\d*)(</sup></span>)", "*"r"\2", main)
        main = re.sub(r"(<b>|</b>)", "", main)
        main = re.sub(r"\[page.*?\].*?\n", "", main)
        main = re.sub(r"<b>.*?</b>", "", main)
    #    main = re.sub(r"<i>.*?</i>", "", main)
        main = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", main)
        main = re.sub(r"(<sup>)(\d*)(</sup>)", "*"r"\2", main)
        main = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"red\">|</span>|<b>|</b>|&nbsp;|&#8216;)", "", main)
        main = re.sub(r"^ ?.*?$", "", main)
        main = re.sub(r"(<BR>\n){2,}", "<BR>\n", main)
        if main[-4:] == "<BR>":
            main = main[:-4]
        result.append([number + "(Pv)", main.strip()])#(Vv, Vm のテキスト名をここに入力しておく)
    write_csv_file("Pv_.csv", result)

@process_print
def Dhp_make(name = "Dhp", targetter = r"\/\/ Dhp_.* \/\/<BR>"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/dhampdou.htm"
    text = download(url)
    text_body = re.sub(r"(\/\/ )(Dhp_.*)( \/\/)", "<section id='" + r"\2" + "'>" + r"\1" + r"\2" + r"\3" + "</section>", copy.deepcopy(text))

    write_text_file("Dhp_.htm", text_body)

    text = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", text)
    main = re.sub(r"\r\n", "\n", text)
    vers_number = re.findall(targetter, main)
    vers_number = [num.replace("<BR>", "").replace(" ", "").replace("/", "").replace("<b>", "") for num in vers_number]
    main = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", main)
    main = re.sub(r"<b>.*?</b>", "", main)
    main = re.sub(r"<i>.*?</i>", "", main)
    main = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", main)
    main = re.sub(r"<BR> ?.*?<BR>", "", main)
    main = re.sub(r"(<sup>)(\d*)(</sup>)", "*"r"\2", main)
    main = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"red\">|</span>|<b>|</b>|&nbsp;|&#8216;|<BR>|\[page 001\])", "", main)
    main = re.sub(r"^ ?.*?$", "", main)
    lines = main.split("\n")
    result_lines = [line for line in lines if line != "" and line[0] != " "]
    final_result = []
    vers_heap = ""
    for line in result_lines:
        if line[-2:] == "//":
            vers_heap += line
            final_result.append(vers_heap)
            vers_heap = ""
        else:
            vers_heap += line + "<BR>"
    out = zip(vers_number, final_result)
    print_out = [list(i) for i in out]
    write_csv_file("Dhp_.csv", print_out)

@process_print
def Bv_make(name = "Bv", targetter = r"\/\/ Bv_.* \/\/<BR>"):
    url = "http://gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit/2_sut/5_khudd/budvmsou.htm"
    text = download(url)
    text_body = re.sub(r"(\/\/ )(Bv_)(\d*?)(\.)(\d*?)( \/\/)", "<section id='" + r"\2" + r"\3" + "_" + r"\5" + "'>" + r"\1"+r"\2"+r"\3"+r"\4"+r"\5"+r"\6" + "</section>", copy.deepcopy(text))

    write_text_file("Bv_.htm", text_body)

    text = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", text)
    main = re.sub(r"\r\n", "\n", text)
    vers_number = re.findall(targetter, main)
    vers_number = [num.replace("<BR>", "").replace(" ", "").replace("/", "").replace("<b>", "") for num in vers_number]
    main = re.sub(r"(<span class=\"red\">)(\d*)(</span>)", "*"r"\2", main)
    main = re.sub(r"<b>.*?</b>", "", main)
    main = re.sub(r"<i>.*?</i>", "", main)
    main = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", main)
    main = re.sub(r"<BR> ?.*?<BR>", "", main)
    main = re.sub(r"(<sup>)(\d*)(</sup>)", "*"r"\2", main)
    main = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"red\">|</span>|<b>|</b>|&nbsp;|&#8216;|<BR>|\[page 001\])", "", main)
    main = re.sub(r"^ ?.*?$", "", main)
    lines = main.split("\n")
    result_lines = [line for line in lines if line != "" and line[0] != " "]
    final_result = []
    vers_heap = ""
    for line in result_lines:
        if line[-2:] == "//":
            vers_heap += line
            final_result.append(vers_heap)
            vers_heap = ""
        else:
            vers_heap += line + "<BR>"
    out = zip(vers_number, final_result)
    print_out = [list(i) for i in out]
    write_csv_file("Bv_.csv", print_out)

@process_print
def Sp_create(text = "Sp"):
    text_for_count, text_for_search = Sp_make(text)
    bin_maker(text_for_count, text_name = "Sp")
    new_text = "Sp_.txt"
    write_text_file(new_text, text_for_search)

@process_print
def Ap_create():
    text_for_count, text_for_search = Ap_make()
    bin_maker(text_for_count, "Ap")
    write_text_file("Ap_.txt", text_for_search)

@process_print
def Sn_create(text = "Sn", text_name = "Sn"):
    text_for_count, text_for_search = Sn_text_make(text)
    Sn(text_for_search)
    bin_maker(text_for_count, text_name)

@process_print
def J_create(text, text_number, text_name):
    text_for_count, text_for_search = text_make(text)
    Jataka(text_for_search, text_number)
    bin_maker(text_for_count, text_name)

# 例: text: "Vin_I.txt"
# 生成されるファイル:
#   static/Vin_I_.htm
#   static/Vin_I_.txt
#   static/Vin_I_index_.bin
#   static/Vin_I_line_.bin
#   static/Vin_I_page_.bin
@process_print
def text_create(text):
    text_for_count, text_for_search = text_make(text)
    name, extention = text.split(".")
    bin_maker(text_for_count, name)
    new_text = name + "_.txt"
    write_text_file(new_text, text_for_search)

if __name__ == "__main__":
    mainpart()
