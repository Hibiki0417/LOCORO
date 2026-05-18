# LOCORO

LOCORO は、レジャーホテル向けのリアルタイム空室確認・部屋状態管理システムです。

ホテル側は部屋の状態をリアルタイムに管理し、ユーザー側はホテル・部屋の空室状況を確認できることを目指しています。
現在は MVP（Minimum Viable Product）として開発中です。

---

## デモURL

Render にデプロイしたデモ環境です。

### 客側ページ
- ホテル一覧: https://locoro.onrender.com/hotels/
- ホテル別部屋一覧（例: hotel_id=1）: https://locoro.onrender.com/hotels/1/rooms/
- 部屋詳細（例: room_id=1）: https://locoro.onrender.com/rooms/1/detail/

### 店側ページ
- 店舗スタッフログイン: https://locoro.onrender.com/manager/login/
- 店舗管理ダッシュボード: https://locoro.onrender.com/manager/
- ホテル設定: https://locoro.onrender.com/manager/hotel/settings/

### 管理画面
- Django Admin: https://locoro.onrender.com/admin/

※ デモ環境は Render の Free プランで動作しているため、アクセスがない時間が続くと初回表示に時間がかかる場合があります。

---

## デモ用ログイン情報

### 客側ユーザー用アカウント

- ログインURL: https://locoro.onrender.com/login/
- ユーザー名: `demo_user`
- パスワード: `demo2026`

### 店舗スタッフ用アカウント

- ログインURL: https://locoro.onrender.com/manager/login/
- ユーザー名: `demo_staff`
- パスワード: `demo2026`

※ デモ用アカウントのため、登録データ・画像・部屋状態は予告なく変更または削除する場合があります。

---

## サービス概要

LOCOROは、レジャーホテル向けのリアルタイム空室・部屋状態管理システムです。

レジャーホテルでは、通常の宿泊予約と異なり、ユーザーが「今すぐ利用できる部屋」を探すケースが多くあります。

一方で、実際の空室状況や清掃完了のタイミングは外から分かりにくく、ユーザーは電話確認や現地到着後の確認に頼ることが多くなります。店舗側にとっても、電話対応や部屋状況の案内が負担になりやすいという課題があります。

LOCOROでは、店舗側が部屋ごとの状態を管理画面から更新し、ユーザー側が空室・利用中・清掃中などの状況を分かりやすく確認できる仕組みを目指しています。

将来的には、空きそうな部屋を一時的に押さえる「様子見予約」や、清掃完了後の短時間HOLD機能など、レジャーホテルの利用シーンに合わせた予約導線を実装予定です。

---

## 開発背景

本アプリは、レジャーホテルの利用シーンにおける「今すぐ使いたい」という即時性に着目して開発しています。

通常の宿泊予約サービスは、数日後・数週間後の宿泊予約を前提としたものが多い一方で、レジャーホテルでは当日・直前・短時間での利用ニーズが中心になります。

LOCOROでは、このような利用特性に合わせて、空室確認・部屋状態管理・将来的な一時キープ機能を組み合わせたサービス設計を目指しています。

## 開発ステータス

現在は MVP 開発中です。

基本的なホテル・部屋管理、店側ダッシュボード、PostgreSQL接続、Cloudinary画像保存、本番デプロイまでは完了しています。
今後は、予約ロジックとユーザー側予約導線を重点的に実装予定です。

## 主な機能

### 客側機能
- ホテル一覧表示
- ホテル別の部屋一覧表示
- 部屋詳細表示
- 部屋ステータス表示
- 部屋画像表示

### 店側管理機能
- 店舗スタッフログイン
- 所属ホテルごとの管理画面
- 部屋一覧表示
- 部屋追加
- 部屋状態変更
- ホテル情報・部屋情報の管理
- 部屋画像アップロード

### 部屋ステータス管理
- 空室
- 利用中
- 清掃中
- HOLD（確保中）
- WAITING（様子見予約）
- 予約停止中

### UI / UX
- 店側専用UI
- 状態別カラー表示
- 部屋カードUI
- JavaScript fetch による非同期通信
- スマホ・タブレット利用を意識したシンプルな管理導線

---

## 使用技術

### Backend
- Python
- Django

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

### Database
- PostgreSQL（本番環境）
- SQLite（ローカル開発用フォールバック）

### Storage
- Cloudinary（アップロード画像の保存）

### Infrastructure
- Docker
- Docker Compose
- Render
- Render PostgreSQL

### Version Control / Workflow
- Git
- GitHub
- Issue / feature branch / Pull Request ベースの開発

---

## システム構成

```text
User / Hotel Staff
        ↓
Django Application on Render
        ↓
Render PostgreSQL
        ↓
Cloudinary
```

- アプリ本体: Render
- DB: Render PostgreSQL
- 画像ファイル: Cloudinary
- ソースコード管理: GitHub

Render の一時ファイル領域に画像を保存すると、再デプロイや再起動で画像が失われる可能性があるため、画像ファイル本体は Cloudinary に保存する構成にしています。

---

## 技術的に工夫した点

### 1. マルチテナントを意識した設計

HotelStaff モデルで、ログインユーザーと所属ホテルを紐づけています。
これにより、店舗スタッフが自分のホテルだけを管理する構成を目指しています。

### 2. レジャーホテル運用に合わせた部屋ステータス設計

一般的なホテル予約とは異なり、レジャーホテルでは「利用中」「清掃中」「空室」などのリアルタイムな状態管理が重要になります。
LOCORO では、現場運用を想定して部屋ステータスを設計しています。

### 3. 本番環境とローカル環境のDB切り替え

環境変数 `DATABASE_URL` の有無で使用するDBを切り替えています。

- `DATABASE_URL` がある場合: PostgreSQL
- `DATABASE_URL` がない場合: SQLite

これにより、ローカルでは軽く開発し、本番では PostgreSQL を使う構成にしています。

### 4. Renderでの自動マイグレーション

Render の Shell が使えない環境でもマイグレーションを反映できるように、Start Command で migrate を実行しています。

```bash
python manage.py migrate && gunicorn locoro_app.wsgi:application
```

### 5. Cloudinaryによる画像永続化

Django の ImageField の保存先を Cloudinary に変更し、Render の再デプロイ後も画像が消えにくい構成にしています。

### 6. GitHub PRベースの開発

一人開発でも、Issue 作成 → ブランチ作成 → PR → マージ の流れを意識して開発しています。
変更理由や作業履歴を残すことで、後から振り返りやすい開発フローにしています。

---

## 本番環境

本番環境では、Render の Environment Variables にDjango設定・DB接続・Cloudinary接続に必要な値を設定しています。

実際の値にはシークレット情報やDB接続情報が含まれるため、GitHubには公開していません。

---

## ローカル開発環境のセットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/Hibiki0417/LOCORO.git
cd LOCORO
```

### 2. `.env` を作成

プロジェクト直下に `.env` を作成します。

ローカルでSQLiteを使う場合は、DB接続用の環境変数を空にして起動できます。
画像アップロードをCloudinaryで確認する場合は、Cloudinaryの管理画面で取得した接続情報を設定します。

### 3. Dockerで起動

```bash
docker compose build
docker compose up -d
```

### 4. マイグレーション実行

```bash
docker compose exec web python manage.py migrate
```

### 5. 管理ユーザー作成

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. 開発サーバー確認

```text
http://localhost:8000/hotels/
```

---

## よく使う開発コマンド

```bash
# コンテナ起動
docker compose up -d

# コンテナ停止
docker compose down

# Djangoチェック
docker compose exec web python manage.py check

# マイグレーション作成
docker compose exec web python manage.py makemigrations

# マイグレーション実行
docker compose exec web python manage.py migrate

# 管理ユーザー作成
docker compose exec web python manage.py createsuperuser
```

---

## 今後実装予定

- 部屋情報・画像編集ページの改善
- 予約ロジック
- 30分HOLD自動解除
- ユーザー側予約UI
- 空室検索機能
- 地図連携
- 通知機能
- ユーザー側マイページ機能
- 予約履歴管理

---

基本的なホテル・部屋管理、店側ダッシュボード、PostgreSQL接続、Cloudinary画像保存、本番デプロイまでは完了しています。
今後は、予約ロジックとユーザー側予約導線を重点的に実装予定です。
