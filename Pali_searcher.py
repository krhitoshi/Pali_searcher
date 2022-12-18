#!/usr/bin/env python3
# coding: utf-8
from flask import Flask, make_response, request, render_template, session, send_from_directory
from array import array
import io
import re
import csv
import os
import webbrowser
import threading
import sys

app_dir = os.path.abspath(os.path.dirname(__file__))
# + でパスを作成している箇所が多くあるため文字列末尾に '/' を追加している
# TODO: os.path.join に置き換える
static_path = os.path.join(app_dir, "static/")
templates_path = os.path.join(app_dir, "templates")

# print("app_dir: {}".format(app_dir))
# print("static_path: {}".format(static_path))
# print("templates_path: {}".format(templates_path))


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


app = Flask(__name__, root_path=os.path.dirname(sys.argv[0]),
            static_folder=static_path, template_folder=templates_path)


class PaliText:
    __slots__ = ("name", "start_page", "end_page", "start_line", "end_line", "text")

    # 環境変数 STATIC_URL が設定されていればベースとなるURLを変更する
    static_url = os.environ.get("STATIC_URL", "static/")

    def __init__(self, name, start_page, start_line, end_page, end_line, text):
        self.name = name
        self.start_page = start_page
        self.end_page = end_page
        self.start_line = start_line
        self.end_line = end_line
        self.text = text

    def __link_url(self):
        sharp = ""
        if self.start_page <= 9:
            sharp = "00" + str(self.start_page)
        elif self.start_page <= 99:
            sharp = "0" + str(self.start_page)
        else:
            sharp = str(self.start_page)

        href_name = ""
        if self.name[:2] == "J_":
            pre = self.name[:2]
            aft = self.name[2:]
            roman = ["I", "II", "III", "IV", "V", "VI"]
            vol = roman.index(aft) + 1
            href_name = "Ja_" + str(vol)

        elif self.name == "Sp":
            if self.start_page <= 284:
                href_name = "Sp_1"
            elif self.start_page <= 516:
                href_name = "Sp_2"
            elif self.start_page <= 734:
                href_name = "Sp_3"
            elif self.start_page <= 950:
                href_name = "Sp_4"
            elif self.start_page <= 1154:
                href_name = "Sp_5"
            elif self.start_page <= 1300:
                href_name = "Sp_6"
            else:
                href_name = "Sp_7"
        else:
            href_name = self.name

        return PaliText.static_url + href_name + "_.htm#" + sharp

    # 結果表示のためのテキスト形成
    def output(self):
        result = ""
        if self.name == "Ap":
            self.text = re.sub(r"~", "", self.text)

        href = self.__link_url()

        if self.name[:2] == "Ja":
            roman = ["I", "II", "III", "IV", "V", "VI"]
            self.name = self.name[:3] + roman[int(self.name[3]) - 1]

        if self.start_line == self.end_line:
            if self.start_page == 1:
                self.start_line -= 1
            result = """<a href = {} target="_blank">""".format(href) + "{} {}.{}</a>: {}".format(self.name, self.start_page, self.start_line, self.text)
        elif self.start_page == self.end_page:
            if self.start_page == 1:
                self.start_line -= 1
                self.end_line -= 1
            result = """<a href = {} target="_blank">""".format(href) +"{} {}.{}-{}</a>: {}".format(self.name, self.start_page, self.start_line, self.end_line, self.text)
        else:
            if self.start_page == 1:
                self.start_line -= 1
                self.end_line -= 1
            result = """<a href = {} target="_blank">""".format(href) +"{} {}.{}-{}.{}</a>: {}".format(self.name, self.start_page, self.start_line, self.end_page, self.end_line, self.text)
        return result


class PaliVerse:
    def __init__(self, text_number, text, text_name, text_id = ""):
        self.name = self
        self.text_number = text_number
        self.text = text
        self.text_name = text_name
        self.text_id = text_id

    def output(self):
        if self.text == "Vm" or self.text == "Pv":
            self.text_id = self.text_number[:-4]
        if self.text_id == "":
            self.text_id = self.text_number
            href = "static/" + self.text_name + "_.htm#" + self.text_id.replace(".", "_")
        return """<a href = {} target="_blank">""".format(href) + "{}</a>: {}".format(self.text_number, self.text)


def kh_changer(word):
    Not_change_flag = 0
    KH_list =  ["A", "I", "U", "R" ,"L", "M", "G", "J", "T", "D", "N", "z", "S", "H"]
    NC_list = ["ā", "ī", "ū", "ṛ" ,"ḷ", "ṃ", "ṅ", "ñ", "ṭ", "ḍ", "ṇ", "ś", "ṣ", "ḥ"]
    result_word = ""
    for i in word:
        if i == "{":
            Not_change_flag = 1
        elif i == "}":
            Not_change_flag = 0
        else:
            for j in range(len(KH_list)):
                if i == KH_list[j] and Not_change_flag == 0:
                    result_word += NC_list[j]
                    break
            else:
                result_word += i
    return result_word


def opener(name, index, line, page):     
    #この関数の前に、中身が空の page, line, index array を作る必要があり
    index_bin = static_path + name + "_index_.bin"
    line_bin = static_path + name + "_page_.bin"
    page_bin = static_path + name + "_line_.bin"
    # I made mistake when I named these bin files; I try to re-name here. 
    f1 = open(index_bin, "rb")
    try:
        index.fromfile(f1, 10**6)
    except EOFError:
        pass
    f1.close()
    f2 = open(line_bin, "rb")
    try:
        line.fromfile(f2, 10**6)
    except EOFError:
        pass
    f2.close()
    f3 = open(page_bin, "rb")
    try:
        page.fromfile(f3, 10**6)
    except EOFError:
        pass
    f3.close()
    data = open(static_path + name + "_.txt", "r", encoding="utf-8")
    text_for_search = data.read()
    return text_for_search


def jataka_opener(number, index, line, page, start_point):
    name = "Ja_{}".format(number)
    index_bin = static_path + name + "_index_.bin"
    line_bin = static_path + name + "_line_.bin"
    page_bin = static_path + name + "_page_.bin"
    start_bin = static_path + "J_" + str(number) + "_start_point_.bin"
    # I made mistake when I named these bin files; I try to re-name here. 
    f1 = open(index_bin, "rb")
    try:
        index.fromfile(f1, 10**6)
    except EOFError:
        pass
    f1.close()
    f2 = open(line_bin, "rb")
    try:
        line.fromfile(f2, 10**6)
    except EOFError:
        pass
    f2.close()
    f3 = open(page_bin, "rb")
    try:
        page.fromfile(f3, 10**6)
    except EOFError:
        pass
    f3.close()
    f4 = open(start_bin, "rb")
    try:
        start_point.fromfile(f4, 1000)
    except EOFError:
        pass
    f4.close()


def sn_opener(index, line, page, start_point):
    index_bin = static_path + "Sn_index_.bin"
    line_bin = static_path + "Sn_line_.bin"
    page_bin = static_path + "Sn_page_.bin"
    start_bin = static_path + "Sn_verse_start_point.bin"
    f1 = open(index_bin, "rb")
    try:
        index.fromfile(f1, 10**6)
    except EOFError:
        pass
    f1.close()
    f2 = open(line_bin, "rb")
    try:
        line.fromfile(f2, 10**6)
    except EOFError:
        pass
    f2.close()
    f3 = open(page_bin, "rb")
    try:
        page.fromfile(f3, 10**6)
    except EOFError:
        pass
    f3.close()
    f4 = open(start_bin, "rb")
    try:
        start_point.fromfile(f4, 1000)
    except EOFError:
        pass
    f4.close()


def pali_word_searcher(s, text_for_search):
    matchs = re.finditer(s, text_for_search, re.IGNORECASE)
    li = [i.start() for i in matchs]
    return li


# text[n] が含まれる sentence の最初の文字のインデックスを返す
def pali_pre_space(n, text, breakpoint={".", ":", "?", "!", "|", "@", ". ", ","}):#モノによっては breakpoint を適時変更してやる必要がある
    while n - 1 != 0 and not(text[n] in breakpoint):
        n = n - 1
    return n + 2 #コンマなどの後ろには基本半角スペースがあるため


# text[n] が含まれる sentence の最後の文字のインデックスを返す
def pali_pos_space(n, text, breakpoint={".", ":", "?", "!", "|", "@", ". ", ","}):
    while (n+1 != len(text) - 1) and not(text[n] in breakpoint):
        n = n + 1
    return n + 1
    #この上で、どこまで出力するのかを決定する。あんまり長いとよくないので、いい感じにしないといけない。


# テキストインデックス(テキスト内の位置)から実際のPTS書籍におけるページ番号,行番号を取得するためのインデックスを取得する
def page_line_search(target, index, start_index):#start は、index[x] の x に相当する汎用インデックス番号を定める
    for i in range(start_index-1, len(index)):#このスタートは単純増加していく汎用インデックス番号
        try:
            index[i+1]
        except IndexError:
            return i
        if (index[i] <= target) and (index[i+1] > target):
            return i


def text_maker(word, BR="0", text_name="", break_point={".", ":", "?", "!", "|", "@", ". ", ","}):
    results = []
    index = array("I"); page = array("I"); line = array("I")
    text = opener(text_name, index, page, line)
    start_index = 0
    start_point_list = pali_word_searcher(word, text)
    for start_point in start_point_list:
        if text_name:#あとで Apadanaの場合などに関して場合分けを考える
            sentence_start = pali_pre_space(start_point, text, break_point)
            sentence_end = pali_pos_space(start_point, text, break_point)
            start_index = page_line_search(sentence_start, index, start_index)
            end_index = page_line_search(sentence_end, index, start_index)
            # キーワードにマッチした sentence
            searched_text = text[sentence_start: sentence_end]
            if BR == "1":
                new_searched_text = ""
                edges = [index[k] - sentence_start 
                         for k in range(start_index, end_index+1) 
                         if index[k] - sentence_start != 0]
                for j in range(len(searched_text)):
                    if j in edges:
                        new_searched_text +=  ("<BR>" + searched_text[j])
                    else:
                        new_searched_text += searched_text[j]
                new_searched_text = re.sub(r"(?<=\S)<BR>", "-<BR>", new_searched_text)
                searched_text = new_searched_text

        # ハイライト処理など
        searched_text = searched_text.replace("@", " . . . ")
        spaned = re.compile(r"(" + word + ")", re.IGNORECASE)
        searched_text = re.sub(spaned, """<span style="color:red">""" + r"\1" + "</span>", searched_text)

        start_page = page[start_index]
        start_line = line[start_index]
        end_page = page[end_index]
        end_line = line[end_index]
        result = PaliText(text_name, start_page, start_line, end_page, end_line,
                          searched_text)
        results.append(result)
    return results


def verse_text_searcher(text_name, searched):
    spaned = re.compile(r"(" + searched + ")", re.IGNORECASE)
    csvfile = open( static_path + text_name + "_.csv", "r", encoding="utf-8", newline="\n")
    lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
    result = [
        PaliVerse(line[0], 
        re.sub(spaned, """<span style="color:red">"""+ r"\1" +"</span>", line[1].lstrip().rstrip()), 
        text_name)
        for line in lines 
        if re.search(searched, re.sub(r"\*\d\d?|<BR>|<br>", "", line[1]), re.IGNORECASE)
            ]
    csvfile.close()
    return result


def th_searcher(text, searched):
    if text == "Th":
        csvfile = open(static_path + "Thera_.csv", "r", encoding="utf-8", newline="\n")
    else:
        csvfile = open(static_path + "Theri_.csv", "r", encoding="utf-8", newline="\n")
    reader = csv.reader(csvfile)
    lines = list(list(reader)[0])

    spaned = re.compile(r"(" + searched + ")", re.IGNORECASE)
    result = [
        PaliVerse(
            re.sub(r"(^.*?\|\| )(Th.*?)( \|\|.*?$)", r"\2", line), 
            re.sub(spaned, """<span style="color:red">"""+ r"\1" + "</span>", line.lstrip().rstrip()), 
            text 
            )
        for line in lines
        if re.search(searched, re.sub(r"\*\d\d?|<BR>|<br>", "", line), re.IGNORECASE)
        ]
    csvfile.close()
    return result


def search_keyword_jataka(keyword, BR):
    result = []
    for num in range(1, 7):
        page = array("I");
        line_start = array("I");
        index = array("I");
        verse_start_point = array("I")
        jataka_opener(num, index, line_start, page, verse_start_point)
        roman_number = ["I", "II", "III", "IV", "V", "VI"]
        csvfile = open(static_path + "J_{}.csv".format(num), "r",
                       encoding="utf-8", newline="\n")
        lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
        i = 0
        start_index = 0
        for line in lines:
            if re.search(keyword, line[0]):
                try:
                    start = verse_start_point[i]
                except IndexError:
                    break
                end = start + len(line[0])
                start_index = page_line_search(start, index, start_index)
                end_index = page_line_search(end, index, start_index)
                searched_text = line[0]
                new_text = ""
                if BR == "1":
                    edges = [index[k] - verse_start_point[i]
                             for k in range(start_index, end_index + 1)
                             if index[k] - verse_start_point[i] != 0]
                    for j in range(len(searched_text)):
                        if j in edges:
                            new_text += ("<BR>" + searched_text[j])
                        else:
                            new_text += searched_text[j]
                else:
                    new_text = line[0]
                searched_text = re.sub(r"(?<=\S)<BR>", "-<BR>", new_text)
                searched_text = searched_text.replace("@", " . . . ")
                spaned = re.compile(r"(" + keyword + ")", re.IGNORECASE)
                searched_text = re.sub(spaned,
                                       """<span style="color:red">""" + r"\1" + "</span>",
                                       searched_text)
                new_set = PaliText("J_{}".format(roman_number[num - 1]),
                                   page[start_index],
                                   line_start[start_index], page[end_index],
                                   line_start[end_index], searched_text)
                result.append(new_set)
            i += 1

        return result


def search_keyword_suttanipata(keyword, BR):
    result = []
    line_start = array("I");
    index = array("I");
    verse_start_point = array("I");
    page = array("I")
    sn_opener(index, line_start, page, verse_start_point)
    csvfile = open(static_path + "Sn_verse.csv", "r", encoding="utf-8",
                   newline="\n")
    lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
    i = 0
    start_index = 0
    for line in lines:
        if re.search(keyword, line[0]):
            try:
                start = verse_start_point[i]
            except IndexError:
                break
            end = start + len(line[0])
            start_index = page_line_search(start, index, start_index)
            end_index = page_line_search(end, index, start_index)
            searched_text = line[0]
            new_text = ""
            if BR == "1":
                edges = [index[k] - verse_start_point[i]
                         for k in range(start_index, end_index + 1)
                         if index[k] - verse_start_point[i] != 0]
                for j in range(len(searched_text)):
                    if j in edges:
                        new_text += ("<BR>" + searched_text[j])
                    else:
                        new_text += searched_text[j]
            else:
                new_text = line[0]
            searched_text = re.sub(r"(?<=\S)<BR>", "-<BR>", new_text)
            searched_text = searched_text.replace("@", " . . . ")
            spaned = re.compile(r"(" + keyword + ")", re.IGNORECASE)
            searched_text = re.sub(spaned,
                                   """<span style="color:red">""" + r"\1" + "</span>",
                                   searched_text)
            new_set = PaliText("Sn", page[start_index],
                               line_start[start_index], page[end_index],
                               line_start[end_index], searched_text)
            result.append(new_set)
        i += 1
    # ここから散文の方の検索；最後に全体をまとめてソートし、完成
    csvfile.close()
    pre_result = text_maker(keyword, BR, "Sn")
    result += pre_result
    result.sort(key=lambda x: (x.start_page, x.start_line))
    return result


def search_keyword(text_type, keyword, BR="0"):
    results = []
    if text_type == "J":
        results += search_keyword_jataka(keyword, BR)
    elif text_type == "Ap":
        results += text_maker(keyword, BR, text_type, break_point={"~"})
    #            results += [re.sub(r"~", "", item.output() + "<BR>") for item in pre_result]
    elif text_type == "Sn":
        results += search_keyword_suttanipata(keyword, BR)

    elif text_type in {"Dhp", "Cp", "Bv", "Vm", "Pv"}:
        results += verse_text_searcher(text_type, keyword)
    elif text_type in {"Th", "Thi"}:
        results += th_searcher(text_type, keyword)
    else:
        results += text_maker(keyword, BR, text_type)
    #            results += [item.output() + "<BR>" for item in pre_result]
    return results


@app.route('/')
def form():
    return render_template('index.html')


@app.route("/static/<string:path>")
def send_static(path):
    target = static_path + path
    return send_from_directory(static_path, path)
# This function is Mac only.


@app.route('/result', methods=["POST"])
def result_view():
    results = []; text_list = []
    searched = str(request.form["word"])
    item_number = int(request.form["item_max_number"])
    if not searched:
        return "No result"
    if str(request.form["KH"]) == "1":
        searched = kh_changer(searched)
    try:
        re.compile(searched)
    except Exception:
        return "Regex Error!"
    BR = str(request.form["BR"])
    cheaklist = request.form.getlist("text")

    text_order = ["Vin_I", "Vin_II", "Vin_III", "Vin_IV", "Vin_V", 
    "DN_I", "DN_II", "DN_III",
    "MN_I", "MN_II", "MN_III",
    "SN_I", "SN_II", "SN_III", "SN_IV", "SN_V",
    "AN_I", "AN_II", "AN_III", "AN_IV", "AN_V",
    "Khp", "Dhp", "Ud", "It", "Sn", "Pv", "Vm", "Th", "Thi", "J", "Nidd_I", "Nidd_II", "Paṭis_I", "Paṭis_II", "Ap", "Bv", "Cp",
    "Dhs", "Vibh", "Dhātuk", "Pugg", "Kv", "Yam_I", "Yam_II", "Mil", "Vism", "Sp", "Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5", "Ja_6"]
    
    #テキストリストを開く
    text_list = []
    for text in cheaklist:
        if text == "Vin":
            text_list += ["Vin_I", "Vin_II", "Vin_III", "Vin_IV", "Vin_V"]
        elif text == "DN":
            text_list += ["DN_I", "DN_II", "DN_III"]
        elif text == "MN":
            text_list += ["MN_I", "MN_II", "MN_III"]
        elif text == "SN":
            text_list += ["SN_I", "SN_II", "SN_III", "SN_IV", "SN_V"]
        elif text == "AN":
            text_list += ["AN_I", "AN_II", "AN_III", "AN_IV", "AN_V"]
        elif text == "Paṭis":
            text_list += ["Paṭis_I", "Paṭis_II"]
        elif text == "Yam":
            text_list += ["Yam_I", "Yam_II"]
        elif text == "Ja":
            text_list += ["Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5", "Ja_6"]
        else:
            text_list.append(text)

    text_list.sort(key = lambda x: text_order.index(x))
    # print("text_list: {}".format(text_list))
    
    for text_type in text_list:
        results += search_keyword(text_type, searched, BR)
    # print(results)

# Send output-text to html 
    if results == []:
        return "No result"

    result_text = ""
    page_counter = 1
    for i in range(len(results)):
#pagination
        if i % item_number == 0 and i != 0:
            result_text += """</div><div class = "selection" id="page-{}">""".format((i // item_number) + 1)
            page_counter += 1
        elif i == 0:
            result_text += """<div class = "selection" id="page-1">"""
            result_text += results[0].output() + "<BR>\n"

        if i >= 1 and results[i].text != results[i - 1].text:
            result_text += results[i].output() + "<BR>\n"
#    return result_text
    result_text += "</div>"
    return render_template('user.html', result=result_text, page_counter=page_counter)


if __name__ == "__main__":
    if len(os.listdir(static_path)) >= 259:
        url = "http://127.0.0.1:1125"
        threading.Timer(1.25, lambda: webbrowser.open(url)).start()
        app.run(port=1125, debug=False)
    else:
        print("Now we are making text for search at first. Please make sure you have internet accusses. It will be done in 10 minutes")
        import NotFound
        NotFound.mainpart()
        input("### Please input Enter key and close this window. When you execute this application again, you can get Pali_searcher on your blowser ###")
        exit()
# To make the package: $ pyinstaller Pali_searcher.py -F --add-data "./templates/*:templates" --add-data "./static/*:static"
    # if debug = True, the webbrowser will open twice.
