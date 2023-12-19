from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField, SelectField, StringField\
, DateField, DateTimeField, FileField, SelectMultipleField, DateTimeLocalField
#from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email
#from . models import Branch, User, Item, ItemBranchRel, db

import datetime

class SchoolForm(FlaskForm):
    name = StringField('name')
    board = SelectField('board')
    address = StringField('address')
    city = StringField('city')
    submit = SubmitField('Add/Update')

class ReviewQuestion(FlaskForm):
    back = SubmitField('<-')
    proceed = SubmitField('->')

class TestQuestionLinker(FlaskForm):
    questionText = StringField('Question')
    board = SelectField('Board')
    grade = SelectField('Grade')
    subject = SelectField('Subject')
    chapter = SelectField('Chapter')
    concept = SelectMultipleField('Concept')
    # concept = SelectField('Concept')
    category = SelectField('Category')
    level = SelectField('Level')
    format = SelectField('Format')
    tags = StringField('Tags')
    pyq = StringField('PYQ')
    tests = SelectField('Tests')
    submit = SubmitField('Search')

class CreateTest(FlaskForm):
    testName = StringField('Test Name', validators= [DataRequired()])
    text2 = StringField('Text2')
    text3 = StringField('Text3')
    imagePath = StringField('Image Path', validators= [DataRequired()])
    description = StringField('Description',validators= [DataRequired()])
    preparedBy = StringField('Prepared By', validators= [DataRequired()])
    syllabus = StringField('Syllabus', validators= [DataRequired()])
    tags = StringField('Tags', validators= [DataRequired()])
    maxCoins = StringField('Max Coins')
    maxTime = StringField('Max Time (Static)')
    testType = SelectField('Type', choices=[('1', 'static'), ('2', 'dynamic'), ('3', 'loop')])
    isPracticeTestNeeded = SelectField('isPracticeTestNeeded', choices=[('1', 'Yes'), ('2', 'No')])
    category = SelectField('Category')
    submit = SubmitField('Create')

    def validate(self):
        return True

class MegaSearchForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    gender = SelectField('Gender', choices= [('None', 'None'), ('male', 'male'), ('female', 'female')])
    dob = DateField('DatePicker', format='%Y-%m-%d')
    email = StringField('Email')
    mobile = StringField('Mobile')
    grade = SelectField('Grade')
    board = SelectField('Board')
    school = SelectField('School')
    status = SelectField('Status', choices=[(1, 'Valid'), (0, 'Invalid')])
    parentName = StringField('Parent Name')
    parentMobile = StringField('Parent Mobile')
    city = StringField('City')
    search = SubmitField('Search')
    addStudent = SubmitField('Add/Update Student')

    def validate(self):
        return True

class ImageHelper(FlaskForm):
    list = SelectField('List')
    image = FileField()
    name = StringField('Name')
    search = SubmitField('Search')
    display = SubmitField('Display')
    upload = SubmitField('Upload')

class SubjectChapter(FlaskForm):
    subjectName = StringField('SubjectName')
    subjectCode = StringField('SubjectCode')
    subjectAcademics = SelectField('isAcademics', choices=[('1', True), ('2', False)])
    # subjectSortOrder = SelectField('SubjectSortOrder')
    grade = SelectField('Grade')
    board = SelectField('Board')
    chapterNumber = StringField('ChapterNumber')
    chapterName = StringField('ChapterName')
    chapterImagePath = StringField('ChapterImagePath')
    chapterCaption = StringField('ChapterCaption')
    chapterDescription = StringField('ChapterDescription')
    chapterTags = StringField('ChapterTags')
    # chapterSortOrder = SelectField('ChapterSortOrder')
    search = SubmitField('Search')
    add = SubmitField('Add')
    update = SubmitField('Update')

class Concepts(FlaskForm):
    name = StringField('name')
    grade = SelectField('grade')
    board = SelectField('board')
    subject = SelectField('subject')
    chapter = SelectField('chapter')
    update = SubmitField('update')
    search = SubmitField('search')

class NotificationsForm(FlaskForm):
    title = StringField('Title')
    message = StringField('Message')
    imagePath = SelectField('ImagePath')
    redirectApi = SelectField('RedirectApi')
    school = SelectMultipleField('school')
    board = SelectMultipleField('board')
    grade = SelectMultipleField('grade')
    triggeringTime = StringField('TriggeringTime')
    submit = SubmitField('Submit')
    #
    # def validate(self):
    #     tUG = self.targetUserGroup.data.split(',')
    #     if self.school.data or self.board.data  self.grade.data:
    #         return 'fill targetUserGroup in _,_,_ fashion'
    #     return None

# class ConceptQuestionLinker(FlaskForm):
#     board = SelectField('Board')
#     grade = SelectField('Grade')
#     subject = SelectField('Subject')
#     chapter = SelectField('Chapter')
#     concept = StringField('Question')
#     question = StringField('Question')
#     submit = SubmitField('Search')

# modify test
class ModifyTest(FlaskForm):
    name = StringField('name')
    text2 = StringField('text2')
    text3 = StringField('text3')
    concept = StringField('concept')
    chapter = StringField('chapter')
    subject = StringField('subject')
    category = SelectField('category')
    imagePath = StringField('imagePath')
    description = StringField('description')
    preparedBy = StringField('preparedBy')
    syllabus = StringField('syllabus')
    tags = StringField('tags')
    maxCoins = StringField('coins')
    isStaticTest = SelectField('isStaticTest', choices=[(1, True), (0, False)])
    isLoop = SelectField('isLoop', choices=[(1, True), (0, False)])
    isPracticeTestNeeded = SelectField('isPracticeTestNeeded', choices=[(1, True), (0, False)])
    questionIds = StringField('questionIds')
    maxTime = StringField('maxTime')
    status = SelectField('status', choices=[(1, "Valid"), (0, "Invalid")])
    update = SubmitField("update")
    delete = SubmitField("Final Delete")

class Subscriptions(FlaskForm):
    name = StringField('name')
    price = StringField('price')
    strikedPrice = StringField('strikedPrice')
    numberOfTests = StringField('numberOfTests')
    maxRedeemableCoins = StringField('maxRedeemableCoins')
    comment = StringField('comment')
    grades = SelectField('grades')
    board = SelectField('board')
    validity = StringField('validity')
    update = SubmitField("add/update")

class Coupons(FlaskForm):
    code = StringField('code')
    value = StringField('value')
    maxUses = StringField('maxUses')
    maxPerUser = StringField('maxPerUser')
    startDate = DateField('DatePicker', format='%Y-%m-%d')
    endDate = DateField('DatePicker', format='%Y-%m-%d')
    update = SubmitField("add/update")

class Sales(FlaskForm):
    school = SelectMultipleField('school')
    board = SelectMultipleField('board')
    grade = SelectMultipleField('grade')
    user = SelectMultipleField('user')
    subscription = SelectMultipleField('subscription')
    coupon = SelectMultipleField('coupon')
    merchantTransId = StringField('merchantTransId')
    transId = StringField('transId')
    startDate = DateField('DatePicker', format='%Y-%m-%d')
    endDate = DateField('DatePicker', format='%Y-%m-%d')
    search = SubmitField('Search')
    export = SubmitField('export/Download')

class AnalyticsHome(FlaskForm):
    boards = SelectMultipleField('boards')
    grades = SelectMultipleField('grades')
    sections = SelectMultipleField('sections')
    search = StringField('search')
    subjects = SelectMultipleField('subjects')
    chapters = SelectMultipleField('chapters')
    boardGradeSectionSubjectPair = SelectMultipleField('boardGradeSectionSubjectPair')
    startDate = DateField('DatePicker', format='%Y-%m-%d')
    endDate = DateField('DatePicker', format='%Y-%m-%d')