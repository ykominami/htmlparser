# App クラスのメソッド呼び出し関係図

## 全体フロー図

```mermaid
graph TD
    Start[__init__] --> Setup[_setup]
    Main[run] --> Loop[loop]
    Loop --> GetLinks[get_links_from_html]
    Loop --> GetArray[get_link_array]
    GetLinks --> Parse[_parse_html_file]
    GetLinks --> Extract[_extract_links_from_info]
    GetArray --> MakeRec[make_record]
    
    Extract -->|mode=udemy| ProcessUdemy[process_for_udemy]
    Extract -->|mode=h3| ProcessH3[process_for_h3]
    Extract -->|mode=a| ProcessA[process_for_a]
    Extract -->|mode=ku| ProcessKu[process_for_ku]
    Extract -->|mode=status| FindAncestors[find_item_ancestors]
    
    ProcessUdemy --> GetCourseId[get_course_id_from_url]
    ProcessUdemy --> GetInstructors[get_instructors]
    ProcessUdemy --> GetProgress[get_progress]
    ProcessUdemy --> AddList[add_list_and_assoc]
    
    ProcessH3 --> GetCourseId
    ProcessH3 --> AddList
    
    ProcessA --> GetCourseId
    ProcessA --> AddList
    
    ProcessKu --> GetCourseId
    ProcessKu --> AddList
    
    AddList --> MakeRec
    
    GetProgress --> ProgressClass[Progress クラス]
    GetCourseId --> UrlParse[urlparse]
    GetCourseId --> ParseQs[parse_qs]
    MakeRec --> UrlParse
    
    OutputYaml[output_link_assoc_in_yaml] --> OutputYamlMethod[output_yaml]
    OutputYamlMethod --> UtilClass[Util.output_yaml]
    
    FindStatusSpan[find_status_span_ancestors] --> FindAncestors
    
    style Start fill:#e1f5ff
    style Main fill:#e1f5ff
    style ProgressClass fill:#fff4e1
    style UtilClass fill:#fff4e1
    style UrlParse fill:#fff4e1
    style ParseQs fill:#fff4e1
```

## 詳細な呼び出し関係図

```mermaid
graph LR
    subgraph "初期化"
        A[__init__] --> B[_setup]
    end
    
    subgraph "メイン処理"
        C[run] --> D[loop]
        D --> E[get_links_from_html]
        D --> F[get_link_array]
        E --> G[_parse_html_file]
        E --> H[_extract_links_from_info]
        F --> I[make_record]
    end
    
    subgraph "モード別処理"
        H --> J[process_for_udemy]
        H --> K[process_for_h3]
        H --> L[process_for_a]
        H --> M[process_for_ku]
        H --> N[find_item_ancestors]
    end
    
    subgraph "共通処理"
        J --> O[get_course_id_from_url]
        J --> P[get_instructors]
        J --> Q[get_progress]
        J --> R[add_list_and_assoc]
        K --> O
        K --> R
        L --> O
        L --> R
        M --> O
        M --> R
        R --> I
    end
    
    subgraph "外部依存"
        Q --> S[Progress]
        O --> T[urlparse]
        O --> U[parse_qs]
        I --> T
        V[output_yaml] --> W[Util.output_yaml]
    end
    
    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style S fill:#fff4e1
    style W fill:#fff4e1
    style T fill:#fff4e1
    style U fill:#fff4e1
```

## メソッド説明

- **初期化系**
  - `__init__`: コンストラクタ
  - `_setup`: インスタンス変数の初期化

- **メイン処理系**
  - `run`: アプリケーションのメイン実行メソッド
  - `loop`: ファイルリストをループ処理
  - `get_links_from_html`: HTMLファイルからリンクを抽出
  - `_parse_html_file`: HTMLファイルをパース
  - `_extract_links_from_info`: モードに応じてリンク抽出処理を分岐

- **モード別処理**
  - `process_for_udemy`: Udemyモードの処理
  - `process_for_h3`: H3モードの処理
  - `process_for_a`: Aモードの処理
  - `process_for_ku`: KUモードの処理

- **ユーティリティ系**
  - `get_course_id_from_url`: URLからコースIDを抽出
  - `get_instructors`: インストラクター情報を取得
  - `get_progress`: 進捗情報を取得
  - `add_list_and_assoc`: リンクをリストと連想配列に追加
  - `make_record`: レコードを作成
  - `get_link_array`: リンクを配列形式に変換

- **出力系**
  - `output_link_assoc_in_yaml`: YAML形式で出力
  - `output_yaml`: YAML出力処理

- **その他**
  - `find_item_ancestors`: アイテムの祖先要素を取得
  - `find_status_span_ancestors`: status spanの祖先要素を取得

