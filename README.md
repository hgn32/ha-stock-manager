# Stock Manager（Home Assistant カスタム統合）

[Stock Manager アドオン](https://github.com/hgn32/ha-addons) の在庫データを Home Assistant に取り込むカスタム統合です。品目ごとの在庫数をセンサーとして公開し、在庫の消費・追加をサービスから実行できます。

## 必要要件

- Home Assistant
- Stock Manager アドオン（または同等の REST API を提供するサーバー）が稼働していること
  - 参照系: `/api/inventory`, `/api/categories`, `/api/locations`
  - 更新系: `/api/inventory/use`, `/api/inventory/add`

## インストール

### HACS（推奨）

1. HACS を開く
2. 右上のメニュー（⋮）→ **カスタムリポジトリ（Custom repositories）**
3. 次を入力して追加
   - リポジトリ: `https://github.com/hgn32/ha-stock-manager`
   - カテゴリ: **統合（Integration）**
4. 一覧から **Stock Manager** を検索してダウンロード
5. Home Assistant を再起動

### 手動インストール

1. このリポジトリの `custom_components/stock_manager/` を、Home Assistant の `config/custom_components/stock_manager/` にコピー
2. Home Assistant を再起動

## 設定（セットアップ）

1. **設定 → デバイスとサービス → 統合を追加** を開く
2. **Stock Manager** を検索
3. 接続情報を入力
   - **アドオンのURL**: 既定 `http://3a30c8ec-stock-manager:8099`（アドオンの内部ホスト名。HA内部ネットワークからのみ到達し、LANには公開されません）
   - **更新間隔（秒）**: デフォルト `300`（最小 `30`）

セットアップ後も、統合の **オプション** から URL・更新間隔を変更できます。接続確認に失敗した場合は「接続できませんでした。URLを確認してください。」と表示されます。

> **アドオンは Ingress 専用構成です。** Stock Manager アドオンは LAN にポートを公開していない（Ingress のみ）ため、統合はアドオンの内部ホスト名 `http://3a30c8ec-stock-manager:8099` で接続します（`localhost:8099` では接続できません）。内部ホスト名はアドオンの slug `3a30c8ec_stock_manager` の `_` を `-` に置き換えたものです。環境により異なる場合はオプションのURLを合わせて変更してください。既存の統合は、オプションでURLをこの値に更新してください。

## エンティティ一覧

### `sensor.product_<product_id>`

品目ごとに 1 つ作成されるセンサーです。状態（state）は **在庫数**（単位「個」）。

| 属性 | 説明 |
|------|------|
| `product_id` | 品目ID |
| `name` | 品目名 |
| `maker` | メーカー |
| `volume` | 容量 |
| `piece_count` | 入数 |
| `category` | カテゴリ名 |
| `location` | 保管場所 |
| `jan_code` | JANコード |
| `amazon_url` | Amazon URL |
| `note` | メモ |
| `quantity` | 在庫数 |

品目に写真が登録されている場合は `entity_picture` として表示されます。

> サービス呼び出しに使う `product_id` は、対象センサーの属性 `product_id` で確認できます（**開発者ツール → 状態** など）。

### `select.products`

全品目の一覧を表す select エンティティです。`options` は各品目の `product_id`、選択した値が状態（state）になります。属性 `products` に、各品目の概要（`id` / `name` / `quantity` / `category` / `piece_count`）が含まれます。

## サービス

### `stock_manager.use` — 在庫消費

指定した品目の在庫を消費します。

| フィールド | 必須 | デフォルト | 説明 |
|-----------|:---:|:---:|------|
| `product_id` | ○ | — | 対象の品目ID |
| `quantity` | | `1` | 消費する数量（1〜9999） |

```yaml
service: stock_manager.use
data:
  product_id: "abc123"
  quantity: 1
```

### `stock_manager.add` — 在庫追加

指定した品目の在庫を追加します。

| フィールド | 必須 | デフォルト | 説明 |
|-----------|:---:|:---:|------|
| `product_id` | ○ | — | 対象の品目ID |
| `quantity` | | `1` | 追加する数量（1〜9999） |

```yaml
service: stock_manager.add
data:
  product_id: "abc123"
  quantity: 3
```

### 自動化の例

在庫が 2 個未満になったら通知する例:

```yaml
automation:
  - alias: 在庫が少なくなったら通知
    trigger:
      - platform: numeric_state
        entity_id: sensor.product_abc123
        below: 2
    action:
      - service: notify.notify
        data:
          message: >-
            {{ state_attr('sensor.product_abc123', 'name') }} の在庫が
            残り {{ states('sensor.product_abc123') }} 個です
```

## ライセンス

提供元リポジトリ [hgn32/ha-addons](https://github.com/hgn32/ha-addons) に準じます。
