# remove_unused-sepc

## 1. 目的

`_private/20260312/remove_unused-req.md` の要求に基づき、現行の `htmlparser` 実装を前提として、未使用のクラスメソッド定義およびクラス外関数定義を削除するための外部仕様を定義する。

本仕様は、公開面、削除判定ルール、保持対象、削除対象を現行コード準拠で明確化することを目的とする。

## 2. スコープ

- 対象は `src/htmlparser/` 配下のクラスメソッド定義とクラス外関数定義とする。
- 主な判定対象は `clix.py`, `top.py`, `topconfigdb.py` とする。
- スクレイパーの解析処理、DB形式、設定ファイル形式、CLI引数仕様の見直しは対象外とする。
- 既存の `htmlparser` CLI の実行経路を維持したまま、未使用定義の削除だけを対象とする。

## 3. 参照ファイル

- `_private/20260312/remove_unused-req.md`
- `pyproject.toml`
- `src/htmlparser/clix.py`
- `src/htmlparser/top.py`
- `src/htmlparser/topconfigdb.py`
- `src/htmlparser/__init__.py`

## 4. 公開面の定義

### 4.1 外部公開起点

外部から呼び出される定義は、`pyproject.toml` の `[project.scripts]` において有効なエントリポイントから到達可能なものだけとする。

現行コードにおける有効な外部公開起点は以下のみとする。

- `htmlparser = "htmlparser.clix:main"`

### 4.2 現行 CLI 公開面

現行コードで公開されているサブコマンドは以下の 4 件とする。

- `run`
- `clear`
- `count`
- `print-list-text`

`prepare` は現行の `clix.py` では公開されていないため、公開面には含めない。

### 4.3 公開面に含めないもの

以下は削除可否判定において、外部公開面を構成する要素とはみなさない。

- コメントアウトされた `project.scripts`
- `src/htmlparser/__init__.py` の import および `__all__`
- 将来利用する可能性のみを理由とした未使用定義

## 5. 削除判定ルール

### 5.1 基本ルール

クラスメソッド定義およびクラス外関数定義のうち、以下の条件をすべて満たすものを削除対象とする。

1. `pyproject.toml` の有効な外部公開起点から到達できない。
2. `src/htmlparser/` 配下の他のクラスメソッドまたはクラス外関数から参照されない。
3. 当該定義を削除しても、現行の `htmlparser` CLI 実行経路を維持できる。

### 5.2 保持ルール

以下は保持対象とする。

- `htmlparser.clix:main`
- `main()` から直接または間接に呼び出される定義
- `run`, `clear`, `count`, `print-list-text` の各サブコマンド処理に必要な定義

## 6. 現行コードにおける保持対象

削除後も保持すべき主要定義は以下とする。

- `clix.py`
  - `Clix.__init__()`
  - `Clix.parse_args()`
  - `build_command_dict()`
  - `resolve_config_path()`
  - `load_config_file_from_args()`
  - `run_command()`
  - `clear_command()`
  - `count_command()`
  - `print_list_text_command()`
  - `main()`
- `top.py`
  - `ConfigFileInfo`
  - `Top.__init__()`
  - `Top.setup()`
  - `Top.db_loadx()`
  - `Top.db_count()`
  - `Top.db_print_list_text()`
- `topconfigdb.py`
  - `TopConfigDb.__init__()`
  - `TopConfigDb.get_env()`
  - `TopConfigDb.get_patterns()`
  - `TopConfigDb.get_db_file_path()`
  - `TopConfigDb.get_db_kind()`

## 7. 現行コードにおける削除対象

現行コードに対して本仕様で削除対象とする定義は以下とする。

- `Top.prepare()`

`Top.prepare()` は `top.py` に定義されているが、現行の外部公開起点 `htmlparser.clix:main` から到達せず、`src/htmlparser/` 内の他の定義からも参照されないため、削除対象とする。

## 8. 要求書記載との整合

要求書で削除対象として明示されている以下の旧シンボル名は、現行コード上ではすでに存在しない。

- `Clix.get_subparsers()`
- `Top.db_load()`
- `Top.save()`
- `TopConfigDb.get_db_file_name()`

そのため、本仕様ではこれらを「今回削除する現存定義」としては扱わない。現行コード準拠の仕様として、実在する未使用定義を削除対象として定義する。

## 9. 非対象

以下は本仕様の対象外とする。

- CLI サブコマンド追加
- CLI 引数仕様変更
- DB 形式変更
- YAML 設定形式変更
- スクレイパーの解析アルゴリズム変更

## 10. 受け入れ条件

- `htmlparser` コマンドのエントリポイントが引き続き `htmlparser.clix:main` であること。
- `main()` から `Clix.parse_args()` と各コマンド関数への実行経路が維持されること。
- `run`, `clear`, `count`, `print-list-text` の 4 サブコマンドが引き続き利用できること。
- `Top.prepare()` が削除対象として明記されていること。
- 要求書記載の旧シンボル 4 件が、現行コードでは既に存在しないことを仕様書内で明示していること。
- 外部公開面ではない未使用定義が、削除判定ルールに従って整理されること。

## 11. 備考

仕様書ファイル名は既存ファイル名に合わせて `remove_unused-sepc.md` とする。
