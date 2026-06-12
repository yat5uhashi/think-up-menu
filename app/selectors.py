"""読み取り系のクエリ（get / list）。

ルール:
- 書き込みは行わない（書き込みは services.py）。
- ``get_`` は単一取得、``list_`` は複数取得で命名する。
- ``request`` を引数に取らない。

詳細は docs/architecture.md を参照。
"""

# 例:
# def list_recipes(*, keyword: str | None = None) -> QuerySet[Recipe]:
#     """レシピ一覧を返す。keyword 指定時は名前で絞り込む。"""
#     ...
