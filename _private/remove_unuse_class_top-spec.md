# remove_unuse_class_top-spec

## 1. 目的

`_private/20260313/remove_unuse_class_top-req.md` の要求を満たすため、`htmlparser` パッケージ内の `Top` クラスに定義された未使用インスタンス変数を削除するための外部仕様を定義する。

この仕様は、削除対象となる属性、削除後に維持する属性、ならびに削除後も維持すべき CLI の動作範囲を明確にすることを目的とする。

## 2. スコープ

- 対象は `src/htmlparser/top.py` に定義された `Top` クラスのインスタンス変数とする。
- 主な対象ファイルは `src/htmlparser/top.py` と `src/htmlparser/clix.py` とする。
- `Top` の属性定義、および利用側コードから見た属性参照の整合を対象とする。
- `TopConfigDb` の設定取得仕様、DB 実装、CLI コマンド体系の変更は対象外とする。
- 依存パッケージ `yklibpy` の実装変更は対象外とする。

## 3. 参照ファイル

- `_private/20260313/remove_unuse_class_top-req.md`
- `_private/remove_subcommand_prepare-spec.md`
- `src/htmlparser/top.py`
- `src/htmlparser/clix.py`
- `src/htmlparser/topconfigdb.py`

## 4. 現行外部仕様

### 4.1 `Top` の現行属性

現行の `Top` クラスには、少なくとも以下のインスタンス変数が定義されている。

- `top_config`
- `patterns`
- `db_file_path`
- `db_kind`
- `db`

### 4.2 現行の利用実態

- `top_config` は、利用側コードから設定情報取得のために参照されている。
- `db` は、DB の読込、保存、件数取得、一覧出力のために参照されている。
- `patterns` は `Top` インスタンス生成時に設定されるが、利用側コードから参照されていない。
- `db_file_path` は `Top.setup()` 内で設定されるが、利用側コードから参照されていない。
- `db_kind` は `Top.setup()` 内で設定されるが、利用側コードから参照されていない。

### 4.3 現行 CLI との関係

- `run_command()` は `Top` から `db` を利用する。
- `run_command()` はパターン取得のために `top.patterns` ではなく `top.top_config.get_patterns()` を利用する。
- `clear_command()`, `count_command()`, `print_list_text_command()` は `Top` から `db` を利用する。

## 5. 変更後外部仕様

### 5.1 維持対象属性

変更後も、`Top` クラスの利用側から必要な属性として以下を維持する。

- `top_config`
- `db`

### 5.2 削除対象属性

変更後は、以下の属性を `Top` クラスから削除対象とする。

- `patterns`
- `db_file_path`
- `db_kind`

上記 3 件は必ず削除しなければならない。

### 5.3 削除後の利用側要件

- 利用側コードは `Top` のパターン取得に `top.patterns` を前提としてはならない。
- 利用側コードは `Top` の DB ファイルパス取得に `top.db_file_path` を前提としてはならない。
- 利用側コードは `Top` の DB 種別取得に `top.db_kind` を前提としてはならない。
- 利用側コードは、変更後も `top.top_config` および `top.db` を通じて必要な処理を継続できなければならない。

### 5.4 変更後の利用者観点の挙動

- `htmlparser` CLI の `run`, `clear`, `count`, `print-list-text` の動作は維持する。
- `Top` の未使用属性削除により、利用者向け CLI 引数、設定ファイル形式、DB 入出力形式は変更しない。
- `Top` の内部属性整理は、利用者向けの正常系動作に影響を与えてはならない。

## 6. 非対象

以下は本仕様の対象外とする。

- `TopConfigDb` が返す `patterns`, `db_file_path`, `db_kind` 自体の算出仕様変更
- `DbYaml` および `get_or_create_db()` の振る舞い変更
- `htmlparser` のコマンド追加、削除、名称変更
- YAML 設定ファイルのキー構成変更
- スクレイパー処理や DB データ内容の変更
- `Top` 以外のクラスにある未使用属性整理

## 7. 互換性方針

- 互換性維持の対象は、`Top` を利用する現行の `htmlparser` CLI 動作とする。
- `Top` の削除対象属性に直接依存していない現行コードについては、挙動互換を維持する。
- `patterns`, `db_file_path`, `db_kind` は未使用属性として扱い、変更後に保持しない。
- `top_config` および `db` を通じて実現されている現行処理フローは維持する。

## 8. 実装制約

- 変更は `htmlparser` 側だけで完結させること。
- `yklibpy` パッケージは変更しないこと。
- 削除対象属性の削除に伴い、利用側コードに不要な参照があれば `htmlparser` 側で整合させること。
- 削除判定は `src/htmlparser/top.py` と `src/htmlparser/clix.py` を基準に行うこと。

## 9. 受け入れ条件

- `src/htmlparser/top.py` の `Top` クラスに `patterns`, `db_file_path`, `db_kind` が定義されていないこと。
- `src/htmlparser/top.py` 内に、削除対象属性への代入処理が残っていないこと。
- `src/htmlparser/clix.py` を含む `htmlparser` 側の利用コードが、`top.patterns`, `top.db_file_path`, `top.db_kind` を参照していないこと。
- `Top` の `top_config` と `db` を用いた現行 CLI 処理が引き続き成立すること。
- `run`, `clear`, `count`, `print-list-text` の既存コマンド仕様に変更が入らないこと。
- 依存パッケージ `yklibpy` に変更が入らないこと。

## 10. 備考

- `db_file_path` と `db_kind` は現行実装では `setup()` 内で設定されるが、外部仕様上の保持義務はない。
- `patterns` は現行実装では設定されるが、利用側は `top.top_config.get_patterns()` を利用しており、`Top` 属性としては不要である。
- この仕様書は外部仕様書であり、削除に伴うローカル変数名や関数内記述の細かな整理方法までは規定しない。
