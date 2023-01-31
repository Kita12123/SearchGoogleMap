環境構築

1. pythonインストール
    https://www.python.org/downloads/

2. 仮想環境作成
    python -m venv .venv

3. 仮想環境反映
    .venv\Scripts\activate.bat

4. モジュールインポート
    pip install -r requirements.txt
    ( selenium, beautifulsoup4, pyinstaller, ... )


テスト
	test.pyを実行する

コンパイル

1. pyinstaller main.py --noconfirm --onefile

2. distフォルダのmain.exeをProgramFileフォルダへコピー


問題点

1. 場所ごとに上位１０件のみしか抽出できない <- スクロールさせることで解決
    県名で抽出せずに、座標を用いて抽出したほうがいいかも

2. Googleの規約に違反しているかも
    GoogleMapAPIを使う方法も模索する

3. 一回一回検索していくので遅い
    requestを用いて直接接続する方法も模索する