#!/usr/bin/env python3
# coding: utf-8
from pali_searcher import PaliSearcher
from flask import Flask, make_response, request, render_template, session, send_from_directory
import re
import os
import webbrowser
import threading
import sys

app_dir = os.path.abspath(os.path.dirname(__file__))
static_path = os.path.join(app_dir, "static")
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


def kh_changer(word):
    Not_change_flag = 0
    KH_list = ["A", "I", "U", "R", "L", "M", "G", "J", "T", "D", "N", "z", "S", "H"]
    NC_list = ["ā", "ī", "ū", "ṛ", "ḷ", "ṃ", "ṅ", "ñ", "ṭ", "ḍ", "ṇ", "ś", "ṣ", "ḥ"]
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


@app.route('/')
def form():
    return render_template('index.html')


@app.route("/static/<string:path>")
def send_static(path):
    return send_from_directory(static_path, path)
# This function is Mac only.


@app.route('/result', methods=["POST"])
def result_view():
    keyword = str(request.form["word"])
    item_number = int(request.form["item_max_number"])

    if not keyword:
        return "No result"

    if str(request.form["KH"]) == "1":
        keyword = kh_changer(keyword)

    try:
        re.compile(keyword)
    except Exception:
        return "Regex Error!"

    # Show line-changes: "0", False
    # Neglect line-changes: "1", True
    if str(request.form["BR"]) == "1":
        br_flag = True
    else:
        br_flag = False

    target_text_groups = request.form.getlist("text")

    searcher = PaliSearcher(static_path)
    results = searcher.search(target_text_groups, keyword, br_flag)
    # print(results)

    # Send output-text to html
    if results == []:
        return "No result"

    result_text = ""
    page_counter = 1
    for i in range(len(results)):
        # pagination
        if i == 0:
            result_text += """<div class = "selection" id="page-1">"""
        elif i % item_number == 0:
            result_text += """</div><div class = "selection" id="page-{}">""".format((i // item_number) + 1)
            page_counter += 1

        # 一部の結果が表示されていなかったの表示するように修正した
        # 元のコードでは一番目の結果が表示されていなかった (バグ?)
        # if i >= 1 and results[i].text != results[i - 1].text:
        # 元のコードでは sentence が前の結果と一致する場合は表示されていなかった
        # (重複を避けるため?)
        result_text += str(i+1) + ". " + results[i].output() + "<BR>\n"
    result_text += "</div>"
    return render_template('user.html', result=result_text, page_counter=page_counter)


if __name__ == "__main__":
    num_files = len(os.listdir(static_path))
    # テキストのダウンロードを行うかどうかはファイルの数で判定している
    if num_files >= 259:
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
