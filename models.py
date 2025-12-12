from typing import Optional, List
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_after_validator_function(
                    cls.validate,
                    core_schema.str_schema(),
                ),
            ]
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        schema = handler(schema)
        schema.update(type="string")
        return schema


class MongoModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    id: Optional[PyObjectId] = Field(default=None, alias="_id")


class Student(MongoModel):
    studentNumber: str
    firstName: str
    lastName: str
    middleName: Optional[str] = None
    email: str
    group: str
    faculty: str
    enrollmentYear: int
    isActive: bool = True


class Teacher(MongoModel):
    teacherNumber: str
    firstName: str
    lastName: str
    middleName: Optional[str] = None
    email: str
    department: str
    position: str
    hiredAt: datetime
    isActive: bool = True


class Course(MongoModel):
    code: str
    name: str
    description: Optional[str] = None
    credits: int
    department: str
    defaultSemester: int


class CourseOffering(MongoModel):
    courseId: PyObjectId
    teacherId: PyObjectId
    academicYear: str          # "2024/2025"
    semester: int
    group: str
    schedule: List[str] = []
    room: Optional[str] = None
    examType: str              # "exam" / "credit" / "project"


class Enrollment(MongoModel):
    studentId: PyObjectId
    courseOfferingId: PyObjectId
    enrolledAt: datetime
    status: str                # "active" / "dropped" / "completed"


class Grade(MongoModel):
    studentId: PyObjectId
    courseOfferingId: PyObjectId
    assessmentType: str        # "exam" / "test" / "lab" / "hw"
    assessmentName: Optional[str] = None
    maxScore: int
    score: int
    grade: str                 
    weight: float
    date: datetime
    attempt: int = 1
