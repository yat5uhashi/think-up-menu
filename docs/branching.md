# ブランチ運用ルール

シンプルな **main + feature/fix** ブランチ運用を採用する。

## ブランチの種類

| ブランチ | 用途 | 例 |
|---|---|---|
| `main` | 常に動く（テストが通る）状態を保つ。デプロイ対象 | `main` |
| `feature/<内容>` | 新機能の追加 | `feature/menu-suggest` |
| `fix/<内容>` | バグ修正 | `fix/login-error` |

- `<内容>` は**英小文字・ハイフン区切り**で、何をするか分かる短い名前にする。
- 必要なら末尾に Issue 番号を付けてもよい：`feature/recipe-search-12`。

## 基本フロー

```powershell
# 1. main を最新にして、そこから作業ブランチを切る
git switch main
git pull
git switch -c feature/menu-suggest

# 2. 作業してコミット（コミット規約は coding-style.md 参照）
git add -A
git commit -m "feat: 献立提案APIを追加"

# 3. リモートに push
git push -u origin feature/menu-suggest

# 4. GitHub で Pull Request を作成 → CI(Lint & Test)が緑になるのを確認 → レビュー → マージ

# 5. マージ後、不要になったブランチは削除
git switch main
git pull
git branch -d feature/menu-suggest
```

## ルール

- **`main` に直接 push しない**。変更は必ず `feature/` または `fix/` ブランチ → Pull Request 経由で入れる。
- **PR は CI(Lint & Test)が緑になってからマージ**する（[ci.md](ci.md)）。
- 1ブランチ＝1つの目的。大きくなりすぎたら分割する。
- マージ済みブランチは削除して、ブランチ一覧を整理しておく。
- ブランチは**こまめに `main` を取り込む**（`git pull origin main` などで）と、コンフリクトが小さく済む。

## マージ方式

- **Squash and merge** を基本にする（PR の細かいコミットを1つにまとめて `main` をきれいに保つ）。
- マージ後のコミットメッセージも規約のプレフィックス（`feat:` / `fix:` など）に揃える。

## ブランチ名とコミットの対応

| ブランチ | 主に使うコミットプレフィックス |
|---|---|
| `feature/...` | `feat:`（付随して `test:` `docs:` `refactor:` も可） |
| `fix/...` | `fix:` |

コミットメッセージのプレフィックス一覧は [coding-style.md](coding-style.md#git-コミット規約) を参照。
