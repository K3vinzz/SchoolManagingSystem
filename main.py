from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import os
from forms import CreateLoginForm, CreateUserForm, CreateStudentForm, CreateCourseForm, EditStudentForm, EditUserForm, \
    EditCourseForm, CreateTestForm, CreateScoreForm, StudentScore


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
Bootstrap5(app)
print(os.environ.get("FLASK_KEY"))

# Flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', "sqlite:///school_v2.db")
db = SQLAlchemy()
db.init_app(app)

# CONFIGURE TABLES
student_course_relation = db.Table(
    "student_course_relation",
    db.Column("student_id", db.ForeignKey("students.id")),
    db.Column("course_id", db.ForeignKey("courses.id"))
)

student_test_relation = db.Table(
    "student_test_relation",
    db.Column("student_id", db.ForeignKey("students.id")),
    db.Column("test_id", db.ForeignKey("tests.id"))
)


# Teachers
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    cellphone = db.Column(db.Integer, nullable=False)
    # Parent
    courses = relationship("Course", back_populates="teacher")
    communications = relationship("Communication", back_populates="teacher")
    tests = relationship("Test", back_populates="teacher")


class Student(db.Model, UserMixin):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    cellphone = db.Column(db.Integer)
    tel_number = db.Column(db.Integer)
    card_number = db.Column(db.String, unique=True)
    note = db.Column(db.String)
    # Parent
    scores = relationship("Score", back_populates="student", cascade="all, delete")
    # Many-to-many relationship
    courses = relationship("Course", secondary=student_course_relation, back_populates="students")
    tests = relationship("Test", secondary=student_test_relation, back_populates="students")


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String)
    # Parent
    communications = relationship("Communication", back_populates="course", cascade="all, delete")
    tests = relationship("Test", back_populates="course", cascade="all, delete")
    # Child
    teacher = relationship("User", back_populates="courses")
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Many-to-many relationship
    students = relationship("Student", secondary=student_course_relation, back_populates="courses")


class Communication(db.Model):
    __tablename__ = "communications"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    # Child
    teacher = relationship("User", back_populates="communications")
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course = relationship("Course", back_populates="communications")
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))


class Test(db.Model):
    __tablename__ = "tests"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    # Parent
    scores = relationship("Score", back_populates="test", cascade="all, delete")
    # Child
    teacher = relationship("User", back_populates="tests")
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course = relationship("Course", back_populates="tests")
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    # Many-to-many
    students = relationship("Student", secondary=student_test_relation, back_populates="tests")


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    # Child
    student = relationship("Student", back_populates="scores")
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    test = relationship("Test", back_populates="scores")
    test_id = db.Column(db.Integer, db.ForeignKey("tests.id"))


with app.app_context():
    db.create_all()


def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if not (current_user.get_id() == 1 or current_user.is_authenticated):
            return abort(403, "Access forbidden - Admin access required")
        return function(*args, **kwargs)

    return wrapper_function


@app.route('/')
def home():
    # result = db.session.execute(db.select(User)).scalars()
    # users = result.all()
    # print(users[1].courses[0].subject)
    # return render_template("index.html")
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = CreateUserForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("Email already existed")
            return redirect(url_for("login"))
        with app.app_context():
            hashed_pwd = generate_password_hash(form.password.data,
                                                method="pbkdf2:sha256",
                                                salt_length=8
                                                )
            new_user = User(name=form.name.data,
                            email=email,
                            password=hashed_pwd,
                            cellphone=form.cellphone.data
                            )
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = CreateLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Wrong Password")
                return redirect(url_for('login'))
        else:
            flash('Email is not registered')
            return redirect(url_for('login'))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_student', methods=["GET", "POST"])
@admin_only
def add_student():
    form = CreateStudentForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(Student).where(Student.email == email))
        student = result.scalar()
        if student:
            flash("The email has been registered")
            return redirect(url_for('add_student'))
        with app.app_context():
            hashed_pwd = generate_password_hash(form.password.data,
                                                method="pbkdf2:sha256",
                                                salt_length=8
                                                )
            new_student = Student(
                name=form.name.data,
                grade=form.grade.data,
                email=email,
                password=hashed_pwd,
                address=form.address.data,
                cellphone=form.cellphone.data,
                tel_number=form.tel_number.data
            )
            db.session.add(new_student)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_student.html", form=form, logged_in=current_user.is_authenticated, is_edit=False)


@app.route('/edit_student/<int:student_id>', methods=["GET", "POST"])
@admin_only
def edit_student(student_id):
    student = db.get_or_404(Student, student_id)
    form = EditStudentForm(
        name=student.name,
        grade=student.grade,
        email=student.email,
        address=student.address,
        cellphone=student.cellphone,
        tel_number=student.tel_number,
        card_number=student.card_number
    )

    if form.validate_on_submit():
        student.name = form.name.data
        student.grade = form.grade.data
        student.email = form.email.data
        student.address = form.address.data
        student.cellphone = form.cellphone.data
        student.tel_number = form.tel_number.data
        student.card_number = form.card_number.data
        db.session.commit()
        return redirect(url_for('all_students'))

    return render_template("add_student.html", form=form, logged_in=current_user.is_authenticated, is_edit_student=True,
                           student_id=student_id)


@app.route('/edit_user/<int:user_id>', methods=["GET", "POST"])
@admin_only
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    form = EditUserForm(
        name=user.name,
        email=user.email,
        cellphone=user.cellphone
    )
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.cellphone = form.cellphone.data
        db.session.commit()
        return redirect(url_for('all_users'))
    return render_template("add_student.html", form=form, logged_in=current_user.is_authenticated, user_id=user_id)


@app.route('/edit_course/<int:course_id>', methods=["GET", "POST"])
@admin_only
def edit_course(course_id):
    course = db.get_or_404(Course, course_id)
    students = db.session.execute(db.select(Student)).scalars().all()
    teachers = db.session.execute(db.select(User)).scalars().all()
    files = [teachers, students]
    form = EditCourseForm(obj=files)
    form.name.default = course.subject
    # provide teachers list dynamically
    form.teacher.choices = [(teacher.id, teacher.name) for teacher in files[0]]
    form.teacher.default = course.teacher_id
    # provide students list dynamically
    form.students.choices = [(student.id, student.name) for student in files[1]]
    # Make the checkbox pre-checked by setting the form.students.default and form.process()
    form.students.default = [student.id for student in course.students]
    # form.process() << will cause CSRF token missing if put above the validate_on_submit()

    if form.validate_on_submit():
        course.subject = form.name.data
        if course.teacher_id is None:
            # add the course to the new_teacher.courses
            new_teacher = db.get_or_404(User, form.teacher.data)  # form.teacher.data returns the id of teacher
            new_teacher.courses.append(course)

            # add the new teacher to the course
            course.teacher = new_teacher

            students_in_course = [db.get_or_404(Student, student_id) for student_id in form.students.data]
            course.students = students_in_course

            db.session.commit()
            return redirect(url_for('all_courses'))

        elif not course.teacher_id == form.teacher.id:
            # remove the course from previous_teacher.courses
            previous_teacher = db.get_or_404(User, course.teacher_id)
            previous_teacher.courses.remove(course)

            # add the course to the new_teacher.courses
            new_teacher = db.get_or_404(User, form.teacher.data)  # form.teacher.data returns the id of teacher
            new_teacher.courses.append(course)

            # change the teacher of the course
            course.teacher = new_teacher

            students_in_course = [db.get_or_404(Student, student_id) for student_id in form.students.data]
            course.students = students_in_course

            db.session.commit()
            return redirect(url_for('all_courses'))

    form.process()
    return render_template("add_course.html", form=form, logged_in=True, course_id=course_id)


@app.route('/all_students')
@admin_only
def all_students():
    result = db.session.execute(db.select(Student)).scalars()
    students = result.all()
    return render_template("all_students.html", all_students=students, logged_in=current_user.is_authenticated)


@app.route('/all_users')
@admin_only
def all_users():
    result = db.session.execute(db.select(User)).scalars()
    users = result.all()
    return render_template("all_users.html", all_users=users, logged_in=current_user.is_authenticated)


@app.route('/all_courses')
@admin_only
def all_courses():
    result = db.session.execute(db.select(Course)).scalars()
    courses = result.all()
    return render_template("all_courses.html", all_courses=courses, logged_in=current_user.is_authenticated)


@app.route('/add_course', methods=["GET", "POST"])
@admin_only
def add_course():
    students = db.session.execute(db.select(Student)).scalars().all()
    teachers = db.session.execute(db.select(User)).scalars().all()
    print(teachers)
    files = [teachers, students]
    form = CreateCourseForm(obj=files)
    form.teacher.choices = [(teacher.id, teacher.name) for teacher in files[0]]
    form.students.choices = [(student.id, student.name) for student in files[1]]
    if form.validate_on_submit():
        with app.app_context():
            new_course = Course(
                subject=form.name.data,
                teacher=db.get_or_404(User, form.teacher.data)
            )
            # print(form.students.data)
            # >>> [1, 2, 3, 4, 5]
            students_in_course = [db.get_or_404(Student, student_id) for student_id in form.students.data]
            new_course.students.extend(students_in_course)
            # add students in course to the new course

            db.session.add(new_course)

            teacher = db.session.execute(db.select(User).where(User.id == form.teacher.data)).scalar()
            teacher.courses.append(new_course)
            # add the new course to the teacher

            db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_course.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/delete_user/<int:user_id>')
@admin_only
def delete_user(user_id):
    user_to_delete = db.get_or_404(User, user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('all_users'))


@app.route('/delete/<int:course_id>')
@admin_only
def delete_course(course_id):
    course_to_delete = db.get_or_404(Course, course_id)
    db.session.delete(course_to_delete)
    db.session.commit()
    return redirect(url_for('all_courses'))


@app.route('/delete/<int:student_id>')
@admin_only
def delete_student(student_id):
    student_to_delete = db.get_or_404(Student, student_id)
    db.session.delete(student_to_delete)
    db.session.commit()
    return redirect(url_for('all_students'))


@app.route('/add_test', methods=["GET", "POST"])
@admin_only
def add_test():
    files = db.session.execute(db.select(Course).where(Course.teacher_id == current_user.id)).scalars().all()
    form = CreateTestForm(obj=files)
    form.course.choices = [(course.id, course.subject) for course in files]
    if form.validate_on_submit():
        course = db.get_or_404(Course, form.course.data)
        new_test = Test(
            title=form.title.data,
            teacher=current_user,
            course=course
        )
        course.tests.append(new_test)
        db.session.add(new_test)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_test.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/add_score/<int:test_id>', methods=["GET", "POST"])
@admin_only
def add_score(test_id):
    test = db.get_or_404(Test, test_id)
    course = test.course  # <Course 2>
    students = course.students  # [<Student 1>, <Student 2>, <Student 3>, <Student 4>]
    form = CreateScoreForm()
    for i in range(len(students)):
        new_student = StudentScore()
        form.scores.append_entry(new_student)
        # Add a new entry for each student
        form.scores.entries[i].label.text = students[i].name
        # Set the label of the new entry as the student's name

    if request.method == "POST":
        for i in range(len(students)):
            new_score = Score(
                score=form.scores.data[i]['score'],
                test=test,
                student=students[i]
            )
            db.session.add(new_score)
            students[i].scores.append(new_score)
        test.students.extend(students)
        db.session.commit()
        return redirect(url_for('home'))

        # form.scores.data = [{'score': 123, 'csrf_token': '...'}, {'score': None, 'csrf_token': '...'},...]
        # 傳回來的資料順序和add entry時的順序相同, 若沒有成績則return None

    return render_template("add_score.html",
                           form=form,
                           test_id=test_id,
                           is_edit=False,
                           logged_in=current_user.is_authenticated
                           )


@app.route('/edit_score/<int:test_id>', methods=["POST", "GET"])
@admin_only
def edit_score(test_id):
    test = db.get_or_404(Test, test_id)
    # scores = db.session.execute(db.select(Score).where(Score.test_id == test_id)).scalars().all()
    scores = test.scores
    students = test.course.students
    form = CreateScoreForm()

    # 放在for loop之下會造成新的資料被for loop覆蓋成就的資料
    if request.method == "POST":
        for i in range(len(students)):
            scores[i].score = form.scores.data[i]['score']
        db.session.commit()
        return redirect(url_for('all_tests'))

    for i in range(len(students)):
        new_student = StudentScore()
        form.scores.append_entry(new_student)
        # Add a new entry for each student
        form.scores.entries[i].label.text = students[i].name
        # Set the label of the new entry as the student's name
        form.scores[i].score.data = scores[i].score

    return render_template("add_score.html",
                           form=form,
                           test_id=test_id,
                           is_edit=True,
                           logged_in=current_user.is_authenticated
                           )


@app.route('/delete_test/<int:test_id>')
@admin_only
def delete_test(test_id):
    test = db.get_or_404(Test, test_id)
    db.session.delete(test)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/all_tests')
@admin_only
def all_tests():
    tests = db.session.execute(db.select(Test)).scalars().all()
    return render_template("all_tests.html", all_tests=tests, logged_in=current_user.is_authenticated)


@app.route('/test/<int:test_id>')
@admin_only
def test(test_id):
    test_result = db.get_or_404(Test, test_id)
    data = [{'name': score.student.name, 'score': score.score} for score in test_result.scores]
    return render_template("test.html", data=data, logged_in=current_user.is_authenticated)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
