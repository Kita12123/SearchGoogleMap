import csv
import logging
import os
import sys
from pathlib import Path


class DB:

    data_dic: dict[str, dict[str, str]] = {}

    def __init__(self):
        search_word = os.environ["SEARCH_WORD"]
        self.file = Path(
            sys.argv[0]
            ).parent / "temp" / f"search-({search_word}).csv"

    def update(self, **kwargs):
        # 重要: web.py > create_shop_info_dic() と同じにする
        url = kwargs.pop("url")
        values = {
            "name": "",
            "kind": "",
            "tell": "",
            "address": "",
            "locatedin": "",
            "review": "",
            "hp": "",
        }
        values.update(**kwargs)
        self.data_dic[url] = values

    def to_csv(self):
        columns = [[
            "店舗名",
            "業界",
            "電話番号",
            "住所",
            "所在施設",
            "レビュー",
            "ホームページ",
            "URL",
        ]]
        values = [
            [*values.values(), url]
            for url, values in self.data_dic.items()
        ]
        logging.info(f"データ件数: {len(values)}件")
        data_csv = columns + values
        while True:
            try:
                with open(
                    self.file,
                    "w",
                    newline="",
                    encoding="cp932",
                    errors="replace"
                ) as f:
                    csv.writer(f).writerows(data_csv)
                break
            except (PermissionError):
                input(f"ERR! ファイル:{self.file}を閉じてください。<Enter>")
