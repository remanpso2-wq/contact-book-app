# seed.py
from datetime import date, timedelta
from app import db, Student, Report  # app.py のモデルを利用

def upsert_student(name: str) -> Student:
    s = Student.query.filter_by(name=name).first()
    if not s:
        s = Student(name=name)
        db.session.add(s)
        db.session.commit()
    return s

def add_report_once(student_id: int, d: date, content: str, cond: int, mental: int, checked: bool):
    # app.py では date は String(20) なので "YYYY-MM-DD" 文字列で保存する
    ds = d.strftime("%Y-%m-%d")
    exists = Report.query.filter_by(student_id=student_id, date=ds).first()
    if exists:
        return False
    r = Report(
        student_id=student_id,
        content=content,
        date=ds,
        is_checked=checked,
        condition_level=cond,
        mental_level=mental,
    )
    db.session.add(r)
    return True

def run():
    # テーブル作成
    db.create_all()

    # サンプル生徒
    names = ["望月 孝義", "佐藤 花子", "田中 太郎"]
    students = [upsert_student(n) for n in names]

    today = date.today()

    # 直近 14 日分を、1日おきに投入（重複はスキップ）
    inserted = 0
    for s in students:
        for i in range(1, 15, 1):          # 1〜14日前
            d = today - timedelta(days=i)
            cond = 2 + (i % 4)             # 2〜5で揺らす
            mental = 2 + ((i + 1) % 4)     # 2〜5で揺らす
            checked = (i % 2 == 0)         # 偶数日を既読
            content = f"{s.name} の記録 {d.isoformat()}"
            if add_report_once(s.id, d, content, cond, mental, checked):
                inserted += 1

    db.session.commit()
    print(f"Seed done. inserted rows: {inserted}")

if __name__ == "__main__":
    run()
