# 学校連絡帳管理 PoC

学校現場で使用されている「連絡帳（体調・メンタル・振り返り）」をデジタル化し、  
**提出状況の可視化・担任の確認作業の効率化・週次分析・担任間の情報共有** を実現した Web アプリです。

課題①（基本 CRUD＋提出制限）をベースに、課題②では **分析・共有・検索などの拡張機能** を追加し、  
実運用を意識した PoC（概念実証）としてまとめています。

バックエンド（Python / Flask）を中心としたポートフォリオ用成果物です。

---

## プロジェクト概要

- **目的**
  - 担任の負担軽減
  - 紙の連絡帳で起こりがちな「見落とし・共有のしづらさ」を改善
  - 提出状況と生徒のコンディションを早期に把握できるようにする

- **想定利用者**
  - 生徒：毎日の体調・メンタル・振り返りを入力して提出
  - 担任：提出状況の確認、週次での傾向把握、教員間での情報共有

- **主な使用技術**
  - Python / Flask / SQLite / SQLAlchemy / Jinja2 / Chart.js
  - 動作確認環境：Windows 10 / 11

---

## 主な機能

- レポート登録（学生名・日付・内容・体調・メンタルスコア）
- レポート一覧・詳細表示
  - 既読 / 未読管理
  - キーワード検索
- 提出状況一覧（/status）
- 週次分析グラフ（/analytics）
- 検索・フィルタ（/search）
- 共有メモ一覧・追加（/shared-notes, /shared-notes/add）

---
⚙ セットアップ手順
git clone https://github.com/remanpso2-wq/contact-book-app.git
cd contact-book-app/mochizuki_takamasa_internproject02

2.（任意） 仮想環境の作成・有効化
python -m venv venv
venv\Scripts\activate  # Windows の場合

3. 依存パッケージのインストール
pip install flask flask_sqlalchemy
requirements.txt を用意する場合は、上記パッケージをベースに追加してください。

4. 開発用サンプルデータの投入（任意）
python seed.py
正常に実行されると、instance/diary.db が作成され、
サンプルの生徒・レポートが登録された状態になります。

5. アプリの起動
python app.py
コンソールに
* Running on http://127.0.0.1:5000
と表示されれば起動成功です。

---

🌐 ブラウザからのアクセス方法
レポート一覧（ホーム）
http://127.0.0.1:5000/

提出状況一覧
http://127.0.0.1:5000/status

週次分析（グラフ）
http://127.0.0.1:5000/analytics

検索
http://127.0.0.1:5000/search

共有メモ一覧
http://127.0.0.1:5000/shared-notes

共有メモ追加
http://127.0.0.1:5000/shared-notes/add

ホーム画面（レポート一覧）から、画面上部のナビゲーションリンクでも各機能に遷移できます。

---

## ディレクトリ構成（抜粋）

```text
mochizuki_takamasa_internproject02/
  app.py               # Flask アプリ本体
  seed.py              # 開発用サンプルデータ投入スクリプト
  instance/            # SQLite DB（diary.db）が生成される（Git 管理外）
  templates/           # HTML テンプレート
  static/              # CSS / JS / 画像 等（必要に応じて）
  doc/
    presentation.md    # 本アプリのプレゼンテーション資料（Markdown 版）
