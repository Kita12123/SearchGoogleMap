"""
注意: Scrollするためにクラスを用いているが変更される可能性がある
    2022/09/08  m6QErb DxyBCb kA9KIf dS8AEf ecceSd
"""
import csv
import logging
import os
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.chrome import service as fs
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

LOGGER = logging.getLogger(__name__)
# Google Chromeのドライバを用意
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
DRIVER = webdriver.Chrome(service=chrome_service, options=options)
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


class InvalidURLError(Exception):
    """無効なURL"""
    pass


def create_place_generator():
    """順番に場所を返すジェレネータ作成

    Yields:
        tuple[int, str]: 回数, 場所名
    """
    for i, place in enumerate(PLACES):
        yield i, place


PLACE_GENERATOR = create_place_generator()


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


def _can_scroll() -> bool:
    """GoogleMapページの店一覧がスクロール可能か

    Returns:
        bool: 可能 - true, 不可能 - flase
    """
    SCROLL_CLASS = os.environ["SCROLL_CLASS"]
    return DRIVER.execute_script(
        # javascript
        # scrollHeight: スクロールバー全体の高さ
        # scrollTop: スクロールの上の位置
        # offsetHeight: スクロールの高さ
        f"""
        var obj = document.getElementsByClassName(
            '{SCROLL_CLASS}'
        )[1];
        return (10 < obj.scrollHeight - obj.scrollTop - obj.offsetHeight)
        """
    )


def create_shop_dic_list(place: str, /) -> list[dict[str, str]]:
    SCROLL_CLASS = os.environ["SCROLL_CLASS"]
    result = []
    # 検索結果が店舗一覧かどうかチェック
    while True:
        try:
            url = _create_url(place)
            DRIVER.get(url)
            time.sleep(1)
            _can_scroll()
            break
        except (JavascriptException):
            # 場所の形式を変更して再度検索
            if place[-1] in "都道府県":
                place = place[:-1]
            else:
                raise InvalidURLError()
    # 10件以上を反映させるためにスクロールして更新する
    while True:
        if _can_scroll():
            # スクロール量を増やす
            DRIVER.execute_script(
                # javascript
                f"""
                var obj = document.getElementsByClassName('{SCROLL_CLASS}')[1];
                obj.scrollTop+=10000;
                """
            )
        else:
            # 追加店一覧更新待ち
            time.sleep(3)
            if not _can_scroll():
                # スクロールできなかったら抜け出す
                break
    # 店舗名, URL取得
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    for a in soup.find_all("a"):
        name = a.get("aria-label")
        url = a.get("href")
        # 不要な部分を取る
        if (
            name is None or
            name == "検索をクリア" or
            "ウェブサイトにアクセス" in name or
            url is None or
            url[:4] != "http"
           ):
            continue
        result.append({
            "名前": name,
            "GoogleMapURL": url
        })
    return result


def create_infomation_dic(url: str) -> dict[str, str]:
    """リンク先の店情報取得
    Return [業種, 電話番号, 住所, レビュー, ホームページ]"""
    DRIVER.get(url)
    time.sleep(0.5)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    kind = ""
    tell = ""
    adress = ""
    review = ""
    hp = ""
    for b in soup.find_all("button"):
        name = str(b.get("aria-label"))
        # 必要な箇所のみ抽出
        if name is None:
            continue
        elif name[:6] == "電話番号: ":
            tell = name[6:]
        elif name[:4] == "住所: ":
            adress = name[4:]
    for m in soup.find_all("meta", attrs={"property": "og:description"}):
        name = str(m.get("content"))
        if (
            name is None or
            "〒" in name
           ):
            continue
        elif "·" in name:
            kr = name.split("·")
            review = kr[0]
            kind = kr[1]
        else:
            kind = name
    for a in soup.find_all("a"):
        name = str(a.get("aria-label"))
        if name is None:
            continue
        elif name[:8] == "ウェブサイト: ":
            hp = "https://" + name[8:]
    return {
        "業界": kind,
        "電話番号": tell,
        "住所": adress,
        "レビュー": review,
        "ホームページ": hp
    }


def main():
    SEARCH_WORD = os.environ["SEARCH_WORD"]
    csv_data = [["名前", "業界", "電話番号", "住所", "レビュー", "ホームページ", "GoogleMapURL"]]
    max_count = len(PLACES)
    print("スクレイピング実行中...")
    while True:
        try:
            i, place = next(PLACE_GENERATOR)
            LOGGER.debug(f"{i} / {max_count}...")
        except (StopIteration):
            # 全ての場所が検索されたので終了
            break
        try:
            shop_dic_list = create_shop_dic_list(place)
        except (InvalidURLError):
            # 無効なURLなので飛ばす
            continue
        for shop_dic in tqdm(shop_dic_list):
            info_dic = create_infomation_dic(shop_dic["GoogleMapURL"])
        csv_data.append([
            shop_dic["名前"],
            info_dic["業界"],
            info_dic["電話番号"],
            info_dic["住所"],
            info_dic["レビュー"],
            info_dic["ホームページ"],
            shop_dic["GoogleMapURL"]
        ])
    print("csvファイルへ出力中...")
    while True:
        try:
            with open(
                f"search{SEARCH_WORD}.csv",
                "w",
                newline="",
                encoding="cp932",
                errors="replace"
            ) as f:
                csv.writer(f).writerows(csv_data)
            break
        except (PermissionError):
            input(f"ERR! ファイル:search{SEARCH_WORD}.csvを閉じてください。<Enter>")
    DRIVER.quit()
    print("完了")


if __name__ == "__main__":
    os.environ["SEARCH_WORD"] = sys.argv[1]
    os.environ["SCROLL_CLASS"] = sys.argv[2]
    main()
