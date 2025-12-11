import os
from seed import seed_database

def str_to_bool(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y"}

def main():
    seed_enabled = str_to_bool(os.getenv("SEED_ENABLED", "false"))
    if not seed_enabled:
        print("Seeding is disabled (SEED_ENABLED is not true).")
        return

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "university_grades")

    n_students = int(os.getenv("SEED_STUDENTS", "10000"))
    n_teachers = int(os.getenv("SEED_TEACHERS", "600"))
    n_courses = int(os.getenv("SEED_COURSES", "80"))
    avg_offerings_per_course = int(os.getenv("SEED_AVG_OFFERINGS_PER_COURSE", "3"))
    avg_courses_per_student = int(os.getenv("SEED_AVG_COURSES_PER_STUDENT", "5"))
    avg_grades_per_enrollment = int(os.getenv("SEED_AVG_GRADES_PER_ENROLLMENT", "4"))

    seed_database(
        mongo_uri=mongo_uri,
        db_name=db_name,
        n_students=n_students,
        n_teachers=n_teachers,
        n_courses=n_courses,
        avg_offerings_per_course=avg_offerings_per_course,
        avg_courses_per_student=avg_courses_per_student,
        avg_grades_per_enrollment=avg_grades_per_enrollment,
    )

if __name__ == "__main__":
    main()
