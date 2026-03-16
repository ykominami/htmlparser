# refactoring_class_clix-spec

## 1. 目的

`_private/20260313/refactoring_class_clix-req.md` の要求を満たすため、`htmlparser` パッケージの `src/htmlparser/clix.py` にある各コマンド関数の共通処理を 1 個の関数へ集約するための外部仕様を定義する。

この仕様は、共通化の対象範囲、変更後に維持すべき CLI 公開挙動、ならびに実装上の制約を明確にすることを目的とする。

## 2. スコープ

- 対象は `src/htmlparser/clix.py` に定義された CLI 用コマンド関数とする。
- 主な対象ファイルは `src/htmlparser/clix.py` と `src/htmlparser/top.py` とする。
- 各 `*_command` 関数が共有する設定読込から `Top` 初期化までの前処理共通化を対象とする。
- `htmlparser` の公開サブコマンド名、引数仕様、戻り値仕様の維持を対象とする。
- `Top` の内部ロジック、`Subapp` の解析処理、DB 実装、依存パッケージ `yklibpy` の変更は対象外とする。

## 3. 参照ファイル

- `_private/20260313/refactoring_class_clix-req.md`
- `_private/clix-spec.md`
- `_private/remove_unuse_class_top-spec.md`
- `src/htmlparser/clix.py`
- `src/htmlparser/top.py`

## 4. 現行外部仕様

### 4.1 対象コマンド関数

現行の `src/htmlparser/clix.py` には、少なくとも以下のコマンド関数が定義されている。

- `run_command(args)`
- `clear_command(args)`
- `count_command(args)`
- `print_list_text_command(args)`

### 4.2 現行の共通前処理

上記 4 関数は、いずれも少なくとも以下の前処理を個別に持っている。

- `load_config_file_from_args(args)` を呼び出して設定ファイル情報を取得する。
- 取得した `parent_path` と `assoc` を使って `Top(parent_path, assoc)` を生成する。

### 4.3 現行の個別処理

共通前処理の後に、各コマンド関数はそれぞれ以下の個別処理を行う。

- `run_command(args)` は `Top` と `Subapp` を使って HTML 解析結果を DB に保存し、件数を表示する。
- `clear_command(args)` は DB を消去して保存する。
- `count_command(args)` は DB を読み込み、件数を表示する。
- `print_list_text_command(args)` は DB を読み込み、指定キーの文字列一覧を表示する。

### 4.4 現行 CLI 仕様

- 公開サブコマンド `run`, `clear`, `count`, `print-list-text` は引き続き利用可能である。
- 全サブコマンドは必須引数 `config_file` を受け付ける。
- `print-list-text` はオプション引数 `--key` を受け付け、既定値は `"title"` である。
- 各コマンド関数は正常終了時に `0` を返す。

## 5. 変更後外部仕様

### 5.1 共通化対象

変更後は、`run_command(args)`, `clear_command(args)`, `count_command(args)`, `print_list_text_command(args)` に共通する前処理を、`src/htmlparser/clix.py` 内の 1 個の共通関数に集約しなければならない。

### 5.2 共通関数の責務

変更後の共通関数は、少なくとも以下の責務を持たなければならない。

- `args` から設定ファイル情報を取得すること。
- 設定ファイル情報をもとに `Top` を初期化すること。
- 各コマンド関数が個別処理に必要とする共通初期化済みオブジェクトを返すこと。

### 5.3 各コマンド関数の責務

変更後の各コマンド関数は、共通関数を呼び出したうえで、自身に固有の処理のみを担当しなければならない。

- `run_command(args)` は解析実行、DB 更新、件数表示を担当する。
- `clear_command(args)` は DB 消去と保存を担当する。
- `count_command(args)` は DB 読込と件数表示を担当する。
- `print_list_text_command(args)` は DB 読込と一覧表示を担当する。

### 5.4 実装自由度

- 共通関数名は本仕様では規定しない。
- 共通関数の戻り値が `Top` 単体であるか、または `Top` を含む補助オブジェクトであるかは本仕様では規定しない。
- `load_config_file_from_args(args)` を共通関数内で再利用するかどうかは本仕様では規定しない。

### 5.5 維持しなければならない公開挙動

共通化後も、利用者から見える以下の挙動は変更してはならない。

- 公開サブコマンド名は `run`, `clear`, `count`, `print-list-text` を維持すること。
- 必須引数 `config_file` の仕様を変更しないこと。
- `print-list-text --key` の仕様と既定値 `"title"` を変更しないこと。
- 正常終了時の終了コード `0` を維持すること。
- 設定ファイル形式、DB 入出力形式、件数表示および一覧表示の利用者向け意味を変更しないこと。

## 6. 非対象

以下は本仕様の対象外とする。

- `Top` クラス内部の設計変更
- `Subapp` および各スクレイパーの処理変更
- `TopConfigDb` の設定取得仕様変更
- YAML 設定ファイル形式の変更
- DB スキーマおよび保存形式の変更
- `yklibpy` パッケージの実装変更
- `run`, `clear`, `count`, `print-list-text` 以外の CLI 仕様変更

## 7. 互換性方針

- 互換性維持の対象は、`htmlparser` の CLI 利用者から観測できる引数、出力、終了コードとする。
- 関数分割や補助関数導入などの内部構造変更は許容する。
- 各 `*_command` 関数の責務が個別処理中心になるよう整理されても、現行 CLI の利用手順は変えない。
- 共通化のために内部実装が整理されても、利用者向けドキュメント上のコマンド利用方法は維持する。

## 8. 実装制約

- 共通化は `htmlparser` 側だけで完結させること。
- 依存パッケージ `yklibpy` は変更しないこと。
- 共通化対象は 1 個の関数として実装すること。
- 各対象コマンド関数は、その共通関数を経由して共通前処理を行うこと。
- 変更判定は `src/htmlparser/clix.py` を基準に行うこと。

## 9. 受け入れ条件

- `src/htmlparser/clix.py` に、対象コマンド関数の共通前処理を担当する関数が 1 個定義されていること。
- `run_command(args)`, `clear_command(args)`, `count_command(args)`, `print_list_text_command(args)` が、その共通関数を呼び出す構造になっていること。
- 各対象コマンド関数に `load_config_file_from_args(args)` と `Top(parent_path, assoc)` 相当の共通処理が重複して残っていないこと。
- `run`, `clear`, `count`, `print-list-text` の公開 CLI 名が変更されていないこと。
- 全サブコマンドの `config_file` 必須引数仕様が維持されていること。
- `print-list-text --key` の既定値 `"title"` が維持されていること。
- 正常終了時に各コマンドが `0` を返す仕様が維持されていること。
- `Top`, `Subapp`, `TopConfigDb`, `yklibpy` の外部仕様に変更が入らないこと。

## 10. 備考

- 本仕様は外部仕様書であり、共通関数の具体的な名称、戻り値型、ローカル変数名、記述順などの実装詳細までは規定しない。
- 本仕様の主眼は、共通処理の一元化と公開 CLI 挙動の不変性にある。
