"""書き込み系のビジネスロジック（create / update / 複雑な処理）。

ルール:
- ``request`` を引数に取らない。必要な値（user 等）は呼び出し側が渡す。
- DB を変更する処理は ``@transaction.atomic`` で囲む。
- HTTP の知識を持たない（ステータスコード等は View 側の責務）。

詳細は docs/architecture.md を参照。
"""

# 例:
# from django.db import transaction
#
# @transaction.atomic
# def create_recipe(*, name: str, ...) -> Recipe:
#     """レシピを1件作成して返す。"""
#     ...
