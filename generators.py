from faker import Faker
import random
from datetime import datetime, date

from models import PyObjectId, Student, Teacher, Course, CourseOffering, Enrollment, Grade

fake = Faker("ru_RU")

def gen_student() -> Student:
    first = fake.first_name()
    last = fake.last_name()
    middle = fake.middle_name()
    year = random.randint(2020, 2024)
    group = f"IU5-{random.randint(11, 41)}"
    faculty = random.choice(["ФКН", "ФПМИ", "ФРТК"])
    email = fake.email()

    return Student(
        studentNumber=f"S{fake.unique.random_number(digits=6)}",
        firstName=first,
        lastName=last,
        middleName=middle,
        email=email,
        group=group,
        faculty=faculty,
        enrollmentYear=year,
        isActive=True,
    )


def gen_teacher() -> Teacher:
    first = fake.first_name()
    last = fake.last_name()
    middle = fake.middle_name()
    dept = random.choice(["ФКН", "ФПМИ", "ФРТК"])
    position = random.choice(["ассистент", "старший преподаватель", "доцент", "профессор"])
    hired = fake.date_time_between(start_date="-10y", end_date="now")

    return Teacher(
        teacherNumber=f"T{fake.unique.random_number(digits=5)}",
        firstName=first,
        lastName=last,
        middleName=middle,
        email=fake.email(),
        department=dept,
        position=position,
        hiredAt=hired,
        isActive=True,
    )


def gen_course() -> Course:
    code = f"CS{random.randint(100, 499)}"
    name = random.choice([
        "Алгоритмы и структуры данных",
        "Базы данных",
        "Операционные системы",
        "Компьютерные сети",
        "Машинное обучение",
    ])
    dept = random.choice(["ФКН", "ФПМИ"])
    credits = random.choice([2, 3, 4, 6])
    sem = random.randint(1, 8)

    return Course(
        code=code,
        name=name,
        description=fake.sentence(nb_words=8),
        credits=credits,
        department=dept,
        defaultSemester=sem,
    )


def gen_course_offering(course_id: PyObjectId, teacher_id: PyObjectId, group: str) -> CourseOffering:
    year_start = random.randint(2022, 2025)
    year = f"{year_start}/{year_start + 1}"
    semester = random.randint(1, 8)
    exam_type = random.choice(["exam", "credit", "project"])
    schedule = [
        f"{random.choice(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])} {random.choice(['08:30', '10:15', '12:00', '13:45'])}"
        for _ in range(2)
    ]

    return CourseOffering(
        courseId=course_id,
        teacherId=teacher_id,
        academicYear=year,
        semester=semester,
        group=group,
        schedule=schedule,
        room=f"Ауд. {random.randint(100, 550)}",
        examType=exam_type,
    )


def gen_enrollment(student_id: PyObjectId, offering_id: PyObjectId) -> Enrollment:
    enrolled_at = datetime.utcnow()
    status = random.choice(["active", "completed"])
    return Enrollment(
        studentId=student_id,
        courseOfferingId=offering_id,
        enrolledAt=enrolled_at,
        status=status,
    )


def gen_grade(student_id: PyObjectId, offering_id: PyObjectId) -> Grade:
    assessment_type = random.choice(["exam", "test", "lab", "hw"])
    max_score = 100
    score = random.randint(40, 100)
    grade = random.choice(["A", "B", "C", "D", "F"])
    weight = random.choice([0.1, 0.2, 0.3, 0.4, 0.5])

    return Grade(
        studentId=student_id,
        courseOfferingId=offering_id,
        assessmentType=assessment_type,
        assessmentName=f"{assessment_type.title()} #{random.randint(1, 3)}",
        maxScore=max_score,
        score=score,
        grade=grade,
        weight=weight,
        date=datetime.utcnow(),
        attempt=random.choice([1, 1, 1, 2, 2, 3]),
    )
