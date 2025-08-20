"""
Form Validation
"""

from flask_wtf import FlaskForm  # type: ignore
from wtforms import (
    StringField,
    IntegerField,
    PasswordField,
    SubmitField,
    SelectField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    NumberRange,
)


# Respondent Form
class RespondentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=200)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=200)])
    age = IntegerField("Age", validators=[Optional(), NumberRange(min=0, max=120)])
    gender = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[Optional()],
    )
    submit = SubmitField("Submit")


# Response Form
class ResponseForm(FlaskForm):
    interpretation = StringField(
        "Interpretation", validators=[DataRequired(), Length(max=200)]
    )
    flagged_suicidal_thoughts = BooleanField("Flagged Suicidal Thoughts")
    submit = SubmitField("Submit")


# Admin Form
class AdminForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=100)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must contain least 8 characters."),
        ],
    )
    submit = SubmitField("Login")
