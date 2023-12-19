from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
import datetime
from src import app, db, indianTime

class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(40))
    city = db.Column(db.String(30))
    tuition = db.Column(db.Boolean())
    status = db.Column(db.Boolean())
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, address, city, tuition, status, datetime):
        self.name = name
        self.address = address
        self.city = city
        self.tuition = tuition
        self.status = status
        self.datetime = datetime


#school teacher, tuition, parent if participate in more than 1 role should use different emails
class Instructor(db.Model):
    __tablename__ = 'instructor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    mobile = db.Column(db.String(10))
    password = db.Column(db.String(15), nullable=False)
    school = db.Column(db.Integer, db.ForeignKey('school.id'))  #for parent schoolId will be None
    status = db.Column(db.Boolean())
    token = db.Column(db.String(20))
    createdBy = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, email, mobile, password, school, status, token, createdBy, datetime):
        self.name = name
        self.email = email
        self.mobile = mobile
        self.password = password
        self.school = school
        self.status = status
        self.token = token
        self.createdBy = createdBy
        self.datetime = datetime

# with app.app_context():
    # Instructor.__table__.drop(db.engine)
    # Instructor.__table__.create(db.engine)


class Avatar(db.Model):
    __tablename__ = 'avatar'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    imagePath = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))

    def __init__(self, name, imagePath, gender):
        self.name = name
        self.imagePath = imagePath
        self.gender = gender


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(15), nullable=False)
    status = db.Column(db.Boolean())
    email = db.Column(db.String(30), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    roles = db.Column(db.String(30), nullable=False)
    token = db.Column(db.String(20))
    createdBy = db.Column(db.Integer, db.ForeignKey('admin.id'))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, password, status, email, mobile, roles, token, createdBy, datetime):
        self.name = name
        self.password = password
        self.status = status
        self.email = email
        self.mobile = mobile
        self.roles = roles
        self.token = token
        self.createdBy = createdBy
        self.datetime = datetime

class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(100), unique=True, nullable=False)
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, description, addedBy, datetime):
        self.description = description
        self.addedBy = addedBy
        self.datetime = datetime


class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.Integer, unique=True)

    def __init__(self, grade):
        self.grade = grade

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(15), nullable=False)
    lastname = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=True)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    grade = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    section = db.Column(db.String(1))
    school = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    tuitions = db.Column(db.String(20)) #comma separated tuitions added
    board = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    testsRemaining = db.Column(db.Integer, nullable=False)
    avatarId = db.Column(db.Integer, db.ForeignKey('avatar.id'), nullable=False)
    coins = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean(), nullable=False)
    referral = db.Column(db.String(10), unique=True, nullable=False)
    parentName = db.Column(db.String(30))
    parentMobile = db.Column(db.String(10), unique=True, nullable=True)
    city = db.Column(db.String(30))
    lastYearResults = db.Column(db.Integer)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    hours = db.Column(db.Integer)

    def __init__(self, firstname, lastname, gender, dob, email, mobile, grade, section, school, tuitions, board, \
    testsRemaining, avatarId, coins, status, referral, \
    parentName, parentMobile, city, lastYearResults, datetime, hours):
        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.dob = dob
        self.email = email
        self.mobile = mobile
        self.grade = grade
        self.section = section
        self.school = school
        self.tuitions = tuitions
        self.board = board
        self.testsRemaining = testsRemaining
        self.avatarId = avatarId
        self.coins = coins
        self.status = status
        self.referral = referral
        self.parentName = parentName
        self.parentMobile = parentMobile
        self.city = city
        self.lastYearResults = lastYearResults
        self.datetime = datetime
        self.hours = hours

class LoginActivity(db.Model):
    __tablename__ = 'loginActivity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deviceInfo = db.Column(db.String(100))
    location = db.Column(db.String(100))
    ip = db.Column(db.String(100))
    dateTime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    user = relationship(User, backref=backref("loginActivity", cascade="all,delete"))

    def __init__(self, userId, deviceInfo, location, ip, dateTime):
        self.userId = userId
        self.deviceInfo = deviceInfo
        self.location = location
        self.ip = ip
        self.dateTime = dateTime

# LoginActivity.__table__.drop(db.engine)
# LoginActivity.__table__.create(db.engine)


class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    grade = db.Column(db.Integer, db.ForeignKey('grade.id'))
    board = db.Column(db.Integer, db.ForeignKey('board.id'))
    academics = db.Column(db.Boolean()) #is academics or general
    sortOrder = db.Column(db.Integer, nullable=False)   #common for all users

    def __init__(self, name, code, grade, board, academics, sortOrder):
        self.name = name
        self.code = code
        self.grade = grade
        self.board = board
        self.academics = academics
        self.sortOrder = sortOrder

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)  #text book chapter number
    name = db.Column(db.String(100), nullable=False)
    imagePath = db.Column(db.String(100), nullable=False)
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    caption = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    tags = db.Column(db.String(200))                #comma separated
    sortOrder = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    subject = relationship(Subject, backref=backref("chapter", cascade="all,delete"))

    def __init__(self, number, name, imagePath, subjectId, caption, description, tags, sortOrder, datetime):
        self.number = number
        self.name = name
        self.imagePath = imagePath
        self.subjectId = subjectId
        self.caption = caption
        self.description = description
        self.tags = tags
        self.sortOrder = sortOrder
        self.datetime = datetime

class Concept(db.Model):    #concept can be mem or general or regular etc
    __tablename__ = 'concept'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    chapterId = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    status = db.Column(db.Boolean())
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, chapterId, subjectId, status, addedBy, datetime):
        self.name = name
        self.addedBy = addedBy
        self.chapterId = chapterId
        self.subjectId = subjectId
        self.status = status
        self.datetime = datetime

class InstructorAssignment(db.Model):
    __tablename__ = 'instructorAssignment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    board = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    grade = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    section = db.Column(db.String(1))
    subject = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    instructorId = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    instructor = relationship(Instructor, backref=backref("instructorAssignment", cascade="all,delete"))

    def __init__(self, board, grade, section, subject, instructorId, datetime):
        self.board = board
        self.grade = grade
        self.section = section
        self.subject = subject
        self.instructorId = instructorId
        self.datetime = datetime


# with app.app_context():
#     InstructorAssignment.__table__.drop(db.engine)
#     InstructorAssignment.__table__.create(db.engine)

class QuestionFormat(db.Model): #mcq or msq or etc
    __tablename__ = 'questionFormat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(15), unique=True, nullable=False)

    def __init__(self, name, code):
        self.name = name
        self.code = code

'''
class QuestionCategory(db.Model):           #memory, analytical ,etc
    __tablename__ = 'questionCategory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __init__(self, name, questionId):
        self.name = name
        self.questionId = questionId
'''
class Question(db.Model):   #enter same question  multiple times for each concept
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(305), nullable=False)
    conceptId = db.Column(db.Integer, db.ForeignKey('concept.id'))
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    difficultyLevel = db.Column(db.String(1), nullable=False)
    format = db.Column(db.Integer, db.ForeignKey('questionFormat.id'), nullable=False)
    category = db.Column(db.String(30))  #PYQ, MEMORY, GK etc   #cannot be None
    hints = db.Column(db.String(100))
    hintsImagePath = db.Column(db.String(100))
    description = db.Column(db.String(200))     #not decided what is this
    tags = db.Column(db.String(200))        #display now but for future
    maxSolvingTime = db.Column(db.Integer, nullable=False)
    ansExplanation = db.Column(db.String(2000))
    ansExpImage = db.Column(db.String(500))
    previousYearApearance = db.Column(db.String(30))    #comma separated
    status = db.Column(db.Boolean())
    concept = relationship(Concept, backref=backref("question", cascade="all,delete"))

    def __init__(self, text, conceptId, addedBy, datetime, difficultyLevel, format, category, hints, hintsImagePath, description, tags, maxSolvingTime, ansExplanation, ansExpImage, previousYearApearance, status):
        self.text = text
        self.conceptId = conceptId
        self.addedBy = addedBy
        self.datetime = datetime
        self.difficultyLevel = difficultyLevel
        self.format = format
        self.category = category
        self.hints = hints
        self.hintsImagePath = hintsImagePath
        self.description = description
        self.tags = tags
        self.maxSolvingTime = maxSolvingTime
        self.ansExplanation = ansExplanation
        self.ansExpImage = ansExpImage
        self.previousYearApearance = previousYearApearance
        self.status = status
#
# class ConceptQuestion(db.Model):
#     __tablename__ = 'conceptQuestion'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     conceptId = db.Column(db.Integer, db.ForeignKey('concept.id'))
#     questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
#
#     concept = relationship(Concept, backref=backref('question', cascade='all, delete-orphan'))
#     def __init__(self, conceptId, questionId):
#         self.conceptId = conceptId
#         self.questionId = questionId


class UserQuestion(db.Model):
    __tablename__ = 'userQuestion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    bookmark = db.Column(db.Boolean())
    report = db.Column(db.Boolean())
    user = relationship(User, backref=backref("userQuestion", cascade="all,delete"))
    question = relationship(Question, backref=backref("userQuestion", cascade="all,delete"))

    def __init__(self, userId, questionId, bookmark, report):
        self.userId = userId
        self.questionId = questionId
        self.bookmark = bookmark
        self.report = report

# UserQuestion.__table__.drop(db.engine)
# UserQuestion.__table__.create(db.engine)

'''
class UserQuestion(db.Model):   #if user looks and skips/answers, record will be added
    __tablename__ = 'userQuestion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    isQuestionReported = db.Column(db.Boolean())
    attemptCount = db.Column(db.Integer)
    skippedCount = db.Column(db.Integer)
    correctedCount = db.Column(db.Integer)
    minTimetaken = db.Column(db.Integer)
    hasAnswered = db.Column(db.Boolean())   #True when correctAnswer
    isBookmarked = db.Column(db.Boolean())
    category = db.Column(db.String(20)) #for saving loops questions, if skipped/wrong answered in loops, the question wont be added to practice test but to sprint tests

    def __init__(self, userId, questionId, isQuestionReported, attemptCount, minTimetaken ,hasAnswered, isBookmarked, category):
        self.userId = userId
        self.questionId = questionId
        self.isQuestionReported = isQuestionReported
        self.attemptCount = attemptCount
        self.minTimetaken = minTimetaken
        self.hasAnswered = hasAnswered
        self.isBookmarked = isBookmarked
        self.category = category
'''

# class QuestionPreviousYearAppearence(db.Model):
#     __tablename__ = 'questionPreviousYearAppearence'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     questionid = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
#     previousYears = db.Column(db.Date, nullable=False)
#
#     def __init__(self, questionId, previousYears):
#         self.questionId = questionId
#         self.previousYears = previousYears

class QuestionMcqMsqDadSeq(db.Model):
    __tablename__ = 'questionMcqMsqDadSeq'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    imagePath = db.Column(db.String(100))
    choice1 = db.Column(db.String(300))
    choice1ImagePath = db.Column(db.String(100))
    choice2 = db.Column(db.String(300))
    choice2ImagePath = db.Column(db.String(100))
    choice3 = db.Column(db.String(300))
    choice3ImagePath = db.Column(db.String(100))
    choice4 = db.Column(db.String(300))
    choice4ImagePath = db.Column(db.String(100))
    correctChoiceSeq = db.Column(db.String(10), nullable=False)#comma separated choices with no spaces in between
    question = relationship(Question, backref=backref("questionMcqMsqDadSeq", cascade="all,delete"))

    def __init__(self,questionId, imagePath, choice1, choice1ImagePath, choice2, choice2ImagePath, choice3, choice3ImagePath, choice4, choice4ImagePath, correctChoiceSeq):
        self.questionId =questionId,
        self.imagePath = imagePath
        self.choice1 = choice1
        self.choice1ImagePath = choice1ImagePath
        self.choice2 = choice2
        self.choice2ImagePath = choice2ImagePath
        self.choice3 = choice3
        self.choice3ImagePath = choice3ImagePath
        self.choice4 = choice4
        self.choice4ImagePath = choice4ImagePath
        self.correctChoiceSeq = correctChoiceSeq

class QuestionFillTorF(db.Model):   #only one blank for FTB
    __tablename__ = 'questionFillTorF'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    imagePath = db.Column(db.String(100))
    correctAnswer = db.Column(db.String(100), nullable=False)
    question = relationship(Question, backref=backref("questionFillTorF", cascade="all,delete"))

    def __init__(self, questionId, imagePath, correctAnswer):
        self.questionId = questionId
        self.imagePath = imagePath
        self.correctAnswer = correctAnswer

class QuestionMatch(db.Model):
    __tablename__ = 'questionMatch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    leftChoice1 = db.Column(db.String(100), nullable=False)
    leftChoice1ImagePath = db.Column(db.String(100))
    leftChoice2 = db.Column(db.String(100), nullable=False)
    leftChoice2ImagePath = db.Column(db.String(100))
    leftChoice3 = db.Column(db.String(100))
    leftChoice3ImagePath = db.Column(db.String(100))
    leftChoice4 = db.Column(db.String(100))
    leftChoice4ImagePath = db.Column(db.String(100))
    rightChoice1 = db.Column(db.String(300))
    rightChoice1ImagePath = db.Column(db.String(100))
    rightChoice2 = db.Column(db.String(300))
    rightChoice2ImagePath = db.Column(db.String(100))
    rightChoice3 = db.Column(db.String(300))
    rightChoice3ImagePath = db.Column(db.String(100))
    rightChoice4 = db.Column(db.String(300))
    rightChoice4ImagePath = db.Column(db.String(100))
    correctChoiceSeq = db.Column(db.String(20), nullable=False)
    question = relationship(Question, backref=backref("questionMatch", cascade="all,delete"))

    def __init__(self, questionId, leftChoice1, leftChoice1ImagePath, leftChoice2, leftChoice2ImagePath , leftChoice3,\
     leftChoice3ImagePath, leftChoice4, leftChoice4ImagePath, rightChoice1, rightChoice1ImagePath, rightChoice2,\
     rightChoice2ImagePath, rightChoice3, rightChoice3ImagePath, rightChoice4, rightChoice4ImagePath, correctChoiceSeq):
        self.questionId = questionId
        self.leftChoice1 = leftChoice1
        self.leftChoice1ImagePath = leftChoice1ImagePath
        self.leftChoice2 = leftChoice2
        self.leftChoice2ImagePath = leftChoice2ImagePath
        self.leftChoice3 = leftChoice3
        self.leftChoice3ImagePath = leftChoice3ImagePath
        self.leftChoice4 = leftChoice4
        self.leftChoice4ImagePath = leftChoice4ImagePath
        self.rightChoice1 = rightChoice1
        self.rightChoice1ImagePath = rightChoice1ImagePath
        self.rightChoice2 = rightChoice2
        self.rightChoice2ImagePath = rightChoice2ImagePath
        self.rightChoice3 = rightChoice3
        self.rightChoice3ImagePath = rightChoice3ImagePath
        self.rightChoice4 = rightChoice4
        self.rightChoice4ImagePath = rightChoice4ImagePath
        self.correctChoiceSeq = correctChoiceSeq

#class Hotspot


#1 test has 1 pratice test, if test taken 2 times then all wrong marked only will be added to practice
class TestCategory(db.Model):           #memory, analytical, chapter, practice, PYQ etc
    __tablename__ = 'testCategory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    caption = db.Column(db.String(30))
    imagePath = db.Column(db.String(100))
    sortOrder = db.Column(db.Integer, nullable=False)
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    subject = relationship(Subject, backref=backref("testCategory", cascade="all,delete"))

    def __init__(self, name, caption, imagePath, sortOrder, subjectId, datetime):
        self.name = name
        self.caption = caption
        self.imagePath = imagePath
        self.sortOrder = sortOrder
        self.subjectId = subjectId
        self.datetime = datetime


class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(75), nullable=False)
    text2 = db.Column(db.String(60))
    text3 = db.Column(db.String(40))
    conceptId = db.Column(db.Integer, db.ForeignKey('concept.id'))  #do not use
    chapterId = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    categoryId = db.Column(db.Integer, db.ForeignKey('testCategory.id'))
    imagePath = db.Column(db.String(100))
    description = db.Column(db.String(500))
    preparedBy = db.Column(db.String(100))
    syllabus = db.Column(db.String(100))    #for display in test instruction page #admin entered
    tags = db.Column(db.String(100))    #for display in test instruction page
    maxCoins = db.Column(db.Integer)
    isStaticTest = db.Column(db.Boolean(), nullable=False)  #from backend UI
    isLoop = db.Column(db.Boolean(), nullable=False)  #from backend UI  #for adding desc images etc
    isPracticeTestNeeded = db.Column(db.Boolean(), nullable=False)  #from backend UI
    questionIds = db.Column(db.String(4000))  #comma separated
    maxTime = db.Column(db.Integer) #only for display static test
    status = db.Column(db.Boolean())
    testBasedOn = db.Column(db.String(15))  #chapter or concept or subject  #use only for display purpose
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, text2, text3, conceptId, chapterId, subjectId, categoryId, imagePath, \
    description, preparedBy, syllabus, tags, maxCoins ,isStaticTest, isLoop, isPracticeTestNeeded, questionIds, maxTime, \
    status, testBasedOn, addedBy, datetime):
        self.name = name
        self.text2 = text2
        self.text3 = text3
        self.conceptId = conceptId
        self.chapterId = chapterId
        self.subjectId = subjectId
        self.categoryId = categoryId
        self.imagePath = imagePath
        self.description = description
        self.preparedBy = preparedBy
        self.syllabus = syllabus
        self.tags = tags
        self.maxCoins = maxCoins
        self.isStaticTest = isStaticTest
        self.isLoop = isLoop
        self.isPracticeTestNeeded = isPracticeTestNeeded
        self.questionIds = questionIds
        self.maxTime = maxTime
        self.status = status
        self.testBasedOn = testBasedOn
        self.addedBy= addedBy
        self.datetime = datetime


class InstructorTestScheduling(db.Model):
    __tablename__ = 'instructorTestScheduling'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instructorId = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    testId = db.Column(db.Integer, db.ForeignKey('test.id'))
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    dateTime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    instructor = relationship(Instructor, backref=backref("instructorTestScheduling", cascade="all,delete"))
    test = relationship(Test, backref=backref("instructorTestScheduling", cascade="all,delete"))

    def __init__(self, instructorId, testId, startTime, endTime, dateTime):
        self.instructorId = instructorId
        self.testId = testId
        self.startTime = startTime
        self.endTime = endTime
        self.dateTime = dateTime

# with app.app_context():
#     InstructorTestScheduling.__table__.drop(db.engine)
#     InstructorTestScheduling.__table__.create(db.engine)


#for custom test, practice tests will be created if answered wrong
#text3 only exists for new dynamic test
class UserTest(db.Model):
    __tablename__ = 'userTest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    testId = db.Column(db.Integer, db.ForeignKey('test.id'))    #same for practice, check practice flag
    customName = db.Column(db.String(50))         #if Test name is given then consider it as a Custom Test and custom Practice test name(check)  #in the end Customtests are static
    customSubjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))  #only for custom test
    customTestChapterIds = db.Column(db.String(20))  #comma separated string #all custom related attr should be mandatorily selected
    customTestConceptIds = db.Column(db.String(20))  #comma separated string
    customTestLevelIds = db.Column(db.String(30))  #comma separated string  #for practice test - using this as number of times this was taken
    customTestFormats = db.Column(db.String(30))  #comma separated string #for loops - using this as sprint counter
    paused = db.Column(db.Boolean())
    progress = db.Column(db.Integer)        #set 100% when any type of test ends; for static based on number of questions taken if paused
    coinsEarned = db.Column(db.Integer, nullable=False) #for results
    timetaken = db.Column(db.Integer)
    bookmark = db.Column(db.Boolean())  #can be done only when user submits the test
    practiceTest = db.Column(db.Boolean())  #practice (dont count this for userTestRemaining)
    coins = db.Column(db.Integer)    #like maxCoins #only for practice test to display on test card    #to display on loop sprints history
    questionIds = db.Column(db.String(4000))  #for practice/custom/static add all questions in comma separated fashion; for dynamic/loops add questionIds for non repeatition
    maxTime = db.Column(db.Integer)    #only for practice test
    displayedOnHomePage = db.Column(db.Boolean())   #this test was initially shown on home page so that later if he pauses the test, these only should be shown as paused tests on home page
    target = db.Column(db.Integer)        #for loops (marks in %)
    sprintQuestions = db.Column(db.String(4000))        #for loops
    dateTime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    accuracy = db.Column(db.Integer)   #for results
    score = db.Column(db.Integer)   #=marks; for results
    scoreTotal = db.Column(db.Integer)   #=marks; for analytics
    confidence = db.Column(db.Integer)   # for analytics
    resumeQuesId = db.Column(db.Integer)
    user = relationship(User, backref=backref("userTest", cascade="all,delete"))
    test = relationship(Test, backref=backref("userTest", cascade="all,delete"))

    def __init__(self, userId, testId, customName, customSubjectId, customTestChapterIds, customTestConceptIds, \
    customTestLevelIds, customTestFormats, paused, progress, coinsEarned, timetaken, \
    bookmark, practiceTest, coins, questionIds, maxTime, displayedOnHomePage, \
    target, sprintQuestions, dateTime, accuracy, score, scoreTotal, confidence, resumeQuesId):
        self.userId = userId
        self.testId = testId
        self.customName = customName
        self.customSubjectId = customSubjectId
        self.customTestChapterIds = customTestChapterIds
        self.customTestConceptIds = customTestConceptIds
        self.customTestLevelIds = customTestLevelIds
        self.customTestFormats = customTestFormats
        self.paused = paused
        self.progress = progress
        self.coinsEarned = coinsEarned
        self.timetaken = timetaken
        self.bookmark = bookmark
        self.practiceTest = practiceTest
        self.coins = coins
        self.questionIds = questionIds
        self.maxTime = maxTime
        self.displayedOnHomePage = displayedOnHomePage
        self.target = target
        self.sprintQuestions = sprintQuestions
        self.dateTime = dateTime
        self.accuracy = accuracy
        self.score = score
        self.scoreTotal = scoreTotal
        self.confidence = confidence
        self.resumeQuesId = resumeQuesId

#for saving loops questions, if skipped/wrong answered in loops, the question wont be added to practice test but to sprint tests
class UserQuestionTest(db.Model):
    __tablename__ = 'userQuestionTest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userTestId = db.Column(db.Integer, db.ForeignKey('userTest.id'))
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    review = db.Column(db.Boolean())
    seen = db.Column(db.Boolean())  #for dynamic tests to generate next set of questions
    answer = db.Column(db.String(50))
    isCorrect = db.Column(db.Boolean())
    isPartial = db.Column(db.Boolean())
    marks = db.Column(db.Float)
    timetaken = db.Column(db.Integer)
    category = db.Column(db.String(20))
    question = relationship(Question, backref=backref("userQuestionTest", cascade="all,delete"))
    userTest = relationship(UserTest, backref=backref("userQuestionTest", cascade="all,delete"))

    def __init__(self, userTestId, questionId, review, seen, answer, isCorrect, \
    isPartial, marks, timetaken, category):
        self.userTestId = userTestId
        self.questionId = questionId
        self.review = review
        self.seen = seen
        self.answer = answer
        self.isCorrect = isCorrect
        self.isPartial = isPartial
        self.marks = marks
        self.timetaken = timetaken
        self.category = category

#
# UserQuestionTest.__table__.drop(db.engine)
# UserTest.__table__.drop(db.engine)
# Test.__table__.drop(db.engine)
# TestCategory.__table__.drop(db.engine)
# UserQuestion.__table__.drop(db.engine)
# QuestionMatch.__table__.drop(db.engine)
# QuestionFillTorF.__table__.drop(db.engine)
# QuestionMcqMsqDadSeq.__table__.drop(db.engine)
# Question.__table__.drop(db.engine)
# Concept.__table__.drop(db.engine)
# Chapter.__table__.drop(db.engine)
# Chapter.__table__.create(db.engine)
# Concept.__table__.create(db.engine)
# Question.__table__.create(db.engine)
# QuestionMcqMsqDadSeq.__table__.create(db.engine)
# QuestionFillTorF.__table__.create(db.engine)
# QuestionMatch.__table__.create(db.engine)
# UserQuestion.__table__.create(db.engine)
# TestCategory.__table__.create(db.engine)
# Test.__table__.create(db.engine)
# UserTest.__table__.create(db.engine)
# UserQuestionTest.__table__.create(db.engine)

class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    strikedPrice = db.Column(db.Integer)
    numberOfTests = db.Column(db.Integer, nullable=False)
    maxRedeemableCoins = db.Column(db.Integer, nullable=False)
    couponValid = db.Column(db.Boolean(), nullable=False)
    comment =  db.Column(db.String(15))                 #config 1 recommended/ most valued
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    validity = db.Column(db.Integer, nullable=False)   #only in months
    grade = db.Column(db.Integer, db.ForeignKey('grade.id'))
    board = db.Column(db.Integer, db.ForeignKey('board.id'))
    status = db.Column(db.Boolean(), nullable=False)
    dateTime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, price, strikedPrice, numberOfTests, maxRedeemableCoins, couponValid, comment,\
     addedBy, validity, grade, board, status, dateTime):
        self.name = name
        self.price = price
        self.strikedPrice = strikedPrice
        self.numberOfTests = numberOfTests
        self.maxRedeemableCoins = maxRedeemableCoins
        self.couponValid = couponValid
        self.comment = comment
        self.addedBy = addedBy
        self.validity = validity
        self.grade = grade
        self.board = board
        self.status = status
        self.dateTime = dateTime

class Coupon(db.Model):
    __tablename__ = 'coupon'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)    #uppercase only
    value = db.Column(db.Integer, nullable=False)
    maxUses = db.Column(db.Integer, nullable=False)
    maxPerUser = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean(), nullable=False)
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, code, value, maxUses, maxPerUser, startDate, endDate, status, addedBy, datetime):
        self.code = code
        self.value = value
        self.maxUses = maxUses
        self.maxPerUser = maxPerUser
        self.startDate = startDate
        self.endDate = endDate
        self.status = status
        self.addedBy = addedBy
        self.datetime = datetime

class SubscriptionActivity(db.Model):
    __tablename__ = 'subscriptionActivity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    subsId = db.Column(db.Integer, db.ForeignKey('subscription.id'))
    amount = db.Column(db.Integer)
    couponId = db.Column(db.Integer, db.ForeignKey('coupon.id'))
    expiryDate = db.Column(db.Date)
    testsRemaining = db.Column(db.Integer)
    success = db.Column(db.Boolean(), nullable=False)
    message = db.Column(db.String(30))
    merchantTransactionId = db.Column(db.String(25))
    transactionId = db.Column(db.String(25))
    typeOfMethod = db.Column(db.String(12))
    paymentInfo = db.Column(db.String(400))
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    user = relationship(User, backref=backref("subscriptionActivity", cascade="all,delete"))

    def __init__(self, userId, subsId, amount, couponId, expiryDate, testsRemaining, success, message,\
    merchantTransactionId, transactionId, typeOfMethod, paymentInfo, datetime):
        self.userId = userId
        self.subsId = subsId
        self.amount = amount
        self.couponId = couponId
        self.expiryDate = expiryDate
        self.testsRemaining = testsRemaining
        self.success = success
        self.message = message
        self.merchantTransactionId = merchantTransactionId
        self.transactionId = transactionId
        self.typeOfMethod = typeOfMethod
        self.paymentInfo = paymentInfo
        self.datetime = datetime

# SubscriptionActivity.__table__.drop(db.engine)
# Subscription.__table__.drop(db.engine)
# Subscription.__table__.create(db.engine)
# SubscriptionActivity.__table__.create(db.engine)

class UserCoupon(db.Model):
    __tablename__ = 'userCoupon'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    couponId = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=False)
    user = relationship(User, backref=backref("userCoupon", cascade="all,delete"))

    def __init__(self, userId, couponId):
        self.userId = userId
        self.couponId = couponId

# UserCoupon.__table__.drop(db.engine)
# UserCoupon.__table__.create(db.engine)


class Badges(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    imagePath = db.Column(db.String(100), nullable=False)
    descBefore = db.Column(db.String(50), nullable=False)   #before user gets the badge
    descAfter = db.Column(db.String(50), nullable=False)    #after user gets the badge
    # types = db.Column(db.String(50))
    nextBadgeDesc = db.Column(db.String(50))    #for notice board
    type = db.Column(db.String(15))     #progress/performance/activity
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, imagePath, descBefore, descAfter, nextBadgeDesc, type, addedBy, datetime):
        self.name = name
        self.imagePath = imagePath
        self.descBefore = descBefore
        self.descAfter = descAfter
        self.nextBadgeDesc = nextBadgeDesc
        self.type = type
        self.addedBy = addedBy
        self.datetime = datetime

class UserBadges(db.Model): #one entry per user per Badgetype activity and progress
    __tablename__ = 'userBadges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badgeId = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    subjectName = db.Column(db.String(20))
    achievedDate = db.Column(db.DateTime, nullable=False)
    user = relationship(User, backref=backref("userBadges", cascade="all,delete"))

    def __init__(self, userId, badgeId, subjectName, achievedDate):
        self.userId = userId
        self.badgeId = badgeId
        self.subjectName = subjectName
        self.achievedDate = achievedDate

# UserBadges.__table__.drop(db.engine)
# Badges.__table__.drop(db.engine)
# Badges.__table__.create(db.engine)
# UserBadges.__table__.create(db.engine)

#TODO referral cannot be calculated by cascade delete
class ReferralActivity(db.Model):
    __tablename__ = 'referralActivity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    peerPhoneNumber = db.Column(db.String(50), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))
    user = relationship(User, backref=backref("referralActivity", cascade="all,delete"))

    def __init__(self, userId, peerPhoneNumber, datetime):
        self.userId = userId
        self.peerPhoneNumber = peerPhoneNumber
        self.datetime = datetime


class Banner(db.Model):
    __tablename__  = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))
    imagePath = db.Column(db.String(100), nullable=False)
    sortOrder = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean(), nullable=False)
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, name, imagePath, sortOrder, status, addedBy, datetime):
        self.name = name
        self.imagePath = imagePath
        self.sortOrder = sortOrder
        self.status = status
        self.addedBy = addedBy
        self.datetime = datetime

#notification- admin trigger group(which will be resolved), auto trigger - user
#this is notification activity
class Notifications(db.Model):
    _tablename_ = 'notifications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    message = db.Column(db.String(500), unique=False, nullable=False)
    imagePath = db.Column(db.String(100), unique=False)
    redirect = db.Column(db.String(50), nullable=True)
    targetUserGroup = db.Column(db.String(50), nullable=True)   #school,board,grade ex None,CBSE,10
    triggeringTime = db.Column(db.DateTime)
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, title, message, imagePath, redirect, targetUserGroup, triggeringTime, addedBy, datetime):
        self.title = title
        self.message = message
        self.imagePath = imagePath
        self.redirect = redirect
        self.targetUserGroup = targetUserGroup
        self.triggeringTime = triggeringTime
        self.addedBy = addedBy
        self.datetime = datetime


class Inits(db.Model):
    __tablename__ = 'inits'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    newBadge = db.Column(db.Boolean())
    newWeeklyReports = db.Column(db.String(200))
    newTests = db.Column(db.String(200))
    subscription = db.Column(db.String(200))
    fcmToken = db.Column(db.String(300))
    user = relationship(User, backref=backref("inits", cascade="all,delete"))

    def __init__(self, userId, newBadge, newWeeklyReports, newTests, subscription, fcmToken):
        self.userId = userId
        self.newBadge = newBadge
        self.newWeeklyReports = newWeeklyReports
        self.newTests = newTests
        self.subscription = subscription
        self.fcmToken = fcmToken

# Inits.__table__.create(db.engine)

class AppVersion(db.Model):
    __tablename__ = 'appVersion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.Integer, nullable=False)
    forced = db.Column(db.Boolean(), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, version, forced, datetime):
        self.version = version
        self.forced = forced
        self.datetime = datetime

# AppVersion.__table__.create(db.engine)

class FAQs(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(300))
    answer = db.Column(db.String(1000))
    imagePath = db.Column(db.String(100))  #preferably answer image
    type = db.Column(db.String(50)) #loop, customTest, home, general, registration, subscription #lowercase
    addedBy = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now(indianTime))

    def __init__(self, question, answer, imagePath, type, addedBy, datetime):
        self.question = question
        self.answer = answer
        self.imagePath = imagePath
        self.type = type
        self.addedBy = addedBy
        self.datetime = datetime
# FAQs.__table__.drop(db.engine)
# FAQs.__table__.create(db.engine)

class SplashScreen(db.Model):
    __tablename__ = 'splashScreen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imagePath = db.Column(db.String(100))
    text1 = db.Column(db.String(100))
    text2 = db.Column(db.String(200))

    def __init__(self, imagePath, text1, text2):
        self.imagePath = imagePath
        self.text1 = text1
        self.text2 = text2
# SplashScreen.__table__.create(db.engine)

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    timeType = db.Column(db.String(15)) #week, month, year
    confidence = db.Column(db.Integer)
    confidenceTotal = db.Column(db.Integer)
    score = db.Column(db.Integer)
    scoreTotal = db.Column(db.Integer)
    totalCorrects = db.Column(db.Integer)
    totalQuestions = db.Column(db.Integer)
    totalTests = db.Column(db.Integer)
    totalConceptTests = db.Column(db.Integer)
    totalLoopTests = db.Column(db.Integer)
    totalCustomTests = db.Column(db.Integer)
    totalStaticTests = db.Column(db.Integer)
    totalOtherTests = db.Column(db.Integer)
    totalUserTests = db.Column(db.Integer)
    difficultyLevelCounts = db.Column(db.String(100))    #format - '[easyCorrect,easyTotal,mediumCorrect,mediumTotal,hardCorrect,hardTotal]'
    formatCounts = db.Column(db.String(200))    #similar as above
    user = relationship(User, backref=backref("analysis", cascade="all,delete"))

    def __init__(self, userId, subjectId, timeType, confidence, confidenceTotal, score, scoreTotal, totalCorrects, \
    totalQuestions, totalTests, totalConceptTests, totalLoopTests, totalCustomTests, totalStaticTests,\
    totalOtherTests, totalUserTests, difficultyLevelCounts, formatCounts):
        self.userId = userId
        self.subjectId = subjectId
        self.timeType = timeType
        self.confidence = confidence
        self.confidenceTotal = confidenceTotal
        self.score = score
        self.scoreTotal = scoreTotal
        self.totalCorrects = totalCorrects
        self.totalQuestions = totalQuestions
        self.totalTests = totalTests
        self.totalConceptTests = totalConceptTests
        self.totalLoopTests = totalLoopTests
        self.totalCustomTests = totalCustomTests
        self.totalStaticTests = totalStaticTests
        self.totalOtherTests = totalOtherTests
        self.totalUserTests = totalUserTests
        self.difficultyLevelCounts = difficultyLevelCounts
        self.formatCounts = formatCounts


class UserConcept(db.Model):
    __tablename__='userConcept'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conceptId = db.Column(db.Integer, db.ForeignKey('concept.id'))
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.id'))
    score = db.Column(db.Integer)
    scoreTotal = db.Column(db.Integer)
    user = relationship(User, backref=backref("userConcept", cascade="all,delete"))

    def __init__(self, userId, conceptId, subjectId, score, scoreTotal):
        self.userId = userId
        self.conceptId = conceptId
        self.subjectId = subjectId
        self.score = score
        self.scoreTotal = scoreTotal

# with app.app_context():
#     Analysis.__table__.create(db.engine)
#     UserConcept.__table__.create(db.engine)

#========================================================================================#

# import os
# cwd = os.getcwd()
# path = os.path.abspath(os.path.join(cwd, "src/Images/TEST_CATEGORY/"))

start2EndReplay = 0
if start2EndReplay == 1:
    path = "src/static/img/"
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(AppVersion(1,True,datetime.datetime.now(indianTime)))
        #name
        db.session.add(Board('cbse'))
        db.session.add(Board('state board'))
        # db.session.add(Board('icse'))

        #image, text1, text2
        db.session.add(SplashScreen(path+"splashscreen1.png", "Time for new way of Learning", "With our platform, you have more than detailed tests to take anywhere, anytime!"))
        db.session.add(SplashScreen(path+"splashscreen2.png", "Dynamic Leveling", "The app adopts to according to your level at each corner and gives fun experience "))
        db.session.add(SplashScreen(path+"splashscreen3.png", "Study beyond your curriculam", "Not just curriculam alligned tests, you will be Enlightned by tests from different categories"))
        db.session.add(SplashScreen(path+"splashscreen4.png", "Custom Tests", "Now you can create your own custom tests upto concept level"))
        db.session.add(SplashScreen(path+"splashscreen5.png", "Weekly Reports", "We bring you weekly report which will showcase your performance, activity and progress for that week"))

        #name,imagepath,gender
        db.session.add(Avatar('Avatar1', path+"Avatar-1.png", 'male'))
        db.session.add(Avatar('Avatar2', path+"Avatar-2.png", 'male'))
        db.session.add(Avatar('Avatar3', path+"Avatar-3.png", 'male'))
        db.session.add(Avatar('Avatar4', path+"Avatar-4.png", 'male'))
        db.session.add(Avatar('Avatar5', path+"Avatar-5.png", 'male'))
        db.session.add(Avatar('Avatar6', path+"Avatar-6.png", 'male'))
        db.session.add(Avatar('Avatar7', path+"Avatar-7.png", 'male'))
        db.session.add(Avatar('Avatar8', path+"Avatar-8.png", 'male'))
        db.session.add(Avatar('Avatar9', path+"Avatar-9.png", 'male'))
        db.session.add(Avatar('Avatar10', path+"Avatar-10.png", 'male'))
        db.session.add(Avatar('Avatar11', path+"Avatar-11.png", 'male'))
        db.session.add(Avatar('Avatar12', path+"Avatar-12.png", 'male'))
        db.session.add(Avatar('Avatar13', path+"Avatar-13.png", 'male'))
        db.session.add(Avatar('Avatar14', path+"Avatar-14.png", 'male'))
        db.session.add(Avatar('Avatar15', path+"Avatar-15.png", 'male'))
        db.session.add(Avatar('Avatar16', path+"Avatar-16.png", 'female'))
        db.session.add(Avatar('Avatar17', path+"Avatar-17.png", 'female'))
        db.session.add(Avatar('Avatar18', path+"Avatar-18.png", 'female'))
        db.session.add(Avatar('Avatar19', path+"Avatar-19.png", 'female'))
        db.session.add(Avatar('Avatar20', path+"Avatar-20.png", 'female'))
        db.session.add(Avatar('Avatar21', path+"Avatar-21.png", 'female'))
        db.session.add(Avatar('Avatar22', path+"Avatar-22.png", 'female'))
        db.session.add(Avatar('Avatar23', path+"Avatar-23.png", 'female'))
        db.session.add(Avatar('Avatar24', path+"Avatar-24.png", 'female'))
        db.session.add(Avatar('Avatar25', path+"Avatar-25.png", 'female'))
        db.session.add(Avatar('Avatar26', path+"Avatar-26.png", 'female'))
        db.session.add(Avatar('Avatar27', path+"Avatar-27.png", 'female'))
        db.session.add(Avatar('Avatar28', path+"Avatar-28.png", 'female'))
        db.session.add(Avatar('Avatar29', path+"Avatar-29.png", 'female'))
        db.session.add(Avatar('Avatar30', path+"Avatar-30.png", 'female'))
        db.session.add(Avatar('Avatar31', path+"Avatar-31.png", 'female'))
        db.session.add(Avatar('Avatar32', path+"Avatar-32.png", 'female'))
        db.session.add(Avatar('Avatar33', path+"Avatar-33.png", 'female'))
        db.session.add(Avatar('Avatar34', path+"Avatar-34.png", 'female'))

        #name,pwd,status,email,phone,roles,createdby
        db.session.add(Admin('tej','tej', 1, 'kktejbhushan@gmail.com', '9768843000', 'all', 1, datetime.datetime.now(indianTime)))
        db.session.add(Admin('raju','raju', 1, 'raju.chilukuri666@gmail.com', '8431757301', 'all', 1, datetime.datetime.now(indianTime)))
        db.session.add(Admin('gayathri','gayathri', 1, 'gayathri@123', '123456987', 'notSales', 1, datetime.datetime.now(indianTime)))

        #classNo
        db.session.add(Grade(10))
        db.session.add(Grade(9))
        db.session.add(Grade(8))
        db.session.add(Grade(7))
        db.session.add(Grade(6))

        #name,code
        db.session.add(QuestionFormat('One option out of 4 is correct', 'MCQ'))
        db.session.add(QuestionFormat('One or more options out of 4 may be correct', 'MSQ'))
        db.session.add(QuestionFormat('Fill in the blanks', 'Fill'))
        db.session.add(QuestionFormat('Drag And Drop', 'Drag & Drop'))
        db.session.add(QuestionFormat('True Or False', 'True/False'))
        # db.session.add(QuestionFormat('Match the Following', 'Match'))
        # db.session.add(QuestionFormat('Arrange in Sequene', 'Sequence'))

        #name,board,addr,city
        # db.session.add(School('Holy Cross School', 1, 'Lakshmi Nagar Camp Bellary', 'Bellary', True, datetime.datetime.now(indianTime)))

        #name,code,grade,board,acadmics,sortorder
        db.session.add(Subject('Physics', 'C10S1', 1, 1, True, 1))
        db.session.add(Subject('Chemistry', 'C10S2', 1, 1, True, 2))
        db.session.add(Subject('Biology', 'C10S3', 1, 1, True, 3))
        db.session.add(Subject('Maths', 'C10M', 1, 1, True, 4))
        db.session.add(Subject('History', 'C10SS1', 1, 1, True, 5))
        db.session.add(Subject('Political Science', 'C10SS2', 1, 1, True, 6))
        db.session.add(Subject('Geography', 'C10SS3', 1, 1, True, 7))
        db.session.add(Subject('Economics', 'C10SS4', 1, 1, True, 8))
        db.session.add(Subject('General', 'C10G', 1, 1, False, 9))

        db.session.add(Subject('Physics', 'C9S1', 2, 1, True, 1))
        db.session.add(Subject('Chemistry', 'C9S2', 2, 1, True, 2))
        db.session.add(Subject('Biology', 'C9S3', 2, 1, True, 3))
        db.session.add(Subject('Maths', 'C9M', 2, 1, True, 4))
        db.session.add(Subject('History', 'C9SS1', 2, 1, True, 5))
        db.session.add(Subject('Political Science', 'C9SS2', 2, 1, True, 6))
        db.session.add(Subject('Geography', 'C9SS3', 2, 1, True, 7))
        db.session.add(Subject('Economics', 'C9SS4', 2, 1, True, 8))
        db.session.add(Subject('General', 'C9G', 2, 1, False, 9))

        db.session.add(Subject('Physics', 'S10S1', 1, 2, True, 1))
        db.session.add(Subject('Chemistry', 'S10S2', 1, 2, True, 2))
        db.session.add(Subject('Biology', 'S10S3', 1, 2, True, 3))
        db.session.add(Subject('Maths', 'S10M', 1, 2, True, 4))
        db.session.add(Subject('History 1', 'S10SS11', 1, 2, True, 5))
        db.session.add(Subject('Political Science 1', 'S10SS12', 1, 2, True, 6))
        db.session.add(Subject('Geography 1', 'S10SS13', 1, 2, True, 7))
        db.session.add(Subject('Economics 1', 'S10SS14', 1, 2, True, 8))
        db.session.add(Subject('Business Studies 1', 'S10SS15', 1, 2, True, 9))
        db.session.add(Subject('Sociology 1', 'S10SS16', 1, 2, True, 10))
        db.session.add(Subject('History 2', 'S10SS12', 1, 2, True, 11))
        db.session.add(Subject('Political Science 2', 'S10SS22', 1, 2, True, 12))
        db.session.add(Subject('Geography 2', 'S10SS322', 1, 2, True, 13))
        db.session.add(Subject('Economics 2', 'S10SS42', 1, 2, True, 14))
        db.session.add(Subject('Business Studies 2', 'S10SS52', 1, 2, True, 15))
        db.session.add(Subject('Sociology 2', 'S10SS62', 1, 2, True, 16))
        db.session.add(Subject('General', 'S10G', 1, 2, False, 17))

        db.session.add(Subject('Physics', 'S9S1', 2, 2, True, 1))
        db.session.add(Subject('Chemistry', 'S9S2', 2, 2, True, 2))
        db.session.add(Subject('Biology', 'S9S3', 2, 2, True, 3))
        db.session.add(Subject('Maths', 'S9M', 2, 2, True, 4))
        db.session.add(Subject('History 1', 'S9SS11', 2, 2, True, 5))
        db.session.add(Subject('Political Science 1', 'S9SS12', 2, 2, True, 6))
        db.session.add(Subject('Geography 1', 'S9SS13', 2, 2, True, 7))
        db.session.add(Subject('Economics 1', 'S9SS14', 2, 2, True, 8))
        db.session.add(Subject('Business Studies 1', 'S9SS15', 2, 2, True, 9))
        db.session.add(Subject('Sociology 1', 'S9SS16', 2, 2, True, 10))
        db.session.add(Subject('History 2', 'S9SS12', 2, 2, True, 11))
        db.session.add(Subject('Political Science 2', 'S9SS22', 2, 2, True, 12))
        db.session.add(Subject('Geography 2', 'S9SS322', 2, 2, True, 13))
        db.session.add(Subject('Economics 2', 'S9SS42', 2, 2, True, 14))
        db.session.add(Subject('Business Studies 2', 'S9SS52', 2, 2, True, 15))
        db.session.add(Subject('Sociology 2', 'S9SS62', 2, 2, True, 16))
        db.session.add(Subject('General', 'S9G', 2, 2, False, 17))


        db.session.commit()

        #FAQ #question,answer,imagePath,type(loop, customTest, home, general, registration, subscription),addedby
        db.session.add(FAQs('How to register at Rao Academy?', 'Add your phone number and get verified then add your personal details like First name, Last name, DOB, Grade, and School to get Registered.', None, 'Registration', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Is registration Free at Rao Academy?', 'Yes, Registration is completely free at Rao Academy.', None, 'Registration', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Why should I give my complete academic details during the signup?', 'The app is designed to provide a personalized experience, so in order to do it we need your academic details.', None, 'Registration', 1, datetime.datetime.now(indianTime)))
        #Subscription & Billing
        db.session.add(FAQs('Where can I download the App?', 'The app is available on the google play store. Search for Rao Academy in the search button.', None, 'Subscription', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Is App Available for free?', 'Yes, the app is available for download on the google play store and it’s free for everyone.', None, 'Subscription', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('When do I start getting charged?', 'You will be given 5 tests initially as Free Trail, Once Free Trail is finished, you will be charged based on the Premium pack selected.', None, 'Subscription', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('What is the cost of Subscribing to Rao academy Premium?', 'It is wholly based on the Package you select, so check our subscription page', None, 'Subscription', 1, datetime.datetime.now(indianTime)))
        #Weekly reports
        db.session.add(FAQs('What are weekly reports?', 'Weekly reports are generated on Saturday evenings. They will show your activity for that entire week on the app. Using this you can analyze your performance and Progress.', None, 'Weekly Reports', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Why do I need weekly reports?', 'It helps you to understand your strengths and weaknesses in detail, You as a student should monitor your activity, progress, and performance on weekly basis and should be improving over time.', None, 'Weekly Reports', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('How to improve performance from insights of weekly reports?', 'Based on the analytics given in the weekly report, a student should look into the parameters given and should take practice tests given in the reports to improve.', None, 'Weekly Reports', 1, datetime.datetime.now(indianTime)))
        #Loops
        db.session.add(FAQs('What are loops?', 'Loops are a unique way of taking tests for an entire chapter, unlike concept-based and custom tests. You will set a target score to achieve in a particular chapter before starting a test. Until you achieve that target you will be inside that loop.', None, 'Loops', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('What are Sprints?', 'Sprints are parts of loops basically, one loop is divided into sprints based on your performance. Sprints are generated based on your performance and also based on Dynamic Leveling.', None, 'Loops', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Benefits of Loops?', 'If you targeting to achieve any percentage of knowledge from a chapter this will help you. Once the target is set then until you achieve it you will be challenged with unique questions.', None, 'Loops', 1, datetime.datetime.now(indianTime)))
        #Badges
        db.session.add(FAQs('What are badges?', 'Badges symbolic representation of students Activity, Progress, and Performance in the App.', None, 'Badges', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Types of Badges and How are they awarded?', 'There are 3 types of badges in the Rao Academy app. Badges-based activity, progress, and performance.', None, 'Badges', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('Benefits of Badges?', "On receiving badges, one can understand the student's position in the app in all aspects. Suggestions will be given to get the next badge.", None, 'Badges', 1, datetime.datetime.now(indianTime)))
        #Refer and Earn
        db.session.add(FAQs('How does it work?', 'If you like the app, if you want your friends to have some fun while learning you can share it with your friends. You will receive some coins you can use while purchasing a premium plan next time after your friend successfully signup. Your friend will also receive some coins.', None, 'Refer and Earn', 1, datetime.datetime.now(indianTime)))
        #Test History
        db.session.add(FAQs('What is Test History?', 'Test history is the place where the tests taken by you will be recorded date-wise. So you can go back to any date to check the tests taken on any particular day and also see your performance in any test you have taken. This will help you to analyze your performance overall.', None, 'Test history', 1, datetime.datetime.now(indianTime)))
        #home
        db.session.add(FAQs('What is Activity?','The activity on the app refers to Tests taken by you on any given day. The above graph shows the Number of Tests v/s Days.', None, 'home', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('What is Progress?', "The progress on the app refers to how many tests you have taken from an individual subject. so select the subject from the dropdown on the graph to see the subject's progress. The above graph shows the Number of Tests taken from Subject v/s Days.", None, 'home', 1, datetime.datetime.now(indianTime)))
        db.session.add(FAQs('What is Performance?', 'The performance on the app refers to how much you score on each test for that day. The above graph shows the Average Score  v/s Days.', None, 'home', 1, datetime.datetime.now(indianTime)))

        #name,caption,imagePath,sortOrder,subjectId
        for i in range(1,52):
            if i == 9 or i == 18 or i == 35:
                continue
            db.session.add(TestCategory('Concept Based', 'this', path+"Dynamictests.png", 1, i, datetime.datetime.now(indianTime)))
            db.session.add(TestCategory('Custom Tests', 'this', path+"Customtests.png", 2, i, datetime.datetime.now(indianTime)))
            db.session.add(TestCategory('PYQs', 'this', path+"PYQs.png", 3, i, datetime.datetime.now(indianTime)))

        #number,name,imagepath,subject,caption,desc,tags(comma separated),sortorder
        # db.session.add(Chapter(1, 'Real Numbers', path+'RealNumbers.png', 1, 'Concept Based', 'This chapter gives brief information about the Mathematical reactions and equations', 'MATHS,NCERT,UPDATED SYLLABUS', 1, datetime.datetime.now(indianTime)))

        #title,message,imagePath,redirect,targetUserGroup,triggeringTime,addedBy
        # db.session.add(Notifications('New Tests', 'Hey checkout New tests', path+"1.jpg", 'Link', 'None,CBSE,10', datetime.datetime.now(indianTime).strftime('%Y-%m-%d'), 2, datetime.datetime.now(indianTime)))
        # db.session.add(Notifications('Practice Test', 'Your Practice test is waiting for you', path+"2.jpg", 'Link', 'None,CBSE,10', datetime.datetime.now(indianTime).strftime('%Y-%m-%d'), 2, datetime.datetime.now(indianTime)))

        #desc,addedby
        db.session.add(Roles('admin', 1, datetime.datetime.now(indianTime)))

        #name,price,striked,numOfTest,coins,couponValid,comment,addedby,validity(in months), grade, board, status
        db.session.add(Subscription('Free Trial', 0, 0, 10, 0, 0, 'Popular', 2, 1, None, None, True, datetime.datetime.now(indianTime)))

        db.session.add(Subscription('Monthly',  149, 299, 15, 0, 1, '', 2, 1, 1, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Quaterly', 399, 599, 40, 50, 1, '', 2, 3, 1, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Half Yearly', 699, 899, 100, 100, 1, 'Recommended', 2, 6, 1, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Annually', 1199, 1499, 200, 150, 1, 'Recommended', 2, 12, 1, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Monthly',  149, 299, 15, 0, 1, '', 2, 1, 2, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Quaterly', 399, 599, 40, 50, 1, '', 2, 3, 2, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Half Yearly', 699, 899, 100, 100, 1, 'Recommended', 2, 6, 2, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Annually', 1199, 1499, 200, 150, 1, 'Recommended', 2, 12, 2, 1, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Monthly',  149, 299, 15, 0, 1, '', 2, 1, 1, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Quaterly', 399, 599, 40, 50, 1, '', 2, 3, 1, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Half Yearly', 699, 899, 100, 100, 1, 'Recommended', 2, 6, 1, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Annually', 1199, 1499, 200, 150, 1, 'Recommended', 2, 12, 1, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Monthly',  149, 299, 15, 0, 1, '', 2, 1, 2, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Quaterly', 399, 599, 40, 50, 1, '', 2, 3, 2, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Half Yearly', 699, 899, 100, 100, 1, 'Recommended', 2, 6, 2, 2, True, datetime.datetime.now(indianTime)))
        db.session.add(Subscription('Annually', 1199, 1499, 200, 150, 1, 'Recommended', 2, 12, 2, 2, True, datetime.datetime.now(indianTime)))

        #code,value,maxUses,maxPerUser,startDate,endDate,status,addedBy
        db.session.add(Coupon('FREE 100', 100, 20, 1, '2022-06-03', '2023-06-10', 1, 2, datetime.datetime.now(indianTime)))
        db.session.add(Coupon('JUST 100', 100, 20, 2, '2022-06-03', '2023-06-10', 1, 2, datetime.datetime.now(indianTime)))

        #name,imagepath,descBefore,descAfter,nextBadgeDesc,type,addedby
        #change in config
        db.session.add(Badges('Streak1',path+"streak1.png",'Use app 1 day','Awarded for using the app for 1 day ', 'you are  away', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak2',path+'streak2.png','Use app 2 days in a Row','Awarded for using the app for 2 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak3',path+'streak3.png','Use app 3 days in a Row','Awarded for using the app for 3 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak4',path+'streak4.png','Use app 4 days in a Row','Awarded for using the app for 4 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak5',path+'streak5.png','Use app 5 days in a Row','Awarded for using the app for 5 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak6',path+'streak6.png','Use app 6 days in a Row','Awarded for using the app for 6 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak7',path+'streak7.png','Use app 7 days in a Row','Awarded for using the app for 7 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak8',path+'streak8.png','Use app 8 days in a Row','Awarded for using the app for 8 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak9',path+'streak9.png','Use app 9 days in a Row','Awarded for using the app for 9 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak10',path+'streak10.png','Use app 10 days in a Row','Awarded for using the app for 10 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak11',path+'streak11.png','Use app 11 days in a Row','Awarded for using the app for 11 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak12',path+'streak12.png','Use app 12 days in a Row','Awarded for using the app for 12 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak13',path+'streak13.png','Use app 13 days in a Roww','Awarded for using the app for 13 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak14',path+'streak14.png','Use app 14 days in a Row','Awarded for using the app for 14 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Streak15',path+'streak15.png','Use app 15 days in a Row','Awarded for using the app for 15 days in a Row', 'nextBadgeDesc', 'activity', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Whizzkid',path+"whizzkid.png",'Score 90% in 5 consecutive tests','For Scoring 90% in 5 consecutive tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Performer',path+"performer.png",'Score 90% in 20 consecutive tests','For scoring 90% in 10 consecutive tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Achiever',path+"achiever.png",'Score 90% in 30 consective tests','For Scoring 90% in 20 consective tests', 'you are away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Soldier',path+"soldier.png",'Take 20 practice tests','For taking 40 Practice tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Warrior',path+"warrior.png",'Take 40 practice tests','For taking 60 Practice tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Legendary',path+"legendary.png",'Score 90% in 50 consecutive tests','For scoring 90% in 30 consecutive tests ', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Unstoppable',path+"unstoppable.png",'Score 80% in 5 consecutive tests', 'For Scoring 80% in 5 consecutive tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Fighter',path+"fighter.png",'Take 20 Practice tests','For taking 10 Practice tests', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Champion',path+"champion.png",'Score 80% in 10 consecutive tests','For Scoring 80% in 10 consecutive tests ', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Allrounder',path+"allrounder.png",'Take atleast 5 tests from all subjects','For taking atleast 5 tests from all subjects', 'you are  away', 'performance', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Maths-beginner',path+"Maths-beginner.png",'Take 5 tests from maths','For taking 5 tests from Maths', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Maths-learner',path+"Maths-learner.png",'Take 20 tests from maths','For taking 20 tests from ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Maths-risingstar',path+"Maths-risingstar.png",'Take 40 tests from maths','For taking 40 tests from Maths', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Maths-expert',path+"Maths-expert.png",'Take 70 tests from maths','For taking 70 tests any from Maths ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Maths-scholar',path+"Maths-scholar.png",'Take 100 tests from maths','For Taking 100 tests any from Maths', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Physics-beginner',path+"Physics-beginner.png",'Take 5 tests from physics','For taking 5 tests from Physics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Physics-learner',path+"Physics-learner.png",'Take 20 tests from physics','For taking 20 tests from Physics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Physics-risingstar',path+"Physics-risingstar.png",'Take 40 tests from physics','For taking 40 tests from Physics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Physics-expert',path+"Physics-expert.png",'Take 70 tests from physics','For taking 70 tests any from Physics ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Physics-scholar',path+"Physics-scholar.png",'Take 100 tests from physics','For Taking 100 tests any from Physics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Chemistry-beginner',path+"Chemistry-beginner.png",'Take 5 tests from chemistry','For taking 5 tests from Chemistry', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Chemistry-learner',path+"Chemistry-learner.png",'Take 20 tests from chemistry','For taking 20 tests from Chemistry', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Chemistry-risingstar',path+"Chemistry-risingstar.png",'Take 40 tests from chemistry','For taking 40 tests from Chemistry', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Chemistry-expert',path+"Chemistry-expert.png",'Take 70 tests from chemistry','For taking 70 tests any from Chemistry ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Chemistry-scholar',path+"Chemistry-scholar.png",'Take 100 tests from chemistry','For Taking 100 tests any from Chemistry', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Biology-beginner',path+"Biology-beginner.png",'Take 5 tests from biology','For taking 5 tests from Biology', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Biology-learner',path+"Biology-learner.png",'Take 20 tests from biology','For taking 20 tests from Biology', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Biology-risingstar',path+"Biology-risingstar.png",'Take 40 tests from biology','For taking 40 tests from Biology', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Biology-expert',path+"Biology-expert.png",'Take 70 tests from biology','For taking 70 tests any from Biology ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Biology-scholar',path+"Biology-scholar.png",'Take 100 tests from biology','For Taking 100 tests any from Biology', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('History-beginner',path+"History-beginner.png",'Take 5 tests from History','For taking 5 tests from History', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History-learner',path+"History-learner.png",'Take 20 tests from History','For taking 20 tests from History', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History-risingstar',path+"History-risingstar.png",'Take 40 tests from History','For taking 40 tests from History', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History-expert',path+"History-expert.png",'Take 70 tests from History','For taking 70 tests any from History ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History-scholar',path+"History-scholar.png",'Take 100 tests from History','For Taking 100 tests any from History', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('History 1-beginner',path+"History 1-beginner.png",'Take 5 tests from History 1','For taking 5 tests from History 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 1-learner',path+"History 1-learner.png",'Take 20 tests from History 1','For taking 20 tests from History 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 1-risingstar',path+"History 1-risingstar.png",'Take 40 tests from History 1','For taking 40 tests from History 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 1-expert',path+"History 1-expert.png",'Take 70 tests from History 1','For taking 70 tests any from History 1 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 1-scholar',path+"History 1-scholar.png",'Take 100 tests from History 1','For Taking 100 tests any from History 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('History 2-beginner',path+"History 2-beginner.png",'Take 5 tests from History 2','For taking 5 tests from History 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 2-learner',path+"History 2-learner.png",'Take 20 tests from History 2','For taking 20 tests from History 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 2-risingstar',path+"History 2-risingstar.png",'Take 40 tests from History 2','For taking 40 tests from History 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 2-expert',path+"History 2-expert.png",'Take 70 tests from History 2','For taking 70 tests any from History 2 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('History 2-scholar',path+"History 2-scholar.png",'Take 100 tests from History 2','For Taking 100 tests any from History 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Political Science-beginner',path+"Political Science-beginner.png",'Take 5 tests from Political Science','For taking 5 tests from Political Science', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science-learner',path+"Political Science-learner.png",'Take 20 tests from Political Science','For taking 20 tests from Political Science', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science-risingstar',path+"Political Science-risingstar.png",'Take 40 tests from Political Science','For taking 40 tests from Political Science', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science-expert',path+"Political Science-expert.png",'Take 70 tests from Political Science','For taking 70 tests any from Political Science ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science-scholar',path+"Political Science-scholar.png",'Take 100 tests from Political Science','For Taking 100 tests any from Political Science', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Political Science 1-beginner',path+"Political Science 1-beginner.png",'Take 5 tests from Political Science 1','For taking 5 tests from Political Science 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 1-learner',path+"Political Science 1-learner.png",'Take 20 tests from Political Science 1','For taking 20 tests from Political Science 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 1-risingstar',path+"Political Science 1-risingstar.png",'Take 40 tests from Political Science 1','For taking 40 tests from Political Science 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 1-expert',path+"Political Science 1-expert.png",'Take 70 tests from Political Science 1','For taking 70 tests any from Political Science 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 1-scholar',path+"Political Science 1-scholar.png",'Take 100 tests from Political Science 1','For Taking 100 tests any from Political Science 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Political Science 2-beginner',path+"Political Science 2-beginner.png",'Take 5 tests from Political Science 2','For taking 5 tests from Political Science 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 2-learner',path+"Political Science 2-learner.png",'Take 20 tests from Political Science 2','For taking 20 tests from Political Science 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 2-risingstar',path+"Political Science 2-risingstar.png",'Take 40 tests from Political Science 2','For taking 40 tests from Political Science 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 2-expert',path+"Political Science 2-expert.png",'Take 70 tests from Political Science 2','For taking 70 tests any from Political Science 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Political Science 2-scholar',path+"Political Science 2-scholar.png",'Take 100 tests from Political Science 2','For Taking 100 tests any from Political Science 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Geography-beginner',path+"Geography-beginner.png",'Take 5 tests from Geography','For taking 5 tests from Geography', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography-learner',path+"Geography-learner.png",'Take 20 tests from Geography','For taking 20 tests from Geography', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography-risingstar',path+"Geography-risingstar.png",'Take 40 tests from Geography','For taking 40 tests from Geography', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography-expert',path+"Geography-expert.png",'Take 70 tests from Geography','For taking 70 tests any from Geography ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography-scholar',path+"Geography-scholar.png",'Take 100 tests from Geography','For Taking 100 tests any from Geography', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Geography 1-beginner',path+"Geography 1-beginner.png",'Take 5 tests from Geography 1','For taking 5 tests from Geography 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 1-learner',path+"Geography 1-learner.png",'Take 20 tests from Geography 1','For taking 20 tests from Geography 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 1-risingstar',path+"Geography 1-risingstar.png",'Take 40 tests from Geography 1','For taking 40 tests from Geography 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 1-expert',path+"Geography 1-expert.png",'Take 70 tests from Geography 1','For taking 70 tests any from Geography 1 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 1-scholar',path+"Geography 1-scholar.png",'Take 100 tests from Geography 1','For Taking 100 tests any from Geography 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))


        db.session.add(Badges('Geography 2-beginner',path+"Geography 2-beginner.png",'Take 5 tests from Geography 2','For taking 5 tests from Geography 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 2-learner',path+"Geography 2-learner.png",'Take 20 tests from Geography 2','For taking 20 tests from Geography 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 2-risingstar',path+"Geography 2-risingstar.png",'Take 40 tests from Geography 2','For taking 40 tests from Geography 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 2-expert',path+"Geography 2-expert.png",'Take 70 tests from Geography 2','For taking 70 tests any from Geography 2 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Geography 2-scholar',path+"Geography 2-scholar.png",'Take 100 tests from Geography 2','For Taking 100 tests any from Geography 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))


        db.session.add(Badges('Economics-beginner',path+"Economics-beginner.png",'Take 5 tests from Economics','For taking 5 tests from Economics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics-learner',path+"Economics-learner.png",'Take 20 tests from Economics','For taking 20 tests from Economics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics-risingstar',path+"Economics-risingstar.png",'Take 40 tests from Economics','For taking 40 tests from Economics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics-expert',path+"Economics-expert.png",'Take 70 tests from Economics','For taking 70 tests any from Economics ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics-scholar',path+"Economics-scholar.png",'Take 100 tests from Economics','For Taking 100 tests any from Economics', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Economics 1-beginner',path+"Economics 1-beginner.png",'Take 5 tests from Economics 1','For taking 5 tests from Economics 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 1-learner',path+"Economics 1-learner.png",'Take 20 tests from Economics 1','For taking 20 tests from Economics 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 1-risingstar',path+"Economics 1-risingstar.png",'Take 40 tests from Economics 1','For taking 40 tests from Economics 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 1-expert',path+"Economics 1-expert.png",'Take 70 tests from Economics 1','For taking 70 tests any from Economics 1 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 1-scholar',path+"Economics 1-scholar.png",'Take 100 tests from Economics 1','For Taking 100 tests any from Economics 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Economics 2-beginner',path+"Economics 2-beginner.png",'Take 5 tests from Economics 2','For taking 5 tests from Economics 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 2-learner',path+"Economics 2-learner.png",'Take 20 tests from Economics 2','For taking 20 tests from Economics 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 2-risingstar',path+"Economics 2-risingstar.png",'Take 40 tests from Economics 2','For taking 40 tests from Economics 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 2-expert',path+"Economics 2-expert.png",'Take 70 tests from Economics 2','For taking 70 tests any from Economics 2 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Economics 2-scholar',path+"Economics 2-scholar.png",'Take 100 tests from Economics 2','For Taking 100 tests any from Economics 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Sociology 1-beginner',path+"Sociology 1-beginner.png",'Take 5 tests from Sociology 1','For taking 5 tests from Sociology 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 1-learner',path+"Sociology 1-learner.png",'Take 20 tests from Sociology 1','For taking 20 tests from Sociology 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 1-risingstar',path+"Sociology 1-risingstar.png",'Take 40 tests from Sociology 1','For taking 40 tests from Sociology 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 1-expert',path+"Sociology 1-expert.png",'Take 70 tests from Sociology 1','For taking 70 tests any from Sociology 1 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 1-scholar',path+"Sociology 1-scholar.png",'Take 100 tests from Sociology 1','For Taking 100 tests any from Sociology 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Sociology 2-beginner',path+"Sociology 2-beginner.png",'Take 5 tests from Sociology 2','For taking 5 tests from Sociology 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 2-learner',path+"Sociology 2-learner.png",'Take 20 tests from Sociology 2','For taking 20 tests from Sociology 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 2-risingstar',path+"Sociology 2-risingstar.png",'Take 40 tests from Sociology 2','For taking 40 tests from Sociology 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 2-expert',path+"Sociology 2-expert.png",'Take 70 tests from Sociology 2','For taking 70 tests any from Sociology 2 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Sociology 2-scholar',path+"Sociology 2-scholar.png",'Take 100 tests from Sociology 2','For Taking 100 tests any from Sociology 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Business Studies 1-beginner',path+"Business Studies 1-beginner.png",'Take 5 tests from Business Studies 1','For taking 5 tests from Business Studies 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 1-learner',path+"Business Studies 1-learner.png",'Take 20 tests from Business Studies 1','For taking 20 tests from Business Studies 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 1-risingstar',path+"Business Studies 1-risingstar.png",'Take 40 tests from Business Studies 1','For taking 40 tests from Business Studies 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 1-expert',path+"Business Studies 1-expert.png",'Take 70 tests from Business Studies 1','For taking 70 tests any from Business Studies 1 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 1-scholar',path+"Business Studies 1-scholar.png",'Take 100 tests from Business Studies 1','For Taking 100 tests any from Business Studies 1', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        db.session.add(Badges('Business Studies 2-beginner',path+"Business Studies 2-beginner.png",'Take 5 tests from Business Studies 2','For taking 5 tests from Business Studies 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 2-learner',path+"Business Studies 2-learner.png",'Take 20 tests from Business Studies 2','For taking 20 tests from Business Studies 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 2-risingstar',path+"Business Studies 2-risingstar.png",'Take 40 tests from Business Studies 2','For taking 40 tests from Business Studies 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 2-expert',path+"Business Studies 2-expert.png",'Take 70 tests from Business Studies 2','For taking 70 tests any from Business Studies 2 ', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))
        db.session.add(Badges('Business Studies 2-scholar',path+"Business Studies 2-scholar.png",'Take 100 tests from Business Studies 2','For Taking 100 tests any from Business Studies 2', 'you are away', 'progress', 2, datetime.datetime.now(indianTime)))

        #name,imgPath,sortOrder,status,addedBy
        db.session.add(Banner('banner1',path+'banner1.jpg', 1, 1, 2, datetime.datetime.now(indianTime)))
        db.session.add(Banner('banner2',path+'banner2.jpg', 1, 1, 2, datetime.datetime.now(indianTime)))
        db.session.add(Banner('banner3',path+'banner3.png', 1, 1, 2, datetime.datetime.now(indianTime)))
        db.session.add(Banner('banner4',path+'banner4.png', 1, 1, 2, datetime.datetime.now(indianTime)))
        db.session.commit()

        db.session.commit()
    start2EndReplay+=1


raju = 0
if raju == 1:
    #do raju changes
    # db.session.add(UserTest(10, 1, 'metal', None, None, None, None, False, 100, 12, True, 'concept', 2, datetime.datetime.now(indianTime)))
    # db.session.add(UserTest(10, 2, 'nonmetal', None, None, None, None, False, 100, 10, True, 'subject', 2, datetime.datetime.now(indianTime)))
    # db.session.add(UserTest(10, 3, 'nobel', None, None, None, None, False, 100, 14, True, 'chapter', 2, datetime.datetime.now(indianTime)))
    db.session.commit()
