"""
Routing
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
)

from models.models import db, Respondent, Response, interpret_phq9
from setup import PHQ9_OPTIONS, PHQ9_QUESTIONS

from models.models import Admin, Respondent, Response
from models.forms import RespondentForm, ResponseForm, AdminForm

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", title="MindCheck | Depression Screening")


@main.route("/qna", methods=["GET", "POST"])
def qna():
    respondent_form = RespondentForm()
    response_form = ResponseForm()

    if respondent_form.validate_on_submit():
        respondent = Respondent(
            name=respondent_form.name.data,
            email=respondent_form.email.data,
            age=respondent_form.age.data,
            gender=respondent_form.gender.data,
        )
        db.session.add(respondent)
        db.session.flush()

        answers = []

        for i in range(len(PHQ9_QUESTIONS)):
            key = f"q{i}"
            val = request.form.get(key)
            
            try:
                num = int(val)
                if num not in (0, 1, 2, 3):
                    flash("Invalid answer detected.", "danger")
                    return redirect(url_for("main.qna"))

                answers.append(num)  # type: ignore
            except Exception as e:
                print(e)

                flash("Please answer all questions.", "danger")
                return redirect(url_for("main.qna"))

        score = sum(answers)  # type: ignore
        interpretation = interpret_phq9(score)
        flagged = answers[-1] > 0  # type: ignore

        resp = Response(
            respondent_id=respondent.id,
            answers=answers,
            score=score,
            interpretation=interpretation,
            flagged_suicidal_thoughts=flagged,
        )
        db.session.add(resp)
        db.session.commit()

        return redirect(url_for("main.result", response_id=resp.id))

    return render_template(
        "qna.html",
        respondent_form=respondent_form,
        response_form=response_form,
        questions=PHQ9_QUESTIONS,
        options=PHQ9_OPTIONS,
    )


@main.route("/result/<int:response_id>")
def result(response_id):
    resp = Response.query.get_or_404(response_id)
    return render_template(
        "result.html", resp=resp, questions=PHQ9_QUESTIONS, options=PHQ9_OPTIONS
    )


# Admin routes


@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    form = AdminForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash("Logged in successfully!", "success")

            return redirect(url_for("main.admin_dashboard"))
        else:
            flash("Error: Invalid credentials.", "danger")

    return render_template("admin_login.html", form=form)


@main.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash("Logged out successfully.", "info")

    return redirect(url_for("main.admin_login"))


@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    severity = request.args.get("severity")
    query = Response.query.join(Respondent).order_by(Response.submitted_at.desc())

    if severity:
        query = query.filter(Response.interpretation.like(f"{severity}%"))

    responses = query.limit(200).all()
    return render_template("admin_dashboard.html", responses=responses)
