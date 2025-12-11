from typing import List
from pymongo import MongoClient
from bson import ObjectId

from models import Student, Teacher, Course, CourseOffering, Enrollment, Grade
from generators import gen_student, gen_teacher, gen_course, gen_course_offering, gen_enrollment, gen_grade

def seed_database(
    mongo_uri: str = "mongodb://localhost:27017",
    db_name: str = "university_grades",
    n_students: int = 200,
    n_teachers: int = 20,
    n_courses: int = 15,
    avg_offerings_per_course: int = 2,
    avg_courses_per_student: int = 5,
    avg_grades_per_enrollment: int = 3,
):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    students_col = db["students"]
    teachers_col = db["teachers"]
    courses_col = db["courses"]
    offerings_col = db["course_offerings"]
    enrollments_col = db["enrollments"]
    grades_col = db["grades"]

    # чистим БД
    students_col.delete_many({})
    teachers_col.delete_many({})
    courses_col.delete_many({})
    offerings_col.delete_many({})
    enrollments_col.delete_many({})
    grades_col.delete_many({})

    # 1. Студенты
    students: List[Student] = [gen_student() for _ in range(n_students)]
    student_docs = [s.model_dump(by_alias=True) for s in students]
    res_students = students_col.insert_many(student_docs)
    student_ids = list(res_students.inserted_ids)

    # 2. Преподаватели
    teachers: List[Teacher] = [gen_teacher() for _ in range(n_teachers)]
    teacher_docs = [t.model_dump(by_alias=True) for t in teachers]
    res_teachers = teachers_col.insert_many(teacher_docs)
    teacher_ids = list(res_teachers.inserted_ids)

    # 3. Курсы
    courses: List[Course] = [gen_course() for _ in range(n_courses)]
    course_docs = [c.model_dump(by_alias=True) for c in courses]
    res_courses = courses_col.insert_many(course_docs)
    course_ids = list(res_courses.inserted_ids)

    # 4. Course offerings (курс + препод + группа)
    offerings_docs = []
    for course_id in course_ids:
        for i in range(avg_offerings_per_course):
            teacher_id = ObjectId(
                teacher_ids[i % len(teacher_ids)]
            )
            group = f"IU5-{i + 11}"
            offering = gen_course_offering(course_id=course_id, teacher_id=teacher_id, group=group)
            offerings_docs.append(offering.model_dump(by_alias=True))

    res_offerings = offerings_col.insert_many(offerings_docs)
    offering_ids = list(res_offerings.inserted_ids)

    # 5. Enrollments (студент записан на поток)
    enrollments_docs = []
    import random

    for student_id in student_ids:
        # для каждого студента — случайный набор потоков
        offerings_for_student = random.sample(
            offering_ids,
            k=min(avg_courses_per_student, len(offering_ids)),
        )
        for off_id in offerings_for_student:
            enrollment = gen_enrollment(student_id=student_id, offering_id=off_id)
            enrollments_docs.append(enrollment.model_dump(by_alias=True))

    res_enrollments = enrollments_col.insert_many(enrollments_docs)
    enrollment_count = len(res_enrollments.inserted_ids)

    # 6. Grades (несколько оценок на каждую запись студента на поток)
    grades_docs = []
    for enrollment_doc in enrollments_docs:
        student_id = enrollment_doc["studentId"]
        offering_id = enrollment_doc["courseOfferingId"]
        for _ in range(avg_grades_per_enrollment):
            grade = gen_grade(student_id=student_id, offering_id=offering_id)
            grades_docs.append(grade.model_dump(by_alias=True))

    if grades_docs:
        grades_col.insert_many(grades_docs)

    print(f"Inserted: {len(student_ids)} students")
    print(f"Inserted: {len(teacher_ids)} teachers")
    print(f"Inserted: {len(course_ids)} courses")
    print(f"Inserted: {len(offering_ids)} course_offerings")
    print(f"Inserted: {enrollment_count} enrollments")
    print(f"Inserted: {len(grades_docs)} grades")
