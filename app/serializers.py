"""DRF シリアライザ（入力バリデーション・出力JSON変換）。

ルール:
- バリデーションはここ。ビジネスロジックは services / selectors に置く。
- DB 更新ロジックを ``create()`` / ``update()`` に直接書きすぎない。
  複雑な場合は service を呼ぶ。

詳細は docs/architecture.md を参照。
"""

# 例:
# from rest_framework import serializers
#
# class RecipeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ["id", "name", ...]
