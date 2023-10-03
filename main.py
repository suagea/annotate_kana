# -*- coding: utf-8 -*-
# @Time : 2023/10/3 10:07
# @Author : LiangBoQing
# @File : main
import sys
import MeCab  # noqa
from enum import Enum

import pyperclip
import locale
import json

LANG = locale.getdefaultlocale()[0][:2]


# 根据LANG加载相应的语言文件
def load_language(lang):
  if getattr(sys, 'frozen', False):
    lang_file_path = f'_internal/langs/lang_{lang}.json'
  else:
    lang_file_path = f'langs/lang_{lang}.json'
  with open(lang_file_path, "r", encoding="utf-8") as f:
    return json.load(f)


# 根据LANG来选择合适的语言
LANG_MAPPING = {
  "en": "en",
  "zh": "zh",
  "ja": "ja"
}

language_data = load_language(LANG_MAPPING.get(LANG, "en"))  # 默认为英语


class KanaType(Enum):
  HIRAGANA = 1
  KATAKANA = 2


def is_kanji(ch):
  return '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4DBF'


def katakana_to_hiragana(kata):
  """将片假名转换为平假名"""
  return ''.join([chr(ord(ch) - 96) if 'ァ' <= ch <= 'ン' else ch for ch in kata])


def annotate_kana_one_row(text, kana_type):
  # 创建MeCab对象
  mecab = MeCab.Tagger()

  # 解析文本
  nodes = mecab.parse(text).split("\n")

  annotated_text = ""
  word = ""
  for node in nodes[:-2]:  # 忽略最后两行，它们通常是EOF和空行
    fields = node.split("\t")
    if len(fields) > 1:
      word = fields[0]
      kana = fields[1].split(",")[0]  # 使用默认格式，假名在第一个字段

      # 根据kana_type转换假名
      if kana_type == KanaType.HIRAGANA:
        kana = katakana_to_hiragana(kana)

      if word != kana and any(is_kanji(ch) for ch in word):  # 检查是否包含汉字
        annotated_text += word + "(" + kana + ")"
      else:
        annotated_text += word
    else:
      annotated_text += word

  return annotated_text


def annotate_kana(text: str, kana_type=KanaType.HIRAGANA):
  t = text.strip().split('\n')
  res = []
  for i in t:
    res.append(annotate_kana_one_row(i, kana_type))
  return '\n'.join(res)


def main():
  print(language_data["choose_annotation"])
  print(f"1. {language_data['hiragana']}")
  print(f"2. {language_data['katakana']}")
  choice = input(language_data["input_choice"])

  if choice == "1":
    kana_type = KanaType.HIRAGANA
  elif choice == "2":
    kana_type = KanaType.KATAKANA
  else:
    print(language_data["invalid_choice"])
    kana_type = KanaType.HIRAGANA

  while True:
    i = input(f"\n{language_data['start_clipboard']}")
    if i == 'e':
      break

    text = pyperclip.paste()
    if not text:
      print(language_data["empty_clipboard"])
      continue

    annotated_text = annotate_kana(text, kana_type)
    print(f"\n{language_data['annotated_text']}")
    print(annotated_text)

    # 复制到剪切板
    pyperclip.copy(annotated_text)
    print(f"\n{language_data['copied_clipboard']}")


if __name__ == "__main__":
  main()
  # print(
  #   annotate_kana_one_row(
  #     '「追加休日カウント」は、祝祭日によって年間の休日が何日増えたかを数えています。'
  #     '土日の場合は元々休日ということでカウントしていません。',
  #     KanaType.KATAKANA
  #   )
  # )
#
