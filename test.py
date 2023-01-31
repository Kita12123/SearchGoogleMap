"""
TEST
"""
#
# Import Module
#
from main import *

def output_html():
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    with open("test.txt", "w", encoding="cp932", errors="replace") as f:
        f.write(soup.prettify())

data_csv = [["名前","電話番号","住所","ホームページ","GoogleMapURL"]]
print("スクレイピング実行中...")
urls = create_urls("test")
name_links = create_shop_links(urls[0], "m6QErb DxyBCb kA9KIf dS8AEf ecceSd")

for i, name_link in enumerate(name_links):
    datas = create_shop_description(name_link[1])
    print(datas)
    #print(f"{i+1}. 名前:{name_link[0]}, 電話:{datas[0]}, 住所:{datas[1]}")
    #output_html()
    #break
DRIVER.quit()
print("完了")