# LOCORO

## サービス概要

LOCORO は、レジャーホテル向けのリアルタイム予約・部屋管理システムです。

従来の「空室待ち」「回転率低下」などの課題に対し、
短時間の予約確保やリアルタイム状態管理を通じて、
ホテル運営の効率化を目指しています。

現在は MVP（Minimum Viable Product）として開発中です。

---

# デモURL

Render にデプロイしたデモ環境です。

## 客側ページ
- ホテル一覧: https://locoro.onrender.com/hotels/
- 部屋一覧: https://locoro.onrender.com/rooms/
- ホテル別部屋一覧（例: hotel_id=1）: https://locoro.onrender.com/hotels/1/rooms/
- 部屋詳細（例: room_id=1）: https://locoro.onrender.com/rooms/1/detail

## 店側ページ
- 店舗スタッフログイン: https://locoro.onrender.com/manager/login/
- 店舗管理ダッシュボード: https://locoro.onrender.com/manager/
- ホテル設定: https://locoro.onrender.com/manager/hotel/settings/

## 管理画面
- Django Admin: https://locoro.onrender.com/admin/

※ デモ環境は Render の Free プランで動作しているため、アクセスがない時間が続くと初回表示に時間がかかる場合があります。

---

# 主な機能

## 店舗管理機能
- ホテルスタッフログイン
- 部屋一覧表示
- 部屋詳細表示
- 部屋状態変更
- 管理ダッシュボード

## 部屋ステータス管理
- 空室
- 利用中
- 清掃中
- HOLD（確保中）
- WAITING（様子見予約）

## UI / UX
- 店側専用UI
- 状態別カラー表示
- 部屋カードUI
- JavaScript(fetch)による非同期通信

---

# 使用技術

## Backend
- Python
- Django

## Frontend
- HTML
- CSS
- JavaScript (fetch)

## Database
- PostgreSQL
- SQLite（ローカル開発用フォールバック）

## Infrastructure
- Docker
- Render
- Render PostgreSQL

## Version Control
- Git
- GitHub

---

# 技術的に工夫した点

- マルチテナント構成を意識した HotelStaff モデル設計
- ホテル運営フローを考慮した状態遷移設計
- 部屋ステータス管理ロジック
- 店舗側で直感的に操作できるUI設計
- fetch API を用いた非同期状態更新
- Render 本番環境では PostgreSQL、ローカル環境では SQLite を使えるように `DATABASE_URL` でDB接続を切り替え
- Render の Start Command で `python manage.py migrate` を自動実行し、デプロイ時にDBマイグレーションを反映

---

# 本番環境・DB構成

LOCORO は Render にデプロイしており、本番環境では Render PostgreSQL を使用しています。

## DB切り替え方針

環境変数 `DATABASE_URL` の有無によって、使用するデータベースを切り替えています。

- `DATABASE_URL` が設定されている環境: PostgreSQL を使用
- `DATABASE_URL` が設定されていない環境: SQLite を使用

これにより、ローカル開発では SQLite のまま簡単に動作確認でき、本番環境では PostgreSQL に接続できます。

## Render の環境変数

Render の Web Service 側に以下の環境変数を設定しています。

```env
DATABASE_URL=Render PostgreSQL の Internal Database URL
```

実際の値には DB パスワードが含まれるため、GitHub には公開していません。

## 自動マイグレーション

Render の Shell が使えない環境でもマイグレーションを反映できるように、Start Command で `migrate` を実行しています。

```bash
python manage.py migrate && gunicorn locoro_app.wsgi:application
```

この設定により、デプロイ時に以下の流れで起動します。

1. PostgreSQL に対して `python manage.py migrate` を実行
2. マイグレーション成功後、Gunicorn でDjangoアプリを起動
3. マイグレーションに失敗した場合はアプリ起動前にエラーとして検知

---

# 今後実装予定

- 予約ロジック
- 30分HOLD自動解除
- ユーザー側予約UI
- 地図連携
- 空室検索機能
- 通知機能
- ユーザー側マイページ機能

---

# 開発背景

実際のレジャーホテル運営を想定し、
「回転率」と「予約」を両立できるシステムを目指して開発しています。

単なる CRUD アプリではなく、
現場運用を意識した設計・ロジック構築に取り組んでいます。

---

# セットアップ方法

```bash
git clone https://github.com/Hibiki0417/LOCORO.git
cd LOCORO
```
