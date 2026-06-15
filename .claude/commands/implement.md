---
description: 確定済み仕様(docs/specs/)に基づき、規約に沿って機能を実装する
argument-hint: <機能名 または specファイル名>
---

あなたは think-up-menu（献立提案アプリ）の実装を担当します。
対象機能: **$ARGUMENTS**

## 前提

- 対応する仕様書が `docs/specs/` にあり、ステータスが「確定」であること。
  無い／ドラフトの場合は実装に入らず、先に `/spec` で仕様を固めるよう促す。

## 進め方

1. **仕様と規約を読む**:
   - 対象の仕様書: @docs/specs/
   - @docs/architecture.md（薄いView / 厚いservices・selectors）
   - @docs/coding-style.md（命名・型・docstring）
   - @docs/api-conventions.md / @docs/error-handling.md / @docs/logging.md
   - @docs/directory.md（配置） / @docs/authentication.md（認証）

2. **作業ブランチを切る**（@docs/branching.md）:
   - 新機能は `feature/<slug>`、バグ修正は `fix/<slug>`。
   - `main` には直接コミットしない。

3. **実装する**（レイヤーを守る）:
   - モデル → serializers → services/selectors → views → urls の順で、責務を分けて書く。
   - ビジネスロジックは services/selectors に置き、View は薄く保つ。
   - 例外は `core/exceptions.py` のドメイン例外を使う。
   - ログは `logging.getLogger(__name__)`。

4. **テストを書く**（@docs/testing.md）:
   - 仕様の「受け入れ基準」をテストに落とす。
   - services/selectors を優先し、API の正常系＋異常系も最低1本ずつ。

5. **品質ゲートを通す**（push 前に必ず）:
   - `uv run ruff format .`
   - `uv run ruff check --fix .`
   - `uv run pytest`
   - 必要に応じて `/code-review` でレビュー。

6. **コミット & push**（@docs/coding-style.md のコミット規約）:
   - `feat:` / `fix:` などのプレフィックス付き。
   - ブランチを push し、PR 作成を促す（main へは PR 経由）。

## 原則

- 仕様にないものを勝手に足さない。仕様で迷ったら確認する（実装を止めて質問）。
- マイグレーションが出たら必ずコミットに含める。
- 秘密情報はコードに書かず `.env` 経由。
