# clix-spec

## 1. 目的

`_private/20260120/clix-req.md` の要求を満たすため、`htmlparser` パッケージに追加する統合 CLI の外部仕様を定義する。

この仕様では、`yklibpy.cli.cli.Cli` を利用する `Clix` クラスと、`Clix` から呼び出されるクラス外関数を定義対象とする。

## 2. スコープ

- 対象は `htmlparser` の CLI 公開面である。
- 既存のスクレイパー実装、`Top`、`TopConfigDb`、`Subapp` の内部処理は原則として再利用する。
- 既存の `amain()`, `clearmain()`, `count()`, `print_list_text()`, `prepare()` は互換性維持のため残してよい。
- 新しい主 CLI はサブコマンド方式とする。

## 3. 参照実装

- `src/htmlparser/top.py`
- `src/htmlparser/__init__.py`
- `pyproject.toml`
- `E:/Ccur/python3/yklibpy/src/yklibpy/cli/cli.py`
- `E:/Ccur/python3/ghrepo/src/ghrepo/clix.py`

## 4. 配置仕様

### 4.1 モジュール

- `src/htmlparser/clix.py`
  - `Clix` クラスを定義する。
- `src/htmlparser/clix.py` または `src/htmlparser/cli_commands.py`
  - CLI 用の独立関数を定義する。

この仕様書では、説明を簡潔にするため独立関数も `clix.py` に定義する前提で記載する。

## 5. CLI 概要

### 5.1 エントリポイント

- 主エントリポイントは `htmlparser` とする。
- 推奨実装は `htmlparser.clix:main` を `project.scripts` に割り当てる。

### 5.2 サブコマンド一覧

| サブコマンド | 役割 | 既存関数との対応 |
| --- | --- | --- |
| `run` | HTML 解析を実行し DB を更新する | `amain()` |
| `clear` | DB を初期化する | `clearmain()` |
| `count` | DB 件数を表示する | `count()` |
| `print-list-text` | DB の文字列一覧を表示する | `print_list_text()` |
| `prepare` | 作業ディレクトリを準備する | `prepare()` |

### 5.3 共通引数

全サブコマンドは位置引数 `config_file` を必須とする。

- 型: `str`
- 内容: YAML 設定ファイルのパス
- 解決規則: カレントディレクトリ基準または絶対パス

### 5.4 個別引数

`print-list-text` は以下のオプションを持つ。

- `--key`
  - 型: `str`
  - 既定値: `"title"`
  - 意味: `DbYaml.list_text()` に渡すキー名

他のサブコマンドは、初版では `config_file` のみを受け付ける。

## 6. クラス仕様

## `Clix`

### 6.1 役割

`Clix` は `yklibpy.cli.Cli` の薄いラッパーであり、`htmlparser` 用サブコマンドと引数を登録する責務を持つ。

### 6.2 依存

- `from yklibpy.cli import Cli`
- `argparse`

### 6.3 外部コンストラクタ仕様

```python
class Clix:
    def __init__(
        self,
        description: str,
        command_dict: dict[str, Callable[[argparse.Namespace], int | None]],
    ) -> None: ...
```

#### 入力

- `description`
  - `argparse.ArgumentParser` の説明文。
- `command_dict`
  - サブコマンド名から実行関数への辞書。
  - 必須キーは `run`, `clear`, `count`, `print-list-text`, `prepare`。

#### 振る舞い

- `Cli(description)` を生成し、内部に保持する。
- `self.cli.get_subparsers("command")` を呼び出し、サブコマンド群を生成する。
- 各サブコマンドに対し `set_defaults(func=...)` を設定する。
- 各サブコマンドへ必要な引数を登録する。

#### 事後条件

- `parse_args()` 実行後、返却される `Namespace` は以下を必ず持つ。
  - `command`
  - `func`
  - `config_file`
- `print-list-text` の場合のみ `key` も持つ。

### 6.4 公開メソッド仕様

```python
def get_subparsers(self, name: str) -> Any: ...
```

- 役割: 内包する `Cli.get_subparsers()` をそのまま委譲する。
- 用途: 追加サブコマンドを外部で定義したい場合の拡張点。

```python
def parse_args(self) -> argparse.Namespace: ...
```

- 役割: コマンドライン引数を解析する。
- 戻り値: `argparse.Namespace`
- 例外:
  - 不正な引数が与えられた場合、`argparse` 標準の終了動作に従う。

### 6.5 非機能要件

- `Clix` は業務処理を持たない。
- HTML 解析、DB 操作、設定ファイル読込は独立関数へ委譲する。
- `Cli` のラッパーとして、構成情報の集約だけを担当する。

## 7. 独立関数仕様

## `build_command_dict`

```python
def build_command_dict() -> dict[str, Callable[[argparse.Namespace], int | None]]: ...
```

### 役割

`Clix` に渡すコマンド辞書を構築する。

### 戻り値

以下のキーを持つ辞書を返す。

- `run`
- `clear`
- `count`
- `print-list-text`
- `prepare`

## `resolve_config_path`

```python
def resolve_config_path(args: argparse.Namespace) -> Path: ...
```

### 役割

`args.config_file` から設定ファイルパスを取得し、`Path` に変換する。

### 入力条件

- `args.config_file` が存在すること。

### 例外

- `config_file` 属性が無い場合は `ValueError`。
- 空文字列の場合は `ValueError`。

## `load_config_file_from_args`

```python
def load_config_file_from_args(args: argparse.Namespace) -> ConfigFileInfo: ...
```

### 役割

CLI 引数から設定ファイルを読み込み、`ConfigFileInfo` を返す。

### 処理

- `resolve_config_path(args)` を呼ぶ。
- `UtilYaml.load_yaml()` で YAML を読み込む。
- `parent_path` と `assoc` を返す。

### 備考

既存の `top.py` にある `sys.argv` 依存の `get_yaml_path()` / `load_config_file()` を、`argparse.Namespace` ベースに置き換えるための関数である。

## `run_command`

```python
def run_command(args: argparse.Namespace) -> int: ...
```

### 役割

既存の `amain()` と同等の処理を、`args.config_file` 基準で実行する。

### 処理概要

1. 設定ファイルを読み込む。
2. `Top` を生成する。
3. `db_loadx()` で DB を読み込む。
4. `Subapp` を生成する。
5. `patterns` を順に処理し、`env.set_pattern()` と `app.run(env)` を呼ぶ。
6. 解析結果を DB に保存する。
7. 件数を表示する。

### 戻り値

- 正常終了時は `0`

### 例外

- `db_file` 未設定時は `ValueError`
- `db_kind` 未設定時は `ValueError`
- 未対応 `db_kind` は `ValueError`
- `env.set_pattern()` の結果が `None` の場合は `ValueError`

## `clear_command`

```python
def clear_command(args: argparse.Namespace) -> int: ...
```

### 役割

既存の `clearmain()` と同等の処理を実行する。

### 処理概要

- 設定ファイルを読み込む。
- `Top` を生成する。
- DB を `clear()` して保存する。

### 戻り値

- 正常終了時は `0`

## `count_command`

```python
def count_command(args: argparse.Namespace) -> int: ...
```

### 役割

既存の `count()` と同等の処理を実行する。

### 処理概要

- 設定ファイルを読み込む。
- `Top` を生成する。
- `db_loadx()` を実行する。
- 件数を表示する。

### 戻り値

- 正常終了時は `0`

## `print_list_text_command`

```python
def print_list_text_command(args: argparse.Namespace) -> int: ...
```

### 役割

既存の `print_list_text()` を拡張し、キー名を引数で受け取れるようにする。

### 入力

- `args.key`
  - 省略時は `"title"`

### 処理概要

- 設定ファイルを読み込む。
- `Top` を生成する。
- `db_loadx()` を実行する。
- `top.db_print_list_text(args.key)` を呼ぶ。

### 戻り値

- 正常終了時は `0`

## `prepare_command`

```python
def prepare_command(args: argparse.Namespace) -> int: ...
```

### 役割

既存の `prepare()` と同等の処理を実行する。

### 処理概要

- 設定ファイルを読み込む。
- `category = "htmlparser"` を使って `Top.prepare()` を呼ぶ。

### 戻り値

- 正常終了時は `0`

## `main`

```python
def main() -> int: ...
```

### 役割

統合 CLI のエントリポイント。

### 処理

1. `build_command_dict()` を呼ぶ。
2. `Clix("HTML parser utility", command_dict)` を生成する。
3. `args = clix.parse_args()` を実行する。
4. `return int(args.func(args) or 0)` を返す。

### 事後条件

- 選択されたサブコマンドの処理結果がプロセス終了コードに反映される。

## 8. 既存 API との対応

| 新仕様 | 既存実装 | 備考 |
| --- | --- | --- |
| `Clix` | なし | `ghrepo.clix.Clix` と同型 |
| `run_command(args)` | `amain()` | `sys.argv` 依存を排除 |
| `clear_command(args)` | `clearmain()` | 同上 |
| `count_command(args)` | `count()` | 同上 |
| `print_list_text_command(args)` | `print_list_text()` | `--key` を追加 |
| `prepare_command(args)` | `prepare()` | `category="htmlparser"` を維持 |
| `main()` | なし | 新しい統合 CLI 入口 |

## 9. 互換性方針

- 既存の個別エントリポイントは、初版では残してよい。
- 既存関数は互換ラッパーとしてもよいが、新規 CLI 実装では `argparse.Namespace` ベースの独立関数を正とする。
- 将来的に `amain()` などを薄い互換関数へ変更しても、この仕様との整合は保たれる。

## 10. 非対象

- `Top`、`TopConfigDb`、`Subapp`、各 `Scraper` の内部アルゴリズム変更
- YAML 設定フォーマットの変更
- DB スキーマ変更
- 新しいスクレイパーモード追加

## 11. 受け入れ条件

- `Clix` が `Cli` を内包していること。
- `run`, `clear`, `count`, `print-list-text`, `prepare` の 5 サブコマンドが定義されること。
- 全サブコマンドが必須引数 `config_file` を受けること。
- `print-list-text` が `--key` を受けること。
- 独立関数が `argparse.Namespace` を入力として受けること。
- 主エントリポイント `main()` が `args.func(args)` を実行すること。
