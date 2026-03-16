# remove_subcommand_prepare-spec

## 1. 目的

`_private/20260312/remove_subcommand_prepare-req.md` の要求を満たすため、`htmlparser` パッケージの公開 CLI 仕様から `prepare` サブコマンドを削除するための外部仕様を定義する。

この仕様は、削除対象となる公開面、削除後に維持する公開面、依存パッケージ `yklibpy` を変更しない条件を明確にすることを目的とする。

## 2. スコープ

- 対象は `htmlparser` パッケージの公開 CLI 仕様とする。
- 主な対象ファイルは `pyproject.toml` と `src/htmlparser/clix.py` とする。
- `prepare` サブコマンドの公開有無、および公開コマンド一覧の変更を対象とする。
- `yklibpy` パッケージの実装変更は対象外とする。
- `htmlparser` のスクレイパー処理、DB 処理、設定ファイル形式の変更は対象外とする。

## 3. 参照ファイル

- `_private/20260312/remove_subcommand_prepare-req.md`
- `_private/clix-spec.md`
- `pyproject.toml`
- `src/htmlparser/clix.py`
- `src/htmlparser/top.py`
- `E:/Ccur/python3/yklibpy/src/yklibpy/htmlparser/preparex.py`

## 4. 現行公開仕様

### 4.1 公開エントリポイント

現行の有効な公開エントリポイントは、`pyproject.toml` の `[project.scripts]` に定義された以下のみとする。

- `htmlparser = "htmlparser.clix:main"`

コメントアウトされた旧エントリポイントは、現行の公開仕様には含めない。

### 4.2 現行サブコマンド一覧

現行の `htmlparser` CLI では、以下の 5 サブコマンドが利用可能である。

- `run`
- `clear`
- `count`
- `print-list-text`
- `prepare`

### 4.3 `prepare` の現行位置づけ

- `prepare` は独立したコンソールスクリプトではなく、`htmlparser` のサブコマンドとして公開されている。
- `prepare` は `config_file` を必須引数として受け取る。
- `prepare` の実処理は `src/htmlparser/clix.py` の `prepare_command()` から `src/htmlparser/top.py` の `Top.prepare()` に委譲される。
- `Top.prepare()` は依存パッケージ `yklibpy` の `Preparex` を利用する。

## 5. 変更後公開仕様

### 5.1 公開エントリポイント

変更後も、公開エントリポイントは以下を維持する。

- `htmlparser = "htmlparser.clix:main"`

### 5.2 公開サブコマンド一覧

変更後に公開仕様として利用可能でなければならないサブコマンドは以下の 4 件とする。

- `run`
- `clear`
- `count`
- `print-list-text`

`prepare` は公開サブコマンド一覧から削除する。

### 5.3 削除対象

公開 CLI 仕様として、少なくとも以下を削除対象とする。

- `Clix` における `prepare` サブコマンド定義
- `build_command_dict()` における `prepare` コマンド登録
- 利用者向け公開仕様上の `prepare` サブコマンド記載

### 5.4 削除後の利用者観点の挙動

- 利用者は `htmlparser prepare <config_file>` を公開手順として利用できない。
- `htmlparser --help` またはサブコマンド一覧に `prepare` は表示されない。
- `htmlparser` CLI の通常利用手順は、`run`, `clear`, `count`, `print-list-text` を前提とする。

## 6. 非対象

以下は本仕様の対象外とする。

- `yklibpy` 側の `Preparex` 実装変更
- `src/htmlparser/top.py` にある内部補助実装の削除要否判断
- `prepare` 以外のサブコマンド仕様変更
- YAML 設定ファイル形式の変更
- DB 形式変更
- スクレイパーの解析アルゴリズム変更

## 7. 互換性方針

- 既存利用者が `htmlparser prepare <config_file>` を実行していた場合、変更後はその呼び出しは互換対象外とする。
- ただし、`prepare` 以外の `run`, `clear`, `count`, `print-list-text` の公開仕様は維持する。
- `prepare` の内部実装がソースコード上に一時的に残るかどうかは、この外部仕様では規定しない。
- 内部未使用定義の整理は、必要に応じて別仕様で扱う。

## 8. 実装制約

- `yklibpy` パッケージは変更しないこと。
- `htmlparser` 側の変更だけで `prepare` の公開停止を実現すること。
- 公開面の変更は、`pyproject.toml` と `src/htmlparser/clix.py` を基準に判断すること。

## 9. 受け入れ条件

- `htmlparser` の公開サブコマンド一覧に `prepare` が含まれないこと。
- `src/htmlparser/clix.py` で `prepare` サブコマンドが登録されていないこと。
- `build_command_dict()` から `prepare` の公開コマンド対応が除去されていること。
- `pyproject.toml` の有効な公開エントリポイントが引き続き `htmlparser = "htmlparser.clix:main"` であること。
- `run`, `clear`, `count`, `print-list-text` の 4 サブコマンドが引き続き利用可能であること。
- 依存パッケージ `yklibpy` に変更が入らないこと。

## 10. 備考

- `prepare` の実処理本体は `htmlparser` 側の公開 CLI から切り離すだけでよく、依存先実装の削除までは要求しない。
- この仕様書は外部仕様書であり、内部実装の後片付けや未使用コード削除の詳細までは定義しない。
