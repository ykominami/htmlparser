# fusion_class_top_and_clix-plan

## 1. 目的

`_private/fusion_class_top_and_clix-spec.md` に沿って、`Top` の責務を `Clix` 側へ統合し、`Top` クラスを削除するための実装変更案を定義する。

この計画は、変更順序、変更対象、確認項目、実装上の注意点を明確にすることを目的とする。

## 2. 前提

- 現行の `Top` は `TopConfigDb` の保持、DB 初期化、`db_loadx()`, `db_count()`, `db_print_list_text()` を担当している。
- 現行の `Clix` は設定ファイル読込と CLI 定義を持ち、各コマンドで `Top` を生成して利用している。
- 変更後は `run`, `clear`, `count`, `print-list-text` の CLI 公開挙動を維持しつつ、`Top` 依存を除去する。

## 3. 変更対象ファイル

- `src/htmlparser/clix.py`
- `src/htmlparser/top.py`
- `src/htmlparser/__init__.py`

必要に応じて確認対象とするファイル:

- `src/htmlparser/topconfigdb.py`

## 4. 実装方針

### 4.1 中心方針

`Top` の責務は新しいクラスへ再配置せず、`Clix` または `clix.py` 内の補助メソッドへ統合する。

### 4.2 `clix.py` で吸収する責務

- `TopConfigDb` を生成する共通初期化
- DB ファイルパスと DB 種別の検証
- `get_or_create_db()` を用いた DB 生成
- YAML タグ付き DB 読込
- 件数表示
- 一覧表示

### 4.3 実装形の推奨

`Clix` に以下のような補助処理を追加して責務を集約する。

1. 設定読込結果から `TopConfigDb` を生成する処理
2. `TopConfigDb` から DB を生成する処理
3. `TopConfigDb` と DB をまとめて返す共通初期化処理
4. DB 読込と出力補助処理

補助データを返すために、`NamedTuple` などの小さな内部データ構造を `clix.py` 内へ追加してよい。

## 5. 実装ステップ

### Step 1. `clix.py` の依存整理

- `from htmlparser.top import ConfigFileInfo, Top` を除去する。
- `ConfigFileInfo` が必要であれば `clix.py` 側へ移す。
- `Top` 依存をなくすために、`TopConfigDb` と `yklibpy.db` の必要シンボルを直接 import する。

### Step 2. 共通初期化処理の追加

- `load_config_file_from_args(args)` は維持する。
- その先に、設定情報から `TopConfigDb` を生成する補助メソッドを追加する。
- `TopConfigDb.get_db_file_path()` と `TopConfigDb.get_db_kind()` を検証し、`ValueError` の条件を現行と同等に維持する。
- `get_or_create_db()` を呼び、未対応 `db_kind` の場合は現行どおり `ValueError` を送出する。

### Step 3. `Top` の補助メソッド相当を移植

- `db_loadx()` 相当の処理を `clix.py` 側へ移す。
- `db_count()` 相当の処理を `clix.py` 側へ移す。
- `db_print_list_text(key)` 相当の処理を `clix.py` 側へ移す。
- YAML タグ文字列は現行と同一値を維持する。

### Step 4. 各コマンドの `Top` 依存を除去

- `run_command(args)` は共通初期化から `TopConfigDb` と DB を取得する形へ変更する。
- `clear_command(args)` は DB を直接 `clear()` と `save()` する形へ変更する。
- `count_command(args)` は DB 読込後に件数表示補助を呼ぶ形へ変更する。
- `print_list_text_command(args)` は DB 読込後に一覧表示補助を呼ぶ形へ変更する。
- `run_command(args)` 内の `top.top_config.get_patterns()` と `top.top_config.get_env()` は、`TopConfigDb` へ直接アクセスする形へ置き換える。

### Step 5. `top.py` の削除または空化

- 最終的に `Top` クラス定義を削除する。
- `ConfigFileInfo` を `clix.py` 側へ移した場合、`top.py` を残す理由が無ければファイル自体を削除する。
- もし一時的にファイルを残す場合でも、`Top` クラスが定義されない状態にする。

### Step 6. `__init__.py` の整合

- `__init__.py` に `Top` の import が無いことを確認する。
- `Top` 削除に伴い不要な import 整理があれば行う。
- 既存の `Clix`, `main`, `TopConfigDb` の公開は維持する。

## 6. 確認項目

### 6.1 コード構造

- `clix.py` に `Top` import が残っていないこと
- `clix.py` 内で `Top(...)` を生成していないこと
- `top.py` に `Top` クラスが残っていないこと

### 6.2 CLI 互換

- `run`, `clear`, `count`, `print-list-text` がそのまま存在すること
- 全サブコマンドの `config_file` 必須引数が維持されていること
- `print-list-text --key` の既定値が `"title"` のままであること
- `main()` が従来どおり終了コード `0` を返せること

### 6.3 動作互換

- `run_command(args)` が DB 読込、解析、保存、件数表示を継続できること
- `clear_command(args)` が DB 消去と保存を継続できること
- `count_command(args)` が DB 読込と件数表示を継続できること
- `print_list_text_command(args)` が DB 読込と一覧表示を継続できること

## 7. 検証手順

1. `uv run ruff check ./src`
2. `uv run mypy ./src`
3. 必要なら `uv run pytest`
4. 少なくとも `run`, `clear`, `count`, `print-list-text` の引数定義が壊れていないことを確認する

## 8. 注意点

- `TopConfigDb` には `get_patterns()` と `get_env()` があるため、`Top` 削除後もこのクラスはそのまま再利用できる。
- `top.py` の `ConfigFileInfo` は `Clix` 専用の補助型なので、`Top` 削除に合わせて `clix.py` へ寄せるのが自然である。
- `db_loadx()` で使う YAML タグは既存 DB 互換性に直結するため変更しない。
- `Top` を別名の新クラスで置き換えると仕様の主旨から外れやすいため避ける。

## 9. 完了条件

- `Top` クラスが削除されていること
- `Clix` が `Top` なしで現行コマンドを実行できる構造になっていること
- `__init__.py` を含む import 整合が取れていること
- 静的検証で新規エラーを出していないこと
