# refactoring_class_clix-2-spec

## 1. 目的

`_private/20260313/refactoring_class_clix-2-req.md` の要求を満たすため、`htmlparser` パッケージの `src/htmlparser/clix.py` にある `Clix` クラス外関数を、`main()` 関数を除いて `Clix` クラスのメソッドへ移行するための外部仕様を定義する。

この仕様は、移行対象、変更後に維持すべき CLI 公開挙動、ならびに実装上の制約を明確にすることを目的とする。

## 2. スコープ

- 対象は `src/htmlparser/clix.py` に定義された `Clix` クラス、および `Clix` クラス外に定義された CLI 関連関数とする。
- 主な対象ファイルは `src/htmlparser/clix.py` とする。
- `Clix` のクラス設計、および CLI コマンド実行処理の配置変更を対象とする。
- `main()` を除くクラス外関数のメソッド化を対象とする。
- `htmlparser` の公開サブコマンド名、引数仕様、戻り値仕様の維持を対象とする。
- `Top`, `TopConfigDb`, `Subapp`, DB 実装、依存パッケージ `yklibpy` の変更は対象外とする。

## 3. 参照ファイル

- `_private/20260313/refactoring_class_clix-2-req.md`
- `_private/refactoring_class_clix-spec.md`
- `_private/clix-spec.md`
- `pyproject.toml`
- `src/htmlparser/clix.py`
- `src/htmlparser/top.py`
- `src/htmlparser/topconfigdb.py`

## 4. 現行外部仕様

### 4.1 現行の `Clix` の責務

現行の `Clix` クラスは、少なくとも以下の責務を持つ。

- `Cli` を内包してサブコマンドを登録すること。
- `run`, `clear`, `count`, `print-list-text` の 4 個の公開サブコマンドを構成すること。
- `parse_args()` により CLI 引数解析を実行すること。

### 4.2 現行のクラス外関数

現行の `src/htmlparser/clix.py` には、`Clix` クラス外に少なくとも以下の関数が定義されている。

- `build_command_dict()`
- `resolve_config_path(args)`
- `load_config_file_from_args(args)`
- `build_top_from_args(args)`
- `run_command(args)`
- `clear_command(args)`
- `count_command(args)`
- `print_list_text_command(args)`
- `main()`

### 4.3 現行の処理分担

- `Clix` は CLI 構成と引数解析のみを担当する。
- 各 `*_command` 関数は、設定読込、`Top` 生成、DB 操作、表示処理などの実行処理を担当する。
- `resolve_config_path(args)`, `load_config_file_from_args(args)`, `build_top_from_args(args)` は、各コマンド関数から利用される補助関数である。
- `main()` はコマンド辞書を生成し、`Clix` を生成し、解析済み引数に基づいて実行関数を呼び出すエントリポイントである。

### 4.4 現行 CLI 仕様

- 公開サブコマンドは `run`, `clear`, `count`, `print-list-text` である。
- 全サブコマンドは必須引数 `config_file` を受け付ける。
- `print-list-text` はオプション引数 `--key` を受け付け、既定値は `"title"` である。
- 各コマンド処理は正常終了時に `0` を返す。
- `pyproject.toml` のエントリポイントは `htmlparser.clix:main` である。

## 5. 変更後外部仕様

### 5.1 メソッド化対象

変更後は、`src/htmlparser/clix.py` において `main()` を除く CLI 関連のクラス外関数を、`Clix` クラスのメソッドとして配置しなければならない。

少なくとも、現行で以下に相当する関数は `Clix` のメソッド化対象とする。

- コマンド辞書構築処理
- 設定ファイルパス解決処理
- CLI 引数からの設定読込処理
- `Top` 生成処理
- `run` の実行処理
- `clear` の実行処理
- `count` の実行処理
- `print-list-text` の実行処理

### 5.2 `Clix` の変更後責務

変更後の `Clix` は、少なくとも以下の責務を持たなければならない。

- 公開サブコマンドと引数を登録すること。
- 各サブコマンドに対応する実行処理を自身のメソッドとして保持すること。
- コマンド実行に必要な補助処理を自身のメソッドとして保持できること。
- `parse_args()` により CLI 引数解析を継続して提供すること。

### 5.3 共通前処理の扱い

前段仕様 `_private/refactoring_class_clix-spec.md` で要求された、対象コマンドに共通する前処理の一元化は、変更後も維持しなければならない。

- `run`, `clear`, `count`, `print-list-text` の各実行処理は、設定読込および `Top` 初期化に関する共通前処理を共有しなければならない。
- その共通前処理は、変更後は `Clix` のメソッドとして配置されてよい。
- 共通前処理の具体的なメソッド名、戻り値型、内部実装の詳細は本仕様では規定しない。

### 5.4 各コマンド処理の責務

変更後の各コマンド処理メソッドは、少なくとも以下の責務を持たなければならない。

- `run` の実行処理は、解析実行、DB 更新、件数表示を担当する。
- `clear` の実行処理は、DB 消去と保存を担当する。
- `count` の実行処理は、DB 読込と件数表示を担当する。
- `print-list-text` の実行処理は、DB 読込と一覧表示を担当する。

### 5.5 `main()` の扱い

変更後も、`main()` は `Clix` クラス外の関数として維持しなければならない。

- `main()` は `pyproject.toml` のエントリポイント `htmlparser.clix:main` と整合すること。
- `main()` は CLI 起動用の外部入口として機能し、`Clix` を生成して実行処理へ委譲すること。
- `main()` の具体的な記述順や局所変数名は本仕様では規定しない。

### 5.6 維持しなければならない公開挙動

メソッド化後も、利用者から見える以下の挙動は変更してはならない。

- 公開サブコマンド名は `run`, `clear`, `count`, `print-list-text` を維持すること。
- 必須引数 `config_file` の仕様を変更しないこと。
- `print-list-text --key` の仕様と既定値 `"title"` を変更しないこと。
- 正常終了時の終了コード `0` を維持すること。
- 設定ファイル形式、DB 入出力形式、件数表示および一覧表示の利用者向け意味を変更しないこと。

## 6. 非対象

以下は本仕様の対象外とする。

- `Top` クラス内部の設計変更
- `TopConfigDb` の設定取得仕様変更
- `Subapp` および各スクレイパーの処理変更
- YAML 設定ファイル形式の変更
- DB スキーマおよび保存形式の変更
- `yklibpy` パッケージの実装変更
- `run`, `clear`, `count`, `print-list-text` 以外の CLI 機能追加
- 旧仕様書にある `prepare` サブコマンドの復活や再導入

## 7. 互換性方針

- 互換性維持の対象は、`htmlparser` の CLI 利用者から観測できる引数、出力、終了コードとする。
- メソッド化は内部構造変更として扱い、利用者向けの操作手順は変えない。
- `main()` は外部エントリポイントとして維持しつつ、実処理を `Clix` に集約してよい。
- 補助処理やコマンド処理の配置が変更されても、現行 CLI の利用方法は維持する。

## 8. 実装制約

- 変更は `htmlparser` 側だけで完結させること。
- 依存パッケージ `yklibpy` は変更しないこと。
- `main()` 以外の CLI 関連クラス外関数は、変更後に `Clix` クラス外へ残してはならない。
- 共通前処理の一元化は失ってはならない。
- 実装可否の判定は `src/htmlparser/clix.py` を基準に行うこと。

## 9. 受け入れ条件

- `src/htmlparser/clix.py` において、`main()` を除く CLI 関連処理が `Clix` クラス内に配置されていること。
- `run`, `clear`, `count`, `print-list-text` に対応する実行処理が、`Clix` のメソッドとして定義されていること。
- 設定ファイルパス解決、設定読込、`Top` 生成に相当する補助処理が、`Clix` のメソッドとして定義されていること。
- `run`, `clear`, `count`, `print-list-text` の各実行処理が、共通前処理を共有する構造になっていること。
- `src/htmlparser/clix.py` に、`main()` を除く CLI 関連クラス外関数が残っていないこと。
- `main()` が `Clix` を生成し、解析済み引数に応じて処理を起動する外部エントリポイントとして維持されていること。
- `run`, `clear`, `count`, `print-list-text` の公開 CLI 名が変更されていないこと。
- 全サブコマンドの `config_file` 必須引数仕様が維持されていること。
- `print-list-text --key` の既定値 `"title"` が維持されていること。
- 正常終了時に各コマンドが `0` を返す仕様が維持されていること。
- `Top`, `TopConfigDb`, `Subapp`, `yklibpy` の外部仕様に変更が入らないこと。

## 10. 備考

- 本仕様は外部仕様書であり、メソッド名、`@staticmethod` や `@classmethod` の利用有無、コマンド辞書の構築方法、ローカル変数名などの実装詳細までは規定しない。
- 本仕様の主眼は、`Clix` への責務集約と公開 CLI 挙動の不変性にある。
- `_private/clix-spec.md` に記載されている `prepare` を含む旧前提とは切り分け、現行実装に存在する 4 コマンドを基準に適用する。
