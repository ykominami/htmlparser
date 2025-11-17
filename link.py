import html5lib
# ElementTreeをインポート
import xml.etree.ElementTree as ET

# 解析したいHTMLファイル（例: 'example.html'）
html_file_path = 'a.html'

def get_text_from_anchor(anchor):
    text_list = []
    # すべての子要素のテキストを取得（再帰的）
    for child in anchor.iter():
        if child.text and child.text.strip():
            # print(f"子要素テキスト ({child.tag}): {child.text.strip()}")
            text_list.append(child.text.strip())
        if child.tail and child.tail.strip():
            # print(f"子要素後のテキスト: {child.tail.strip()}")
            text_list.append(child.tail.strip())
        # print('-------')
    return text_list

def get_text_from_img_alt(item):
  alt_list = []
  for child in item.iter():
    if child.tag.endswith('img'):
      alt_value = child.attrib.get('alt', '').strip()
      alt_list.append(alt_value)
      # print(f'img子要素のalt属性: {alt_value}')
  return alt_list

def listup_x2(tree, ns):
    links_list = []
    # 2. 親要素マップ (parent_map) を構築
    # {子要素: 親要素} の辞書を作成します
    # root.iter() ですべての要素(p)をたどり、その子要素(c)をキーにします
    parent_map = {c: p for p in tree.iter() for c in p}

    anchor_tags = tree.findall('.//xhtml:a[@class="a-link-normal"]', namespaces=ns)
    
    print(f"class='a-link-normal'のアンカータグ (計 {len(anchor_tags)} 件)")
    for i, anchor in enumerate(anchor_tags):
        href = anchor.attrib.get('href', 'N/A')

        try:
          text = anchor.text if anchor.text else 'N/A'
          if len(text.strip()) == 0:
            list1 = get_text_from_anchor(anchor)
            text = ''.join(list1).strip()
            if len(text) == 0:
              list2 = get_text_from_img_alt(anchor)
              text = ''.join(list2).strip()

          asin = get_asin(href)
          assoc = {'href': href, 'text': text.strip(), 'asin': asin}
          # print(f'assoc={assoc}')
          links_list.append(assoc)

        except Exception as e:
          print(f'エラー: {e}')

    return links_list

def get_asin(href):
  array = href.split('/')
  index = array.index('product') + 1
  asin = array[index]
  return asin

def listup_x_sub(target_element, parent_map : dict):
  assoc = {}
  if target_element is not None:
      print(f"■ 対象要素: <{target_element.tag} id='{target_element.get('id')}'>")
      # 属性 (href) を取得
      href = target_element.attrib.get('href', 'N/A')
      text = target_element.text if target_element.text else 'N/A'
      print(f"  Text: {text.strip()}")
      print(f"  Href: {href}")
      print('------')
      assoc = { 'href': href, 'text': text.strip() }
      
      # 先祖要素を列挙
      ancestors = []
      current = target_element
      
      # parent_map にキーが存在する間 (つまり、ルートに達するまで) ループ
      while current in parent_map:
          parent = parent_map[current]
          ancestors.append(parent)
          current = parent # 次のループのために、親を現在の要素に設定
          
      # 結果の表示
      print("\n■ すべての親要素 (先祖):")
      for i, elem in enumerate(ancestors):
          # タグ名と、あればid属性を表示
          elem_id = elem.get('id')
          id_str = f" id='{elem_id}'" if elem_id else ""
          print(f"  [{i+1}] <{elem.tag}{id_str}>")
          
          # テキスト内容があれば表示
          text = elem.text
          if text is not None:
              text = text.strip()
              if text:
                  print(f"      Text: {text}")
          
          # クラス属性があれば表示
          class_attr = elem.get('class')
          if class_attr:
              print(f"      Class: {class_attr}")

  return assoc

def listup_y(root, ns):
  links_list = []
  # 2. 親要素マップ (parent_map) を構築
  # {子要素: 親要素} の辞書を作成します
  # root.iter() ですべての要素(p)をたどり、その子要素(c)をキーにします
  parent_map = {c: p for p in root.iter() for c in p}

  # 3. 対象の要素を取得 (例: id="target_span" の span 要素)
  # XPath風のfindを使います (標準etreeはXPathの一部のみサポート)
  # target_element = root.find(".//*[@id='target_span']")
  # target_element = root.find(".//*[@id='target_span']")
  target_elements = root.findall('.//xhtml:div[@class="readNowClassSelector"]', namespaces=ns)
  

  for target_element in target_elements:
    assoc = listup_x_sub(target_element, parent_map)
    links_list.append(assoc)

  return links_list

def listup_x(root, ns):
    links_list = []
    # 2. 親要素マップ (parent_map) を構築
    # {子要素: 親要素} の辞書を作成します
    # root.iter() ですべての要素(p)をたどり、その子要素(c)をキーにします
    parent_map = {c: p for p in root.iter() for c in p}

    # 3. 対象の要素を取得 (例: id="target_span" の span 要素)
    # XPath風のfindを使います (標準etreeはXPathの一部のみサポート)
    # target_element = root.find(".//*[@id='target_span']")
    # target_element = root.find(".//*[@id='target_span']")
    target_elements = root.findall('.//xhtml:a[@class="a-link-normal"]', namespaces=ns)

    for target_element in target_elements:
      assoc = listup_x_sub(target_element, parent_map)
      links_list.append(assoc)

    return links_list

def listup_x0(root, ns):
    links_list = []
    # 2. 親要素マップ (parent_map) を構築
    # {子要素: 親要素} の辞書を作成します
    # root.iter() ですべての要素(p)をたどり、その子要素(c)をキーにします
    parent_map = {c: p for p in root.iter() for c in p}

    # 3. 対象の要素を取得 (例: id="target_span" の span 要素)
    # XPath風のfindを使います (標準etreeはXPathの一部のみサポート)
    # target_element = root.find(".//*[@id='target_span']")
    # target_element = root.find(".//*[@id='target_span']")
    target_element = root.find('.//xhtml:a[@class="a-link-normal"]', namespaces=ns)

    if target_element is not None:
        print(f"■ 対象要素: <{target_element.tag} id='{target_element.get('id')}'>")
        # 属性 (href) を取得
        href = target_element.attrib.get('href', 'N/A')
        text = target_element.text if target_element.text else 'N/A'
        print(f"  Text: {text.strip()}")
        print(f"  Href: {href}")
        print('------')
        # 4. 親要素を遡って取得
        ancestors = []
        current = target_element
        
        # parent_map にキーが存在する間 (つまり、ルートに達するまで) ループ
        while current in parent_map:
            parent = parent_map[current]
            ancestors.append(parent)
            current = parent # 次のループのために、親を現在の要素に設定
            
        # 5. 結果の表示
        print("\n■ すべての親要素 (先祖):")
        for i, elem in enumerate(ancestors):
            # タグ名と、あればid属性を表示
            elem_id = elem.get('id')
            id_str = f" id='{elem_id}'" if elem_id else ""
            print(f"  <{elem.tag}{id_str}>")

            text = elem.text
            if text is not None:
              text = text.strip()

            assoc = {'tag': elem.tag, 'text': text}
            print(f'assoc={assoc}')
            links_list.append(assoc)
        
            # 親要素を取得
            print(f"\n[{i+1}] アンカータグの親要素:")
            for j, parent in enumerate(elem.iter()):
                print(f"  親要素 {j+1}: {parent.tag}")
                print(f"  属性: {parent.attrib}")
        

    return links_list

def parse_html(html_file_path):
  print(f'parse_html html_file_path={html_file_path}')
    # HTMLファイルを開いて読み込む
  try:
      with open(html_file_path, 'rb') as f:
          # html5lib.parse() を使って解析
          # treebuilder='etree' を指定し、ElementTreeオブジェクトを取得
          # html5libは名前空間を自動的に追加します
          root = html5lib.parse(f, treebuilder='etree')

      # HTML (XHTML) の名前空間を定義
      # これが ElementTree で html5lib を使う際の「お約束」です
      ns = {'xhtml': 'http://www.w3.org/1999/xhtml'}

      print('-------------------------------- 1')
      # listup_a_tag(root, ns)
      print('--------------------------------')
      # assoc = listup_x(root, ns)
      # assoc = listup_x2(root, ns)
      assoc = listup_y(root, ns)
      for item in assoc:
        print(item)
        print(f'item["href"]={item["href"]}')
        print(f'item["text"]={item["text"]}')
        print(f'item["asin"]={item["asin"]}')
        print('--------------------------------')
      print('--------------------------------')

  except FileNotFoundError:
      print(f"エラー: ファイル '{html_file_path}' が見つかりません。")
  except Exception as e:
      print(f"解析エラー: {e}")

parse_html(html_file_path)
