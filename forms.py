from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField, SelectMultipleField, widgets, \
    FieldList, IntegerField, FormField
from wtforms.validators import DataRequired, Email, Length


class CreateCourseForm(FlaskForm):
    name = StringField("Name of the Course", validators=[DataRequired()])
    teacher = SelectField("Teacher", coerce=int)
    students = SelectMultipleField("Students",
                                   coerce=int,
                                   option_widget=widgets.CheckboxInput(),
                                   widget=widgets.ListWidget(prefix_label=False)
                                   )
    submit = SubmitField("Add Course")


class EditCourseForm(FlaskForm):
    name = StringField("Name of the Course", validators=[DataRequired()])
    teacher = SelectField("Teacher", coerce=int)
    students = SelectMultipleField("Students",
                                   coerce=int,
                                   option_widget=widgets.CheckboxInput(),
                                   widget=widgets.ListWidget(prefix_label=False)
                                   )
    submit = SubmitField("Edit Course")


class CreateUserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    cellphone = StringField("Cellphone Number", validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField("Sign up")


class CreateStudentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    grade = SelectField("Grade", choices=[4, 5, 6, 7, 8, 9, 10, 11, 12])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    address = StringField("Address")
    cellphone = StringField("Cellphone Number (e.g. 0987654321)", validators=[DataRequired(), Length(min=10, max=10)])
    tel_number = StringField("Telephone Number (e.g. 23456789)", validators=[DataRequired(), Length(min=8, max=8)])
    card_number = StringField("Card Number")
    submit = SubmitField("Add Student")


class EditStudentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    grade = SelectField("Grade", choices=[4, 5, 6, 7, 8, 9, 10, 11, 12])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address")
    cellphone = StringField("Cellphone Number (e.g. 0987654321)", validators=[DataRequired(), Length(min=10, max=10)])
    tel_number = StringField("Telephone Number (e.g. 23456789)", validators=[DataRequired(), Length(min=8, max=8)])
    card_number = StringField("Card Number")
    submit = SubmitField("Edit Student")


class EditUserForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    cellphone = StringField("Cellphone Number", validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField("Edit User")


class CreateLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class CreateTestForm(FlaskForm):
    title = StringField("Test Title", validators=[DataRequired()])
    course = SelectField("Course", coerce=int)
    submit = SubmitField("Create")


class StudentScore(FlaskForm):
    score = IntegerField()


class CreateScoreForm(FlaskForm):
    scores = FieldList(FormField(StudentScore))
    submit = SubmitField("Submit")


class CreateNotifyForm(FlaskForm):
    teachers = SelectMultipleField("Teachers",
                                   coerce=int,
                                   option_widget=widgets.CheckboxInput(),
                                   widget=widgets.ListWidget(prefix_label=False)
                                   )
    message = StringField(validators=[DataRequired()])
    submit = SubmitField("推播gogo")


class CreateCommForm(FlaskForm):
    title = StringField("Title")
    course = SelectField("Course", coerce=int)
    body = StringField("Body")
    submit = SubmitField("Submit")










