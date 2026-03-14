すべてのクラスのメソッド定義、クラス独立の関数定義のうち、pyproject.tomlにおいて外部から呼び出されるものを除いて、内部において、他のクラス定義メソッド、クラス独立の関数から呼び出されないものを削除して。
そのうち、以下のものは必ず削除して。
- Clix.get_subparsers()
- Top.db_load()
- Top.save()
- TopConfigDb.get_db_file_name()