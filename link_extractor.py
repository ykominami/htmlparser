from bs4 import BeautifulSoup
import os # os.path.join を使うためにインポート

def read_html_file(file_path: str) -> str | None:
    """
    指定されたパスからHTMLファイルを読み込み、その内容を文字列として返します。

    Args:
        file_path (str): 読み込むHTMLファイルのパス。

    Returns:
        str | None: ファイルの内容。ファイルが存在しない場合や
                    読み込みエラーが発生した場合はNoneを返します。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        print(f"エラー: ファイル読み込み中に問題が発生しました: {e}")
        return None

def extract_links_from_html(html_content: str) -> list[str]:
    """
    HTMLコンテンツの文字列から全てのリンク(URL)を抽出します。

    Args:
        html_content (str): 解析対象のHTMLコンテンツ。

    Returns:
        list[str]: 抽出されたURLのリスト。
    """
    soup = BeautifulSoup(html_content, 'lxml')
    links = []
    # href属性を持つ全ての<a>タグを検索
    for a_tag in soup.find_all('a', href=True):
        # href属性が空でないことを確認
        if a_tag['href']:
            links.append(a_tag['href'])
    return links

def list_links_from_file(file_path: str) -> list[str]:
    """
    HTMLファイルを読み込み、そこに含まれる全てのリンクを列挙するメイン関数。

    Args:
        file_path (str): 解析するHTMLファイルのパス。

    Returns:
        list[str]: 抽出されたURLのリスト。
                   処理に失敗した場合は空のリストを返します。
    """
    print(f"'{file_path}' からリンクを抽出します...")
    # 手順1: HTMLファイルを読み込む
    html_content = read_html_file(file_path)

    # 手順2: 読み込んだ内容からリンクを抽出する
    if html_content:
        return extract_links_from_html(html_content)

    return []

if __name__ == '__main__':
    # --- このスクリプトの使い方 ---

    # 1. 解析したいHTMLファイルを作成します
    #    例: sample.html
    html_for_test = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>ようこそ！</h1>
        <p>いくつかのリンク先です。</p>
        <ul>
            <li><a href="https://www.google.com">Google</a></li>
            <li><a href="https://www.python.org">Python公式サイト</a></li>
            <li><a href="/about.html">内部リンク</a></li>
            <li><a href="https://example.com/page#section">セクションへのリンク</a></li>
            <li><a>hrefのないaタグ</a></li>
            <li><a href="">空のhref</a></li>
        </ul>
    </body>
    </html>
    """
    # スクリプトと同じディレクトリにテスト用のHTMLファイルを作成
    file_name = "sample.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_for_test)
    print(f"テスト用のHTMLファイル '{file_name}' を作成しました。")


    # 2. メイン関数を呼び出してリンクを抽出します
    # target_file = "sample.html"
    # target_file = "new_event_list.html"
    target_file = "3/新着イベント一覧.html"
    extracted_links = list_links_from_file(target_file)

    # 3. 結果を出力します
    if extracted_links:
        print("\n--- 抽出されたリンク一覧 ---")
        for i, link in enumerate(extracted_links, 1):
            print(f"{i}: {link}")
        print("--------------------------")
    else:
        print("リンクは見つかりませんでした、もしくはファイルの読み込みに失敗しました。")
    
    # テスト用ファイルを削除
    os.remove(file_name)

