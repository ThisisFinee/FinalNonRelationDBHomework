## Итоговое задание по модулю 2(NoSQL)
### Первичные требования:
+ Наличие Docker
### Примечания:
+ .env файл был оставлен специально для удобства
+ poetry.lock файл был оставлен специально для удобства
### Запуск бд и заполнение данными
#### 1. Собираем образ
```bash
docker build -t university-mongo .
```    
#### Запускаем MongoDB-контейнер
```bash
docker run -d --name university-mongo --env-file .env -p 27017:27017 -v mongo-data:/data/db university-mongo
```    
#### Запускаем сидер(для обогащения бд данными) 
```bash
docker exec -it university-mongo poetry run python run_seed.py
```    
### Общая работа с бд
#### Описание бд
База данных описывает университетскую систему успеваемости: отдельные коллекции хранят студентов, преподавателей, курсы, потоки курсов, записи студентов на потоки и оценки.​    
База разбита на 6 коллекций, чтобы явно моделировать связи «многие‑ко‑многим» и упростить аналитические запросы.​

##### teachers:
```Описание
Документ teachers представляет отдельного преподавателя и используется как справочник кадрового состава.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```teacherNumber```: внешний идентификатор студента, строка, уникален в рамках университета.
+ ```firstName```: имя студента.
+ ```lastName```: фамилия студента.
+ ```middleName```: отчество, может отсутствовать.
+ ```email```: учебная почта студента.
+ ```department```: кафедра или подразделение.
+ ```position```: должность.
+ ```hiredAt```: дата найма.
+ ```isActive```: работает?

##### students:
```Описание
Документ students описывает одного студента университета как участника учебного процесса.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```studentNumber```: внешний идентификатор студента, строка, уникален в рамках университета(будем считать что номер зачётки).
+ ```firstName```: имя студента.
+ ```lastName```: фамилия студента.
+ ```middleName```: отчество, может отсутствовать.
+ ```email```: учебная почта студента.
+ ```group```: академическая группа, используется для формирования списков группы.
+ ```faculty```: факультет или институт, к которому относится студент (например, ФКН).
+ ```enrollmentYear```: год зачисления, используется для определения потока и срока обучения.
+ ```isActive```: флаг актуальности, позволяет исключать неактивных студентов из отчётов.

##### courses:
```Описание
Документ courses описывает абстрактную учебную дисциплину, без привязки к конкретному году, группе или преподавателю.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```code```: код дисциплины, используется в учебном плане и для ссылок.
+ ```name```: краткое название курса.
+ ```description```: краткое текстовое описание курса, может быть пустым..
+ ```credits```: трудоёмкость курса в зачетных единицах.
+ ```department```: кафедра/факультет, за которым закреплён курс.
+ ```defaultSemester```:  рекомендованный семестр прохождения курса.

##### course_offerings:
```Описание
Документ course_offerings представляет конкретное «предложение» курса в определённый период обучения.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```courseId```: ссылка на _id документа в courses, определяет, какая именно дисциплина читается.
+ ```teacherId```: ссылка на _id документа в teachers, кто ведёт этот поток.
+ ```academicYear```: учебный год в формате YYYY/YYYY+1.
+ ```semester```: номер семестра в рамках программы, в котором читается этот поток.
+ ```group```: группа или поток, для которого предназначено занятие.
+ ```schedule```:  массив строк с расписанием, например ["Mon 10:00", "Thu 12:00"], для отображения расписания и контроля нагрузки.
+ ```room```: аудитория или онлайн‑канал.
+ ```examType```: тип итогового контроля.

##### enrollments:
```Описание
Документ enrollments фиксирует факт записи конкретного студента на конкретный поток курса.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```studentId```: ссылка на _id документа в students, кто записан.
+ ```courseOfferingId```: ссылка на _id документа в course_offerings, на какой именно поток записан.
+ ```enrolledAt```: дата/время записи студента на поток, datetime.
+ ```status```: статус записи ("active" — учится, "dropped" — отчислен/снялся с курса, "completed" — завершил курс), помогает отслеживать историю и актуальные нагрузки.

##### grades:
```Описание
Документ grades представляет одну оценку, полученную студентом в рамках определённого потока курса.
```
+ ```_id```: внутренний идентификатор MongoDB, ObjectId.
+ ```studentId```: ссылка на _id документа в students, чья это оценка.
+ ```courseOfferingId```: ссылка на _id документа в course_offerings, по какому потоку выставлена оценка.
+ ```assessmentType```: тип контроля ("exam", "test", "lab", "hw").
+ ```assessmentName```: название контроля.
+ ```maxScore```: максимальный возможный балл за работу.
+ ```score```: фактический балл студента.
+ ```grade```: итоговая оценка в принятой шкале.
+ ```weight```: вклад этой работы в итоговую оценку по курсу.
+ ```date```: дата/время выставления оценки, datetime.
+ ```attempt```: номер попытки (1 — первая сдача, 2 и далее — пересдачи), позволяет разделять первичные и повторные результаты.

#### Общая работа
##### Типовые запросы и оптимизация
###### 1. Найти студента по номеру зачетки
**Запрос:**    
```js
db.students.findOne({ studentNumber: "S353301" })
```
**Результат:**    
```js
{
  _id: ObjectId('693b3b8035057b0758c40768'),
  studentNumber: 'S353301',
  firstName: 'Анжела',
  lastName: 'Ершов',
  middleName: 'Борисовна',
  email: 'pantelemon53@example.org',
  group: 'IU5-28',
  faculty: 'ФРТК',
  enrollmentYear: 2022,
  isActive: true
}
```
###### 2. Список студентов группы
**Запрос:**

```js
db.students.find({ group: "IU5-31", isActive: true })
```
**Результат:**
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c3f904'),
    studentNumber: 'S976207',
    firstName: 'Ипполит',
    lastName: 'Бобров',
    middleName: 'Федосеевич',
    email: 'mihail52@example.com',
    group: 'IU5-31',
    faculty: 'ФПМИ',
    enrollmentYear: 2023,
    isActive: true
  },
  {
    _id: ObjectId('693b3b8035057b0758c3f933'),
    studentNumber: 'S760865',
    firstName: 'Марфа',
    lastName: 'Щукина',
    middleName: 'Бориславович',
    email: 'gushchinmoise@example.com',
    group: 'IU5-31',
    faculty: 'ФПМИ',
    enrollmentYear: 2021,
    isActive: true
  },
  {
    _id: ObjectId('693b3b8035057b0758c3f97d'),
    studentNumber: 'S71931',
    firstName: 'Зиновий',
    ...,
  }
]
```

###### 3. Курсы одного преподавателя в учебном году
**Запрос:**    
```js
db.course_offerings.find({
  teacherId: ObjectId("693b3b8035057b0758c42002"),
  academicYear: "2024/2025"
})
```
**Результат:**    
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c422ad'),
    courseId: ObjectId('693b3b8035057b0758c4225b'),
    teacherId: ObjectId('693b3b8035057b0758c42002'),
    academicYear: '2024/2025',
    semester: 7,
    group: 'IU5-11',
    schedule: [ 'Wed 13:45', 'Tue 12:00' ],
    room: 'Ауд. 342',
    examType: 'project'
  },
  {
    _id: ObjectId('693b3b8035057b0758c422b0'),
    courseId: ObjectId('693b3b8035057b0758c4225c'),
    teacherId: ObjectId('693b3b8035057b0758c42002'),
    academicYear: '2024/2025',
    semester: 4,
    ...,
  },
  ...,
]
```

###### 4. Студенты, записанные на конкретный поток курса
**Запрос:**    
```js
db.enrollments.aggregate([
  { $match: { courseOfferingId: ObjectId("693b3b8035057b0758c42364"), status: "active" } },
  {
    $lookup: {
      from: "students",
      localField: "studentId",
      foreignField: "_id",
      as: "student"
    }
  },
  { $unwind: "$student" }
])
```
**Результат:**    
```js
b.enrollments.aggregate([
  { $match: { courseOfferingId: ObjectId("693b3b8035057b0758c42364"), status: "active" } },
  {
    $lookup: {
      from: "students",
      localField: "studentId",
      foreignField: "_id",
      as: "student"
    }
  },
  { $unwind: "$student" }
])
```
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c42412'),
    studentId: ObjectId('693b3b8035057b0758c3f90a'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42364'),
    enrolledAt: ISODate('2025-12-11T21:45:36.335Z'),
    status: 'active',
    student: {
      _id: ObjectId('693b3b8035057b0758c3f90a'),
      studentNumber: 'S593713',
      firstName: 'Леон',
      lastName: 'Сорокин',
      middleName: 'Бориславович',
      email: 'valeri_1995@example.net',
      group: 'IU5-41',
      faculty: 'ФРТК',
      enrollmentYear: 2022,
      isActive: true
    }
  },
  {
    _id: ObjectId('693b3b8035057b0758c426b2'),
    studentId: ObjectId('693b3b8035057b0758c3f990'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42364'),
    enrolledAt: ISODate('2025-12-11T21:45:36.344Z'),
    status: 'active',
    student: {
      _id: ObjectId('693b3b8035057b0758c3f990'),
      ...},
    ...,
  },
]
```

###### 5. Все потоки курса (для построения расписания)
**Запрос:**    

```js
db.course_offerings.find({
  courseId: ObjectId("693b3b8035057b0758c422a0"),
  academicYear: "2024/2025"
}).sort({ semester: 1, group: 1 })
```

**Результат:**    
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c4237c'),
    courseId: ObjectId('693b3b8035057b0758c422a0'),
    teacherId: ObjectId('693b3b8035057b0758c42002'),
    academicYear: '2024/2025',
    semester: 3,
    group: 'IU5-11',
    schedule: [ 'Fri 10:15', 'Tue 10:15' ],
    room: 'Ауд. 326',
    examType: 'credit'
  },
  {
    _id: ObjectId('693b3b8035057b0758c4237d'),
    courseId: ObjectId('693b3b8035057b0758c422a0'),
    teacherId: ObjectId('693b3b8035057b0758c42003'),
    academicYear: '2024/2025',
    semester: 3,
    group: 'IU5-12',
    schedule: [ 'Wed 13:45', 'Thu 08:30' ],
    room: 'Ауд. 297',
    examType: 'project'
  }
]
```

**Оптимизация:**    
```js
db.course_offerings.createIndex(
  { courseId: 1, academicYear: 1, semester: 1, group: 1 }
)
```
Составной индекс по схеме «равенство → равенство → сортировка» позволяет получить covered‑query без дополнительной сортировки в памяти.​

###### 6. Все оценки студента по всем курсам
**Запрос:**

```js
db.grades.find({ studentId: ObjectId("693b3b8035057b0758c3f990") }).sort({ date: -1 })
```

**Результат:**

```js
[
  {
    _id: ObjectId('693b3b8535057b0758c4f342'),
    studentId: ObjectId('693b3b8035057b0758c3f990'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42326'),
    assessmentType: 'exam',
    assessmentName: 'Exam #1',
    maxScore: 100,
    score: 94,
    grade: 'A',
    weight: 0.4,
    date: ISODate('2025-12-11T21:45:37.609Z'),
    attempt: 1
  },
  {
    _id: ObjectId('693b3b8535057b0758c4f343'),
    studentId: ObjectId('693b3b8035057b0758c3f990'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42326'),
    assessmentType: 'lab',
    assessmentName: 'Lab #1',
    maxScore: 100,
    score: 77,
    grade: 'F',
    weight: 0.5,
    date: ISODate('2025-12-11T21:45:37.609Z'),
    attempt: 3
  },
  ...
]
```

###### 7. Итоговая успеваемость студента (средний балл)
**Запрос:**

```js
db.grades.aggregate([
  { $match: { studentId: ObjectId("693b3b8035057b0758c3f990") } },
  {
    $group: {
      _id: "$studentId",
      avgScore: { $avg: "$score" },
      exams: { $sum: 1 }
    }
  }
])
```

**Результат:**
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c3f990'),
    avgScore: 77.45,
    exams: 20
  }
]
```

###### 8. Средний балл по курсу (в одном учебном году)
**Запрос:**

```js
db.grades.aggregate([
  { $lookup: {
      from: "course_offerings",
      localField: "courseOfferingId",
      foreignField: "_id",
      as: "offering"
  }},
  { $unwind: "$offering" },
  { $match: { "offering.courseId": ObjectId("693b3b8035057b0758c422a0"), "offering.academicYear": "2024/2025" } },
  {
    $group: {
      _id: "$offering.courseId",
      avgScore: { $avg: "$score" }
    }
  }
])
```

**Результат:**
```js
[
  {
    _id: ObjectId('693b3b8035057b0758c422a0'),
    avgScore: 70.19050343249428
  }
]
```

**Оптимизация:**
```js
db.grades.createIndex({ courseOfferingId: 1 })
db.course_offerings.createIndex({ courseId: 1, academicYear: 1 })
```

Индексация courseOfferingId и courseId + academicYear уменьшает объём данных, обрабатываемых в $lookup и $match, что критично для больших таблиц оценок.​

###### 9. Средний балл по курсу у конкретного преподавателя
**Запрос:**

```js
db.grades.aggregate([
  { $lookup: {
      from: "course_offerings",
      localField: "courseOfferingId",
      foreignField: "_id",
      as: "offering"
  }},
  { $unwind: "$offering" },
  {
    $match: {
      "offering.courseId": ObjectId("693b3b8035057b0758c4225c"),
      "offering.teacherId": ObjectId("693b3b8035057b0758c42002"),
      "offering.academicYear": "2024/2025"
    }
  },
  { $group: { _id: "$offering.teacherId", avgScore: { $avg: "$score" } } }
])
```

**Результат:**

```js
[
  {
    _id: ObjectId('693b3b8035057b0758c42002'),
    avgScore: 69.54122340425532
  }
]
```

**Оптимизация:**

```js
db.course_offerings.createIndex(
  { courseId: 1, teacherId: 1, academicYear: 1 }
)
db.grades.createIndex({ courseOfferingId: 1 })
```

Составной индекс по курсу, преподавателю и году поддерживает фильтрацию и аналитические отчёты по конкретным преподавателям.​

###### 10. Список студентов с задолженностями (неуд по экзамену)
**Запрос:**

```js
db.grades.aggregate([
  {
    $match: {
      assessmentType: "exam",
      grade: { $in: ["F", "2", "незачет"] }
    }
  },
  {
    $group: {
      _id: "$studentId",
      failedExams: { $sum: 1 }
    }
  },
  { $match: { failedExams: { $gt: 0 } } }
])
```

**Результат:**

```js
[
  { _id: ObjectId('693b3b8035057b0758c402e5'), failedExams: 2 },
  { _id: ObjectId('693b3b8035057b0758c40825'), failedExams: 1 },
  { _id: ObjectId('693b3b8035057b0758c40d67'), failedExams: 1 },
  { _id: ObjectId('693b3b8035057b0758c41873'), failedExams: 1 },
  ...,
]
```

**Оптимизация:**

```js
db.grades.createIndex({ assessmentType: 1, grade: 1, studentId: 1 })
```
Индекс по типу контроля и оценке позволяет быстро выделить «неудачные» экзамены и сгруппировать их по студентам.​

###### 11. История сдач экзаменов по студенту и курсу
**Запрос:**

```js
db.grades.aggregate([
  {
    $match: {
      studentId: ObjectId("693b3b8035057b0758c402e5"),
      courseOfferingId: ObjectId("693b3b8035057b0758c42376"),
      assessmentType: 'exam'
    }
  },
  { $sort: { date: 1 } }
])
```

**Результат:**

```js
[
  {
    _id: ObjectId('693b3b8535057b0758c5ade6'),
    studentId: ObjectId('693b3b8035057b0758c402e5'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42376'),
    assessmentType: 'exam',
    assessmentName: 'Exam #2',
    maxScore: 100,
    score: 61,
    grade: 'C',
    weight: 0.3,
    date: ISODate('2025-12-11T21:45:38.429Z'),
    attempt: 1
  },
  {
    _id: ObjectId('693b3b8535057b0758c5ade9'),
    studentId: ObjectId('693b3b8035057b0758c402e5'),
    courseOfferingId: ObjectId('693b3b8035057b0758c42376'),
    assessmentType: 'exam',
    assessmentName: 'Exam #2',
    maxScore: 100,
    score: 55,
    grade: 'F',
    weight: 0.5,
    date: ISODate('2025-12-11T21:45:38.429Z'),
    attempt: 3
  }
]
```

###### 12. Нагрузка преподавателя (количество студентов)
**Запрос:**

```js
db.enrollments.aggregate([
  { $lookup: {
      from: "course_offerings",
      localField: "courseOfferingId",
      foreignField: "_id",
      as: "offering"
  }},
  { $unwind: "$offering" },
  {
    $group: {
      _id: "$offering.teacherId",
      studentsCount: { $sum: 1 }
    }
  }
])
```

**Результат:**
```js
[
  { _id: ObjectId('693b5b94887abdef82d4814d'), studentsCount: 207 },
  { _id: ObjectId('693b5b94887abdef82d48262'), studentsCount: 217 },
  { _id: ObjectId('693b5b94887abdef82d4817a'), studentsCount: 203 },
  { _id: ObjectId('693b5b94887abdef82d4821b'), studentsCount: 424 },
  { _id: ObjectId('693b5b94887abdef82d480c3'), studentsCount: 219 },
  ...
]
```

**Оптимизация:**

```js
db.enrollments.createIndex({ courseOfferingId: 1 })
db.course_offerings.createIndex({ teacherId: 1 })
```

Индексы позволяют быстро подсчитывать нагрузку в разрезе преподавателей.​

###### 13. Список всех курсов, на которые записан студент в году
**Запрос:**

```js
db.enrollments.aggregate([
  { $match: { studentId: ObjectId("693b5b94887abdef82d45913"), status: "active" } },
  {
    $lookup: {
      from: "course_offerings",
      localField: "courseOfferingId",
      foreignField: "_id",
      as: "offering"
    }
  },
  { $unwind: "$offering" },
  {
    $match: { "offering.academicYear": "2023/2024" }
  },
  {
    $lookup: {
      from: "courses",
      localField: "offering.courseId",
      foreignField: "_id",
      as: "course"
    }
  },
  { $unwind: "$course" },
  { $project: { _id: 0, courseCode: "$course.code", courseName: "$course.name" } }
])
```

**Результат:**

```js
[ { courseCode: 'CS337', courseName: 'Операционные системы' } ]
```

###### 14. ТОП‑N лучших студентов по среднему баллу
**Запрос:**

```js
db.grades.aggregate([
  {
    $group: {
      _id: "$studentId",
      avgScore: { $avg: "$score" }
    }
  },
  { $sort: { avgScore: -1 } },
  { $limit: 100 }
])
```

**Результат:**

```js
[
  { _id: ObjectId('693b5b94887abdef82d46507'), avgScore: 83.3 },
  { _id: ObjectId('693b5b94887abdef82d47b87'), avgScore: 82.85 },
  { _id: ObjectId('693b5b94887abdef82d46c69'), avgScore: 82.5 },
  { _id: ObjectId('693b5b94887abdef82d45a12'), avgScore: 82.4 },
  { _id: ObjectId('693b5b94887abdef82d47160'), avgScore: 82.4 },
  { _id: ObjectId('693b5b94887abdef82d468e4'), avgScore: 82.35 },
  { _id: ObjectId('693b5b94887abdef82d46f81'), avgScore: 82.3 },
  ...,
]
```
