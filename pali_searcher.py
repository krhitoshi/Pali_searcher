#!/usr/bin/env python3
# coding: utf-8
from array import array
import re
import csv
import os
from enum import Enum

SENTENCE_SEPARATORS = {".", ":", "?", "!", "|", "@", ". ", ","}

# TODO: app.py へ移行する
# 環境変数 STATIC_URL が設定されていればベースとなるURLを変更する
STATIC_URL = os.environ.get("STATIC_URL", "static/")


class PaliSearcherMode(Enum):
    Web = 0
    CLI = 1


class PaliSearcher:
    __slots__ = ("static_dir_path", "target_text_groups", "mode")

    text_vols = ["Vin_I", "Vin_II", "Vin_III", "Vin_IV", "Vin_V",
                 "DN_I", "DN_II", "DN_III",
                 "MN_I", "MN_II", "MN_III",
                 "SN_I", "SN_II", "SN_III", "SN_IV", "SN_V",
                 "AN_I", "AN_II", "AN_III", "AN_IV", "AN_V",
                 "Khp", "Dhp", "Ud", "It", "Sn", "Pv", "Vm", "Th", "Thi", "J", "Nidd_I", "Nidd_II", "Patis_I", "Patis_II", "Ap", "Bv", "Cp",
                 "Dhs", "Vibh", "Dhatuk", "Pugg", "Kv", "Yam_I", "Yam_II", "Mil", "Vism", "Sp", "Ja_1", "Ja_2", "Ja_3", "Ja_4", "Ja_5", "Ja_6"]

    def __init__(self, static_dir_path, mode=PaliSearcherMode.Web):
        self.static_dir_path = static_dir_path
        self.mode = mode

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

    # 表示する前のハイライト処理などを行う
    def display_sentence(self, sentence, keyword):
        new_sentence = sentence.replace("@", " . . . ")
        return self.highlight(new_sentence, keyword)

    def highlight(self, sentence, keyword):
        regex = re.compile(r"({})".format(keyword), re.IGNORECASE)
        if self.mode == PaliSearcherMode.CLI:
            # ANSIエスケープ 赤色
            replace = "\u001b[31m" + r"\1" + "\u001b[0m"
        else:
            replace = r'<span style="color:red">\1</span>'
        return re.sub(regex, replace, sentence)

    def search(self, target_text_groups, keyword, br_flag=False):
        results = []
        for text_vol in self.target_text_vols(target_text_groups):
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

    # J_1, J_2, J_3, J_4, J_5, J_6 (韻文)
    def search_jataka(self, keyword, br_flag):
        results = []
        for num in range(1, 7):
            page = array("I")
            line_start = array("I")
            index = array("I")
            verse_start_point = array("I")
            self.load_jataka_bin_files(num, index, line_start, page,
                                       verse_start_point)
            roman_number = ["I", "II", "III", "IV", "V", "VI"]

            text_vol = "J_{}".format(roman_number[num - 1])
            csv_file_name = "J_{}.csv".format(num)

            results += self.search_csv_base(text_vol, csv_file_name, keyword,
                                            br_flag, index, line_start, page,
                                            verse_start_point)
        return results

    # Sn (散文), Sn_verse.csv (韻文)
    def search_suttanipata(self, keyword, br_flag):
        line_start = array("I")
        index = array("I")
        verse_start_point = array("I")
        page = array("I")

        self.load_suttanipata_bin_files(index, line_start, page,
                                        verse_start_point)

        results = self.search_csv_base("Sn", "Sn_verse.csv", keyword, br_flag,
                                       index, line_start, page,
                                       verse_start_point)
        # ここから散文の方の検索；最後に全体をまとめてソートし、完成
        pre_result = self.search_text_vol_base(keyword, br_flag, "Sn")
        results += pre_result
        results.sort(key=lambda x: (x.start_page, x.start_line))
        return results

    # Sn_verse, J_1, J_2, J_3, J_4, J_5, J_6
    def search_csv_base(self, text_vol, csv_file_name, keyword, br_flag, index,
                        line_start, page, verse_start_point):
        results = []
        path = self.__static_dir_file_path(csv_file_name)
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
                start_index = self.page_line_search(sentence_start, index,
                                                    start_index)
                end_index = self.page_line_search(end, index, start_index)
                if br_flag:
                    sentence = self.restore_new_line(index, start_index,
                                                     end_index, sentence,
                                                     sentence_start)

                sentence = self.display_sentence(sentence, keyword)

                start_page = page[start_index]
                start_line = line_start[start_index]
                end_page = page[end_index]
                end_line = line_start[end_index]

                result = SearchResult(text_vol, start_page,
                                      start_line, end_page,
                                      end_line, sentence)
                results.append(result)
            i += 1
        csvfile.close()
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

    def target_text_vols(self, target_text_groups):
        result = []
        for text_group in target_text_groups:
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
            elif text_group == "Patis":
                result += ["Patis_I", "Patis_II"]
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
    # モノによっては breakpoint を適時変更してやる必要がある
    def pali_pre_space(self, n, text, breakpoint=SENTENCE_SEPARATORS):
        while n - 1 != 0 and not (text[n] in breakpoint):
            n = n - 1
        return n + 2  # コンマなどの後ろには基本半角スペースがあるため

    # text[n] が含まれる sentence の最後の文字のインデックスを返す
    def pali_pos_space(self, n, text, breakpoint=SENTENCE_SEPARATORS):
        while (n + 1 != len(text) - 1) and not (text[n] in breakpoint):
            n = n + 1
        return n + 1
        # この上で、どこまで出力するのかを決定する。あんまり長いとよくないので、いい感じにしないといけない。

    # テキストインデックス(テキスト内の位置)から実際のPTS書籍におけるページ番号,行番号を取得するためのインデックスを取得する
    # start は、index[x] の x に相当する汎用インデックス番号を定める
    def page_line_search(self, target, index, start_index):
        # このスタートは単純増加していく汎用インデックス番号
        for i in range(start_index - 1, len(index)):
            try:
                index[i + 1]
            except IndexError:
                return i
            if (index[i] <= target) and (index[i + 1] > target):
                return i

    def search_text_vol_base(self, keyword, br_flag=False, text_vol="",
                             break_point=SENTENCE_SEPARATORS):
        results = []
        index = array("I")
        page = array("I")
        line = array("I")
        text_vol_data = self.load_text_vol(text_vol)
        self.load_bin_files(text_vol, index, page, line)
        start_index = 0
        start_point_list = self.search_pali_text(keyword, text_vol_data)
        for start_point in start_point_list:
            # あとで Apadana の場合などに関して場合分けを考える
            if text_vol:
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

            sentence = self.display_sentence(sentence, keyword)

            start_page = page[start_index]
            start_line = line[start_index]
            end_page = page[end_index]
            end_line = line[end_index]

            result = SearchResult(text_vol, start_page, start_line, end_page,
                                  end_line, sentence)

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

    # Dhp, Cp, Bv, Vm, Pv
    def verse_text_searcher(self, text_name, keyword):
        path = self.__static_dir_file_path(text_name + "_.csv")
        csvfile = open(path, "r", encoding="utf-8", newline="\n")
        lines = csv.reader(csvfile, delimiter=",", skipinitialspace=True)
        result = [
            PaliVerse(line[0],
                      self.highlight(line[1].lstrip().rstrip(), keyword),
                      text_name)
            for line in lines
            if re.search(keyword, re.sub(r"\*\d\d?|<BR>|<br>", "", line[1]),
                         re.IGNORECASE)
        ]
        csvfile.close()
        return result

    # Thera_.csv, Theri_.csv
    def th_searcher(self, text, keyword):
        if text == "Th":
            path = self.__static_dir_file_path("Thera_.csv")
        else:
            path = self.__static_dir_file_path("Theri_.csv")

        csvfile = open(path, "r", encoding="utf-8", newline="\n")
        reader = csv.reader(csvfile)
        lines = list(list(reader)[0])

        result = [
            PaliVerse(
                re.sub(r"(^.*?\|\| )(Th.*?)( \|\|.*?$)", r"\2", line),
                self.highlight(line.lstrip().rstrip(), keyword),
                text
            )
            for line in lines
            if re.search(keyword, re.sub(r"\*\d\d?|<BR>|<br>", "", line),
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
    __slots__ = ("name", "start_page", "end_page", "start_line", "end_line",
                 "sentence")

    def __init__(self, name, start_page, start_line, end_page, end_line,
                 sentence):
        self.name = name
        self.start_page = start_page
        self.end_page = end_page
        self.start_line = start_line
        self.end_line = end_line
        self.sentence = sentence

    def __eq__(self, other):
        return self.name == other.name and \
            self.start_page == other.start_page and \
            self.end_page == other.end_page and \
            self.start_line == other.start_line and \
            self.end_line == other.end_line and \
            self.sentence == other.sentence

    def __link_url(self):
        if self.start_page <= 9:
            sharp = "00" + str(self.start_page)
        elif self.start_page <= 99:
            sharp = "0" + str(self.start_page)
        else:
            sharp = str(self.start_page)

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

        return STATIC_URL + href_name + "_.htm#" + sharp

    def reference_info(self):
        if self.name[:2] == "Ja":
            roman = ["I", "II", "III", "IV", "V", "VI"]
            text_vol = self.name[:3] + roman[int(self.name[3]) - 1]
        else:
            text_vol = self.name

        if self.start_line == self.end_line:
            if self.start_page == 1:
                self.start_line -= 1
            res = "{} {}.{}".format(text_vol, self.start_page, self.start_line)
        elif self.start_page == self.end_page:
            if self.start_page == 1:
                self.start_line -= 1
                self.end_line -= 1
            res = "{} {}.{}-{}".format(text_vol, self.start_page, self.start_line, self.end_line)
        else:
            if self.start_page == 1:
                self.start_line -= 1
                self.end_line -= 1
            res = "{} {}.{}-{}.{}".format(text_vol, self.start_page, self.start_line, self.end_page, self.end_line)
        return res

    # 結果表示のためのテキスト形成
    def output(self):
        if self.name == "Ap":
            self.sentence = re.sub(r"~", "", self.sentence)
        base = '<a href={} target="_blank">{}</a>: {}'
        res = base.format(self.__link_url(), self.reference_info(), self.sentence)
        return res


class PaliVerse:
    def __init__(self, text_number, sentence, text_name, text_id=""):
        self.name = self
        self.text_number = text_number
        self.sentence = sentence
        self.text_name = text_name
        self.text_id = text_id

    def reference_info(self):
        return self.text_number

    def output(self):
        if self.sentence == "Vm" or self.sentence == "Pv":
            self.text_id = self.text_number[:-4]
        if self.text_id == "":
            self.text_id = self.text_number
            href = STATIC_URL + self.text_name + "_.htm#" + self.text_id.replace(".", "_")
            base = '<a href = {} target="_blank">{}</a>: {}'
        return base.format(href, self.text_number, self.sentence)
