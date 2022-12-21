#!/usr/bin/env python3
# coding: utf-8
from array import array
import re
import csv
import os


class PaliSearcher:
    __slots__ = ("static_dir_path", "target_text_groups")

    text_vols = ["Vin_I", "Vin_II", "Vin_III", "Vin_IV", "Vin_V",
    "DN_I", "DN_II", "DN_III",
    "MN_I", "MN_II", "MN_III",
    "SN_I", "SN_II", "SN_III", "SN_IV", "SN_V",
    "AN_I", "AN_II", "AN_III", "AN_IV", "AN_V",
    "Khp", "Dhp", "Ud", "It", "Sn", "Pv", "Vm", "Th", "Thi", "J", "Nidd_I", "Nidd_II", "Paṭis_I", "Paṭis_II", "Ap", "Bv", "Cp",
    "Dhs", "Vibh", "Dhātuk", "Pugg", "Kv", "Yam_I", "Yam_II", "Mil", "Vism", "Sp", "Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5", "Ja_6"]

    def __init__(self, static_dir_path, target_text_groups):
        self.static_dir_path = static_dir_path
        self.target_text_groups = target_text_groups

    def __static_dir_file_path(self, path):
        return os.path.join(self.static_dir_path, path)

    def __load_bin(self, file_name, array_data):
        path = self.__static_dir_file_path(file_name)
        f = open(path, "rb")
        try:
            array_data.fromfile(f, 10 ** 6)
        except EOFError:
            pass
        f.close()

    def search(self, keyword, br_flag=False):
        results = []
        for text_vol in self.target_text_vols():
            results += self.search_text_vol(text_vol, keyword, br_flag)
        return results

    def search_text_vol(self, text_vol, keyword, br_flag):
        results = []
        if text_vol == "J":
            results += self.search_jataka(keyword, br_flag)
        elif text_vol == "Ap":
            results += self.search_text_vol_base(keyword, br_flag, text_vol,
                                                 break_point={"~"})
        # results += [re.sub(r"~", "", item.output() + "<BR>") for item in pre_result]
        elif text_vol == "Sn":
            results += self.search_suttanipata(keyword, br_flag)

        elif text_vol in {"Dhp", "Cp", "Bv", "Vm", "Pv"}:
            results += self.verse_text_searcher(text_vol, keyword)
        elif text_vol in {"Th", "Thi"}:
            results += self.th_searcher(text_vol, keyword)
        else:
            results += self.search_text_vol_base(keyword, br_flag, text_vol)
        # results += [item.output() + "<BR>" for item in pre_result]
        return results

    def search_jataka(self, keyword, br_flag):
        results = []
        for num in range(1, 7):
            page = array("I");
            line_start = array("I");
            index = array("I");
            verse_start_point = array("I")
            self.load_jataka_bin_files(num, index, line_start, page,
                                       verse_start_point)
            roman_number = ["I", "II", "III", "IV", "V", "VI"]
            path = self.__static_dir_file_path("J_{}.csv".format(num))
            csvfile = open(path, "r", encoding="utf-8", newline="\n")
            lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
            i = 0
            start_index = 0
            for rows in lines:
                sentence = rows[0]
                if re.search(keyword, sentence):
                    try:
                        sentence_start = verse_start_point[i]
                    except IndexError:
                        break
                    end = sentence_start + len(sentence)
                    start_index = self.page_line_search(sentence_start, index, start_index)
                    end_index = self.page_line_search(end, index, start_index)
                    if br_flag:
                        sentence = self.restore_new_line(index, start_index,
                                                         end_index, sentence,
                                                         sentence_start)

                    sentence = sentence.replace("@", " . . . ")
                    spaned = re.compile(r"(" + keyword + ")", re.IGNORECASE)
                    sentence = re.sub(spaned,
                                           """<span style="color:red">""" + r"\1" + "</span>",
                                           sentence)
                    new_set = SearchResult("J_{}".format(roman_number[num - 1]),
                                           page[start_index],
                                           line_start[start_index], page[end_index],
                                           line_start[end_index], sentence)
                    results.append(new_set)
                i += 1

            return results

    def search_suttanipata(self, keyword, br_flag):
        results = []
        line_start = array("I");
        index = array("I");
        verse_start_point = array("I");
        page = array("I")
        path = self.__static_dir_file_path("Sn_verse.csv")
        self.load_suttanipata_bin_files(index, line_start, page,
                                        verse_start_point)
        csvfile = open(path, "r", encoding="utf-8", newline="\n")
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
                start_index = self.page_line_search(start, index, start_index)
                end_index = self.page_line_search(end, index, start_index)
                searched_text = line[0]
                new_text = ""
                if br_flag:
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
                new_set = SearchResult("Sn", page[start_index],
                                       line_start[start_index], page[end_index],
                                       line_start[end_index], searched_text)
                results.append(new_set)
            i += 1
        # ここから散文の方の検索；最後に全体をまとめてソートし、完成
        csvfile.close()
        pre_result = self.search_text_vol_base(keyword, br_flag, "Sn")
        results += pre_result
        results.sort(key=lambda x: (x.start_page, x.start_line))
        return results

    def load_jataka_bin_files(self, number, index, line, page, start_point):
        name = "Ja_{}".format(number)
        self.__load_bin(name + "_index_.bin", index)
        self.__load_bin(name + "_line_.bin", line)
        self.__load_bin(name + "_page_.bin", page)
        self.__load_bin("J_" + str(number) + "_start_point_.bin", start_point)
        # I made mistake when I named these bin files; I try to re-name here.

    def load_suttanipata_bin_files(self, index, line, page, start_point):
        self.__load_bin("Sn_index_.bin", index)
        self.__load_bin("Sn_line_.bin", line)
        self.__load_bin("Sn_page_.bin", page)
        self.__load_bin("Sn_verse_start_point.bin", start_point)

    def target_text_vols(self):
        result = []
        for text_group in self.target_text_groups:
            if text_group == "Vin":
                result += ["Vin_I", "Vin_II", "Vin_III", "Vin_IV",
                                     "Vin_V"]
            elif text_group == "DN":
                result += ["DN_I", "DN_II", "DN_III"]
            elif text_group == "MN":
                result += ["MN_I", "MN_II", "MN_III"]
            elif text_group == "SN":
                result += ["SN_I", "SN_II", "SN_III", "SN_IV", "SN_V"]
            elif text_group == "AN":
                result += ["AN_I", "AN_II", "AN_III", "AN_IV", "AN_V"]
            elif text_group == "Paṭis":
                result += ["Paṭis_I", "Paṭis_II"]
            elif text_group == "Yam":
                result += ["Yam_I", "Yam_II"]
            elif text_group == "Ja":
                result += ["Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5",
                                     "Ja_6"]
            else:
                result.append(text_group)

        # PaliSearcher.text_vols の順番でソートする
        result.sort(key=lambda x: PaliSearcher.text_vols.index(x))

        return result

    # パーリテキストデータからキーワードを検索してマッチした文字列について
    # 最初の文字の位置のリストを返す
    def search_pali_text(self, keyword, text_data):
        matches = re.finditer(keyword, text_data, re.IGNORECASE)
        li = [i.start() for i in matches]
        return li

    # text[n] が含まれる sentence の最初の文字のインデックスを返す
    def pali_pre_space(self, n, text, breakpoint={".", ":", "?", "!", "|", "@", ". ",
                                            ","}):  # モノによっては breakpoint を適時変更してやる必要がある
        while n - 1 != 0 and not (text[n] in breakpoint):
            n = n - 1
        return n + 2  # コンマなどの後ろには基本半角スペースがあるため

    # text[n] が含まれる sentence の最後の文字のインデックスを返す
    def pali_pos_space(self, n, text,
                       breakpoint={".", ":", "?", "!", "|", "@", ". ", ","}):
        while (n + 1 != len(text) - 1) and not (text[n] in breakpoint):
            n = n + 1
        return n + 1
        # この上で、どこまで出力するのかを決定する。あんまり長いとよくないので、いい感じにしないといけない。

    # テキストインデックス(テキスト内の位置)から実際のPTS書籍におけるページ番号,行番号を取得するためのインデックスを取得する
    def page_line_search(self, target, index,
                         start_index):  # start は、index[x] の x に相当する汎用インデックス番号を定める
        for i in range(start_index - 1,
                       len(index)):  # このスタートは単純増加していく汎用インデックス番号
            try:
                index[i + 1]
            except IndexError:
                return i
            if (index[i] <= target) and (index[i + 1] > target):
                return i

    def search_text_vol_base(self, keyword, br_flag=False, text_vol="",
                   break_point={".", ":", "?", "!", "|", "@", ". ", ","}):
        results = []
        index = array("I")
        page = array("I")
        line = array("I")
        text_vol_data = self.load_text_vol(text_vol)
        self.load_bin_files(text_vol, index, page, line)
        start_index = 0
        start_point_list = self.search_pali_text(keyword, text_vol_data)
        for start_point in start_point_list:
            if text_vol:  # あとで Apadanaの場合などに関して場合分けを考える
                sentence_start = self.pali_pre_space(start_point, text_vol_data,
                                                     break_point)
                sentence_end = self.pali_pos_space(start_point, text_vol_data,
                                                   break_point)
                start_index = self.page_line_search(sentence_start, index,
                                                    start_index)
                end_index = self.page_line_search(sentence_end, index,
                                                  start_index)
                # キーワードにマッチした sentence
                sentence = text_vol_data[sentence_start: sentence_end]

                if br_flag:
                    sentence = self.restore_new_line(index, start_index,
                                                     end_index, sentence,
                                                     sentence_start)

            # ハイライト処理など
            sentence = sentence.replace("@", " . . . ")
            spaned = re.compile(r"(" + keyword + ")", re.IGNORECASE)
            sentence = re.sub(spaned,
                                   """<span style="color:red">""" + r"\1" + "</span>",
                                   sentence)

            start_page = page[start_index]
            start_line = line[start_index]
            end_page = page[end_index]
            end_line = line[end_index]

            result = SearchResult(text_vol, start_page, start_line, end_page,
                                  end_line,
                                  sentence)

            # 全く同一の sentence の場合は結果としての登録をスキップする
            if len(results) > 0:
                last_result = results[-1]
                if last_result == result:
                    continue

            results.append(result)
        return results

    # 元のテキストの行またぎの状態に戻す処理
    def restore_new_line(self, index, start_index, end_index, sentence,
                         sentence_start):
        new_sentence = ""
        edges = [index[k] - sentence_start
                 for k in range(start_index, end_index + 1)
                 if index[k] - sentence_start != 0]
        for j in range(len(sentence)):
            if j in edges:
                new_sentence += ("<BR>" + sentence[j])
            else:
                new_sentence += sentence[j]
        new_sentence = re.sub(r"(?<=\S)<BR>", "-<BR>", new_sentence)
        sentence = new_sentence
        return sentence

    def verse_text_searcher(self, text_name, searched):
        spaned = re.compile(r"(" + searched + ")", re.IGNORECASE)
        path = self.__static_dir_file_path(text_name + "_.csv")
        csvfile = open(path, "r", encoding="utf-8", newline="\n")
        lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
        result = [
            PaliVerse(line[0],
                      re.sub(spaned,
                             """<span style="color:red">""" + r"\1" + "</span>",
                             line[1].lstrip().rstrip()),
                      text_name)
            for line in lines
            if re.search(searched, re.sub(r"\*\d\d?|<BR>|<br>", "", line[1]),
                         re.IGNORECASE)
        ]
        csvfile.close()
        return result

    def th_searcher(self, text, searched):
        if text == "Th":
            path = self.__static_dir_file_path("Thera_.csv")
            csvfile = open(path, "r", encoding="utf-8", newline="\n")
        else:
            path = self.__static_dir_file_path("Theri_.csv")
            csvfile = open(path, "r", encoding="utf-8", newline="\n")
        reader = csv.reader(csvfile)
        lines = list(list(reader)[0])

        spaned = re.compile(r"(" + searched + ")", re.IGNORECASE)
        result = [
            PaliVerse(
                re.sub(r"(^.*?\|\| )(Th.*?)( \|\|.*?$)", r"\2", line),
                re.sub(spaned,
                       """<span style="color:red">""" + r"\1" + "</span>",
                       line.lstrip().rstrip()),
                text
            )
            for line in lines
            if re.search(searched, re.sub(r"\*\d\d?|<BR>|<br>", "", line),
                         re.IGNORECASE)
        ]
        csvfile.close()
        return result

    def load_text_vol(self, text_vol):
        file = self.__static_dir_file_path(text_vol + "_.txt")
        f = open(file, "r", encoding="utf-8")
        return f.read()

    def load_bin_files(self, name, index, page, line):
        # この関数の前に、中身が空の page, line, index array を作る必要があり
        self.__load_bin(name + "_index_.bin", index)
        self.__load_bin(name + "_page_.bin", page)
        self.__load_bin(name + "_line_.bin", line)
        # I made mistake when I named these bin files; I try to re-name here.


class SearchResult:
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

    def __eq__(self, other):
        return self.name == other.name and \
            self.start_page == other.start_page and \
            self.end_page == other.end_page and \
            self.start_line == other.start_line and \
            self.end_line == other.end_line and \
            self.text == other.text

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

        return SearchResult.static_url + href_name + "_.htm#" + sharp

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
    def __init__(self, text_number, text, text_name, text_id=""):
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