# fusion_class_top_and_clix-spec

## 1. 目的

`_private/20260313/fusion_class_top_and_clix-req.md` の要求を満たすため、`htmlparser` パッケージ内の `Top` クラスを `Clix` 側へ統合し、`Top` クラスを削除するための外部仕様を定義する。

この仕様は、統合対象となる責務、削除後に維持すべき CLI 公開挙動、ならびに実装上の制約を明確にすることを目的とする。

## 2. スコープ

- 対象は `src/htmlparser/top.py` に定義された `Top` クラスと `src/htmlparser/clix.py` に定義された `Clix` クラスおよび CLI コマンド処理とする。
- 主な対象ファイルは `src/htmlparser/top.py`、`src/htmlparser/clix.py`、`src/htmlparser/__init__.py` とする。
- `Top` が担っている DB 初期化、DB 読込補助、件数表示、一覧表示の責務を `Clix` 側へ移すことを対象とする。
- `run`, `clear`, `count`, `print-list-text` の CLI 公開挙動維持を対象とする。
- `TopConfigDb`、`Subapp`、各 scraper、DB 実装、依存パッケージ `yklibpy` の変更は対象外とする。

## 3. 参照ファイル

- `_private/20260313/fusion_class_top_and_clix-req.md`
- `_private/refactoring_class_clix-spec.md`
- `_private/remove_unuse_class_top-spec.md`
- `src/htmlparser/top.py`
- `src/htmlparser/clix.py`
- `src/htmlparser/topconfigdb.py`
- `src/htmlparser/__init__.py`

## 4. 現行外部仕様

### 4.1 `Top` の現行責務

現行の `Top` クラスは、少なくとも以下の責務を持つ。

- `TopConfigDb(parent_path, assoc)` を生成し、`top_config` として保持する。
- `top_config` から DB ファイルパスと DB 種別を取得し、DB を生成して `db` として保持する。
- `db_loadx()` により YAML タグ指定付きの DB 読込を行う。
- `db_count()` により DB 件数を表示する。
- `db_print_list_text(key)` により DB の文字列一覧を表示する。

### 4.2 `Clix` の現行責務

現行の `Clix` クラスは、少なくとも以下の責務を持つ。

- `run`, `clear`, `count`, `print-list-text` の各サブコマンドを登録する。
- 各サブコマンドに必須引数 `config_file` を登録する。
- `print-list-text` にオプション引数 `--key` を登録し、既定値を `"title"` とする。
- `load_config_file_from_args(args)` により設定ファイルを読込む。
- `build_top_from_args(args)` により `Top` を生成する。
- 各 `*_command` 関数で `Top` を利用して業務処理を実行する。

### 4.3 現行 CLI 仕様

- 公開サブコマンドは `run`, `clear`, `count`, `print-list-text` である。
- 全サブコマンドは必須引数 `config_file` を受け付ける。
- `print-list-text` はオプション引数 `--key` を受け付け、既定値は `"title"` である。
- `run_command(args)`, `clear_command(args)`, `count_command(args)`, `print_list_text_command(args)` は正常終了時に `0` を返す。

### 4.4 現行の処理分担

- 設定ファイルのパス解決と YAML 読込は `Clix` 側が担当する。
- `TopConfigDb` の保持と DB 生成は `Top` 側が担当する。
- DB 読込補助と出力補助は `Top` 側が担当する。
- 実際の CLI 業務処理の流れ制御は `Clix` 側が担当する。

## 5. 変更後外部仕様

### 5.1 統合方針

変更後は、`Top` クラスが担っていた責務を `Clix` または `src/htmlparser/clix.py` 内の補助関数へ統合し、`Top` クラスを削除しなければならない。

### 5.2 `Top` から移管する責務

変更後は、少なくとも以下の責務を `Clix` 側へ移管しなければならない。

- `TopConfigDb` の生成と保持に必要な共通初期化処理
- DB ファイルパスと DB 種別の検証
- DB インスタンス生成
- YAML タグ指定付き DB 読込
- DB 件数表示
- DB 一覧表示

### 5.3 変更後のコマンド処理要件

変更後の `run_command(args)`, `clear_command(args)`, `count_command(args)`, `print_list_text_command(args)` は、`Top` に依存せず、`Clix` 側へ統合された初期化済みオブジェクトまたは補助処理を通じて必要な処理を実行しなければならない。

- `run_command(args)` は設定読込、DB 読込、HTML 解析、DB 保存、件数表示を継続できなければならない。
- `clear_command(args)` は設定読込、DB 消去、DB 保存を継続できなければならない。
- `count_command(args)` は設定読込、DB 読込、件数表示を継続できなければならない。
- `print_list_text_command(args)` は設定読込、DB 読込、一覧表示を継続できなければならない。

### 5.4 `Clix` 側の責務

変更後の `Clix` 側は、少なくとも以下を満たさなければならない。

- 現行どおり CLI サブコマンドと引数定義を提供すること。
- 設定ファイル読込から `TopConfigDb` 準備、DB 準備までの初期化を一貫して実行できること。
- `Top` が持っていた DB 補助処理を、`Clix` 自身または `clix.py` 内の補助処理として再提供できること。
- 各コマンド関数が `Top` を経由せずに業務処理を継続できること。

### 5.5 実装自由度

- `Top` の責務を `Clix` のメソッドに移すか、`clix.py` 内の補助関数に移すかは本仕様では規定しない。
- `TopConfigDb` と DB をまとめる補助データ構造を導入するかどうかは本仕様では規定しない。
- YAML タグの保持方法、共通初期化メソッド名、ローカル変数名は本仕様では規定しない。

### 5.6 削除要件

変更後は、少なくとも以下を満たさなければならない。

- `src/htmlparser/top.py` に `Top` クラスが定義されていないこと。
- `src/htmlparser/clix.py` が `Top` を import していないこと。
- `Clix` の各コマンド処理が `Top(...)` の生成に依存していないこと。

### 5.7 維持しなければならない公開挙動

統合後も、利用者から見える以下の挙動は変更してはならない。

- 公開サブコマンド名は `run`, `clear`, `count`, `print-list-text` を維持すること。
- 必須引数 `config_file` の仕様を変更しないこと。
- `print-list-text --key` の仕様と既定値 `"title"` を変更しないこと。
- 正常終了時の終了コード `0` を維持すること。
- 設定ファイル形式、DB 入出力形式、件数表示、一覧表示の利用者向け意味を変更しないこと。
- `run_command(args)` における `Subapp` を用いた HTML 解析と DB 更新フローを変更しないこと。

## 6. 非対象

以下は本仕様の対象外とする。

- `TopConfigDb` の設定取得仕様変更
- `Subapp` および各 scraper の処理変更
- YAML 設定ファイル形式の変更
- DB スキーマおよび保存形式の変更
- `yklibpy` パッケージの実装変更
- `run`, `clear`, `count`, `print-list-text` 以外の CLI 仕様変更
- `Top` 削除以外を目的とした `__init__.py` の公開 API 拡張

## 7. 互換性方針

- 互換性維持の対象は、`htmlparser` の CLI 利用者から観測できる引数、出力、終了コードとする。
- `Top` の削除は内部実装変更として扱い、CLI 利用者から見える操作手順は変更しない。
- `Top` の責務移管に伴う関数分割、補助メソッド導入、データ構造導入などの内部構造変更は許容する。
- `TopConfigDb` を通じて取得している設定情報の意味は維持する。
- 既存の DB 読込時に必要な YAML タグの互換性は維持する。

## 8. 実装制約

- 統合は `htmlparser` 側だけで完結させること。
- 依存パッケージ `yklibpy` は変更しないこと。
- `Top` の責務を代替する処理は `src/htmlparser/clix.py` を中心に実装すること。
- `run_command(args)`, `clear_command(args)`, `count_command(args)`, `print_list_text_command(args)` は、いずれも `Top` を経由しないこと。
- `Top` 削除後も `TopConfigDb` は再利用することを妨げない。
- 変更判定は `src/htmlparser/top.py`、`src/htmlparser/clix.py`、必要に応じて `src/htmlparser/__init__.py` を基準に行うこと。

## 9. 受け入れ条件

- `src/htmlparser/top.py` に `Top` クラスが存在しないこと。
- `src/htmlparser/clix.py` に `from htmlparser.top import ... Top` 相当の依存が残っていないこと。
- `src/htmlparser/clix.py` が、設定読込後に `TopConfigDb` と DB を使って現行同等の処理を継続できる構造になっていること。
- `run_command(args)` が DB 読込、`Subapp` 実行、DB 保存、件数表示を引き続き行えること。
- `clear_command(args)` が DB 消去と保存を引き続き行えること。
- `count_command(args)` が DB 読込と件数表示を引き続き行えること。
- `print_list_text_command(args)` が DB 読込と `--key` に基づく一覧表示を引き続き行えること。
- `run`, `clear`, `count`, `print-list-text` の公開 CLI 名が変更されていないこと。
- 全サブコマンドの `config_file` 必須引数仕様が維持されていること。
- `print-list-text --key` の既定値 `"title"` が維持されていること。
- 正常終了時に各コマンドが `0` を返す仕様が維持されていること。
- `TopConfigDb`、`Subapp`、各 scraper、`yklibpy` の外部仕様に変更が入らないこと。

## 10. 備考

- 本仕様は外部仕様書であり、`Top` の責務を置き換える具体的なメソッド名、補助関数名、補助クラス名までは規定しない。
- 本仕様の主眼は、`Top` と `Clix` の責務を統合して `Top` を削除することと、公開 CLI 挙動を不変に保つことにある。
