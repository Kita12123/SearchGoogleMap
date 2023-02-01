import os
import time

import web
from db import DB

os.environ["SCROLL_CLASS"] = "m6QErb DxyBCb kA9KIf dS8AEf ecceSd"
os.environ["SHOP_LINK_CLASS"] = "hfpxzc"

shop_list_url = "https://www.google.co.jp/maps/search/いちご+岡山県"
shop_info_url = "https://www.google.com/maps/place/中山いちご園/@34.746871,133.8833268,17z/data=!3m1!4b1!4m6!3m5!1s0x3554046139547919:0x9319ebd5f66b8a4c!8m2!3d34.746871!4d133.8833268!16s%2Fg%2F1vzg01y_?authuser=0&hl=ja"  # noqa
shop_info_url2 = "https://www.google.co.jp/maps/place/%E3%81%BF%E3%81%AE%E3%82%8B%E7%94%A3%E6%A5%AD%E3%88%B1+%E5%8C%97%E6%B5%B7%E9%81%93%E5%B7%A5%E5%A0%B4/@43.2369188,141.8093702,17z/data=!4m6!3m5!1s0x5f0b4e988199db01:0x565f0cc39cb771ab!8m2!3d43.23716!4d141.810233!16s%2Fg%2F1vl9r8rb?authuser=0&hl=ja"  # noqa


def test_can_scroll():
    web.DRIVER.get(shop_list_url)
    assert web._can_scroll() is True


def test_create_info_dic():
    dic = web.create_shop_info_dic(shop_info_url)
    assert dic["tell"] == "086-294-2747"


def test_create_shop_url_list():
    SHOP_LINK_CLASS = os.environ["SHOP_LINK_CLASS"]
    url = shop_list_url
    web.DRIVER.get(url)
    time.sleep(2)
    # 検索結果が店舗一覧かどうかチェック
    count = len(web.shop_list_first_url)
    if web.DRIVER.current_url[:count] == web.shop_list_first_url:
        pass
    else:
        raise web.InvalidURLError
    # スクロールクラスチェック
    try:
        web._can_scroll()
    except (web.JavascriptException):
        raise web.JavascriptException
    # 10件以上を反映させるためにスクロールして更新する
    while True:
        if web._can_scroll():
            web._scroll_down(5000)
        else:
            # 追加店一覧更新待ち
            time.sleep(3)
            if not web._can_scroll():
                # スクロールできなかったら抜け出す
                break
    # 店舗名, URL取得
    soup = web.BeautifulSoup(web.DRIVER.page_source, "html.parser")
    result = []
    for a in soup.find_all("a", class_=SHOP_LINK_CLASS):
        shop_url = a.get("href")
        result.append(shop_url)
    assert result


if __name__ == "__main__":
    db = DB()
    db.update(**web.create_shop_info_dic(shop_info_url2))
