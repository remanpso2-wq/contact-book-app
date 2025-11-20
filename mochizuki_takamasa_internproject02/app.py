from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------
# モデル定義
# -------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    content = db.Column(db.String(260))
    date = db.Column(db.String(20))
    is_checked = db.Column(db.Boolean, default=False)
    condition_level = db.Column(db.Integer, default=3)
    mental_level = db.Column(db.Integer, default=3)
    student = db.relationship('Student', backref='reports')

# ✅ 担任共有メモモデル
class TeacherNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.String(20))

# -------------------------
# 起動時のDBマイグレーション
# -------------------------
def _ensure_columns():
    try:
        db.session.execute(text("SELECT condition_level FROM report LIMIT 1;"))
    except Exception:
        try:
            db.session.execute(text("ALTER TABLE report ADD COLUMN condition_level INTEGER DEFAULT 3;"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    try:
        db.session.execute(text("SELECT mental_level FROM report LIMIT 1;"))
    except Exception:
        try:
            db.session.execute(text("ALTER TABLE report ADD COLUMN mental_level INTEGER DEFAULT 3;"))
            db.session.commit()
        except Exception:
            db.session.rollback()

# -------------------------
# 共通: 学生取得 or 作成
# -------------------------
def _get_or_create_student(name: str) -> Student:
    s = Student.query.filter_by(name=name).first()
    if not s:
        s = Student(name=name)
        db.session.add(s)
        db.session.commit()
    return s

# -------------------------
# トップページ
# -------------------------
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    if q:
        reports = Report.query.filter(Report.content.contains(q)).order_by(Report.id.desc()).all()
    else:
        reports = Report.query.order_by(Report.id.desc()).limit(10).all()
    students = Student.query.order_by(Student.name.asc()).all()
    return render_template('index.html', reports=reports, students=students, q=q)

# -------------------------
# 検索ページ
# -------------------------
@app.route('/search')
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = Report.query.filter(Report.content.contains(q)).order_by(Report.date.desc()).all()
    return render_template("search.html", q=q, results=results)

# -------------------------
# 新規レポート追加
# -------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_report():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        content = request.form.get('content', '').strip()
        date = request.form.get('date', '').strip()
        try:
            condition_level = int(request.form.get('condition_level', 3))
        except Exception:
            condition_level = 3
        try:
            mental_level = int(request.form.get('mental_level', 3))
        except Exception:
            mental_level = 3

        if not student_name or not date:
            return redirect(url_for('index'))

        student = _get_or_create_student(student_name)
        new_report = Report(
            student_id=student.id,
            content=content,
            date=date,
            is_checked=False,
            condition_level=condition_level,
            mental_level=mental_level
        )
        db.session.add(new_report)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

# -------------------------
# 既読処理
# -------------------------
@app.route('/check/<int:report_id>')
def check_report(report_id):
    r = Report.query.get_or_404(report_id)
    r.is_checked = True
    db.session.commit()
    return redirect(url_for('index'))

# -------------------------
# 提出状況
# -------------------------
@app.route('/status')
def status():
    rows = []
    for s in Student.query.order_by(Student.name.asc()).all():
        rs = Report.query.filter_by(student_id=s.id).order_by(Report.date.asc()).all()
        total = len(rs)
        checked = sum(1 for r in rs if r.is_checked)
        unchecked = total - checked
        latest = rs[-1].date if rs else '-'

        if total > 0:
            avg_c = round(sum(r.condition_level or 0 for r in rs) / total, 2)
            avg_m = round(sum(r.mental_level or 0 for r in rs) / total, 2)
        else:
            avg_c = avg_m = 0

        rows.append({
            'id': s.id,
            'name': s.name,
            'total': total,
            'checked': checked,
            'unchecked': unchecked,
            'latest_date': latest,
            'avg_condition': avg_c,
            'avg_mental': avg_m
        })

    all_reports = Report.query.all()
    if all_reports:
        g_avg_c = round(sum(r.condition_level or 0 for r in all_reports) / len(all_reports), 2)
        g_avg_m = round(sum(r.mental_level or 0 for r in all_reports) / len(all_reports), 2)
    else:
        g_avg_c = g_avg_m = 0

    summary = {
        'students': len(rows),
        'reports': len(all_reports),
        'avg_condition': g_avg_c,
        'avg_mental': g_avg_m
    }
    return render_template('status.html', summary=summary, rows=rows)

# -------------------------
# 学生詳細
# -------------------------
@app.route('/student/<int:student_id>')
def student_detail(student_id):
    s = Student.query.get_or_404(student_id)
    rs = Report.query.filter_by(student_id=student_id).order_by(Report.date.asc()).all()

    labels = [r.date for r in rs]
    cond_values = [r.condition_level or 0 for r in rs]
    mental_values = [r.mental_level or 0 for r in rs]

    total = len(rs)
    checked = sum(1 for r in rs if r.is_checked)

    return render_template(
        'student_detail.html',
        student=s,
        reports=rs,
        total=total,
        checked=checked,
        labels=labels,
        cond_values=cond_values,
        mental_values=mental_values
    )

# -------------------------
# 📢 担任共有メモ 一覧
# -------------------------
@app.route('/notes/shared')
def shared_notes():
    notes = TeacherNote.query.order_by(TeacherNote.date.desc()).all()
    return render_template('shared_notes.html', notes=notes)

# -------------------------
# 📥 担任共有メモ 追加
# -------------------------
@app.route('/notes/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        teacher_name = request.form.get("teacher_name")
        content = request.form.get("content")
        date = datetime.now().strftime("%Y-%m-%d")

        note = TeacherNote(teacher_name=teacher_name, content=content, date=date)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for("shared_notes"))

    return render_template("add_note.html")

# -------------------------
# 起動
# -------------------------
if __name__ == "__main__":
    print("✅ Flaskサーバーを起動しようとしています...")
    with app.app_context():
        db.create_all()
        _ensure_columns()
    print("✅ DB作成/更新完了、サーバー起動直前です！")
    app.run(host="127.0.0.1", port=5000, debug=True)
