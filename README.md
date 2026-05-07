# LOCORO

## サービス概要

LOCORO は、ラブホテル向けのリアルタイム予約・部屋管理システムです。

従来の「空室待ち」「回転率低下」などの課題に対し、
短時間の予約確保やリアルタイム状態管理を通じて、
ホテル運営の効率化を目指しています。

現在は MVP（Minimum Viable Product）として開発中です。

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
- SQLite（開発初期）

## Infrastructure
- Docker
- Render

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
