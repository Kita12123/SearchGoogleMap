import logging
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.chrome import service as fs
from webdriver_manager.chrome import ChromeDriverManager

# 店舗一覧の先頭URL
shop_list_first_url = "https://www.google.co.jp/maps/search/"
# Google Chromeのドライバを用意
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
DRIVER = webdriver.Chrome(service=chrome_service, options=options)


class InvalidURLError(Exception):
    """無効なURL"""
    pass


def _can_scroll() -> bool:
    """GoogleMapページの店一覧がスクロール可能か
    SubFunction For create_shop_url_list

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


def _scroll_down(amount: int, /):
    """スクロールダウン"""
    SCROLL_CLASS = os.environ["SCROLL_CLASS"]
    DRIVER.execute_script(
        # javascript
        f"""
        var obj = document.getElementsByClassName('{SCROLL_CLASS}')[1];
        obj.scrollTop+={amount};
        """
    )


def _get_shop_url_list() -> list[str]:
    """現在のページから店舗URLリストを取得する
    SubFunction For create_shop_url_list

    Returns:
        list[str]: 店舗URLリスト
    """
    result = []
    SHOP_LINK_CLASS = os.environ["SHOP_LINK_CLASS"]
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    for a in soup.find_all("a", class_=SHOP_LINK_CLASS):
        shop_url = a.get("href")
        result.append(shop_url)
    return result


def create_shop_url_list(url: str, /) -> list[str]:
    """GoogleMapの店舗一覧ページから店舗URLリストを取得

    Args:
        url (str): 店舗一覧URL

    Raises:
        InvalidURLError: 店舗一覧のページではないとき
        JavascriptException: JavaScriptが実行できなかったとき

    Returns:
        list[str]: 店舗URLリスト
    """
    DRIVER.get(url)
    time.sleep(2)
    # 検索結果が店舗一覧かどうかチェック
    count = len(shop_list_first_url)
    if DRIVER.current_url[:count] != shop_list_first_url:
        raise InvalidURLError
    # スクロールクラスチェック
    try:
        _can_scroll()
    except (JavascriptException):
        logging.critical("スクロールクラスが変更された可能性があります！")
        return _get_shop_url_list()
    # 10件以上を反映させるためにスクロールして更新する
    while True:
        if _can_scroll():
            _scroll_down(5000)
        else:
            # 追加店一覧更新待ち
            time.sleep(3)
            if not _can_scroll():
                # スクロールできなかったら抜け出す
                break
    return _get_shop_url_list()


def create_shop_info_dic(url: str, /) -> dict[str, str]:
    """GoogleMapの店舗ページから情報取得

    Args:
        url (str): 店舗URL

    Returns:
        dict[str, str]: 店舗情報
    """
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    name = ""
    kind = ""
    tell = ""
    address = ""
    locatedin = ""
    review = ""
    hp = ""
    for m in soup.find_all("meta"):
        property_: str = m.get("property")
        content: str = m.get("content")
        if property_ is None:
            continue
        elif property_ == "og:description":
            if " · " in content:
                review, kind = content.split(" · ")
            else:
                kind = content
        elif property_ == "og:title":
            if " · " in content:
                name, address = content.split(" · ")
            else:
                name = content
        else:
            continue
    for b in soup.find_all("button"):
        id: str = b.get("data-item-id")
        label: str = b.get("aria-label")
        if id is None:
            continue
        elif id[:10] == "phone:tel:":
            tell = label.replace("電話番号: ", "").replace(" ", "")
        elif id == "address":
            address = label.replace("住所: ", "")
        elif id == "locatedin":
            locatedin = label.replace("所在施設: ", "")
        else:
            continue
    for a in soup.find_all("a"):
        id = a.get("data-item-id")
        label = a.get("aria-label")
        if id is None:
            continue
        elif id == "authority":
            hp = "https://" + label.replace("ウェブサイト: ", "")
        else:
            continue
    return {
        "name": name,
        "kind": kind,
        "tell": tell,
        "address": address,
        "locatedin": locatedin,
        "review": review,
        "hp": hp,
    }
