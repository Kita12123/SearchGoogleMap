"""
注意: Scrollするためにクラスを用いているが変更される可能性がある
    2022/09/08
        Scroll_Class: m6QErb DxyBCb kA9KIf dS8AEf ecceSd
        Shop_Link_Class: hfpxzc
"""
import logging
import os
import sys

from tqdm import tqdm

from db import DB
from web import InvalidURLError, create_shop_info_dic, create_shop_url_list

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s"
)
PLACES = [
    "北海道",
    "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県",
    "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]


def _create_url(place, /) -> str:
    """検索URL作成

    Args:
        place (str): 場所

    Returns:
        str: URL
    """
    SEARCH_WORD = os.environ["SEARCH_WORD"]
    sw = SEARCH_WORD.replace(" ", "+").replace(",", "+").replace("++", "+")
    return f"https://www.google.co.jp/maps/search/{sw}+{place}"


def main():
    # データベース定義
    db = DB()
    logging.info(f"データファイル -> {db.file}")
    max_count = len(PLACES)
    logging.info("スクレイピング実行中...")
    for i, place in enumerate(PLACES):
        logging.info(f"場所: {place} ({i} / {max_count}) ...")
        url = _create_url(place)
        try:
            shop_url_list = create_shop_url_list(url)
        except (InvalidURLError):
            # いきなり店舗が出たとき
            # ミニトマト+宮城県
            if place[-1] in "都府県":
                place = place[:-1]
                try:
                    shop_url_list = create_shop_url_list(url)
                except (InvalidURLError):
                    continue
            else:
                continue
        for url in tqdm(shop_url_list):
            shop_info_dic = create_shop_info_dic(url)
            db.update(**shop_info_dic)
    logging.info("csvファイルへ出力中...")
    db.to_csv()
    logging.info("完了")


if __name__ == "__main__":
    os.environ["SEARCH_WORD"] = sys.argv[1]
    os.environ["SCROLL_CLASS"] = sys.argv[2]
    os.environ["SHOP_LINK_CLASS"] = sys.argv[3]
    main()
