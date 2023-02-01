import csv
import os
from pathlib import Path


class DB:

    data_dic: dict[str, dict[str, str]] = {}

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
        SEARCH_WORD = os.environ["SEARCH_WORD"]
        file = Path(__file__).parent / f"search-({SEARCH_WORD}).csv"
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
            list(*values, url)
            for url, values in self.data_dic.items()
        ]
        data_csv = columns + values
        while True:
            try:
                with open(
                    file,
                    "w",
                    newline="",
                    encoding="cp932",
                    errors="replace"
                ) as f:
                    csv.writer(f).writerows(data_csv)
                break
            except (PermissionError):
                input(f"ERR! ファイル:{file}を閉じてください。<Enter>")
