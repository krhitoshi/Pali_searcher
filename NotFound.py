#!/usr/bin/env python
# coding: utf-8

import re
from array import array
import csv
import requests
import sys
import os
import copy
import functools
from concurrent import futures
from urllib.parse import urljoin

app_dir = os.path.abspath(os.path.dirname(__file__))
static_path = os.path.join(app_dir, "static")
html_cache_path = os.path.join(app_dir, "html_cache")
tmp_path = os.path.join(app_dir, "tmp")


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


text_dict = {
    "Vin_I": "2_pali/1_tipit/1_vin/vin1maou.htm",
    "Vin_II": "2_pali/1_tipit/1_vin/vin2cuou.htm",
    "Vin_III": "2_pali/1_tipit/1_vin/vin3s1ou.htm",
    "Vin_IV": "2_pali/1_tipit/1_vin/vin4s2ou.htm",
    "Vin_V": "2_pali/1_tipit/1_vin/vin5paou.htm",
    "DN_I": "2_pali/1_tipit/2_sut/1_digh/dighn1ou.htm",
    "DN_II": "2_pali/1_tipit/2_sut/1_digh/dighn2ou.htm",
    "DN_III": "2_pali/1_tipit/2_sut/1_digh/dighn3ou.htm",
    "MN_I": "2_pali/1_tipit/2_sut/2_majjh/majjn1ou.htm",
    "MN_II": "2_pali/1_tipit/2_sut/2_majjh/majjn2ou.htm",
    "MN_III": "2_pali/1_tipit/2_sut/2_majjh/majjn3ou.htm",
    "AN_I": "2_pali/1_tipit/2_sut/4_angu/angut1ou.htm",
    "AN_II": "2_pali/1_tipit/2_sut/4_angu/angut2ou.htm",
    "AN_III": "2_pali/1_tipit/2_sut/4_angu/angut3ou.htm",
    "AN_IV": "2_pali/1_tipit/2_sut/4_angu/angut4ou.htm",
    "AN_V": "2_pali/1_tipit/2_sut/4_angu/angut5ou.htm",
    "SN_I": "2_pali/1_tipit/2_sut/3_samyu/samyu1ou.htm",
    "SN_II": "2_pali/1_tipit/2_sut/3_samyu/samyu2ou.htm",
    "SN_III": "2_pali/1_tipit/2_sut/3_samyu/samyu3ou.htm",
    "SN_IV": "2_pali/1_tipit/2_sut/3_samyu/samyu4ou.htm",
    "SN_V": "2_pali/1_tipit/2_sut/3_samyu/samyu5ou.htm",
    "Ap": "2_pali/1_tipit/2_sut/5_khudd/apadanou.htm",
    "Khp": "2_pali/1_tipit/2_sut/5_khudd/khudp_ou.htm",
    "Dhp": "2_pali/1_tipit/2_sut/5_khudd/dhampdou.htm",
    "Sn": "2_pali/1_tipit/2_sut/5_khudd/sutnipou.htm",
    "Ud": "2_pali/1_tipit/2_sut/5_khudd/udana_ou.htm",
    "It": "2_pali/1_tipit/2_sut/5_khudd/itivutou.htm",
    "Vm": "2_pali/1_tipit/2_sut/5_khudd/vimvatou.htm",
    "Pv": "2_pali/1_tipit/2_sut/5_khudd/petvatou.htm",
    "Th": "2_pali/1_tipit/2_sut/5_khudd/theragou.htm",
    "Thi": "2_pali/1_tipit/2_sut/5_khudd/therigou.htm",
    "Nidd_I": "2_pali/1_tipit/2_sut/5_khudd/nidde1ou.htm",
    "Nidd_II": "2_pali/1_tipit/2_sut/5_khudd/nidde2ou.htm",
    "Bv": "2_pali/1_tipit/2_sut/5_khudd/budvmsou.htm",
    "Cp": "2_pali/1_tipit/2_sut/5_khudd/carpitou.htm",
    "Ja_1": "2_pali/1_tipit/2_sut/5_khudd/jatak1ou.htm",
    "Ja_2": "2_pali/1_tipit/2_sut/5_khudd/jatak2ou.htm",
    "Ja_3": "2_pali/1_tipit/2_sut/5_khudd/jatak3ou.htm",
    "Ja_4": "2_pali/1_tipit/2_sut/5_khudd/jatak4ou.htm",
    "Ja_5": "2_pali/1_tipit/2_sut/5_khudd/jatak5ou.htm",
    "Ja_6": "2_pali/1_tipit/2_sut/5_khudd/jatak6ou.htm",
    "Dhātuk": "2_pali/1_tipit/3_abh/dhatukou.htm",
    "Yam_I": "2_pali/1_tipit/3_abh/yamak_1ou.htm",
    "Yam_II": "2_pali/1_tipit/3_abh/yamak_2ou.htm",
    "Kv": "2_pali/1_tipit/3_abh/kathavou.htm",
    "Pugg": "2_pali/1_tipit/3_abh/pugpan_ou.htm",
    "Paṭis_I": "2_pali/1_tipit/2_sut/5_khudd/patis1ou.htm",
    "Paṭis_II": "2_pali/1_tipit/2_sut/5_khudd/patis2ou.htm",
    "Vibh": "2_pali/1_tipit/3_abh/vibhanou.htm",
    "Dhs": "2_pali/1_tipit/3_abh/dhamsgou.htm",
    "Mil": "2_pali/2_parcan/milindou.htm",
    "Vism": "2_pali/4_comm/buvismou.htm",
    "Sp_1": "2_pali/4_comm/samp_1ou.htm",
    "Sp_2": "2_pali/4_comm/samp_2ou.htm",
    "Sp_3": "2_pali/4_comm/samp_3ou.htm",
    "Sp_4": "2_pali/4_comm/samp_4ou.htm",
    "Sp_5": "2_pali/4_comm/samp_5ou.htm",
    "Sp_6": "2_pali/4_comm/samp_6ou.htm",
    "Sp_7": "2_pali/4_comm/samp_7ou.htm",
}


def static_file_path(file_name):
    global static_path
    return os.path.join(static_path, file_name)


# html_cache_path にHTMLファイルがあればそれを利用する
# ダウンロードしたHTMLの改行コードは CRLF
# $ file html_cache/vin1maou.htm
# html_cache/vin1maou.htm: HTML document text, Unicode text, UTF-8 text, with very long lines (333), with CRLF line terminators
def download(path):
    base = "https://gretil.sub.uni-goettingen.de/gretil/"
    url = urljoin(base, path)
    file_name = os.path.basename(path)
    path = os.path.join(html_cache_path, file_name)

    if os.path.exists(path):
        # 改行コードを保ったまま開く
        with open(path, "r", encoding="utf-8", newline="") as f:
            result = f.read()
    else:
        print(f"Downloading {url}...")
        response = requests.get(url)
        response.encoding = "utf-8"
        result = response.text
        # 改行コードを保ったまま保存する
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(result)
    return result

# plain text のファイルを保存する
def write_text_file(file_name, content, newline=None):
    with open(static_file_path(file_name), "w", encoding="utf-8", newline=newline) as f:
        f.write(content)

# CSV ファイルを保存する
def write_csv_file(file_name, data, oneline=False):
    with open(static_file_path(file_name), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if oneline:
            # 単一行のCSV
            writer.writerow(data)
        else:
            writer.writerows(data)

# バイナリファイルを保存する
def write_bin_file(file_name, data):
    with open(static_file_path(file_name), "wb") as f:
        data.tofile(f)


def main_proc(text_name=None):
    print(f"Static file directory: {static_path}")
    if text_name is not None:
        print(f"Processing '{text_name}'...")
        url = text_dict[text_name]
        print(f"URL: {url}")
        text_requests((text_name, url))
        print(f"Done with '{text_name}'")
    else:
        print("### Start ###")
        print(" ")
        with futures.ThreadPoolExecutor() as executor:
            res = executor.map(text_requests, text_dict.items())
            list(res)
        print("\n\n#### All texts were installed" + ": Process 100 %"+  "*" * (100 // 5))#八百長


Sp_flag = 0
def text_requests(text_dict_item):
    print(text_dict_item)
    global Sp_flag
    name, url = text_dict_item
    if name == "Th":
        Thera_make(url)
    elif name == "Thi":
        Theri_make(url)
    elif name == "Ap":
        Ap_create()
    elif name == "Sn":
        Sn_create()
    elif name in {"Cp", "Vm", "Pv", "Dhp", "Bv"}:
        exec("{}_make()".format(name))
    elif name in ["Ja_{}".format(i) for i in range(1, 7)]:
        J_create(name, url)
    elif name in ["Sp_{}".format(i) for i in range(1,8)]:
        if Sp_flag == 1:
            pass
        else:
            Sp_flag = 1
            Sp_create()
    else:
        create_data_files(name, url)


# デコレータを一旦無効にする
# def process_print(func):
#     @functools.wraps(func)
#     def printer(*args, **kwargs):
#         proc_per = ( len(os.listdir(static_path)) * 100 // 268 )
#         if args:
#             text_name = args[0].split(".")[0]
#             txt_path = static_file_path(text_name + "_.txt")
#             htm_path = static_file_path(text_name + "_.htm")
#             if not(os.path.exists(txt_path)) and not(os.path.exists(htm_path)):
#                 print("\r#### Preparing {:14}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end = "")
#                 result = func(*args, **kwargs)
#                 print("\r#### Done with {:14}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
#                 return result
#             else:
#                 print("\r#### Pass {:19}: ".format(text_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end = "")
#         else:
#             file_name = func.__name__.split("_")[0]
#             txt_path = static_file_path(file_name + "_.txt")
#             csv_path = static_file_path(file_name + "_.csv")
#             htm_path = static_file_path(file_name + "_.htm")
#             if not(os.path.exists(txt_path)) and not(os.path.exists(csv_path)) and not(os.path.exists(htm_path)):
#                 print("\r#### Preparing {:14}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
#                 result = func(*args, **kwargs)
#                 print("\r#### Done with {:14}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
#                 return result
#             else:
#                 print("\r#### Pass {:19}: ".format(file_name) + "Process {:3} %".format(proc_per) + "*" * (proc_per // 5) + "_" * (20 - (proc_per // 5)), end="")
#     return printer


def create_txt_file(name, text_for_count):
    file_name = name + "_.txt"
    content = generate_txt_file_content(text_for_count)
    write_text_file(file_name, content)

def create_htm_file_base(text_name, html, pattern, replace):
    file_name = text_name + "_.htm"
    new_html = copy.deepcopy(html)
    contents = re.sub(pattern, replace, new_html)
    write_text_file(file_name, contents)

# 例: text_name: "Vin_I"
# 生成されるファイル:
#   static/Vin_I_.htm
# ページ表記に section タグを追加する
# <section id ='223'>[page 223]</section>
def create_htm_file(text_name, html):
    pattern = r"(\[page )(\d{1,4})(\])"
    replace = """<section id ='""" + r"\2" + """'>""" + r"\1" + r"\2" + r"\3" + """</section>"""
    create_htm_file_base(text_name, html, pattern, replace)

def preprocess_html(content, text_name):
    res = copy.deepcopy(content)
    # `[page` の直前までを削除する `[page` という文字列自体はマッチしない (先読み)
    res = re.sub(r"<!DOCTYPE html>(.|\s)*?(?=\[page)", "", res)
    # 改行コードをCRLFからLFに変換する
    res = re.sub(r"\r\n", "\n", res)#これが大事な一行になる

    if text_name in {"SN_II", "SN_III", "SN_IV", "SN_V"}:
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=CHAPTER)", "", res)
    elif text_name == "SN_I":
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=<b>SN_1)", "", res)
    elif text_name == "Khp":
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=Buddhaṃ)", "", res)
    elif text_name == "Nidd_I":
        res = re.sub(r"""(?<=page 001\])(.|\s)*?Part I""", "", res)
    elif text_name == "Nidd_II":
        res = re.sub(r"""(?<=page 001\])(.|\s)*?Vatthugāthā\.""", "", res)
    elif text_name == "Ja_1":
        # Ja_1, Ja_2 などなのでここは実際に実行されることはない
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=JaNi)", "", res)
    elif text_name == "Paṭis_II":
        res = re.sub(r"""(?<=page 001\])(.|\s)*?INDRIYAKATHĀ</span><BR>""", "", res)
    elif text_name == "Dhs":
        res = re.sub(r"(?<=page 001\])(.|\s)*?{MĀTIKĀ\.}<br>", "", res)
    elif text_name == "Dhātuk":
        res = re.sub(r"(?<=page 001\])(.|\s)*?BUDDHASSA<BR>", "", res)
    elif text_name == "Mil":
        res = re.sub(r"(?<=page 001\])(.|\s)*?TASSA BHAGAVATO ARAHATO SAMMĀSAMBUDDHASSA\.<BR>", "", res)
    elif text_name == "Vism":
        res = re.sub(r"(?<=page 001\])(.|\s)*?NIDĀNĀDIKATHĀ<BR>", "", res)
    elif "&nbsp;" in res[:1000] or text_name in {"Yam_I", "Yam_II", "Pugg", "Paṭis_I"}:
        # Yam_I, Yam_II, Pugg, Paṭis_I 以外は実際には実行されることはない
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=\n(\w|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\w))", "", res)
    else:
        # 基本的な処理: page 001 から実際の本文が始まるまでの部分を削除する
        # 改行直後に空文字5文字の後に行数をカウントするための本文が始まる
        res = re.sub(r"(?<=page 001\])(.|\s)*?(?=\n     \S)", "", res)

    # ページ表記 `[page ddd]` を `%` に置換する
    res = re.sub(r"\[page(.|\s)*?\]", "%", res)

    res = re.sub(r"<span class=\"red\">\d*?</span>", "", res)
    res = re.sub(r"\((.|\s).*?\d\)", "", res)
    res = re.sub(r"\[\d.*?\]", "", res)#カッコで括られたセクションの名前のようなところを削除したい
    res = re.sub(r"\s+\d{1,3}\. .*?VAGGA\.", "", res)#Jataka の ~ vagga っていうのを消したい
    res = re.sub(r"\s+\[.*?\](\<BR\>|\<br\>)", "", res)
    res = re.sub(r"\s+VAGGA (I[VX]|V*?I{0,3})\..*?\.", "", res)
    res = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", res)
    res = re.sub(r"(<span class=\"large\">)(.|\s)*?(</span>)", "", res)
    res = re.sub(r"\. \. \.", "@", res)
    res = re.sub(r"(?<=\n)\s+?\[.*?\](<BR>|<br>)", "", res)#Majjhimanikaya の数字のやつを消したい
    res = re.sub(r"(?<=\n)\s+?(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\.\s{0,1}(?=(<BR>|<br>))", "", res)
    res = re.sub(r"(?<=\n)\s+?(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}|I{1,3})\. \w*?\.\s{0,1}(?=(<BR>|<br>))", "", res)
    res = re.sub(r"(?<=\n)\s+?.*?, ((C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[VX]|V?I{0,3}))\.\s{0,1}(?=(<BR>\n|<br>\n))", "", res)
    res = re.sub(r"(<i>(.|\s)*?</i>|<span class=\"(red|blue)\">|</span>|<b>|</b>|&nbsnbsp;|&nbsp;|&#8216;|&lt;|&gt;|_{3,})", "", res)
    res = re.sub(r"(<BR>|<br>)", "", res)
    res = re.sub(r"\n{2,}", "\n", res)
    res = re.sub(r"\n%\n", "%", res)
    res = re.sub(r"(\w)-%", r"\1"+"&", res)
    res = re.sub(r"&{2,}", "&", res)#これ特に要らない気もするけど、とりあえず残す。
    res = re.sub(r"(\w)\-\n", r"\1"+"#", res)# -改行 は # でとりあえず置き換えておく)
    res = re.sub(r"\n", " \n", res)
    res = re.sub(r"--", "@", res)#--pa--, --la-- が検索のときに入らないようにするだけ
    res = re.sub(r"%", " %", res)
    # TODO: ページ末のHTMLタグを削除する `</body></html>`

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, text_name + "_.pre")
    write_text_file(path, res)

    return res


def generate_txt_file_content(text_for_count):
    return re.sub(r"[%&#\n]", "", text_for_count)


# 例: text_name: "Vin_I"
# 生成されるファイル:
#   static/Vin_I_index_.bin
#   static/Vin_I_line_.bin
#   static/Vin_I_page_.bin
def create_bin_files(text_for_count, text_name):
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
            create_htm_file("Sp_1", vin_)
            vin_ = re.sub(r"(?<=page 001\])(.|\s)*?sammāsambuddhassa\.<br>", "", vin_)
        elif i == 2:
            create_htm_file("Sp_2", vin_)
            start, end = re.search(r"(?<=\d\])(.|\s)*?II<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
#            vin_ = re.sub(r"(?<=\d\])(.|\s)*?II<br>", "", vin_)
        elif i == 3:
            create_htm_file("Sp_3", vin_)
            start, end = re.search(r"(?<=\d\])(.|\s)*?SAṄGHĀDISESA I-XIII<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 4:
            create_htm_file("Sp_4", vin_)
            start, end = re.search(r"""(?<=\d\])(.|\s)*?SAMBUDDHASSA\.<span class="red"><sup>1</sup></span><br>""", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
            vin_ += "%"#For page 950 is not exist.
        elif i == 5:
            create_htm_file("Sp_5", vin_)
            start, end = re.search(r"(?<=\d\])(.|\s)*?SAMANTAPĀSĀDIKĀ<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 6:
            create_htm_file("Sp_6", vin_)
            start, end = re.search(r"(?<=\d\])(.|\s)*?KAMMAKKHANDHAKA-VAṆṆANĀ<br>", vin_).span()
            vin_ = vin_[:start] + vin_[end:]
        elif i == 7:
            create_htm_file("Sp_7", vin_)
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


def create_jataka_files(txt_file_content, text_number):
    pre_long = len(txt_file_content)
    verse = []
    J_verse_start = array("I")
    J_verse_end = []
    Jataka = r"Ja\_(.|\s)*?\da?b? \|\|"
    A = re.finditer(Jataka, txt_file_content)
    for text in A:
        J_verse_start.append(text.start())#keep startpoints of verses
        J_verse_end.append(text.end())
        verse.append([text.group(0)])
        verse_long = len(txt_file_content[text.start(): text.end()])
        txt_file_content = txt_file_content[0: text.start()] + "." * verse_long + txt_file_content[text.end():]
    new_Ja = "Ja_" + str(text_number) + "_.txt"
    write_text_file(new_Ja, txt_file_content)

    new_bin = "J_" + str(text_number) + "_start_point_.bin"
    write_bin_file(new_bin, J_verse_start)

    new_verse = "J_" + str(text_number) + ".csv"
    write_csv_file(new_verse, verse)

def Sn_text_make(text = "Sn"):
    vin_ = download(text_dict["Sn"])
    create_htm_file(text, vin_)
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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Sn_.pre")
    write_text_file(path, text_for_count)

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


def Ap_make():
    text_name = "Ap"
    url = text_dict[text_name]
    vin_ = download(url)
    create_htm_file(text_name, vin_)
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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Ap_.pre")
    write_text_file(path, text_for_count)

    text_for_search = re.sub(r"[%&#\n]", "", text_for_count)
    return text_for_count, text_for_search


#@process_print
def Theri_make(url):
    text_name = "Thi"
    vin_ = download(url)
    create_htm_file_base(text_name, vin_, r"(\|\| Thī_)(.*?)( \|\|)",
                  "<section id ='Thī_" + r"\2" + "'>" + r"\1" +r"\2" +r"\3" + "</section>")

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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Thi_.pre")
    write_text_file(path, vin_)

    vs = re.finditer(r"(\s|.)*? Thī_.*? \|\|", vin_)
    verse_set = []
    for v in vs:
        verse = v.group(0)
        verse = re.sub(r" \|\n", "|<BR>", verse)
        verse = re.sub(r"\n", "", verse)
        verse_set.append(verse)
    write_csv_file("Theri_.csv", verse_set, oneline=True)


#@process_print
def Thera_make(url):
    text_name = "Th"
    vin_ = download(url)
    vin_ = re.sub(r"\|\| 939 \|\|", "|| Th_939 ||", vin_)

    create_htm_file_base(text_name, vin_, r"(\|\| Th_)(.*?)( \|\|)",
                  "<section id ='Th_" + r"\2" + "'>" + r"\1" +r"\2" +r"\3" + "</section>")

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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Th_.pre")
    write_text_file(path, vin_)

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


#@process_print
def Cp_make():
    text_name = "Cp"
    Cp_number = r"<b>Cp_.*</b>"
    Cp_vers = r"\d\s\|\|</b><BR>"
    url = text_dict[text_name]
    text = download(url)

    # 確認用に加工前のデータを tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Cp_.pre")
    write_text_file(path, text)

    create_htm_file_base(text_name, text, r"(<b>)(Cp_.*?)(\.)(.*?)(</b>)",
                  "<section id ='" + r"\2" + "_" + r"\4" + "'>" + r"\1" +r"\2" +r"\3" +r"\4" +r"\5" + "</section>")

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


#@process_print
def Vm_make():
    text_name = "Vm"
    url = text_dict[text_name]
    text = download(url)

    create_htm_file_base(text_name, text,
                  r"(<b>)(Vv_.*?)(\d*?)(\[.*?\])(\.)(\d*?)(</b>)",
                  "<section id='" + r"\2" + r"\3" + r"\4" + "_" + r"\6" + "'>".replace(".", "_") + r"\1" +r"\2" +r"\3" +r"\4" +r"\5" +r"\6" +r"\7" + "</section>")

    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\[page.*?\].*?<BR>\n", "", text)
    text = re.sub(r"(?<=\n)\s*?<b>\d.*?<BR>\n", "", text)
#    text = re.sub(r"<b>.*?</b>", "", text)
    text = re.sub(r"<i>.*?</i>", "", text)
    text = re.sub(r"(<span class=\"red\">)(.|\s)*?(</span>)", "", text)

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Vm_.pre")
    write_text_file(path, text)

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


#@process_print
def Pv_make():
    text_name = "Pv"
    url = text_dict[text_name]
    text = download(url)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"(?<=48 Akkharukkhapetavatthu</b><BR>\r\n) ", "<b>Vv_IV,13[=48].1</b>", text)

    create_htm_file_base(text_name, text,
                  r"(<b>)(Vv_.*?)(\d*?)(\[.*?\])(\.)(\d*?)(</b>)",
                  "<section id='" + r"\2" + r"\3" + r"\4" + "_" + r"\6" + "'>" + r"\1" +r"\2" +r"\3" +r"\4" +r"\5" +r"\6" +r"\7" + "</section>")

    text = re.sub(r"\[page.*?\].*?<BR>\n", "", text)
    text = re.sub(r"(?<=\n)\s*?<b>\d.*?<BR>\n", "", text)
#    text = re.sub(r"<b>.*?</b>", "", text)
    text = re.sub(r"<i>.*?</i>", "", text)

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Pv_.pre")
    write_text_file(path, text)

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


#@process_print
def Dhp_make(targetter = r"\/\/ Dhp_.* \/\/<BR>"):
    text_name = "Dhp"
    url = text_dict[text_name]
    text = download(url)

    create_htm_file_base(text_name, text, r"(\/\/ )(Dhp_.*)( \/\/)",
                  "<section id='" + r"\2" + "'>" + r"\1" + r"\2" + r"\3" + "</section>")

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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Dhp_.pre")
    write_text_file(path, main)

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


#@process_print
def Bv_make(targetter = r"\/\/ Bv_.* \/\/<BR>"):
    text_name = "Bv"
    url = text_dict[text_name]
    text = download(url)

    create_htm_file_base(text_name, text, r"(\/\/ )(Bv_)(\d*?)(\.)(\d*?)( \/\/)",
                  "<section id='" + r"\2" + r"\3" + "_" + r"\5" + "'>" + r"\1" +r"\2" +r"\3" +r"\4" +r"\5" +r"\6" + "</section>")

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

    # 確認用に中間生成物を tmp ディレクトリに保存する
    path = os.path.join(tmp_path, "Bv_.pre")
    write_text_file(path, main)

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


#@process_print
def Sp_create(text = "Sp"):
    text_for_count, text_for_search = Sp_make(text)
    create_bin_files(text_for_count, text_name ="Sp")
    new_text = "Sp_.txt"
    write_text_file(new_text, text_for_search)


#@process_print
def Ap_create():
    text_for_count, text_for_search = Ap_make()
    create_bin_files(text_for_count, "Ap")
    write_text_file("Ap_.txt", text_for_search)


#@process_print
def Sn_create(text = "Sn", text_name = "Sn"):
    text_for_count, text_for_search = Sn_text_make(text)
    Sn(text_for_search)
    create_bin_files(text_for_count, text_name)


#@process_print
def J_create(text_name, url):
    text_number = text_name[-1]
    html = download(url)
    create_htm_file(text_name, html)
    text_for_count = preprocess_html(html, text_name)
    txt_file_content = generate_txt_file_content(text_for_count)
    create_jataka_files(txt_file_content, text_number)
    create_bin_files(text_for_count, text_name)

# 対象PTSテキスト:
# Vin_I, Vin_II, Vin_III, Vin_IV, Vin_V, DN_II, DN_III, DN_I,
# MN_I, MN_II, MN_III, AN_I, AN_II, AN_III, AN_IV, AN_V,
# SN_I, SN_II, SN_III, SN_IV, SN_V, Khp, Ud, It,
# Nidd_I, Nidd_II, Dhātuk, Yam_I, Yam_II, Kv, Pugg, Paṭis_I, Paṭis_II, Vibh,
# Dhs, Mil, Vism
# 例: text_name: "Vin_I"
# 生成されるファイル:
#   static/Vin_I_.htm
#   static/Vin_I_.txt
#   static/Vin_I_index_.bin
#   static/Vin_I_line_.bin
#   static/Vin_I_page_.bin
#@process_print
def create_data_files(text_name, url):
    html = download(url)
    create_htm_file(text_name, html)
    text_for_count = preprocess_html(html, text_name)
    create_bin_files(text_for_count, text_name)
    create_txt_file(text_name, text_for_count)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        text_name = sys.argv[1]
    else:
        text_name = None
    main_proc(text_name)
