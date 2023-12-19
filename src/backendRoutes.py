from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, send_from_directory, send_file, render_template_string
from . models import User, School, Avatar, Admin, Roles, Grade, Board, Subject, Concept, Question,\
QuestionFormat, QuestionMcqMsqDadSeq, QuestionFillTorF, Coupon, Instructor, UserBadges, Badges,\
QuestionMatch, Chapter, TestCategory, Test, Notifications, Subscription, SubscriptionActivity, LoginActivity, Inits, UserTest,\
UserQuestionTest, InstructorAssignment, InstructorTestScheduling
from . forms import ReviewQuestion, TestQuestionLinker, CreateTest, MegaSearchForm, AnalyticsHome, \
ImageHelper, SubjectChapter, NotificationsForm, ModifyTest, Subscriptions, Coupons, Sales, SchoolForm, Concepts
from . dbOps import getGrade, getAllGrades, getBoard, getAllBoards, getSchool, insertSchool,\
getAvatar, getAllAvatars, getUser, getAllUsers, updateUser, getSubscription, getSubscriptionActivity, getAllSubscriptionActivity, insertSubscriptionActivity, \
updateSubscriptionActivity, insertReferralActivity, insertUserBadge, \
getInits, insertInits, updateInits, getSubject, getAllSubjects, getUserTest, getAllUserTests, updateUserTest, insertUserTest, getTest, \
getAllTestsByIds, getAllTests, getAllUserQuestions, getQuestion,\
getAllQuestions, getConcept, getAllConcepts, getQuestionFormat, getAllQuestionFormats, getAnalysis, updateAnalysis, getAllUserConcepts, getChapter,\
getAllChapters, getAllTestCategories, getAllFaqs, getUserQuestionTest, getAllUserQuestionTests, deleteAllUserQuestionTests, \
updateUserQuestionTest, insertUserQuestionTest, getQuestionMcqMsqDadSeq, getQuestionFillTorF, getQuestionMatch, getInstructor, getAllInstructors, insertInstructor, updateInstructor,\
getAdmin, updateAdmin, getAllInstructorAssignments, insertInstructorAssignment, deleteInstructorAssignment, getInstructorTestScheduling, getAllInstructorTestSchedulings, insertInstructorTestScheduling, deleteInstructorScheduling,\
getAllSchools

#, ConceptQuestionLinker
#, SignUpForm, FillingForm, BranchForm, BillForm, SearchInventoryForm, BillDetailsForm, SalesForm
from src import app, db, username, password, db_name, indianTime
import datetime, json, requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, exc, or_, and_, case, Integer, String
from pandas_ods_reader import read_ods
import traceback, sys

from collections import OrderedDict
from pyexcel_ods3 import save_data
import os, time, pandas

from . frontendRoutes import addStudent, fnotification, getDates, addSchool, ftestResultsFunc
import logging, inspect

from logging.handlers import RotatingFileHandler
log_handler = RotatingFileHandler('debug.log', maxBytes=1000000, backupCount=1)
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%m-%d %H:%M:%S'))
log_handler.formatter.converter = lambda *args: datetime.datetime.now(indianTime).timetuple()
logging.handlers = []
logging.basicConfig(level=logging.DEBUG, handlers=[log_handler])

with open('src/config') as f:
    lines = f.readlines()
config1 = json.loads(lines[0])
config2 = json.loads(lines[1])
config3 = json.loads(lines[2])
config4 = json.loads(lines[3])

#<===cron jobs===>#
from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler()

# Database backup function
import subprocess, getpass
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
def backup_db():
    try:
        backupFileName = datetime.datetime.today().strftime('%m_%d') + 'sqlBackup.sql'
        os.system('mysqldump -u '+username+ ' ' +'-p'+password+' '+ db_name +' > '+ backupFileName)

        credentials = service_account.Credentials.from_service_account_file('src/serviceAccountKey.json', scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=credentials)
        media = MediaFileUpload(backupFileName, mimetype='application/sql')
        file_metadata = {
            'name': backupFileName,
            'parents':['1dyexWdsl05yKVMKpPNeft5nC-qwnrDiX']
        }
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        os.remove(backupFileName)
        app.logger.debug(inspect.currentframe().f_code.co_name+ ' backup db successful.')
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' failed')


def scheduledJobDay1():
    #TODO reset admin/instructor tokens
    app.logger.debug(inspect.currentframe().f_code.co_name+ ' started...')
    backup_db()

    ctx = app.app_context()
    ctx.push()
    today, boardGrade = datetime.datetime.now(indianTime), {}
    yesterday, endDate = today - datetime.timedelta(1), today

    testsData, errorCode = getAllTests({'startEnd':[yesterday, endDate]})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+ ' error:'+testsData)
        return jsonify({'error':testsData}), errorCode

    for test in testsData:
        subjectData, errorCode = getSubject({'id':test['subjectId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+subjectData)
            return jsonify({'error':subjectData}), errorCode

        boardGrade[subjectData.board] = subjectData.grade

    usersData, errorCode = getAllUsers({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+usersData)
        return jsonify({'error':usersData}), errorCode

    for user in usersData:
        initsUpdateData = {}
        subscriptionActivitiesData, errorCode = getAllSubscriptionActivity({'userId':user['id']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+subscriptionActivitiesData)
            return jsonify({'error':subscriptionActivitiesData}), errorCode

        for subsAct in subscriptionActivitiesData:
            if today.date() - subsAct.datetime.date() == datetime.timedelta(3):
                userTestData, errorCode = getUserTest({})
                if errorCode == 500:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
                    return jsonify({'error': userTestData}), errorCode
                elif errorCode == 404:
                    # notification for student not taking any test after 3 days of registration
                    fnotification("Fantastic Tests are waiting for you", "", None, user['id'],\
                    {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'fhome', 'userId':str(user['id'])})

            if today.date() > subsAct.expiryDate and subsAct.testsRemaining != 0:
                error, errorCode = updateUser({'id':user['id']}, {'addTests':-1*subsAct.testsRemaining})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+error)
                    return jsonify({'error':error}), errorCode

                error, errorCode = updateSubscriptionActivity({'id':subsAct.id},{'testsRemaining':0})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+str(subsAct.id))
                    return jsonify({'error':str(subsAct.id)}), errorCode

            if subsAct.subsId == 1:
                if subsAct.expiryDate - today.date()  > datetime.timedelta(1):
                    initsUpdateData['subscription'] = 'Your FREE TRIAL duration has ended, subscribe to continue'
                elif subsAct.testsRemaining == 0:
                    initsUpdateData['subscription'] = 'Your FREE TRIAL tests have ended, subscribe to continue'

        #new test notifications
        if user['board'] in boardGrade.keys() and boardGrade['board'] == user['grade']:
            initsUpdateData['newTests'] = 'New tests are added. check it out'

        if initsUpdateData:
            error, errorCode = updateInits({'userId':user['id']}, initsUpdateData)
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+error)
                return jsonify({'error':error}), errorCode

        loginActivity = LoginActivity.query.filter_by(userId=user['id'], dateTime=yesterday).first()
        userBadge = db.session.query(UserBadges).filter(UserBadges.userId==user['id']).filter(UserBadges.badgeId == Badges.id).filter(Badges.type == 'activity').first()
        if loginActivity:
            userBadge.badgeId = 1
        else:
            userBadge.badgeId = 15 if userBadge.badgeId == 15 else userBadge.badgeId + 1
        db.session.commit()

        # notification paused test
        userTestData, errorCode = getUserTest({'userId':user['id'], 'paused':True})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+userTestData)
            return jsonify({'error':userTestData}), errorCode
        elif errorCode == 200:
            testData, errorCode = getTest({'id':userTestData.testId})
            if errorCode == 404:
                subjectId = userTestData.customSubjectId
            elif errorCode == 200:
                 subjectId = testData.subjectId
            else:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
                return jsonify({'error':testData + ' at recommended tests.'}), errorCode
            fnotification("Hey Paused test is waiting for you. ", "", "", user['id'],\
            {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'fhome', 'userId':str(user['id']), 'subjectId':str(subjectId)})

    # notification admin generated
    for n in Notifications.query.all():
        if n.triggeringTime.date() == today.date():
            usersData, errorCode = getAllUsers({'grades':[g for g in n.targetUserGroup.split('-')[2].split(',')], \
            'boards':[b for b in n.targetUserGroup.split('-')[1].split(',')], 'school':[s for s in n.targetUserGroup.split('-')[0].split(',')]})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+usersData)
                return jsonify({'error':usersData}), errorCode

            for user in usersData:
                if n.redirect == 'fhome' or n.redirect == 'fsubscription' or n.redirect == 'fprofile' or n.redirect == 'freports' or n.redirect == 'fanalytics': 
                    fnotification(n.title, n.message, n.imagePath, user['id'],\
                    {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':n.redirect, 'userId':str(user['id'])})
                elif n.redirect == 'ftestHome':
                    subjectData, errorCode = getSubject({'grade':user['grade'], 'board':user['board']})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+subjectData)
                        return jsonify({'error':subjectData}), errorCode

                    fnotification(n.title, n.message, n.imagePath, user['id'],\
                    {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':n.redirect, 'userId':str(user['id']), 'subjectId':str(subjectData.id)})

    ctx.pop()
    app.logger.debug(inspect.currentframe().f_code.co_name+ ' successfully ended...')

#weekly reports
def scheduledJobDay2():
    app.logger.debug(inspect.currentframe().f_code.co_name)
    ctx = app.app_context()
    ctx.push()

    usersData, errorCode = getAllUsers({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+usersData)
        return jsonify({'error':usersData}), errorCode

    for i, user in enumerate(usersData):
        error, errorCode = updateInits({'userId':user['id']}, {'newWeeklyReports':'New weekly report generated'})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(user['id'])+'. error:'+error)
            return jsonify({'error':error}), errorCode

    ctx.pop()

sched.add_job(scheduledJobDay1, 'interval', hours=24)
sched.add_job(scheduledJobDay2, 'interval', days=6)
sched.start()


@app.route('/')
def i():
    return render_template('index.html')

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    school = request.form.get('sname')
    tuition = request.form.get('tname')
    parent = request.form.get('name')

    error = ''
    if school or tuition:
        org = school or tuition
        name = request.form.get('name')
        mobile = request.form.get('number')
        email = request.form.get('email')
        psw = request.form.get('psw')

        app.logger.debug(inspect.currentframe().f_code.co_name+ ' -school:'+school + ' -name:'+name+ ' -mobile:'+mobile\
        + ' -email:'+email+ ' -psw:'+psw)

        schoolData, errorCode = getSchool({'name':org})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+schoolData)
            return render_template('signup.html', error='school not found, contact support. ')

        instructor = Instructor(name, email, mobile, psw, schoolData.id, False, None, None, datetime.datetime.now(indianTime))
        instructorId, errorCode = insertInstructor(instructor)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+ ' -email:'+email +'. error:'+str(instructorId))
            return jsonify({'error':str(instructorId)}), errorCode

        error = 'successfully added user. contact support for further approval'
    elif parent:
        mobile = request.form.get('number')
        email = request.form.get('email')
        psw = request.form.get('psw')

        app.logger.debug(inspect.currentframe().f_code.co_name+ ' -parent:'+parent+' -mobile:'+mobile\
        + ' -email:'+email+ ' -psw:'+psw)

        userData, errorCode = getUser({'parentMobile':mobile})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+userData)
            return render_template('signup.html', error=' Parent mobile not found, contact support. ')

        instructor = Instructor(parent, email, mobile, psw, None, True, None, None, datetime.datetime.now(indianTime))
        db.session.add(instructor)
        db.session.commit()
        error = 'successfully added user. contact support for further approval'
    return render_template('signup.html', error=error)


@app.route('/deleteAssignedUser', methods=['GET', 'POST'])
def deleteAssignedUser():
    data = request.get_json()
    id = data.get('id')
    email = data.get('email')
    name = data.get('name')
    assign = data.get('assign')

    error, errorCode = deleteInstructorAssignment({'id':id})
    if errorCode != 204:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ email +'. error:'+error)
        error = 'fail'
    else:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error+ ', instructor:'+name+'assignment:'+assign+' successfully deleted by email:'+ email)
        error = 'success'
    
    return jsonify({'error':error})



@app.route('/addAndAssignUser', methods=['GET', 'POST'])
def addAndAssignUser():
    data = request.get_json()
    email = data.get('creatorEmail')
    name = data.get('name')
    instructorEmail = data.get('email')
    password = data.get('password')
    instructorId = data.get('instructor')
    board = data.get('board')
    grade = data.get('grade')
    section = data.get('section')
    subject = data.get('subject')
    app.logger.debug(inspect.currentframe().f_code.co_name+ ' -initiatedBy:'+email+ ' -name:'+name+ ' -instructorEmail:'+instructorEmail+ ' -password:'+password+ \
    ' -instructorId:'+instructorId + ' -board:'+board+ ' -grade:'+grade+ ' -section:'+section+ ' -subject:'+subject)

    instructorData, errorCode = getInstructor({'email':email})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+'. error:'+instructorData)
        return jsonify({'error':instructorData})


    if board and grade and section and subject:
        if name and instructorEmail and password: 
            instructor = Instructor(name, instructorEmail, None, password, instructorData.school, False, None, instructorData.id, datetime.datetime.now(indianTime))
            instructorId, errorCode = insertInstructor(instructor)
            if errorCode != 201:
                app.logger.debug(inspect.currentframe().f_code.co_name+ '. error:'+str(instructorId))
                return jsonify({'error':instructorId})

        instructorAssigment = InstructorAssignment(board, grade, section, subject, instructorId, datetime.datetime.now(indianTime))
        instructorAssigmentId, errorCode = insertInstructorAssignment(instructorAssigment)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+ ' -email:'+email +'. error:'+str(instructorAssigmentId))
            return jsonify({'error':instructorAssigmentId})

    return jsonify({'error':'success'})


@app.route('/addUser', methods=['GET', 'POST'])
def addUser():
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    startDate, endDate = getDates('This Week')
    result = {
        'isAdmin':False,
        'school':None,
        'isOrgHead':True,
        'error':None,
        'instructorId':None,
        'tuition':False,
        'schoolSel': [],
        'boardSel': [],
        'gradeSel': [],
        'sectionSel': [],
        'subjectSel': [],
        'boardGradeSectionSubjectPairSel': [],
        'chapterSel': [],
        'conceptSel': [],
        'dashboardUserTests':False,
        'dashboardAddUser':True,
        'dashboardStudent':False,
        'dashboard':False,
        'startDateSel': startDate.strftime('%m/%d/%Y'),
        'endDateSel': endDate.strftime('%m/%d/%Y')
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('add-user.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school

    result['name'] = instructorData.name
    result['email'] = instructorData.email

    response = requests.post('http://localhost:5000/getDashboardUserTests', data=json.dumps({
        'result':result,
        }),headers = {'Content-Type': 'application/json'})
    result = response.json()

    return render_template('add-user.html', result=result, s=session, error='')

@app.route('/signin.html', methods=['GET', 'POST'])
def signin():
    app.logger.debug(inspect.currentframe().f_code.co_name)

    error = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        adminData, errorCode = getAdmin({'email':email})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+adminData)
            return render_template('signup.html', error=adminData)

        if adminData is None:
            error = 'account not found'
        elif errorCode != 404 and adminData.status == False:
            error = 'your status is not active'
        elif errorCode != 404 and adminData.password == password:
            session['adminName'] = adminData.name
            session['adminId'] = adminData.id
            session['adminAvailable'] = True
            session['adminRole'] = adminData.roles
            session['isAdmin'] = True
            return redirect(url_for('dashboard'))
            # return redirect(url_for('userInfo', error='success', userId=0))

        instructorData, errorCode = getInstructor({'email':email})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+instructorData)
            return render_template('signup.html', error=instructorData)

        if instructorData is None:
            error = ' account not found.'
        elif errorCode != 404 and instructorData.status == False:
            error = 'your status is not active, contact support.'
        elif errorCode != 404 and instructorData.password == password:
            session['instructorId'] = instructorData.id
            session['isAdmin'] = False
            if not instructorData.school:
                userData, errorCode = getUser({'parentMobile':instructorData.mobile})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+userData)
                    return render_template('signup.html', error=' Parent mobile not found, contact support. ')

                date = datetime.datetime.today().date().strftime('%m-%d-%Y')
                return redirect(url_for('studentResults', userId=userData.id, startDate=date, endDate=date))
            return redirect(url_for('dashboard'))
    return render_template('signin.html', error=error, s=session)


import smtplib, random, string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@app.route('/forgot.html', methods=['GET', 'POST'])
def forgotPassword():
    email = request.form.get('email')

    if email:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email))
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = 'loops.future2022@gmail.com'
        sender_password = 'rdwh hleh dfeo bvko'
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = 'Forgot password, link valid for 10 mins'
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        msg.attach(MIMEText('https://raoacademy.com/reset.html/'+token, 'plain'))

        error, errorCode = updateInstructor({'email':email}, {'token':token})
        if errorCode != 200:
            error, errorCode = updateAdmin({'email':email}, {'token':token})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(email)+'. error:'+error)
                return jsonify({'error':error}), errorCode

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()
            return redirect(url_for('signin'))
        except Exception as e:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ email +' -error:'+str(e))
    return render_template('forgot.html')


@app.route('/reset.html/<token>', methods=['GET', 'POST'])
def reset(token):
    password = request.form.get('password')
    confirmpassword = request.form.get('confirmpassword')
    if password and password == confirmpassword:
        error, errorCode = updateInstructor({'token':token}, {'password':password})
        if errorCode != 200:
            error, errorCode = updateAdmin({'token':token}, {'password':password})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -token:'+ str(token)+'. error:'+error)
                return jsonify({'error':error}), errorCode

        return redirect(url_for('signin'))
    return render_template('reset.html')


@app.route('/userInfo/<error>/<userId>', methods=['GET', 'POST'])
def userInfo(error, userId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error+' -userId:'+str(userId)\
    +' -adminName:'+str(session['adminName']))

    megaSearch = MegaSearchForm()
    userInfo, t = [], 0
    userCols = ['user Id','status', 'firstname', 'lastname', 'gender', 'dob', 'email', 'mobile',\
    'test remaining', 'coins', 'added at', 'school', 'grade', 'action', 'action', 'action']
    megaSearch.grade.choices = [('None', 'None')] + [(g.id, g.grade) for g in Grade.query.order_by(-Grade.id).all()]
    megaSearch.board.choices = [('None', 'None')] + [(b.id, b.name) for b in Board.query.all()]
    megaSearch.school.choices = [('None', 'None')] + [(s.id, s.name) for s in School.query.all()]

    if error == 'update' and request.method != 'POST':
        user = User.query.filter_by(id=userId).first()
        megaSearch.grade.default = int(user.grade)
        megaSearch.board.default = int(user.board)
        megaSearch.school.default = int(user.school)
        megaSearch.status.default = 1 if user.status else 0
        megaSearch.process()
        megaSearch.firstname.data = user.firstname
        megaSearch.lastname.data = user.lastname
        megaSearch.gender.data = user.gender
        megaSearch.dob.data = user.dob
        megaSearch.email.data = user.email
        megaSearch.mobile.data = user.mobile
        megaSearch.parentName.data = user.parentName
        megaSearch.parentMobile.data = user.parentMobile
        megaSearch.city.data = user.city
    elif error  == 'delete' and request.method != 'POST':
        user = db.session.query(User).filter(User.id==userId).first()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('userInfo', error='sucess', userId=0))
    elif error == 'status' and request.method != 'POST':
        user = db.session.query(User).filter(User.id==userId).first()
        user.status = (user.status + 1)%2
        db.session.commit()
        return redirect(url_for('userInfo', error='success', userId=0))
    elif error == 'add100Tests' and request.method != 'POST':
        user = db.session.query(User).filter(User.id == userId).first()
        user.testsRemaining += 100
        db.session.commit()
        subscriptionActivity = SubscriptionActivity(userId, 1, 0, None, datetime.datetime.now(indianTime) + datetime.timedelta(days=30), \
        100, True, 'admin added tests', None, None, None, None, datetime.datetime.now(indianTime))
        subsActivityId, errorCode = insertSubscriptionActivity(subscriptionActivity)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+str(subsActivityId))
            return redirect(url_for('userInfo', error='success', userId=0))

    userInfo = db.session.query(User.status, User.firstname, User.lastname, User.gender, User.dob,\
    User.email, User.mobile, User.testsRemaining, User.coins, User.datetime,\
    School.name, Grade.grade, User.id).filter(User.board == Board.id).\
    filter(User.school == School.id).filter(User.grade == Grade.id)
    if request.method == 'POST':
        if megaSearch.search.data:
            if megaSearch.firstname.data:
                userInfo = userInfo.filter(User.firstname == megaSearch.firstname.data)
            if megaSearch.lastname.data:
                userInfo = userInfo.filter(User.lastname == megaSearch.lastname.data)
            if megaSearch.gender.data != 'None':
                userInfo = userInfo.filter(User.gender == megaSearch.gender.data)
            if megaSearch.dob.data:
                userInfo = userInfo.filter(User.dob == megaSearch.dob.data)
            if megaSearch.email.data:
                userInfo = userInfo.filter(User.email == megaSearch.email.data)
            if megaSearch.mobile.data:
                userInfo = userInfo.filter(User.mobile == megaSearch.mobile.data)
            if megaSearch.grade.data != 'None':
                userInfo = userInfo.filter(User.grade == megaSearch.grade.data)
            if megaSearch.board.data != 'None':
                userInfo = userInfo.filter(User.board == megaSearch.board.data)
            if megaSearch.school.data != 'None':
                userInfo = userInfo.filter(User.school == megaSearch.school.data)
            if megaSearch.status.data == 0:
                userInfo = userInfo.filter(User.status == False)
            if megaSearch.parentName.data:
                userInfo = userInfo.filter(User.parentName == megaSearch.parentName.data)
            if megaSearch.parentMobile.data:
                userInfo = userInfo.filter(User.parentMobile == megaSearch.parentMobile.data)
            if megaSearch.city.data:
                userInfo = userInfo.filter(User.city == megaSearch.city.data)

        if megaSearch.addStudent.data:
            user = db.session.query(User).filter(User.id == userId).first()
            if user:
                user.firstname = megaSearch.firstname.data
                user.lastname = megaSearch.lastname.data
                user.dob = megaSearch.dob.data
                user.email = megaSearch.email.data
                user.mobile = megaSearch.mobile.data
                user.parentName = megaSearch.parentName.data
                user.parentMobile = megaSearch.parentMobile.data
                user.city = megaSearch.city.data
                user.gender = megaSearch.gender.data
                user.grade = megaSearch.grade.data
                user.board = megaSearch.board.data
                user.school = megaSearch.school.data
                db.session.commit()
            elif megaSearch.firstname.data and megaSearch.lastname.data and megaSearch.gender.data != 'None' and\
            megaSearch.dob.data and megaSearch.mobile.data and megaSearch.grade.data != 'None' and \
            megaSearch.school.data != 'None' and megaSearch.board.data != 'None' and megaSearch.parentName.data\
            and megaSearch.parentMobile.data and megaSearch.city.data:
                userId = addStudent(megaSearch.firstname.data, megaSearch.lastname.data, megaSearch.gender.data,\
                megaSearch.dob.data, megaSearch.board.data, megaSearch.grade.data, megaSearch.school.data,\
                megaSearch.mobile.data, None, megaSearch.parentName.data, megaSearch.parentMobile.data, \
                megaSearch.city.data, None)
                if type(userId) != type(1):
                    error = userId

    userInfo = userInfo.all()
    return render_template('userInfo.html', ui=userInfo, uc=userCols, error=error, t=len(userInfo), s=session, mSForm=megaSearch)

@app.route('/schoolInfo/<error>/<schoolId>', methods=['GET', 'POST'])
def schoolInfo(error, schoolId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error+' -adminName:'+str(session['adminName']))

    schoolForm = SchoolForm()
    # schoolForm.board.choices = [(b.id, b.name) for b in Board.query.all()]

    schoolCols = ['name', 'board', 'address', 'city', 'datetime', 'status', 'action']
    # schoolInfo = db.session.query(School.id, School.name, Board.name, School.address, School.city, School.datetime, School.status).\
    # filter(School.board == Board.id).all()

    # if 'update' in error and request.method != 'POST':
    #     school = db.session.query(School).filter(School.id==schoolId).first()
    #     schoolForm.name.data = school.name
    #     schoolForm.address.data = school.address
    #     schoolForm.board.data = str(school.board)
    #     schoolForm.city.data = school.city
    #     return render_template('schoolInfo.html', si=schoolInfo, sc=schoolCols, error=error, \
    #     t=0, schoolForm=schoolForm, s=session)
    # if 'status' in error:
    #     school = db.session.query(School).filter(School.id==schoolId).first()
    #     school.status = (school.status + 1)%2
    #     db.session.commit()
    #     return redirect(url_for('schoolInfo', error='success', schoolId=0))

    # if request.method == 'POST':
    #     school = db.session.query(School).filter(School.id==schoolId).first()
    #     if school:
    #         #only Update
    #         school.name = schoolForm.name.data
    #         school.board = schoolForm.board.data
    #         school.address = schoolForm.address.data
    #         school.city = schoolForm.city.data
    #     elif schoolForm.name.data:
    #         #add
    #         db.session.add(School(schoolForm.name.data, schoolForm.board.data, schoolForm.address.data,\
    #         schoolForm.city.data, True, datetime.datetime.now(indianTime)))
    #     db.session.commit()
    #     return redirect(url_for('schoolInfo', error='success', schoolId=0))

    # t = len(schoolInfo)
    # return render_template('schoolInfo.html', si=schoolInfo, sc=schoolCols, error=error, \
    # t=t, schoolForm=schoolForm, s=session)
    return render_template('schoolInfo.html', si=[], sc=[], error='error', t=0, schoolForm=None, s=session)

@app.route('/subjectChapter/<error>/<subjectId>/<chapterId>', methods=['GET', 'POST'])
def subjectChapter(error, subjectId, chapterId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error\
    +' -subjectId:'+str(subjectId)+' -chapterId:'+str(chapterId)+' -adminName:'+str(session['adminName']))

    if error == 'delete':
        if chapterId != '0':
            chapterDel = db.session.query(Chapter).filter(Chapter.id==chapterId).first()
            db.session.delete(chapterDel)
            db.session.commit()
            return redirect(url_for('subjectChapter', error='success', subjectId=subjectId, chapterId='0'))
        subjectDel = db.session.query(Subject).filter(Subject.id==subjectId).first()
        db.session.delete(subjectDel)
        db.session.commit()
        return redirect(url_for('subjectChapter', error='success', subjectId='0', chapterId='0'))

    sC = SubjectChapter()
    if subjectId == '0':
        sC.board.choices = [(b.id, b.name) for b in Board.query.all()]
        sC.grade.choices = [(g.id, g.grade) for g in Grade.query.all()]
        subjectCols = ['subjectId', 'name', 'code', 'sortorder', 'action']
        subjectInfo = db.session.query(Subject.id, Subject.name, Subject.code, Subject.sortOrder)
        if request.method == 'POST':
            if sC.search.data:
                subjectInfo = subjectInfo.filter(Subject.grade == sC.grade.data).filter(Subject.board == sC.board.data)
            if subjectId == '0' and sC.add.data:
                subjectAcademics = False
                if sC.subjectAcademics.data == '1':
                    subjectAcademics = True
                try:
                    subjectSortOrder = db.session.query(Subject.sortOrder).filter(Subject.board==sC.board.data).filter(Subject.grade==sC.grade.data).\
                    order_by(-Subject.sortOrder).all()
                    subjectSortOrder = subjectSortOrder[0][0]+1
                except:
                    subjectSortOrder = 1
                subject = Subject(sC.subjectName.data, sC.subjectCode.data, sC.grade.data, sC.board.data, \
                subjectAcademics, subjectSortOrder)
                db.session.add(subject)
                db.session.flush()
                subjectId = subject.id
                db.session.commit()
                path = "src/static/img/"
                if sC.subjectName.data != 'General':
                    db.session.add(TestCategory('Concept Based', 'this', path+"Dynamictests.png", 1, subjectId, datetime.datetime.now(indianTime)))
                    db.session.add(TestCategory('Custom Tests', 'this', path+"Customtests.png", 2, subjectId, datetime.datetime.now(indianTime)))
                    db.session.add(TestCategory('PYQs', 'this', path+"PYQs.png", 3, subjectId, datetime.datetime.now(indianTime)))
                    db.session.commit()
                return redirect(url_for('subjectChapter', error='success', subjectId='0', chapterId='0'))
        subjectInfo = subjectInfo.all()
    else:
        chapterInfo, conceptInfo = None, None
        chapterCols = ['chapterId', 'number', 'name', 'imgPath', 'caption', 'description', 'tags', 'sortOrder', 'action', 'action']
        chapterInfo = db.session.query(Chapter.id, Chapter.number, Chapter.name, \
        Chapter.imagePath, Chapter.caption, Chapter.description, Chapter.tags, Chapter.sortOrder).\
        filter(Chapter.subjectId == subjectId).order_by(Chapter.number).all()
        if request.method == 'POST':
            if sC.add.data:
                try:
                    chapterSortOrder = db.session.query(Chapter.sortOrder).filter(Chapter.subjectId==subjectId).\
                    order_by(-Chapter.sortOrder).all()
                    chapterSortOrder = chapterSortOrder[0][0]+1
                except:
                    chapterSortOrder = 1
                db.session.add(Chapter(sC.chapterNumber.data, sC.chapterName.data, 'src/static/img/'+sC.chapterImagePath.data, \
                subjectId, sC.chapterCaption.data, sC.chapterDescription.data, sC.chapterTags.data, chapterSortOrder,\
                datetime.datetime.now(indianTime)))
                db.session.commit()
                return redirect(url_for('subjectChapter', error='success', subjectId=subjectId, chapterId='0'))
            if sC.update.data:
                chapterUp = db.session.query(Chapter).filter(Chapter.id==chapterId).first()
                chapterUp.number = sC.chapterNumber.data
                chapterUp.name = sC.chapterName.data
                chapterUp.imagePath = sC.chapterImagePath.data
                chapterUp.caption = sC.chapterCaption.data
                chapterUp.description = sC.chapterDescription.data
                chapterUp.tags = sC.chapterTags.data
                db.session.commit()
                return redirect(url_for('subjectChapter', error='success', subjectId=subjectId, chapterId='0'))
        if error == 'update':
            if chapterId != '0':
                chapterUp = db.session.query(Chapter).filter(Chapter.id==chapterId).first()
                sC.chapterNumber.data = chapterUp.number
                sC.chapterName.data = chapterUp.name
                sC.chapterImagePath.data = chapterUp.imagePath
                sC.chapterCaption.data = chapterUp.caption
                sC.chapterDescription.data = chapterUp.description
                sC.chapterTags.data = chapterUp.tags
                error = 'success'
        t = len(chapterInfo)
        return render_template('subjectChapter.html', subjectId=subjectId, chi=chapterInfo, chc=chapterCols, error=error, t=t, s=session, sC=sC)
    t = len(subjectInfo)
    return render_template('subjectChapter.html', si=subjectInfo, sc=subjectCols, error=error, t=t, s=session, sC=sC)

@app.route('/concepts/<error>/<board>/<grade>/<subjectId>/<chapterId>/<conceptId>/', methods=['GET', 'POST'])
def concepts(error, board, grade, subjectId, chapterId, conceptId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    conceptCols = ['conceptId', 'name', 'status', 'modifiedBy', 'action']
    conceptInfo = db.session.query(Concept.id, Concept.name, Concept.status, Admin.name).\
    filter(Admin.id==Concept.addedBy).all()

    concepts = Concepts()
    concepts.board.choices = [(b.id, b.name) for b in Board.query.all()]
    concepts.grade.choices = [(g.id, g.grade) for g in Grade.query.all()]
    concepts.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
    concepts.chapter.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if board != '0' and grade != '0':
        concepts.board.data = board
        concepts.grade.data = grade
        concepts.subject.choices = [(s.id, s.name) for s in Subject.query.filter_by(board=board, grade=grade).all()]
    if subjectId != '0':
        concepts.subject.data = subjectId
        concepts.chapter.choices = [(c.id, c.name) for c in Chapter.query.filter_by(subjectId=subjectId).all()]
    if chapterId != '0':
        concepts.chapter.data = chapterId
        conceptInfo = db.session.query(Concept.id, Concept.name, Concept.status, Admin.name).\
        filter(Admin.id==Concept.addedBy).filter(Concept.chapterId==chapterId).all()

    t = len(conceptInfo)

    if 'update' in error and request.method != 'POST':
        concepts.name.data = Concept.query.filter_by(id=conceptId).first().name
        return render_template('concepts.html', error='success', cc=conceptCols, ci=conceptInfo, si=subjectId, chi=chapterId, s=session, t=t, concepts=concepts, board=board, grade=grade)
    elif 'status' in error:
        concept = db.session.query(Concept).filter(Concept.id==conceptId).first()
        concept.status = (concept.status + 1)%2
        db.session.commit()
        return redirect(url_for('concepts', error='success', board=board, grade=grade, subjectId=subjectId, chapterId=chapterId, conceptId=0))

    if request.method == 'POST':
        con = db.session.query(Concept).filter(Concept.id==conceptId).first()
        con.name = concepts.name.data
        db.session.commit()
        return redirect(url_for('concepts', error='success', board=board, grade=grade, subjectId=subjectId, chapterId=chapterId, conceptId=0))

    return render_template('concepts.html', error=error, cc=conceptCols, ci=conceptInfo, si=subjectId, chi=chapterId, s=session, t=t, concepts=concepts, board=board, grade=grade)

@app.route('/uploadExcels/<error>', methods=['GET', 'POST'])
def uploadExcels(error):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))
    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error+' -adminName:'+str(session['adminName']))
    return render_template('uploadExcels.html', error=error, s=session)

@app.route('/uploadFile', methods = ['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files['filename']
        if f.filename:
            f.save(f.filename)
            return redirect(url_for('reviewQuestion', filename=f.filename))
    return redirect(url_for('uploadExcels', error='failed'))

@app.route('/generateExcel', methods = ['GET', 'POST'])
def generateExcel():
    if request.method == 'POST':
        f = request.files['filename']
        if f.filename:
            f.save(f.filename)
            return redirect(url_for('setQuestions', filename=f.filename))
    return redirect(url_for('uploadExcels', error='failed'))

@app.route('/uploadTests', methods = ['GET', 'POST'])
def uploadTests():
    if request.method == 'POST':
        f = request.files['filename']
        if f.filename:
            f.save(f.filename)
            return redirect(url_for('addTests', filename=f.filename))
    return redirect(url_for('uploadExcels', error='failed'))

@app.route('/uploadChapters', methods = ['GET', 'POST'])
def uploadChapters():
    if request.method == 'POST':
        f = request.files['filename']
        if f.filename:
            f.save(f.filename)
            return redirect(url_for('addChapters', filename=f.filename))
    return redirect(url_for('uploadExcels', error='failed'))

def getQuestionList(filename):
    base_path = filename
    sheet_index = 1
    # sheet = "sheet_name"
    # df = read_ods(base_path , sheet)
    reviewTableMcqMsqDadSeq, reviewTableFillTorF, reviewTableMatch  = [], [], []
    columns=["Question Number",	"QL 1,2,3",	"Question",	"Question Image", "Options",\
     "Option Image", "Answer", "Format", "Hints", "Hints Image", "Answer with explanation", \
     "Answer with explanation Image", "Tags","Question Category", "PYQ Years"]
    df = read_ods(base_path, 1, columns=columns)
    reviewTableMcqMsqDadSeq.append(["concept", "question", "question image", "opt1",  "img1",\
    "opt2", "img2", "opt3", "img3", "opt4", "img4", "ans", "tags", "hints", "hints image", "answer exp", \
    "ans exp image", "difficultyLevel", "maxSolvingTime", "category", "PYQ Years", "format"])
    reviewTableFillTorF.append(["concept", "question", "question image", "ans", "tags", "hints", "hints image",\
     "answer exp", "ans exp image", "difficultyLevel", "maxSolvingTime", "category", "PYQ Years", "format"])
    reviewTableMatch.append(["concept", "question", "opt1",  "img1", "opt2", "img2", "opt3", \
    "img3", "opt4", "img4", "ans1",  "img1", "ans2",  "img2", "ans3",  "img3",\
     "ans4",  "img4", "ans", "tags", "hints", "hints image", "answer exp", "ans exp image", "difficultyLevel", \
     "maxSolvingTime", "category", "PYQ Years", "format"])
    conceptName = None
    error = None
    questionFormatDict = {'mcq':1, 'msq':2,'ftb':3,'dad':4,'tof':5}#,'mtf':6,'seq':7}
    for row in range(df.shape[0]):
        try:
            if type(df["Question Number"][row]) == type("") :
                conceptName = [df["Question Number"][row], df["QL 1,2,3"][row], df["Question"][row], df["Question Image"][row], df["Options"][row]]
            if conceptName[0] and type(df["Question Number"][row]) == type(1.0) and type(df["Format"][row]) == type("1.0"):
                format = (df["Format"][row]).lower()
                ans = ""

                solvingTime = config4['time'][config2['difficultyLevel'][str(df["QL 1,2,3"][row]).split('.')[0]]]
                if format not in questionFormatDict:
                    error = {
                        'error': 'invalid format ',
                        'questionNumber':df["Question Number"][row]
                    }
                    break
                if format == "mcq" or format == "msq" or format == "dad" or format == "seq":
                    if type(df["Answer"][row]) == type(None):
                        error = 'No ans'
                    else:
                        ans = str(df["Answer"][row]).split('.')[0]
                        if type(df["Answer"][row+1]) != type(None):
                            ans += ','+str(df["Answer"][row+1]).split('.')[0]
                        if type(df["Answer"][row+2]) != type(None):
                            ans += ','+str(df["Answer"][row+2]).split('.')[0]
                        if type(df["Answer"][row+3]) != type(None):
                            ans += ','+str(df["Answer"][row+3]).split('.')[0]
                        ans.lower()
                    reviewTableMcqMsqDadSeq.append([conceptName, df["Question"][row], df["Question Image"][row],\
                    df["Options"][row], df["Option Image"][row], df["Options"][row+1], df["Option Image"][row+1],\
                    df["Options"][row+2], df["Option Image"][row+2], df["Options"][row+3], df["Option Image"][row+3],\
                    ans, df["Tags"][row], df["Hints"][row], df["Hints Image"][row], df["Answer with explanation"][row],\
                    df["Answer with explanation Image"][row], int(df["QL 1,2,3"][row]), solvingTime,\
                    df["Question Category"][row], df["PYQ Years"][row], format])
                elif format == "ftb" or format == "tof":
                    reviewTableFillTorF.append([conceptName, df["Question"][row], df["Question Image"][row],\
                    str(df["Answer"][row]).lower(), df["Tags"][row], df["Hints"][row], df["Hints Image"][row], df["Answer with explanation"][row],\
                    df["Answer with explanation Image"][row], int(df["QL 1,2,3"][row]), solvingTime,\
                    df["Question Category"][row], df["PYQ Years"][row], format])
                elif format == "mtf":
                    if type(df["Answer"][row+1]) == type(None):
                        error = 'No ans'
                    else:
                        ans = str(df["Answer"][row+1]).split('.')[0]
                        if type(df["Answer"][row+2]) != type(None):
                            ans += ','+str(df["Answer"][row+2]).split('.')[0]
                        if type(df["Answer"][row+3]) != type(None):
                            ans += ','+str(df["Answer"][row+3]).split('.')[0]
                        if type(df["Answer"][row+4]) != type(None):
                            ans += ','+str(df["Answer"][row+4]).split('.')[0]
                        ans.lower()
                    # print(df["QL 1,2,3"][row], "_+++_",df["Solving Time"][row])
                    reviewTableMatch.append([conceptName, df["Question"][row], df["Question"][row+1], \
                    df["Question Image"][row+1], df["Question"][row+2], df["Question Image"][row+2],\
                    df["Question"][row+3], df["Question Image"][row+3], df["Question"][row+4], df["Question Image"][row+4],\
                    df["Options"][row+1], df["Option Image"][row+1], df["Options"][row+2], df["Option Image"][row+2],\
                    df["Options"][row+3], df["Option Image"][row+3], df["Options"][row+4], df["Option Image"][row+4],\
                    ans, df["Tags"][row], df["Hints"][row], df["Hints Image"][row], df["Answer with explanation"][row],\
                    df["Answer with explanation Image"][row], int(df["QL 1,2,3"][row]), solvingTime,\
                    df["Question Category"][row], df["PYQ Years"][row], format])
                    # print([conceptName, df["Question"][row], df["Question"][row+1], \
                    # df["Question Image"][row+1], df["Question"][row+2], df["Question Image"][row+2],\
                    # df["Question"][row+3], df["Question Image"][row+3], df["Question"][row+4], df["Question Image"][row+4],\
                    # df["Options"][row+1], df["Option Image"][row+1], df["Options"][row+2], df["Option Image"][row+2],\
                    # df["Options"][row+3], df["Option Image"][row+3], df["Options"][row+4], df["Option Image"][row+4],\
                    # ans, df["Tags"][row], df["Hints"][row], df["Hints Image"][row], df["Answer with explanation"][row],\
                    # df["Answer with explanation Image"][row], int(df["QL 1,2,3"][row]), solvingTime,\
                    # df["Question Category"][row], df["PYQ Years"][row], format])
        except Exception as e:
            error = {
                'Actual Qno':df["Question Number"][row],
                'error':e
            }
            break
    return error, [reviewTableMcqMsqDadSeq, reviewTableFillTorF, reviewTableMatch]

@app.route('/setQuestions/<filename>', methods=['GET', 'POST'])
def setQuestions(filename):
    columns=["Format","Question", "How it comes"]
    df = read_ods(filename, 1, columns=columns)
    os.remove(filename)
    format = None
    ql = [['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']]
    ansDict = {'a':1, 'b':2, 'c':3, 'd':4, 'A':1, 'B':2, 'C':3, 'D':4}
    iter = 1
    for row in range(df.shape[0]):
        try:
            if df["Format"][row] == '-':
                break
            if df['Format'][row]:
                format = df['Format'][row]
            if df["Question"][row]:
                # print(df["How it comes"][row])
                optionsA, optionsB, optionsC, optionsD = 'a)', 'b)', 'c)', 'd)'
                if 'A)' in df["How it comes"][row] and 'B)' in df["How it comes"][row]:
                    optionsA, optionsB, optionsC, optionsD = 'A)', 'B)', 'C)', 'D)'
                if 'a.' in df["How it comes"][row] and 'b.' in df["How it comes"][row]:
                    optionsA, optionsB, optionsC, optionsD = 'a.', 'b.', 'c.', 'd.'
                if 'A.' in df["How it comes"][row] and 'B.' in df["How it comes"][row]:
                    optionsA, optionsB, optionsC, optionsD = 'A.', 'B.', 'C.', 'D.'

                if format == 'MCQ':
                    question, optA = df["How it comes"][row].split(optionsA, 1)
                    optA, optB = optA.split(optionsB, 1)
                    optB, optC = optB.split(optionsC, 1)
                    optC, optD = optC.split(optionsD, 1)
                    if "Explanation" in df["How it comes"][row]:
                        optD, ans = optD.split('Answer:')
                        ans, ansExplanation = ans.split(' Explanation:')
                        ans = ans.replace('(','').replace(' ','').replace('.','')
                        ans = ansDict[ans[0]]
                    elif "Explanation" in df["How it comes"][row+1]:
                        ans, ansExplanation = df["How it comes"][row+1].split(' Explanation:')
                        ans = ans.replace('(','').replace(' ','').replace('.','')
                        ans = ansDict[ans[7]]
                    else:
                        ans = df["How it comes"][row+1].replace('(','').replace(' ','').replace('.','')
                        ans = ansDict[(ans[7]).lower()]
                        ansExplanation = df["How it comes"][row+2][13:]

                    ql.append([iter, '', question, '', optA, '', ans, 'MCQ', '', '', ansExplanation, '', '', '', ''])
                    ql.append(['', '', '', '', optB, '', '', '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optC, '', '', '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optD, '', '', '', '', '', '', '', '', '', ''])

                elif format == 'Fill':
                    if "Explanation" in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ans, ansExplanation = ans.split(' Explanation:')
                    elif 'Answer' in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ansExplanation = df["How it comes"][row+1][13:]
                    else:
                        question = df["How it comes"][row]
                        ans, ansExplanation = df["How it comes"][row+1].split(' Explanation:')
                        ans = ans[7:]

                    ql.append([iter, '', question, '', '', '', ans, 'FTB', '', '', ansExplanation, '', '', '', ''])

                elif format == 'Sequence':
                    if "Explanation" in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        question, optA = question.split(optionsA, 1)
                        optA, optB = optA.split(optionsB, 1)
                        optB, optC = optB.split(optionsC, 1)
                        optC, optD = optC.split(optionsD, 1)
                        ans, ansExplanation = ans.split(' Explanation:')
                    elif 'Answer' in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        question, optA = question.split(':')
                        optA, optB = optA.split(',', 1)
                        optB, optC = optB.split(',', 1)
                        optC, optD = optC.split(',',1)
                        ansExplanation = df["How it comes"][row+1][13:]
                    elif optA in df["How it comes"][row]:
                        question, optA = df["How it comes"][row].split(optionsA, 1)
                        optA, optB = optA.split(optionsB, 1)
                        optB, optC = optB.split(optionsC, 1)
                        optC, optD = optC.split(optionsD, 1)
                        ans = df["How it comes"][row+1][7:]
                        ansExplanation = df["How it comes"][row+2][13:]
                    else:
                        question = df["How it comes"][row]
                        optA = df["How it comes"][row+1]
                        optB = df["How it comes"][row+2]
                        optC = df["How it comes"][row+3]
                        optD = df["How it comes"][row+4]
                        ans, ansExplanation = df["How it comes"][row+5].split(' Explanation:')
                        ans = ans[7:]

                    ans = ans.replace(')','').replace('and','').replace(' ', '').replace('(','').replace('.','').split(',')
                    answer = ['','','','']
                    for i, a in enumerate(ans):
                        answer[i] = ansDict[a.lower()]

                    ql.append([iter, '', question, '', optA, '', answer[0], 'SEQ', '', '', ansExplanation, '', '', '', ''])
                    ql.append(['', '', '', '', optB, '', answer[1], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optC, '', answer[2], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optD, '', answer[3], '', '', '', '', '', '', '', ''])

                elif format == 'True or False':
                    if "Explanation" in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ans, ansExplanation = ans.split(' Explanation:')
                    elif 'Answer' in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ansExplanation = df["How it comes"][row+1][13:]
                    elif 'Explanation' in df["How it comes"][row+1]:
                        question = df["How it comes"][row]
                        ans, ansExplanation = df["How it comes"][row+1].split(' Explanation:')
                        ans = ans[7:]
                    else:
                        question = df["How it comes"][row]
                        ans = df["How it comes"][row+1][7:]
                        ansExplanation = df["How it comes"][row+2][13:]

                    ans = 'True' if 't' in ans or 'T' in ans else 'False'

                    ql.append([iter, '', question, '', '', '', ans, 'TOF', '', '', ansExplanation, '', '', '', ''])

                elif format == 'MSQ':
                    if "Explanation" in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ans, ansExplanation = ans.split(' Explanation:')
                    elif 'Explanation' in df["How it comes"][row+1]:
                        question= df["How it comes"][row]
                        ans, ansExplanation = df["How it comes"][row+1].split(' Explanation:')
                        ans = ans[7:]
                    elif 'Explanation' in df["How it comes"][row+2]:
                        question = df["How it comes"][row]
                        ans = df["How it comes"][row+1][7:]
                        ansExplanation = df["How it comes"][row+2][13:]

                    question, optA = question.split(optionsA, 1)
                    optA, optB = optA.split(optionsB, 1)
                    optB, optC = optB.split(optionsC, 1)
                    optC, optD = optC.split(optionsD, 1)
                    ans = ans.replace(')','').replace('and','').replace(' ', '').replace('.','').replace('(','').split(',')
                    answer = ['', '', '', '']
                    for i, a in enumerate(ans):
                        answer[i] = ansDict[a.lower()]

                    ql.append([iter, '', question, '', optA, '', answer[0], 'MSQ', '', '', ansExplanation, '', '', '', ''])
                    ql.append(['', '', '', '', optB, '', answer[1], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optC, '', answer[2], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optD, '', answer[3], '', '', '', '', '', '', '', ''])

                elif format == 'DAD':
                    enterIf = True
                    if "Explanation" in df["How it comes"][row]:
                        question, ans = df["How it comes"][row].split('Answer:')
                        ans, ansExplanation = ans.split(' Explanation:')
                    elif 'Explanation' in df["How it comes"][row+1]:
                        question= df["How it comes"][row]
                        ans, ansExplanation = df["How it comes"][row+1].split(' Explanation:')
                        ans = ans[7:]
                    elif 'Explanation' in df["How it comes"][row+2]:
                        question = df["How it comes"][row]
                        ans = df["How it comes"][row+1][7:]
                        ansExplanation = df["How it comes"][row+2][13:]
                    elif df["How it comes"][row+2] and 'Options' in df["How it comes"][row+2]:
                        question = df["How it comes"][row] + df["How it comes"][row+1]
                        optA = df["How it comes"][row+3]
                        optB = df["How it comes"][row+4]
                        optC = df["How it comes"][row+5]
                        optD = df["How it comes"][row+6]
                        ans = df["How it comes"][row+7][7:]
                        ansExplanation = df["How it comes"][row+8][13:]
                        enterIf = False

                    if enterIf:
                        question, optA = question.split(optionsA, 1)
                        optA, optB = optA.split(optionsB, 1)
                        optB, optC = optB.split(optionsC, 1)
                        optC, optD = optC.split(optionsD, 1)

                    ans = ans.replace(')','').replace('and','').replace(' ', '').replace('.','').replace('(','').split(',')
                    answer = ['','','','']
                    for i, a in enumerate(ans):
                        answer[i] = ansDict[a.lower()]

                    ql.append([iter, '', question, '', optA, '', answer[0], 'DAD', '', '', ansExplanation, '', '', '', ''])
                    ql.append(['', '', '', '', optB, '', answer[1], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optC, '', answer[2], '', '', '', '', '', '', '', ''])
                    ql.append(['', '', '', '', optD, '', answer[3], '', '', '', '', '', '', '', ''])

                # elif format == "Match":
                #     question = df['How it comes'][row]
                #     optA, optB, optC, optD = df["How it comes"][row+2].replace('A.','-'), df["How it comes"][row+3].replace('B.','-')\
                #     , df["How it comes"][row+4].replace('C.','-'), df["How it comes"][row+5].replace('D.','-')
                #     remaining = df["How it comes"][row+9].split(' B. ')
                #     opt1, remaining = remaining[0][3], remaining[1]
                #     remaining = df["How it comes"][row+9].split(' C. ')
                #     opt2, remaining = remaining[0], remaining[1]
                #     remaining = df["How it comes"][row+9].split(' D. ')
                #     opt3, opt4 = remaining[0], remaining[1]
                #     ans = df["How it comes"][row+13][0].split('-')
                #     ansExplanation = df["How it comes"][row+15][12:]
                #     # print(question,'====', optA,'====', optB,'====', optC,'====', optD,'====', opt1,'====', opt2,'===='\
                #     # , opt3,'====', opt4,'====', ans,'====', ansExplanation)
                #     ql.append([iter, '', question, '', '', '', '', 'MTF', '', '', ansExplanation, '', '', '', ''])
                #     ql.append(['', '', optA, '', opt1, '', ans[0][-1], '', '', '', '', '', '', '', ''])
                #     ql.append(['', '', optB, '', opt2, '', ans[1][-1], '', '', '', '', '', '', '', ''])
                #     ql.append(['', '', optC, '', opt3, '', ans[2][-1], '', '', '', '', '', '', '', ''])
                #     ql.append(['', '', optD, '', opt4, '', ans[3][-1], '', '', '', '', '', '', '', ''])

                ql.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
                iter += 1
        except Exception as e:
            return redirect(url_for('uploadExcels', error='error '+str(e)+' at question '+ str(int(df["Question"][row]))))
    data = OrderedDict()
    data.update({"Sheet 1": [["Question Number",	"QL 1,2,3",	"Question",	"Question Image", "Options",\
     "Option Image", "Answer", "Format", "Hints", "Hints Image", "Answer with explanation", \
     "Answer with explanation Image", "Tags","Question Category", "PYQ Years"]]+ql})
    mh=["Question Number",	"QL 1,2,3",	"Question",	"Question Image", "Options",\
     "Option Image", "Answer", "Format", "Hints", "Hints Image", "Answer with explanation", \
     "Answer with explanation Image", "Tags","Question Category", "PYQ Years"]
    # return render_template("reviewQuestion.html", s=session, mh=mh, ml=ql)
    save_data("src/questionFile.ods", data)
    return send_file('questionFile.ods', as_attachment=True)

@app.route('/addTests/<filename>', methods=['GET', 'POST'])
def addTests(filename):
    columns=["number","board","grade","subject","chapterNumber","conceptName","testname","text2","text3","imagePath","description","preparedBy","syllabus","tags","coins","practiceTest",
    'concept/pyq',	'loop/noloop']
    df = read_ods(filename, 1, columns=columns)
    os.remove(filename)
    testCategories = {'concept':'Concept Based', 'pyq':'PYQs'}
    isLoop = {'loop':True, 'noloop':False}
    practiceTest = {'yes':True, 'no':False}
    info = {
        'TAdded':0,
        'TUpdated':0,
        'TRepeated':0
    }
    for row in range(df.shape[0]):
        if not df["number"][row]:
            continue
        if df["number"][row] == '-':
            break
        try:
            path = "src/static/img/"
            grade = Grade.query.filter_by(grade = int(str(df["grade"][row]).split('.')[0])).first().id
            board = Board.query.filter_by(name=df['board'][row]).first().id
            subject = Subject.query.filter_by(name = df["subject"][row], grade=grade, board=board).first().id
            chapter = Chapter.query.filter_by(number = int(str(df["chapterNumber"][row]).split('.')[0]), subjectId=subject).first().id
            if isLoop[df['loop/noloop'][row]]:
                concepts = Concept.query.filter_by(chapterId=chapter).all()
                questions = Question.query.filter(Question.conceptId.in_([con.id for con in concepts])).all()
                test = Test.query.filter_by(name=df['testname'][row], chapterId=chapter).first()
                concept, category = None, None
            else:
                concept = Concept.query.filter_by(name=df['conceptName'][row], chapterId=chapter).first().id
                questions = Question.query.filter_by(conceptId=concept).all()
                test = Test.query.filter_by(name=df['testname'][row], conceptId=concept).first()
                category = TestCategory.query.filter_by(name=testCategories[df['concept/pyq'][0]], subjectId=subject).first().id
            questionIds = ''
            time = 0
            for qId in questions:
                questionIds += str(qId.id) + ','
                time += qId.maxSolvingTime
            questionIds = questionIds[:-1]
            if test:
                if test.questionIds != questionIds:
                    test.questionIds = questionIds
                    db.session.commit()
                    info['TUpdated']+=1
                else:
                    info['TRepeated']+=1
            else:
                test = Test(df['testname'][row], df['text2'][row], df['text3'][row], concept, chapter, subject, \
                category, path+df['imagePath'][row], df['description'][row], df['preparedBy'][row], df['syllabus'][row],\
                df['tags'][row], int(str(df['coins'][row]).split('.')[0]), False, isLoop[df['loop/noloop'][row]],\
                practiceTest[df['practiceTest'][row]], questionIds, time, True, None, 1, datetime.datetime.now(indianTime))
                db.session.add(test)
                db.session.commit()
                info['TAdded']+=1
        except Exception as e:
            return redirect(url_for('uploadExcels', error='info '+str(info)+' and error '+str(e)+' at number '+ str(df["number"][row])))
    return redirect(url_for('uploadExcels', error=info))


@app.route('/addChapters/<filename>', methods=['GET', 'POST'])
def addChapters(filename):
    columns=['number', 'name', 'imgPath', 'caption', 'description', 'tags', 'subject', 'class', 'board']
    df = read_ods(filename, 1, columns=columns)
    os.remove(filename)
    info = {
        'CAdded':0,
        'CRepeated':0,
    }
    iter = 0
    for row in range(df.shape[0]):
        if df["number"][row] == '-':
            break
        iter += 1
        try:
            path = "src/static/img/"
            grade = Grade.query.filter_by(grade = int(str(df["class"][row]).split('.')[0])).first().id
            board = Board.query.filter_by(name=df['board'][row]).first().id
            subjectId = Subject.query.filter_by(name = df["subject"][row], grade=grade, board=board).first().id
            chapter = Chapter.query.filter_by(name=df['name'][row], subjectId=subjectId).first()
            if chapter:
                info['CRepeated']+=1
            else:
                chapter = Chapter(int(str(df['number'][row]).split('.')[0]), df['name'][row], df['imgPath'][row], subjectId, df['caption'][row], \
                df['description'][row], df['tags'][row], df['number'][row], datetime.datetime.now(indianTime))
                db.session.add(chapter)
                db.session.commit()
                info['CAdded']+=1
        except Exception as e:
            return redirect(url_for('uploadExcels', error='info '+str(info)+' and error '+str(e)+' at row number '+ str(iter)))
    return redirect(url_for('uploadExcels', error=info))

@app.route('/reviewQuestion/<filename>', methods=['GET', 'POST'])
def reviewQuestion(filename):
    # if 'adminAvailable' not in session.keys():
    #     return redirect(url_for('signin'))
    reviewQuestion = ReviewQuestion()
    error, getQuestions = getQuestionList(filename)
    os.remove(filename)
    if error:
        # os.remove(filename)
        return redirect(url_for('uploadExcels', error=error))
    error = ''
    mcqMsqDadSeqHeader = getQuestions[0].pop(0)
    fillTorFHeader = getQuestions[1].pop(0)
    matchHeader = getQuestions[2].pop(0)
    mcqMsqDadSeqList = getQuestions[0]
    fillTorFList = getQuestions[1]
    matchList = getQuestions[2]
    # "tags", "hints", "hints image", "answer exp", "ans exp image", "difficultyLevel","maxSolvingTime", "category", "PYQ Years"
    questionFormatDict = {'mcq':1, 'msq':2,'ftb':3,'dad':4,'tof':5}#,'dad':6,'seq':7}
    info = {
        'CAdded':0,
        'QAdded':0,
        'QRepeated':0,
        'formatAdded':{'mcq':0, 'msq':0,'ftb':0,'mtf':0,'tof':0,'dad':0,'seq':0},
        'formatRepeated':{'mcq':0, 'msq':0,'ftb':0,'mtf':0,'tof':0,'dad':0,'seq':0}
    }

    if request.method == 'POST':
        if reviewQuestion.proceed.data:
            error='success'
            exception = False
            questionNumber = None
            for rows in mcqMsqDadSeqList+fillTorFList+matchList:
                questionNumber = None
                try:
                    conceptName = rows.pop(0)
                    questionText = rows[0]
                    format = rows.pop(-1)
                    path = "src/static/img/"
                    gradeData, errorCode = getGrade({'id':int(str(conceptName[3]).split('.')[0])})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+gradeData)
                        return redirect(url_for('uploadExcels', error=gradeData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    boardData, errorCode = getGrade({'id':conceptName[4]})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+boardData)
                        return redirect(url_for('uploadExcels', error=boardData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    subjectData, errorCode = getSubject({'name':conceptName[2], 'board':boardData.id, 'grade':gradeData.id})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+subjectData)
                        return redirect(url_for('uploadExcels', error=subjectData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    chapterData, errorCode = getChapter({'number':int(str(conceptName[1]).split('.')[0]), 'subjectId':subjectData.id})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+chapterData)
                        return redirect(url_for('uploadExcels', error=chapterData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    qImgP = qHintImgP = qExpImgP = qC1ImgP = qC2ImgP = qC3ImgP = qC4ImgP = aC1ImgP = aC2ImgP = aC3ImgP = aC4ImgP = path
                    if rows[-7] and rows[-7] != '':
                        rows[-7] = qHintImgP + rows[-7]
                    if rows[-5] and rows[-5] != '':
                        rows[-5] = qExpImgP + rows[-5]

                    conceptData, errorCode = getConcept({'name':conceptName[0], 'chapterId':chapterData.id})
                    if errorCode == 200:
                        conceptId = conceptData.id
                    elif errorCode == 404:
                        concept = Concept(conceptName[0], chapterData.id, subjectData.id, True, 1, datetime.datetime.now(indianTime))
                        conceptId, errorCode = insertConcept(concept)
                        if errorCode != 201:
                            return redirect(url_for('uploadExcels', error=conceptId+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                        info['CAdded']+=1
                    elif errorCode == 500:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+conceptData)
                        return redirect(url_for('uploadExcels', error=conceptData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    questionData, errorCode = getQuestion({'text':questionText, 'conceptId':conceptId})
                    if errorCode == 404:
                        try:
                            question = Question(questionText, conceptId, session['adminId'],\
                            datetime.datetime.now(indianTime), rows[-4], questionFormatDict[format],\
                            rows[-2], rows[-8], rows[-7], None, rows[-9], rows[-3], rows[-6], rows[-5], rows[-1], True)
                            db.session.add(question)
                            db.session.flush()
                            questionId = question.id

                            if format != 'mtf':
                                if rows[1] and rows[1] != '':
                                    rows[1] = qImgP + rows[1]
                            if format == "mcq" or format == "msq" or format == "dad" or format == "seq":
                                #questionId, "question image", "opt1",  "img1","opt2", "img2", "opt3", "img3", "opt4", "img4", "ans",
                                db.session.add(QuestionMcqMsqDadSeq(questionId, rows[1], rows[2], rows[3],\
                                rows[4], rows[5], rows[6], rows[7], rows[8], rows[9], rows[10]))

                            elif format == "ftb" or format == "tof":
                                #questionId, "question image", "ans"
                                db.session.add(QuestionFillTorF(questionId, rows[1], rows[2]))
                            elif format == "mtf":
                                rows.pop(0) #removed questionText
                                if rows[1] and rows[1] != '':
                                    rows[1] = qC1ImgP + rows[1]
                                if rows[3] and rows[3] != '':
                                    rows[3] = qC2ImgP + rows[3]
                                if rows[5] and rows[5] != '':
                                    rows[5] = qC3ImgP + rows[5]
                                if rows[7] and rows[7] != '':
                                    rows[7] = qC4ImgP + rows[7]
                                if rows[9] and rows[9] != '':
                                    rows[9] = aC1ImgP + rows[9]
                                if rows[11] and rows[11] != '':
                                    rows[11] = aC2ImgP + rows[11]
                                if rows[13] and rows[13] != '':
                                    rows[13] = aC3ImgP + rows[13]
                                if rows[15] and rows[15] != '':
                                    rows[15] = aC4ImgP + rows[15]
                                #questionId, "opt1",  "img1", "opt2", "img2", "opt3","img3", "opt4", "img4", "ans1",  "img1", "ans2",  "img2", "ans3",  "img3","ans4",  "img4", ans
                                db.session.add(QuestionMatch(questionId, rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],\
                                rows[7],  rows[8], rows[9], rows[10], rows[11],  rows[12], rows[13], rows[14], rows[15], rows[16]))
                            db.session.commit()
                            info['QAdded']+=1
                            info['formatAdded'][format] += 1
                        except Exception as e:
                            db.session.rollback()
                            app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error: failed to add question, details: '+str(e))
                            return redirect(url_for('uploadExcels', error='failed to add question. error: '+ str(e)+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                    elif errorCode == 200:
                        info['QRepeated']+=1
                        info['formatRepeated'][format] += 1
                    elif errorCode == 500:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+ str(session['adminName'])+'. error:'+questionData)
                        return redirect(url_for('uploadExcels', error=questionData+ ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))

                except Exception as e:
                    return redirect(url_for('uploadExcels', error= str(e) + ' questionNumber:'+str(info['QRepeated']+info['QAdded']+1)))
            # os.remove(filename)

        elif reviewQuestion.back.data:
            error='error'
            # os.remove(filename)
            return redirect(url_for('uploadExcels', error='Check excel and re-upload'))
    return render_template('reviewQuestion.html', rq=reviewQuestion, s=session, mh=mcqMsqDadSeqHeader,\
    fh=fillTorFHeader, mah=matchHeader, ml=mcqMsqDadSeqList, fl=fillTorFList, mal=matchList)


#filters    loops/static/dynamic,
@app.route('/testQuestionLinker/<error>/<board>/<grade>/<subjectId>/<chapterId>', methods=['GET', 'POST'])
def testQuestionLinker(error, board, grade, subjectId, chapterId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error+' -board:'+str(board)+' -grade:'+str(grade)\
    +' -subjectId:'+str(subjectId)+' -chapterId:'+str(chapterId)+' -adminName:'+str(session['adminName']))

    if 'delete' in error:
        question = db.session.query(Question).filter(Question.id==error.split('-')[1]).first()
        db.session.delete(question)
        db.session.commit()
        return redirect(url_for('testQuestionLinker', error='success', board=board, grade=grade, subjectId=subjectId, chapterId=chapterId))
    elif 'statusUpdate' in error:
        question = db.session.query(Question).filter(Question.id==error.split('-')[1]).first()
        question.status = (question.status + 1)%2
        db.session.commit()
        return redirect(url_for('testQuestionLinker', error='success', board=board, grade=grade, subjectId=subjectId, chapterId=chapterId))

    tQForm = TestQuestionLinker()
    tQForm.board.choices = [(b.id, b.name) for b in Board.query.all()]
    tQForm.grade.choices = [(g.id, g.grade) for g in Grade.query.all()]

    if board != 'None':
        tQForm.board.data = board
    if grade != 'None':
        tQForm.grade.data = grade
    if tQForm.grade.data and tQForm.board.data:
        tQForm.subject.choices = [('None', 'None')] + [(sub.id, sub.name) for sub in Subject.query.\
        filter_by(grade=tQForm.grade.data, board=tQForm.board.data).all()]
    else:
        tQForm.subject.choices = [('None', 'None')] + [(sub.id, sub.name) for sub in Subject.query.\
        filter_by(grade=Grade.query.first().id, board=Board.query.first().id).all()]

    ml = []
    if subjectId != 'None':
        tQForm.subject.data = subjectId
        tQForm.tests.choices = [('None', 'None')] + [(test.id, test.name + (" - Loop" if test.isLoop else '')) for test in Test.query.\
        filter_by(subjectId=subjectId).all()]
        tQForm.chapter.choices = [('None', 'None')] + [(chap.id, chap.name) for chap in Chapter.query.\
        filter_by(subjectId=tQForm.subject.data).all()]
        tQForm.category.choices = [('None', 'None')] + [(cat.name, cat.name) for cat in TestCategory.query.\
        filter_by(subjectId=tQForm.subject.data).all()]

        question = db.session.query(Question.id, Question.text, QuestionFormat.code, Question.difficultyLevel, Question.category,\
        Question.tags, Question.maxSolvingTime, Question.previousYearApearance, Concept.id, Concept.name, Question.status).\
        filter(Question.format == QuestionFormat.id).filter(Question.conceptId == Concept.id).\
        filter(Subject.id == Concept.subjectId).filter(Subject.id == tQForm.subject.data)
        if chapterId == 'None':
            tQForm.concept.choices = [('None', 'None')] + [(concept.id, concept.name) for concept in Concept.query.\
            filter_by(subjectId=tQForm.subject.data).all()]
        else:
            tQForm.chapter.data = chapterId
            tQForm.concept.choices = [('None', 'None')] + [(concept.id, concept.name) for concept in Concept.query.\
            filter_by(chapterId=tQForm.chapter.data).all()]
            tQForm.tests.choices = [('None', 'None')] + [(test.id, test.name + (" - Loop" if test.isLoop else '')) for test in Test.query.\
            filter_by(subjectId=subjectId, chapterId=chapterId).all()]
            question = question.filter(Concept.chapterId == tQForm.chapter.data)
        if not request.method == 'POST':
            ml = question.all()
    else:
        question = db.session.query(Question.id, Question.text, QuestionFormat.code, Question.difficultyLevel, Question.category,\
        Question.tags, Question.maxSolvingTime, Question.previousYearApearance, Concept.id, Concept.name, Question.status).\
        filter(Question.format == QuestionFormat.id).filter(Question.conceptId == Concept.id).\
        filter(Subject.id == Concept.subjectId).all()

    level = config2['difficultyLevel']
    tQForm.level.choices = [('None', 'None')] + [(l, level[l]) for l in level]
    tQForm.format.choices = [('None', 'None')] + [(format.id, format.code) for format in QuestionFormat.query.all()]

    mh = ['Q id-text', 'format', 'difficulty', 'category', 'tags', 'maxTime', 'pyq', 'concept id-name', 'status', 'action', 'test id-name']
    time, coins, formats = 0, 0, {}

    if request.method == 'POST':
        if tQForm.level.data != 'None':
            question = question.filter(Question.difficultyLevel == tQForm.level.data)
        if tQForm.format.data != 'None':
            question = question.filter(QuestionFormat.id == tQForm.format.data)
        if len(tQForm.concept.data):
            question = question.filter(Concept.id.in_([c for c in tQForm.concept.data]))
        if tQForm.questionText.data and tQForm.questionText.data != 'None':
            question = question.filter(Question.text.ilike("%"+tQForm.questionText.data+"%"))
        if tQForm.pyq.data and tQForm.pyq.data != 'None':
            question = question.filter(Question.previousYearApearance.ilike("%"+tQForm.pyq.data+"%"))
        if tQForm.tags.data and tQForm.tags.data != 'None':
            question = question.filter(Question.tags.ilike("%"+tQForm.tags.data+"%"))

        ml = question.all()
        question = question.all()

        if tQForm.category.data != 'None':
            ml = []
            for ques in question:
                if ques.category and tQForm.category.data in ques.category:
                    ml.append(ques)

        if tQForm.tests.data and tQForm.tests.data != 'None':
            ml = []
            for q in Test.query.filter_by(id=tQForm.tests.data).first().questionIds.split(','):
                question = db.session.query(Question.id, Question.text, QuestionFormat.code, Question.difficultyLevel, Question.category,\
                Question.tags, Question.maxSolvingTime, Question.previousYearApearance, Concept.id, Concept.name, Question.status).\
                filter(Question.format == QuestionFormat.id).filter(Question.conceptId == Concept.id).\
                filter(Question.id == q).filter(Subject.id == Concept.subjectId).\
                filter(Subject.grade == Grade.id).filter(Concept.chapterId == Chapter.id).first()
                ml.append(question)

    for i, question in enumerate(ml):
        ml[i] = []
        level = config2['difficultyLevel'][question.difficultyLevel]
        time += config4['time'][level]
        coins += config3['coins'][level]
        if question.code not in formats.keys():
            formats[question.code] = 0
        formats[question.code] += 1
        for q in question:
            ml[i].append(q)
        tests = []
        for test in Test.query.filter_by(subjectId=tQForm.subject.data).all():
            if str(question[0]) in test.questionIds.split(','):
                tests.append([test.name, test.id])
        ml[i].append(tests)
    summary = {'NoOfQs':len(ml), 'time':time, 'coins':coins, 'formats':formats}
    return render_template('testQuestionLinker.html', tQForm=tQForm, error=error, mh=mh, ml=ml, summary=summary, questionIds='None', s=session)

@app.route('/createTest/<questionIds>/<error>/<mains>', methods=['GET', 'POST'])
def createTest(questionIds, error, mains):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -questionIds:'+str(questionIds)+' -error:'+error+' -mains(g,b,s,c,co):'+str(mains)\
    +' -adminName:'+str(session['adminName']))

    mains = mains.split(',')
    board, grade, subject, chapter, concepts = mains[0], mains[1], mains[2], mains[3], ''
    if chapter == 'None':
        return redirect(url_for('testQuestionLinker', error='please select chapter'\
    , board='None', grade='None', subjectId='None', chapterId='None'))
    for c in mains[4:-1]:
        if c != 'None':
            concepts += Concept.query.filter_by(id=int(c)).first().name +','
        else:
            concepts = None
            break

    mc = 'count='+str(len(questionIds[:-1].split(',')))
    mh = ['question', 'concept', 'difficulty', 'format', 'category', 'hints', 'tags', 'pyq']
    ml = []
    time, coins = 0, 0
    for id in questionIds[:-1].split(','):
        question = db.session.query(Question.text, Concept.name, Question.difficultyLevel,\
        QuestionFormat.code, Question.category, Question.hints, Question.tags,\
        Question.previousYearApearance).filter(Question.id == int(id)).\
        filter(Question.conceptId == Concept.id).filter(Question.format == QuestionFormat.id).first()
        ml.append(question)
        level = config2['difficultyLevel'][question.difficultyLevel]
        time += config4['time'][level]
        coins += config3['coins'][level]

    summary = {
         'count':len(questionIds[:-1].split(',')),
         'coins':coins,
         'time':time,
         'board':Board.query.filter_by(id=board).first().name,
         'grade':Grade.query.filter_by(id=grade).first().grade,
         'subject':Subject.query.filter_by(id=subject).first().name,
         'chapter':Chapter.query.filter_by(id=chapter).first().name if chapter else None,
         'concepts':concepts
    }
    exception = False
    createTest = CreateTest()
    createTest.category.choices = [(cat.id, cat.name) for cat in TestCategory.query.filter_by(subjectId=subject).all()]
    if request.method == 'POST':
        if createTest.submit.data:
            path = "src/static/img/"
            isStaticTest, isLoop, isPracticeTestNeeded = False, False, False
            if createTest.testType.data == '1':
                isStaticTest = True
            elif createTest.testType.data == '3':
                isLoop = True
                createTest.maxCoins.data = 0
                createTest.maxTime.data = 0
            if createTest.isPracticeTestNeeded.data == '1':
                isPracticeTestNeeded = True
            # print(createTest.testName.data, createTest.text2.data, createTest.text3.data, \
            # None, chapter,
            # subject, createTest.category.data, path+createTest.imagePath.data,
            # createTest.description.data, createTest.preparedBy.data, createTest.syllabus.data, \
            # createTest.tags.data, \
            # createTest.maxCoins.data, isStaticTest, isLoop, isPracticeTestNeeded,\
            # questionIds[:-1], createTest.maxTime.data, True, None,datetime.datetime.now(indianTime))
            try:
                db.session.add(Test(createTest.testName.data, createTest.text2.data, \
                createTest.text3.data, None, chapter,
                subject, createTest.category.data, path+createTest.imagePath.data,
                createTest.description.data, createTest.preparedBy.data, createTest.syllabus.data, \
                createTest.tags.data,
                createTest.maxCoins.data, isStaticTest, isLoop, isPracticeTestNeeded,\
                questionIds[:-1], createTest.maxTime.data, True, None, session['adminId'], datetime.datetime.now(indianTime)))
                db.session.commit()
            except exc.DataError as e:
                error = {
                    'errorStatement':str(e.statement),
                    'errorParams':str(e.params),
                    'errorOrig':str(e.orig),
                }
                exception = True
            except Exception as e:
                error = {
                'error':e
                }
                exception = True
            if exception:
                return redirect(url_for('testQuestionLinker', error=error, board='None', grade='None', subjectId='None', chapterId='None'))
            return redirect(url_for('testQuestionLinker', error='success', board='None', grade='None', subjectId='None', chapterId='None'))
    return render_template('createTest.html', createTest=createTest, summary=summary, mh=mh, ml=ml, testType=createTest.testType.data, s=session)

@app.route('/deleteAllQuestions/<questionIds>/<error>/<mains>', methods=['GET', 'POST'])
def deleteAllQuestions(questionIds, error, mains):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -questionIds:'+str(questionIds)+' -error:'+error+' -mains(g,b,s,c):'+str(mains)\
    +' -adminName:'+str(session['adminName']))

    mains = mains.split(',')
    board, grade, subject, chapter = mains[0], mains[1], mains[2], mains[3]
    for id in questionIds[:-1].split(','):
        question = Question.query.filter_by(id=id).first()
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('testQuestionLinker', error='success', board=board, grade=grade, subjectId=subject, chapterId=chapter))

# modify test
@app.route('/modifyTest/<testId>/', methods=['GET', 'POST'])
def modifyTest(testId):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -testId:'+str(testId)\
    +' -adminName:'+str(session['adminName']))

    modifyTest = ModifyTest()
    test = db.session.query(Test).filter(Test.id==testId).first()
    modifyTest.category.choices = [(cat.id, cat.name) for cat in TestCategory.query.\
    filter_by(subjectId=test.subjectId).all()]
    if request.method != "POST":
        modifyTest.isLoop.default = 1 if test.isLoop else 0
        modifyTest.isStaticTest.default = 1 if test.isStaticTest else 0
        modifyTest.status.default = 1 if test.status else 0
        modifyTest.isPracticeTestNeeded.default = 1 if test.isPracticeTestNeeded else 0
        modifyTest.category.default = test.categoryId
        modifyTest.process()
        modifyTest.name.data = test.name
        modifyTest.text2.data = test.text2
        modifyTest.text3.data = test.text3
        modifyTest.concept.data = test.conceptId
        modifyTest.chapter.data = Chapter.query.filter_by(id=test.chapterId).first().name
        modifyTest.subject.data = Subject.query.filter_by(id=test.subjectId).first().name
        modifyTest.imagePath.data = test.imagePath
        modifyTest.description.data = test.description
        modifyTest.preparedBy.data = test.preparedBy
        modifyTest.syllabus.data = test.syllabus
        modifyTest.tags.data = test.tags
        modifyTest.maxCoins.data = test.maxCoins
        modifyTest.questionIds.data = test.questionIds
        modifyTest.maxTime.data = test.maxTime
    if request.method == "POST":
        if modifyTest.update.data:
            test.isLoop = True if modifyTest.isLoop.data != '0' else False
            test.isStaticTest = True if modifyTest.isStaticTest.data != '0' else False
            test.status = True if modifyTest.status.data != '0' else False
            test.isPracticeTestNeeded = True if modifyTest.isPracticeTestNeeded.data != '0' else False
            test.text2 = modifyTest.text2.data
            test.text3 = modifyTest.text3.data
            # test.conceptId = modifyTest.concept.data
            # Chapter.query.filter_by(id=test.chapterId).first().name = modifyTest.chapter.data
            # Subject.query.filter_by(id=test.subjectId).first().name = modifyTest.subject.data
            test.categoryId = modifyTest.category.data
            test.imagePath = modifyTest.imagePath.data
            test.description = modifyTest.description.data
            test.preparedBy = modifyTest.preparedBy.data
            test.syllabus = modifyTest.syllabus.data
            test.tags = modifyTest.tags.data
            test.maxCoins = modifyTest.maxCoins.data
            test.questionIds = modifyTest.questionIds.data
            test.maxTime = modifyTest.maxTime.data
        if modifyTest.delete.data:
            db.session.delete(test)
        db.session.commit()
        return redirect(url_for('testQuestionLinker', error='success', board='None', grade='None', subjectId='None', chapterId='None'))
    return render_template('modifyTest.html', mT=modifyTest, s=session)


@app.route('/docx/<filename>', methods=['GET', 'POST'])
def docx(filename):
    # from pdf2image import convert_from_path
    # images = convert_from_path('.pdf')
    # for i in range(len(images)):
    #     images[i].save(filename+ str(i) +'.jpg', 'JPEG')
    path = []
    count = [f for f in os.listdir('src/static/img/') if f.startswith(filename)]
    for i in range(len(count)):
            path.append('img/'+filename+ str(i) +'.jpg')
    return render_template('docx.html', images=path)


# modify question
@app.route('/modifyQuestion/<questionId>/', methods=['GET', 'POST'])
def modifyQuestion(questionId):
    question = db.session.query(Question.id, Question.text, Concept.name, Admin.name, Question.datetime, \
    Question.difficultyLevel, QuestionFormat.code, Question.category, Question.hints, Question.hintsImagePath, \
    Question.description, Question.tags, Question.maxSolvingTime, Question.ansExplanation, Question.ansExpImage,\
    Question.previousYearApearance).filter_by(id=questionId).filter(Question.conceptId == Concept.id).\
    filter(Question.format == QuestionFormat.id).filter(Question.addedBy==Admin.id).first()
    c = ['id', 'text', 'ConceptName', 'addedBy', 'datetime', \
    'difficultyLevel', 'format', 'category', 'hints', 'hintsImagePath', \
    'description', 'tags', 'maxSolvingTime', 'ansExplanation', 'ansExpImage',\
    'previousYearApearance']
    e, d, l = [], None, 0
    if question.code == 'MCQ' or question.code == 'MSQ' or question.code == 'Drag & Drop' or question.code == 'Sequence':
        d = db.session.query(QuestionMcqMsqDadSeq.imagePath, QuestionMcqMsqDadSeq.choice1, \
        QuestionMcqMsqDadSeq.choice1ImagePath, QuestionMcqMsqDadSeq.choice2, \
        QuestionMcqMsqDadSeq.choice2ImagePath, QuestionMcqMsqDadSeq.choice3,\
        QuestionMcqMsqDadSeq.choice3ImagePath, QuestionMcqMsqDadSeq.choice4,\
        QuestionMcqMsqDadSeq.choice4ImagePath, QuestionMcqMsqDadSeq.correctChoiceSeq).\
        filter(QuestionMcqMsqDadSeq.questionId==question.id).first()
        e += ['imagePath', 'choice1', \
        'choice1ImagePath', 'choice2', \
        'choice2ImagePath', 'choice3',\
        'choice3ImagePath', 'choice4',\
        'choice4ImagePath', 'correctChoiceSeq']
    elif  question.code == 'Fill' or question.code == 'True/False':
        d = db.session.query(QuestionFillTorF.imagePath, QuestionFillTorF.correctAnswer).\
        filter(QuestionFillTorF.questionId==question.id).first()
        e += ['imagePath', 'correctAnswer']
    elif question.code == 'Match':
        d = db.session.query(QuestionMatch.leftChoice1,QuestionMatch.leftChoice1ImagePath,QuestionMatch.leftChoice2,QuestionMatch.leftChoice2ImagePath,QuestionMatch.leftChoice3,QuestionMatch.leftChoice3ImagePath,QuestionMatch.leftChoice4,QuestionMatch.leftChoice4ImagePath,QuestionMatch.rightChoice1,QuestionMatch.rightChoice1ImagePath,QuestionMatch.rightChoice2,QuestionMatch.rightChoice2ImagePath,QuestionMatch.rightChoice3,QuestionMatch.rightChoice3ImagePath,QuestionMatch.rightChoice4,QuestionMatch.rightChoice4ImagePath,QuestionMatch.correctChoiceSeq).\
        filter(QuestionMatch.questionId==question.id).first()
        e += ['leftChoice1','leftChoice1ImagePath','leftChoice2','leftChoice2ImagePath','leftChoice3','leftChoice3ImagePath','leftChoice4','leftChoice4ImagePath','rightChoice1','rightChoice1ImagePath','rightChoice2','rightChoice2ImagePath','rightChoice3','rightChoice3ImagePath','rightChoice4','rightChoice4ImagePath','correctChoiceSeq']
    l = len(e)
    return render_template('modifyQuestion.html', c=c, q=list(question), d=d, e=e, l=l, s=session)


@app.route('/src/<static>/<img>/<image>', methods=['GET', 'POST'])
def src(static, img, image):
    return render_template('imageHelper.html', image='img/'+image, s=session)

@app.route('/imageHelper/<error>', methods=['POST', 'GET'])
def imageHelper(error):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))
    imageHelper = ImageHelper()
    imageHelper.list.choices = [(l,l) for l in os.listdir('src/static/img')]
    imageHelper.list.choices.sort()
    if '.' in error:
        os.remove("src/static/img/"+error)
        return redirect(url_for('imageHelper', error='success'))
    if request.method == 'POST':
        if imageHelper.display.data:
            return render_template('imageHelper.html', iH=imageHelper, image='img/'+imageHelper.list.data, s=session)
            # return redirect(url_for('src', static='static', img='img', image=imageHelper.list.data))
        if imageHelper.search.data:
            if imageHelper.name.data in os.listdir('src/static/img'):
                return redirect(url_for('imageHelper', error='name repeated or failed'))
            elif not imageHelper.name.data:
                return redirect(url_for('imageHelper', error='enter name'))
            return render_template('imageHelper.html', iH=imageHelper, upload='upload', s=session)
        f = request.files['filename']
        if f.filename:
            f.save(os.getcwd()+'/src/static/img/'+ f.filename)
    return render_template('imageHelper.html', iH=imageHelper, error=error, s=session)

apis = [
    'fhome', 'ftestHome', 'freports', 'fanalytics', 'fsubscription', 'fprofile'
    # 'fschool', 'fsignup', 'flogin', 'fuserActive', 'fvalidateReferral', 'favatar',\
    # 'fprofile', 'fprofileDetailed', 'fprofileUpdate', 'fbookmarkTest', 'fbookmarkQuestion',\
    # 'fsubscription', 'fcoupon', 'fpayment', 'freferralPage', 'fhome', 'fnoticeClick',\
    # 'ftestHome', 'fpyq', 'ftestChapters', 'ftestChapterConcept', 'fcustomTest',\
    # 'ftestInstructions', 'floopsHome', 'ftestStart', 'fquestionBookmark', 'fquestionNext',\
    # 'ftestPaused', 'ftestSummary', 'ftestSubmit', 'ftestBookmark', 'ftestResults',\
    # 'fsprintHistory', 'ftestHistory', 'fanalytics', 'fanalyticsSubject', 'freports',\
    # 'fappVersion', 'ffaq', 'fnotification'
]


@app.route('/notifications/<error>', methods=['POST', 'GET'])
def notifications(error):
    if 'adminAvailable' not in session.keys():
        return redirect(url_for('signin'))
    nf = NotificationsForm()
    nh = ['title', 'message', 'redirectTo', 'user group', 'trigger Time']
    nl = db.session.query(Notifications.title, Notifications.message, Notifications.redirect, \
    Notifications.targetUserGroup, Notifications.triggeringTime).order_by(-Notifications.id).all()
    newNl = []
    for n in nl:
        targetGroup = '['
        for i in n[3].split('-')[0].split(','):
            targetGroup += School.query.filter_by(id=i).first().name + ','
        targetGroup += ']['
        for i in n[3].split('-')[1].split(','):
            targetGroup += Board.query.filter_by(id=i).first().name + ','
        targetGroup += ']['
        for i in n[3].split('-')[2].split(','):
            targetGroup += str(Grade.query.filter_by(id=i).first().grade) + ','
        targetGroup += ']'
        newNl.append([n[0], n[1], n[2], targetGroup, n[4]])
    nl = newNl
    nf.redirectApi.choices = [(a,a) for a in apis]
    nf.grade.choices = [(g.id, g.grade) for g in Grade.query.order_by(-Grade.id).all()]
    nf.board.choices = [(b.id, b.name) for b in Board.query.all()]
    nf.school.choices = [(s.id, s.name) for s in School.query.all()]
    nf.imagePath.choices = [(None, None)] + [(l,l) for l in os.listdir('src/static/img')]
    error = 'success'
    if request.method == 'POST':
        path = None
        if nf.imagePath.data:
            path = "src/static/img/" + nf.imagePath.data
        schools = ''.join(o+',' for o in nf.school.data)[:-1]
        boards = ''.join(o+',' for o in nf.board.data)[:-1]
        grades = ''.join(o+',' for o in nf.grade.data)[:-1]
        targetUserGroup = schools + '-' + boards + '-' + grades
        db.session.add(Notifications(nf.title.data, nf.message.data, path, nf.redirectApi.data,\
        targetUserGroup, nf.triggeringTime.data, session['adminId'], datetime.datetime.now(indianTime)))
        db.session.commit()
        if datetime.datetime.now(indianTime).strftime('%Y-%m-%d') == nf.triggeringTime.data:
            users = User.query.filter(User.grade.in_([g for g in nf.grade.data])).filter(User.school.\
            in_([s for s in nf.school.data])).filter(User.board.in_([b for b in nf.board.data])).all()
            for user in users:
                if n.redirect == 'fhome' or n.redirect == 'fsubscription' or n.redirect == 'fprofile' or n.redirect == 'freports' or n.redirect == 'fanalytics':
                    fnotification(nf.title.data, nf.message.data, path, user.id,\
                    {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':n.redirect, 'userId':str(user.id)})
                elif n.redirect == 'ftestHome':
                    subjectId = Subject.query.filter_by(grade=u.grade, board=u.board).order_by(Subject.sortOrder).first().id
                    fnotification(nf.title.data, nf.message.data, path, user.id,\
                    {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':n.redirect, 'userId':str(user.id), 'subjectId':str(subjectId)})
    return render_template('notifications.html', nf=nf, nh=nh, nl=nl, error=error, s=session)

@app.route('/subscriptions/<error>/<subsId>', methods=['POST', 'GET'])
def subscriptions(error, subsId):
    if 'adminAvailable' not in session.keys() or session['adminRole'] != 'all':
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error\
    +' -subsId:'+str(subsId)+' -adminName:'+str(session['adminName']))

    subscriptions = Subscriptions()
    subscriptions.board.choices = [(b.id, b.name) for b in Board.query.all()]
    subscriptions.grades.choices = [(g.id, g.grade) for g in Grade.query.all()]

    sh = ['name', 'price', 'strikedPrice', 'number of Tests', 'maxRedeemable coins', 'comment', 'grade', 'board', 'modified by', 'datetime', 'validity(Months)', 'coupon Valid', 'status', 'action']
    sl = db.session.query(Subscription.id, Subscription.name, Subscription.price, Subscription.strikedPrice, Subscription.numberOfTests, Subscription.maxRedeemableCoins,  \
    Subscription.comment, Grade.grade, Board.name, Admin.name, Subscription.dateTime, Subscription.validity, Subscription.status, Subscription.couponValid).filter(Subscription.addedBy==Admin.id).\
    filter(Subscription.board == Board.id).filter(Subscription.grade == Grade.id).all()

    if 'update' in error and request.method != 'POST':
        subscription = Subscription.query.filter_by(id=subsId).first()
        subscriptions.name.data = subscription.name
        subscriptions.price.data = subscription.price
        subscriptions.strikedPrice.data = subscription.strikedPrice
        subscriptions.numberOfTests.data = subscription.numberOfTests
        subscriptions.maxRedeemableCoins.data = subscription.maxRedeemableCoins
        subscriptions.comment.data = subscription.comment
        subscriptions.validity.data = subscription.validity
        subscriptions.grades.data = str(subscription.grade)
        subscriptions.board.data = str(subscription.board)
        return render_template('subscriptions.html', sh=sh, sl=sl, subscriptions=subscriptions, error='success', subsId=subsId, s=session)
    elif 'delete' in error:
        subscription = db.session.query(Subscription).filter(Subscription.id==subsId).first()
        db.session.delete(subscription)
        db.session.commit()
        return redirect(url_for('subscriptions', error='success', subsId=0))
    elif 'coupon' in error:
        subscription = db.session.query(Subscription).filter(Subscription.id==subsId).first()
        subscription.couponValid = (subscription.couponValid + 1)%2
        db.session.commit()
        return redirect(url_for('subscriptions', error='success', subsId=0))
    elif 'status' in error:
        subscription = db.session.query(Subscription).filter(Subscription.id==subsId).first()
        subscription.status = (subscription.status + 1)%2
        db.session.commit()
        return redirect(url_for('subscriptions', error='success', subsId=0))

    if request.method == 'POST':
        subs = db.session.query(Subscription).filter(Subscription.id==subsId).first()
        if subs:
            #update
            subs.price = subscriptions.price.data
            subs.strikedPrice = subscriptions.strikedPrice.data
            subs.numberOfTests = subscriptions.numberOfTests.data
            subs.maxRedeemableCoins = subscriptions.maxRedeemableCoins.data
            subs.comment = subscriptions.comment.data
            subs.validity = subscriptions.validity.data
            if subsId != '1':
                subs.name = subscriptions.name.data
                subs.grades = subscriptions.grades.data
                subs.board = subscriptions.board.data
        else:
            #add
            db.session.add(Subscription(subscriptions.name.data, subscriptions.price.data, subscriptions.strikedPrice.data,\
            subscriptions.numberOfTests.data, subscriptions.maxRedeemableCoins.data, True, subscriptions.comment.data,\
            session['adminId'], subscriptions.validity.data, subscriptions.grades.data, subscriptions.board.data, True, datetime.datetime.now(indianTime)))
        db.session.commit()
        return redirect(url_for('subscriptions', error='success', subsId=0))
        # return render_template('subscriptions.html', sh=sh, sl=sl, subscriptions=subscriptions, error='success', subsId=subsId, s=session)
    return render_template('subscriptions.html', sh=sh, sl=sl,  subscriptions=subscriptions, error='success', subsId=subsId, s=session)


@app.route('/coupons/<error>/<couponId>', methods=['POST', 'GET'])
def coupons(error, couponId):
    if 'adminAvailable' not in session.keys() or session['adminRole'] != 'all':
        return redirect(url_for('signin'))

    app.logger.debug(inspect.currentframe().f_code.co_name+' -error:'+error\
    +' -couponId:'+str(couponId)+' -adminName:'+str(session['adminName']))

    coupons = Coupons()

    ch = ['code', 'value', 'maxUses', 'maxPerUser', 'start date', 'end date', 'added by', 'status', 'action']
    cl = db.session.query(Coupon.id, Coupon.code, Coupon.value, Coupon.maxUses, Coupon.maxPerUser, Coupon.startDate,  \
    Coupon.endDate, Admin.name, Coupon.status).filter(Coupon.addedBy==Admin.id).all()

    if 'update' in error and request.method != 'POST':
        coupon = Coupon.query.filter_by(id=couponId).first()
        coupons.code.data = coupon.code
        coupons.value.data = coupon.value
        coupons.maxUses.data = coupon.maxUses
        coupons.maxPerUser.data = coupon.maxPerUser
        coupons.startDate.data = coupon.startDate
        coupons.endDate.data = coupon.endDate
        return render_template('coupons.html', ch=ch, cl=cl, coupons=coupons, error='success', couponId=couponId, s=session)
    elif 'delete' in error:
        coupon = db.session.query(Coupon).filter(Coupon.id==couponId).first()
        db.session.delete(coupon)
        db.session.commit()
        return redirect(url_for('coupons', error='success', couponId=0))
    elif 'status' in error:
        coupon = db.session.query(Coupon).filter(Coupon.id==couponId).first()
        coupon.status = (coupon.status + 1)%2
        db.session.commit()
        return redirect(url_for('coupons', error='success', couponId=0))

    if request.method == 'POST':
        coupon = db.session.query(Coupon).filter(Coupon.id==couponId).first()
        if coupon:
            #only Update
            coupon.code = coupons.code.data
            coupon.value = coupons.value.data
            coupon.maxUses = coupons.maxUses.data
            coupon.maxPerUser = coupons.maxPerUser.data
            coupon.startDate = coupons.startDate.data
            coupon.endDate = coupons.endDate.data
        else:
            #add
            db.session.add(Coupon(coupons.code.data, coupons.value.data, coupons.maxUses.data,\
            coupons.maxPerUser.data, coupons.startDate.data, coupons.endDate.data, True,\
            session['adminId'], datetime.datetime.now(indianTime)))
        db.session.commit()
        return redirect(url_for('coupons', error='success', couponId=0))
    return render_template('coupons.html', ch=ch, cl=cl,  coupons=coupons, error='success', couponId=couponId, s=session)


@app.route('/sales/<board>/<school>/<grade>/', methods=['POST', 'GET'])
def sales(board, school, grade):
    if 'adminAvailable' not in session.keys() or session['adminRole'] != 'all':
        return redirect(url_for('signin'))
    try:
        os.remove('src/salesReport.ods')
    except Exception as e:
        pass

    app.logger.debug(inspect.currentframe().f_code.co_name+' -adminName:'+str(session['adminName']))

    sales = Sales()
    sales.board.choices = [(b.id, b.name) for b in Board.query.all()]
    sales.school.choices = [(s.id, s.name) for s in School.query.all()]
    sales.grade.choices = [(g.id, g.grade) for g in Grade.query.all()]
    sales.user.choices = [(u.id, u.firstname+' '+u.lastname) for u in User.query.all()]
    sales.subscription.choices = [(s.id, s.name) for s in Subscription.query.all()]
    sales.coupon.choices = [(c.id, c.code) for c in Coupon.query.all()]
    sales.school.choices = [(s.id, s.name) for s in School.query.all()]
    if board != '0':
        sales.board.data = board
    if school != '0':
        sales.school.data = school
        sales.user.choices = [(u.id, u.firstname +' '+ u.lastname) for u in User.query.filter(User.school.in_([s for s in sales.school.data])).all()]
    if grade != '0':
        sales.grade.data = grade
        sales.user.choices = [(u.id, u.firstname +' '+ u.lastname) for u in User.query.filter(User.grade.in_([s for s in sales.grade.data])).all()]
    if grade != '0' and school != '0':
        sales.user.choices = [(u.id, u.firstname +' '+ u.lastname) for u in User.query.filter(User.school.in_([s for s in sales.school.data])).\
        filter(User.grade.in_([s for s in sales.grade.data])).all()]

    summary = {
        '#': 0,
        "Raju's worth":0,
        '#subscriptions':0,
        '#coupons':0
    }

    sh = ['orderId', 'transactionId', 'status', 'comments', 'datetime', 'user', 'subscription', 'amount', 'coupons']
    sh = ['subsActId', 'user', 'subscription', 'amount', 'coupons', 'datetime', 'success', 'message', 'testsRemaining', 'expiryDate', 'merchantTransId', 'TransId', 'misc']
    sl = []
    if request.method == 'POST':
        tsl = db.session.query(SubscriptionActivity.id, User.firstname+' '+User.lastname, Subscription.name, SubscriptionActivity.amount,\
        SubscriptionActivity.couponId, SubscriptionActivity.datetime, SubscriptionActivity.success, SubscriptionActivity.message,\
        SubscriptionActivity.testsRemaining, SubscriptionActivity.expiryDate,\
        SubscriptionActivity.merchantTransactionId, SubscriptionActivity.transactionId, SubscriptionActivity.paymentInfo).filter(SubscriptionActivity.userId == User.id).\
        filter(SubscriptionActivity.subsId == Subscription.id)
        if sales.school.data:
            tsl = tsl.filter(User.school.in_([s for s in sales.school.data]))
        if sales.board.data:
            tsl = tsl.filter(User.board.in_([b for b in sales.board.data]))
        if sales.grade.data:
            tsl = tsl.filter(User.grade.in_([b for b in sales.grade.data]))
        if sales.user.data:
            tsl = tsl.filter(User.id.in_([b for b in sales.user.data]))
        if sales.subscription.data:
            tsl = tsl.filter(Subscription.id.in_([b for b in sales.subscription.data]))
        if sales.coupon.data:
            tsl = tsl.filter(SubscriptionActivity.couponId == Coupon.id).filter(Coupon.id.in_([b for b in sales.coupon.data]))
        if sales.merchantTransId.data:
            tsl = tsl.filter(SubscriptionActivity.merchantTransactionId == sales.merchantTransId.data)
        if sales.transId.data:
            tsl = tsl.filter(SubscriptionActivity.transactionId == sales.transId.data)
        if sales.startDate.data:
            tsl = tsl.filter(SubscriptionActivity.datetime >= sales.startDate.data)
        if sales.endDate.data:
            tsl = tsl.filter(SubscriptionActivity.datetime <= sales.endDate.data)
        tsl = tsl.order_by(-SubscriptionActivity.id).all()
        sl = []
        for row in tsl:
            rsl = []
            summary["Raju's worth"] += row[3]
            for i, col in enumerate(row):
                if row[i] is not None:
                    if i == 4:
                        col = Coupon.query.filter_by(id=SubscriptionActivity.couponId).first().code
                    rsl.append(str(col))
                else:
                    rsl.append('')
            sl.append(rsl)

        if sales.export.data:
            data = OrderedDict()
            data.update({"Sheet 1": [sh]+sl})
            save_data("src/salesReport.ods", data)
            return send_file('salesReport.ods', as_attachment=True)

    if summary["Raju's worth"] >= 10000:
        summary['important notice'] = "raju is rich"
    return render_template('sales.html', error='success', sales=sales, sh=sh, sl=sl, summary=summary, s=session)


def calculateAnalyticsHomeScorePercentages(userIds, subjectIds, startDate, endDate, score_percentage_threshold):
    countUsers = db.session.query(func.count(UserTest.id)).filter(UserTest.score * 100 / UserTest.scoreTotal >= score_percentage_threshold).\
    filter(UserTest.dateTime.between(startDate, endDate)).filter(UserTest.userId.in_(userIds))
    if subjectIds:
        countUsers = countUsers.filter(or_(UserTest.customSubjectId.in_(subjectIds), \
        and_(UserTest.customSubjectId.is_(None), UserTest.testId == Test.id, Test.subjectId.in_(subjectIds))))
    # print('+',countUsers.all())
    return countUsers.scalar()


@app.route('/calculateStudentsPerformance', methods=['POST'])
def calculateStudentsPerformance():
    data = request.get_json()
    userIds = data.get('userIds')
    if not userIds:
        return jsonify({'performance':[0,0,0]})
    userIds = [int(id) for id in userIds.split(',')]
    subjectIds = data.get('subjectIds')
    startDate = data.get('startDate')
    endDate = data.get('endDate')
    groupBy = data.get('groupBy')
    type = data.get('type')
    startDate = datetime.datetime.strptime(startDate, '%m/%d/%Y').strftime('%Y-%m-%d')
    endDate = datetime.datetime.strptime(endDate, '%m/%d/%Y').strftime('%Y-%m-%d')

    confidence = case(((type == 'confidence'), func.avg(UserTest.confidence)),else_=None)
    accuracy = case(((type == 'accuracy'), func.avg(UserTest.accuracy)),else_=None)
    performance = case(((type == 'performance'), func.avg(UserTest.score*100//UserTest.scoreTotal)),else_=None)
    persistance = case(((type == 'persistance'), func.sum(UserTest.customTestLevelIds)),else_=None)
    count = case(((type == 'count'), func.count(UserTest.id)),else_=None)
    index = {'confidence':1, 'accuracy':2, 'performance':3, 'persistance':4, 'count':5}

    if startDate != endDate:
        countUserTests = db.session.query(func.date_format(UserTest.dateTime, '%d/%m'),func.coalesce(confidence,0), func.coalesce(accuracy,0), \
        func.coalesce(performance,0), func.coalesce(persistance,0), func.coalesce(count,0))
    else:
        countUserTests = db.session.query(func.hour(UserTest.dateTime),func.coalesce(confidence,0), func.coalesce(accuracy,0), \
        func.coalesce(performance,0), func.coalesce(persistance,0), func.coalesce(count,0))
    countUserTests = countUserTests.filter(UserTest.dateTime.between(startDate, endDate)).filter(UserTest.progress == 100).\
    join(User, or_(*[UserTest.userId == id for id in userIds]))

    if type == 'persistance':
        countUserTests = countUserTests.filter(UserTest.practiceTest == True)

    if groupBy == 'questionFormat':
        countUserTests = countUserTests.outerjoin(UserQuestionTest, UserTest.id == UserQuestionTest.userTestId) \
        .outerjoin(Question, UserQuestionTest.questionId == Question.id) \

    if startDate != endDate:
        if groupBy == 'gender':
            countUserTests = countUserTests.group_by(func.date_format(UserTest.dateTime, '%d/%m'), User.gender).all()
            sendList = [['time', "male", "female"]]
            i=0
            while i < len(countUserTests):
                sendList.append([countUserTests[i][0].strftime('%d-%m'), int(float(countUserTests[i][index[type]])), int(float(countUserTests[i+1][index[type]]))])
                i+=2
            else:
                sendList.append([startDate, 0, 0])
            print(sendList)
            return jsonify({'performance':sendList})
        elif groupBy == 'grades':
            countUserTests = countUserTests.group_by(func.date_format(UserTest.dateTime, '%d/%m'), User.grade).all()
        elif groupBy == 'questionFormat':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), Question.format).all()
        elif groupBy == 'questionLevel':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), Question.difficultyLevel).all()
        else:
            countUserTests = countUserTests.group_by(func.date_format(UserTest.dateTime, '%d/%m')).all()
    else:
        if groupBy == 'gender':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), User.gender).all()
            sendList = [['time', "male", "female"]]
            i=0
            while i < len(countUserTests):
                sendList.append([countUserTests[i][0], int(float(countUserTests[i][index[type]])), int(float(countUserTests[i+1][index[type]]))])
                i+=2
            else:
                sendList.append([startDate, 0, 0])
            print(sendList)
            return jsonify({'performance':sendList})
        elif groupBy == 'grades':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), User.grade).all()
        elif groupBy == 'questionFormat':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), Question.format).all()
        elif groupBy == 'questionLevel':
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime), Question.difficultyLevel).all()
        else:
            countUserTests = countUserTests.group_by(func.hour(UserTest.dateTime)).all()

    # ERROR-if either gender has no rows on a date/hour, results might get mixed
    print(type, [['time', type], [[userTest[0], int(float(userTest[index[type]]))]\
    for i, userTest in enumerate(countUserTests)][0] if countUserTests else [startDate, 0]])
    return jsonify({'performance':[['time', type], [[userTest[0], int(float(userTest[index[type]]))]\
    for i, userTest in enumerate(countUserTests)][0] if countUserTests else [startDate, 0]]})


@app.route('/dashboard.html', methods=['POST', 'GET'])
def dashboard():
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    startDate, endDate = getDates('This Week')
    result = {
        'isAdmin':False,
        'school':None,
        'isOrgHead':True,
        'error':None,
        'instructorId':None,
        'tuition':False,
        'schoolSel': [],
        'boardSel': [],
        'gradeSel': [],
        'sectionSel': [],
        'subjectSel': [],
        'boardGradeSectionSubjectPairSel': [],
        'chapterSel': [],
        'conceptSel': [],
        'dashboardUserTests':False,
        'dashboardAddUser':False,
        'dashboardStudent':False,
        'dashboard':True,
        'startDateSel': startDate.strftime('%m/%d/%Y'),
        'endDateSel': endDate.strftime('%m/%d/%Y')
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('add-user.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
        if instructorData.createdBy:
            result['isOrgHead'] = False


    result['name'] = instructorData.name
    result['email'] = instructorData.email

    response = requests.post('http://localhost:5000/getDashboardUserTests', data=json.dumps({
        'result':result,
        }),headers = {'Content-Type': 'application/json'})
    result = response.json()

    return render_template('dashboard.html', result=result, s=session, error='')

    # if result['dashboard']:
    #     pass
    #     # result['graphStudentPerformanceTests'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, None, 'count')
    #     # result['graphStudentPerformancePerformance'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, None, 'performance')
    #     # result['graphStudentPerformanceAccuracy'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, None, 'accuracy')
    #     # result['graphStudentPerformanceConfidence'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, None, 'confidence')
    #     # result['graphStudentPerformancePersistance'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, None, 'persistance')

    #     # result['graphBoysVsGirlsTests'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, 'gender', 'count')
    #     # result['graphBoysVsGirlsPerformance'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, 'gender', 'performance')
    #     # result['graphBoysVsGirlsAccuracy'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, 'gender', 'accuracy')
    #     # result['graphBoysVsGirlsConfidence'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, 'gender', 'confidence')
    #     # result['graphBoysVsGirlsPersistance'] = calculateStudentsPerformance(userIds, subjects, startDateSel, endDateSel, 'gender', 'persistance')




@app.route('/studentResults/<userId>/<startDate>/<endDate>', methods=['POST', 'GET'])
def studentResults(userId, startDate, endDate):
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    result = {
        'userId':userId,
        'startDate':startDate,
        'endDate':endDate,
        'isOrgHead':True,
        'isAdmin':False,
        'school':None
    }

    startDate = datetime.datetime.strptime(startDate, '%m-%d-%Y').strftime('%Y-%m-%d')
    endDate = datetime.datetime.strptime(endDate, '%m-%d-%Y').strftime('%Y-%m-%d')

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorData)
            return render_template('tests.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
            schoolData, errorCode = getSchool({'id':result['school']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolData)
                result['error'] = schoolData
                return jsonify(result)

        else:
            result['isOrgHead'] = False

        if instructorData.createdBy:
            result['isOrgHead'] = False

    result['name'] = instructorData.name
    result['email'] = instructorData.email

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+userData)
        return render_template('studentResults.html', result=result, s=session, error=userData)

    result['name'] = userData.firstname+ ' ' + userData.lastname

    userTestsData, errorCode = getAllUserTests({'userId':userData.id, 'startEnd':[startDate, endDate]})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+userTestsData)
        return render_template('studentResults.html', result=result, s=session, error=userTestsData)

    result['testTaken'] = len(userTestsData)

    gradeData, errorCode = getGrade({'id':userData.grade})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+gradeData)
        return render_template('studentResults.html', result=result, s=session, error=gradeData)

    result['grade'] = gradeData.grade

    boardData, errorCode = getBoard({'id':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boardData)
        return render_template('studentResults.html', result=result, s=session, error=boardData)

    result['board'] = boardData.name

    subscriptionActivityData, errorCode = getSubscriptionActivity({'userId':userData.id, 'active':True})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+subscriptionActivityData)
        return render_template('studentResults.html', result=result, s=session, error=subscriptionActivityData)

    result['testsRemaining'] = subscriptionActivityData.testsRemaining

    subscriptionData, errorCode = getSubscription({'id':subscriptionActivityData.subsId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+subscriptionData)
        return render_template('studentResults.html', result=result, s=session, error=subscriptionData)

    result['subscriptionName'] = subscriptionData.name

    print(' Student Results===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ')
    for key, value in result.items():
        print(key, value)
    return render_template('studentResults.html', result=result, s=session, error='')

@app.route('/history/<userId>', methods=['POST', 'GET'])
def history(userId):
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    startDate, endDate = getDates('This Week')

    result = {
        'instructorId':session['instructorId'] if 'instructorId' in session.keys() else session['adminId'],
        'userId':int(userId),
        'isOrgHead':True,
        'isAdmin':False,
        'school':None,
        'parent':False,
        'startDate':startDate.strftime('%m-%d-%Y'),
        'endDate':endDate.strftime('%m-%d-%Y'),
        'test':[]
    }

    data = {
        'userId':int(userId),
        'startDate':startDate.strftime('%m/%d/%Y'),
        'endDate':endDate.strftime('%m/%d/%Y'),
        'search': ''
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorData)
            return render_template('tests.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
            schoolData, errorCode = getSchool({'id':result['school']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolData)
                result['error'] = schoolData
                return jsonify(result)

        else:
            result['isOrgHead'] = False
            result['parent'] = True

        if instructorData.createdBy:
            result['isOrgHead'] = False

    result['name'] = instructorData.name
    result['email'] = instructorData.email

    response = requests.post('http://localhost:5000/ftestHistory', data=json.dumps({
        'data':data,
        }),headers = {'Content-Type': 'application/json'})
    data = response.json()

    result['data'] = data
    print(' Student History===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ')
    for key, value in result.items():
        print(key, value)

    return render_template('history.html', result=result, s=session, error='')


@app.route('/student.html', methods=['POST', 'GET'])
def student():
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    startDate, endDate = getDates('This Week')
    print(startDate, endDate,'21211212')
    result = {
        'isAdmin':False,
        'school':None,
        'isOrgHead':True,
        'error':None,
        'instructorId':None,
        'tuition':False,
        'schoolSel': [],
        'boardSel': [],
        'gradeSel': [],
        'sectionSel': [],
        'subjectSel': [],
        'boardGradeSectionSubjectPairSel': [],
        'chapterSel': [],
        'conceptSel': [],
        'dashboardUserTests':False,
        'dashboardAddUser':False,
        'dashboardStudent':True,
        'dashboard':False,
        'startDateSel': startDate.strftime('%m/%d/%Y'),
        'endDateSel': endDate.strftime('%m/%d/%Y')
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('add-user.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
        if instructorData.createdBy:
            result['isOrgHead'] = False


    result['name'] = instructorData.name
    result['email'] = instructorData.email

    response = requests.post('http://localhost:5000/getDashboardUserTests', data=json.dumps({
        'result':result,
        }),headers = {'Content-Type': 'application/json'})
    result = response.json()
    
    return render_template('student.html', result=result,s=session, error='')


@app.route('/getDashboardUserTests', methods=['POST'])
def getDashboardUserTests():
    data = request.get_json()
    result = data.get('result')

    startDateSel = datetime.datetime.strptime(result['startDateSel'], '%m/%d/%Y').strftime('%Y-%m-%d')
    endDateSel = datetime.datetime.strptime(result['endDateSel'], '%m/%d/%Y').strftime('%Y-%m-%d')
    isOrgHead = result['isOrgHead']
    usersInputData, testsInputData, subjectsInputData, chaptersInputData = {}, {}, {}, {}
    instructorsInputData = {}
    if isOrgHead:
        if result['isAdmin']:
            schoolsData, errorCode = getAllSchools({})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolsData)
                result['error'] = schoolsData
                return jsonify(result)

            result['schools'] = schoolsData
            schools =  [school for school in result['schoolSel']]
            if not schools:
                schools =  [school['id'] for school in schoolsData]
            usersInputData['schools'] = schools
            instructorsInputData['schools'] = schools
        else:
            usersInputData['school'] = result['school']
            instructorsInputData['school'] = result['school']
            schoolData, errorCode = getSchool({'id':result['school']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolData)
                result['error'] = schoolData
                return jsonify(result)

            result['tuition'] = schoolData.tuition

        boardsData, errorCode = getAllBoards({})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boardsData)
            result['error'] = boardsData
            return jsonify(result)

        result['boards'] = [[board['id'], board['board']] for board in boardsData]
        boards =  [board for board in result['boardSel']]
        if not boards:
            boards =  [board['id'] for board in boardsData]
        usersInputData['boards'] = boards
        subjectsInputData['boards'] = boards

        gradesData, errorCode = getAllGrades({})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+gradesData)
            result['error'] = gradesData
            return jsonify(result)

        result['grades'] = [[grade['id'], grade['grade']] for grade in gradesData]
        grades =  [grade for grade in result['gradeSel']]
        if not grades:
            grades =  [grade['id'] for grade in gradesData]
        usersInputData['grades'] = grades
        subjectsInputData['grades'] = grades

        subjectsData, errorCode = getAllSubjects(subjectsInputData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+subjectsData)
            result['error'] = subjectsData
            return jsonify(result)

        result['subjects'] = {subject['id']: subject['name'] for subject in subjectsData}
        subjects = [subject for subject in result['subjectSel']]
        if not subjects:
            subjects = [subject['id'] for subject in subjectsData]
        chaptersInputData['subjectIds'] = subjects

        result['sections'] = [section for section in 'A,B,C,D,E'.split(',')]
        sections =  [section for section in result['sectionSel']]
        if not sections:
            sections = 'A,B,C,D,E'.split(',')
        usersInputData['sections'] = sections

    else:
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorData)
            result['error'] = instructorData
            return jsonify(result)

        instructorAssignmentsData, errorCode = getAllInstructorAssignments({'instructorId':instructorData.id})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorAssignmentsData)
            result['error'] = instructorAssignmentsData
            return jsonify(result)
        elif errorCode == 404:
            instructorAssignmentsData = []

        subjectsActual, boardGradeSectionPairActual, result['boardGradeSectionSubjectPair'] = [], [], {}
        for bGSSP in instructorAssignmentsData:
            boardData, errorCode = getBoard({'id':bGSSP.board})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boardData)
                result['error'] = boardData
                return jsonify(result)

            gradeData, errorCode = getGrade({'id':bGSSP.grade})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+gradeData)
                result['error'] = gradeData
                return jsonify(result)

            subjectData, errorCode = getSubject({'id':bGSSP.subject})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+subjectData)
                result['error'] = subjectData
                return jsonify(result)

            result['boardGradeSectionSubjectPair'] = {bGSSP.id: str(boardData.name)+'-'+str(gradeData.grade)+\
            '-'+str(bGSSP.section)+'-'+str(subjectData.name)}
            boardGradeSectionPairActual.append([bGSSP.board, bGSSP.grade, bGSSP.section])
            subjectsActual.append([bGSSP.subject])

        subjects, boardGradeSectionPair = [], []
        if result['boardGradeSectionSubjectPairSel']:
            instructorAssignmentsData, errorCode = getAllInstructorAssignments({'ids':result['boardGradeSectionSubjectPairSel']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorAssignmentsData)
                result['error'] = instructorAssignmentsData
                return jsonify(result)

            for insAss in instructorAssignmentsData:
                subjects.append(insAss.subject)
                boardGradeSectionPair.append([insAss.board, insAss.grade , insAss.section])

        if not boardGradeSectionPair:
            subjects = subjectsActual
            boardGradeSectionPair = boardGradeSectionPairActual
        usersInputData['boardGradeSectionPair'] = boardGradeSectionPair
        chaptersInputData['subjectIds'] = subjects

    if result['dashboardAddUser'] or result['dashboardUserTests']:
        instructorTestSchedulingInputData = {
            'startEnd':[startDateSel, endDateSel]
        }
        if isOrgHead:
            instructorsData, errorCode = getAllInstructors(instructorsInputData)
            if errorCode == 404:
                instructorsData = []
            elif errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorsData)
                result['error'] = instructorsData
                return jsonify(result)

            instructorTestSchedulingInputData['instructorIds'] = [instructor['id'] for instructor in instructorsData]
        else:
            instructorTestSchedulingInputData['instructorId'] = instructorData.id



    if result['dashboardAddUser']:
        result['instructors'] = []
        for instructor in instructorsData:
            if instructor['email'] != result['email']:
                result['instructors'].append([instructor['id'], instructor['name']])
        count = 1
        result['assignedList'] = []
        for i, instructor in enumerate(instructorsData):
            instructorAssignmentsData, errorCode = getAllInstructorAssignments({'instructorId':instructor['id'], \
            'boards':boards, 'grades':grades, 'sections':sections, 'subjects':subjects})
            if errorCode == 200:
                for insAss in instructorAssignmentsData:
                    boardData, errorCode = getBoard({'id':insAss.board})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boardData)
                        result['error'] = boardData
                        return jsonify(result)

                    gradeData, errorCode = getGrade({'id':insAss.grade})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+gradeData)
                        result['error'] = gradeData
                        return jsonify(result)

                    subjectData, errorCode = getSubject({'id':insAss.subject})
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+subjectData)
                        result['error'] = subjectData
                        return jsonify(result)

                    result['assignedList'].append({
                        'id':instructor['id'],
                        'bGSSId':insAss.id,
                        'count': count,
                        'datetime':instructor['datetime'],
                        'name':instructor['name'],
                        'email':instructor['email'],
                        'password':instructor['password'],
                        'assigned': str(boardData.name)+'-'+str(gradeData.grade)+'-'+str(insAss.section)+'-'+str(subjectData.name),
                        'userLevel': 'Teacher'
                    })
                    count += 1

            elif errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorAssignmentsData)
                result['error'] = instructorAssignmentsData
                return jsonify(result)

    if result['dashboardUserTests'] or result['dashboardStudent'] or result['dashboard']:
        usersData, errorCode = getAllUsers(usersInputData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+usersData)
            result['error'] = usersData
            return jsonify(result)

        result['usersCount'] = usersCount = len(usersData)
        result['userIds'] = ','.join([str(user['id']) for user in usersData])

    if result['dashboardUserTests']:
        chaptersData, errorCode = getAllChapters(chaptersInputData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+chaptersData)
            result['error'] = chaptersData
            return jsonify(result)

        result['chapters'] = {chapter['id']: chapter['name'] for chapter in chaptersData}
        chapters = [chapter for chapter in result['chapterSel']]
        if not chapters:
            chapters = [chapter['id'] for chapter in chaptersData]
        chaptersInputData['chapters'] = chapters

        conceptsData, errorCode = getAllConcepts({'chapterIds':chapters})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+conceptsData)
            result['error'] = conceptsData
            return jsonify(result)

        result['concepts'] = {concept['id']: concept['name'] for concept in conceptsData}
        concepts = [concept for concept in result['conceptSel']]
        if not concepts:
            concepts = [concept['id'] for concept in conceptsData]

        testsData, errorCode = getAllTests({'conceptIds': concepts})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+testsData)
            result['error'] = testsData
            return jsonify(result)

        result['tests'] = {test['id']: test['name'] for test in testsData}


        result['testCount'] = 0
        result['testList'] = []
        instructorTestSchedulingsData, errorCode = getAllInstructorTestSchedulings(instructorTestSchedulingInputData)
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+instructorTestSchedulingsData)
            result['error'] = instructorTestSchedulingsData
            return jsonify(result)

        elif errorCode == 200:
            curDateTime = datetime.datetime.strptime(datetime.datetime.now(indianTime).strftime('%d/%m/%y %H:%M'), '%d/%m/%y %H:%M')
            result['userIds'] = [user['id'] for user in usersData]
            for i, iTS in enumerate(instructorTestSchedulingsData):
                testData, errorCode = getTest({'id': iTS.testId})
                if errorCode == 500:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+testsData)
                    result['error'] = testsData
                    return jsonify(result)

                conceptData, errorCode = getConcept({'id':testData.conceptId})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+conceptData)
                    result['error'] = conceptData
                    return jsonify(result)

                startTimeStr = instructorTestSchedulingsData[i].startTime.strftime('%d/%m/%y %H:%M')
                endTimeStr = instructorTestSchedulingsData[i].endTime.strftime('%d/%m/%y %H:%M')
                endTime = datetime.datetime.strptime(endTimeStr, '%d/%m/%y %H:%M')
                userTestInputData = {'userIds': [user['id'] for user in usersData], 'testId': testData.id,\
                'startEnd':[startDateSel, endDateSel]}

                result['testList'].append({
                    'id':iTS.id,
                    'count': i+1,
                    'testId': testData.id,
                    'date': startTimeStr,
                    'end': endTimeStr,
                    'name': testData.name,
                    'conceptName': conceptData.name,
                    'Test_Category':'Concept Based',
                    'performance': [0,0,0,'grey'],
                    'attendance': [0,0,0],
                    'action': 'results' if endTime < curDateTime else 'delete'
                })
                if result['testList'][i]['action'] == 'results':
                    userTestsData, errorCode = getAllUserTests(userTestInputData)
                    if errorCode != 200:
                        app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+userTestsData)
                        result['error'] = userTestsData
                        return jsonify(result)

                    for userTest in userTestsData:
                        result['testList'][i]['performance'][0] += userTest['score']
                        result['testList'][i]['performance'][1] += userTest['scoreTotal']

                    result['testList'][i]['performance'][2] = result['testList'][i]['performance'][0]*100//result['testList'][i]['performance'][1] if result['testList'][i]['performance'][1] else 0
                    result['testList'][i]['performance'][0] = result['testList'][i]['performance'][0]//len(userTestsData) if len(userTestsData) and result['testList'][i]['performance'][0] > 0 else 0
                    result['testList'][i]['performance'][1] = result['testList'][i]['performance'][1]//len(userTestsData) if len(userTestsData) else 0
                    result['testList'][i]['performance'][2] = result['testList'][i]['performance'][0]*100//result['testList'][i]['performance'][1] if result['testList'][i]['performance'][1] else 0
                    result['testList'][i]['attendance'][0] = len(userTestsData)
                    result['testList'][i]['attendance'][1] = len(usersData)
                    result['testList'][i]['attendance'][2] = result['testList'][i]['attendance'][0] * 100//result['testList'][i]['attendance'][1] if result['testList'][i]['attendance'][1] else 0
            result['testCount'] = len(result['testList'])

    if result['dashboardUserTests'] or result['dashboardStudent'] or result['dashboard']:
        usersInputData['gender'] = 'male'
        boysData, errorCode = getAllUsers(usersInputData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boysData)
            return jsonify(error=boysData)

        boysIds = [boy['id'] for boy in boysData]
        boysCount = len(boysData)

        usersInputData['gender'] = 'female'
        girlsData, errorCode = getAllUsers(usersInputData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+girlsData)
            return jsonify(error=girlsData)

        girlsIds = [girl['id'] for girl in girlsData]
        girlsCount = len(girlsData)

        result['excellentStudents'] = [calculateAnalyticsHomeScorePercentages([user['id'] for user in usersData], subjects, \
        startDateSel, endDateSel, 80), 0, 0]
        result['excellentStudents'][1]  = usersCount
        result['excellentStudents'][2] = (result['excellentStudents'][0]*100 // usersCount) if usersCount else 0
        result['dullStudents'] = [usersCount-result['excellentStudents'][0], usersCount, 100-result['excellentStudents'][2]]
        result['goodStudents'] = [calculateAnalyticsHomeScorePercentages([user['id'] for user in usersData], subjects, startDateSel, endDateSel, 60), 0, 0]
        result['goodStudents'][1]  = usersCount
        result['goodStudents'][2] = (result['goodStudents'][0]*100 // usersCount) if usersCount else 0
        result['averageStudents'] = [calculateAnalyticsHomeScorePercentages([user['id'] for user in usersData], subjects, startDateSel, endDateSel, 40), 0, 0]
        result['averageStudents'][1]  = usersCount
        result['averageStudents'][2] = (result['averageStudents'][0]*100 // usersCount) if usersCount else 0
        result['boysAvg'] = [calculateAnalyticsHomeScorePercentages(boysIds, subjects, startDateSel, endDateSel, 80), 0, 0]
        result['boysAvg'][1]  = boysCount
        result['boysAvg'][2] = (result['boysAvg'][0]*100 // boysCount) if boysCount else 0
        result['girlsAvg'] = [calculateAnalyticsHomeScorePercentages(girlsIds, subjects, startDateSel, endDateSel, 80), 0, 0]
        result['girlsAvg'][1]  = girlsCount
        result['girlsAvg'][2] = (result['girlsAvg'][0]*100 // girlsCount) if girlsCount else 0


    if result['dashboardStudent']:
        boardsData, errorCode = getAllBoards({})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+boardsData)
            result['error'] = boardsData
            return jsonify(result)

        boardDict = {board['id']:board['board'] for board in boardsData}

        gradesData, errorCode = getAllGrades({})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+gradesData)
            result['error'] = gradesData
            return jsonify(result)

        gradeDict = {grade['id']:grade['grade'] for grade in gradesData}

        result['usersList'] = []
        for i, user in enumerate(usersData):
            userTestResults = db.session.query(func.count(UserTest.id), func.sum(UserTest.score), func.sum(UserTest.scoreTotal)).\
            filter(UserTest.userId==user['id']).all()
            performance = userTestResults[0][1]*100//userTestResults[0][2] if userTestResults[0][2] and userTestResults[0][1] > 0 else 0
            result['usersList'].append({
                'id':user['id'],
                'count':i+1,
                'name': user['firstname']+ ' ' + user['lastname'],
                'gender':user['gender'],
                'grade':gradeDict[user['grade']],
                'board':boardDict[user['board']],
                'section':user['section'],
                'testsTaken':userTestResults[0][0],
                'performance': [userTestResults[0][1] if userTestResults[0][1] and userTestResults[0][1] > 0 else 0, userTestResults[0][2] if userTestResults[0][2] else 0, performance]
            })

    print(' MAIN===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ===== ')
    for key, value in result.items():
        print(key, value)
    return jsonify(result)


# @app.route('/tests/<boards>/<grades>/<subjects>/<chapters>/<startDate>/<endDate>/', methods=['POST', 'GET'])
# def tests(boards, grades, subjects, chapters, startDate, endDate):
@app.route('/tests.html/', methods=['POST', 'GET'])
def tests():
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    startDate, endDate = getDates('This Week')

    result = {
        'isAdmin':False,
        'school':None,
        'isOrgHead':True,
        'error':None,
        'instructorId':None,
        'tuition':False,
        'schoolSel': [],
        'boardSel': [],
        'gradeSel': [],
        'sectionSel': [],
        'subjectSel': [],
        'boardGradeSectionSubjectPairSel': [],
        'chapterSel': [],
        'conceptSel': [],
        'dashboardUserTests': True,
        'dashboardAddUser': False,
        'dashboardStudent':False,
        'dashboard':False,
        'startDateSel': startDate.strftime('%m/%d/%Y'),
        'endDateSel': endDate.strftime('%m/%d/%Y')
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('tests.html', result=result, s=session, error=instructorData)

        result['school'] = instructorData.school
        if instructorData.createdBy:
            result['isOrgHead'] = False

    result['name'] = instructorData.name
    result['email'] = instructorData.email


    response = requests.post('http://localhost:5000/getDashboardUserTests', data=json.dumps({
        'result':result,
        }),headers = {'Content-Type': 'application/json'})
    result = response.json()
    return render_template('tests.html', result=result, s=session, error='')



@app.route('/testResults/<iTSId>/<testId>/<userIds>/<userTestId>', methods=['GET'])
def testResults(iTSId, testId, userIds, userTestId):
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    result = {
        'instructorId':session['instructorId'] if 'instructorId' in session.keys() else session['adminId'],
        'isAdmin':False,
        'isOrgHead':False,
        'school':None,
        'accuracy':0,
        'iTSId':iTSId,
        'userTestId':userTestId,
        'testId':testId,
        'score':0,
        'users':{},
        'format':{},
        'level':{},
        'concept':{},
        'overall':{}
    }

    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('tests.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
            schoolData, errorCode = getSchool({'id':result['school']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolData)
                result['error'] = schoolData
                return jsonify(result)

            result['tuition'] = schoolData.tuition

        if instructorData.createdBy:
            result['isOrgHead'] = False

    result['name'] = instructorData.name
    result['email'] = instructorData.email

    userIds = userIds.split(',')
    iTSData, errorCode = getInstructorTestScheduling({'id':int(iTSId)})
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+iTSData)
        return redirect(url_for('tests'))
    elif errorCode == 404 and userTestId:
        userTestsData, errorCode = getAllUserTests({'ids':[int(userTestId)]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+userTestsData)
            return redirect(url_for('tests'))

        result['accuracy'] = userTestsData[0]['accuracy']
        result['score'] = userTestsData[0]['score']*100//userTestsData[0]['scoreTotal']
        result['endDate'] = result['startDate'] = result['dateTime'] = userTestsData[0]['dateTime'].strftime('%m-%d-%Y')
        result['userId'] = userTestsData[0]['userId']
        result['userTestId'] = userTestId
    else:
        userTestsData, errorCode = getAllUserTests({'userIds':userIds, 'testId':testId, 'startEnd':[iTSData.startTime, iTSData.endTime]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+userTestsData)
            return redirect(url_for('tests'))

        result['accuracy'] = int(db.session.query(func.avg(UserTest.accuracy)).filter(UserTest.userId.in_(userIds)).\
        filter(UserTest.testId == testId).filter(UserTest.dateTime.between(iTSData.startTime, iTSData.endTime)).scalar())

        result['score'] = db.session.query(func.avg(UserTest.score*100/UserTest.scoreTotal)).filter(UserTest.userId.in_(userIds)).\
        filter(UserTest.testId == testId).filter(UserTest.dateTime.between(iTSData.startTime, iTSData.endTime)).scalar()

        result['dateTime'] = iTSData.startTime.strftime('%m-%d-%Y')
    # for userTest in userTestsData:
    #     result['accuracy'] += userTest['accuracy']
    #     result['score'] += userTest['score']
    #     result['scoreTotal'] += userTest['scoreTotal']

    result['score'] = result['score'] if int(result['score']) > 0 else 0
    result['performance'] = result['score']

    usersData, errorCode = getAllUsers({'ids':userIds})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+usersData)
        return jsonify(error=usersData)

    for i, user in enumerate(usersData):
        result['users'][user['id']] = {
            'srno':i+1,
            'date':None,
            'name':user['firstname']+ user['lastname'],
            'gender':user['gender'],
            'status':'Not yet Started',
            'performance':[0,0,0],
            'action':False
        }

    testData, errorCode = getTest({'id':testId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+testData)
        return jsonify(error=testData)

    result['overall'] = {
        'name':testData.name,
        'round':0,
        'count':0,
        'time':0,
        'correctTotal':0,
        'incorrectTotal':0,
        'partialTotal':0,
        'notAnsweredTotal':0
        }

    for format in QuestionFormat.query.all():
        result['format'][format.code] = {
            'round':0,
            'count':0,
            'time':0,
            'correctTotal':0,
            'incorrectTotal':0,
            'partialTotal':0,
            'notAnsweredTotal':0
        }

    for level in config2['difficultyLevel'].values():
        result['level'][level] = {
            'round':0,
            'count':0,
            'time':0,
            'correctTotal':0,
            'incorrectTotal':0,
            'partialTotal':0,
            'notAnsweredTotal':0
        }

    for userTest in userTestsData:
        result['users'][userTest['userId']]['date'] = userTest['dateTime']
        result['users'][userTest['userId']]['performance'] = [userTest['score'], userTest['scoreTotal'], \
        userTest['score']*100//userTest['scoreTotal'] if userTest['score'] > 0 and userTest['scoreTotal'] else 0]
        result['users'][userTest['userId']]['status'] = 'Completed' if userTest['progress'] == 100 else 'Paused'
        result['users'][userTest['userId']]['action'] = True

        _, overall, concepts, difficultyLevel, questionFormat = ftestResultsFunc(userTest['id'])

        for format in questionFormat:
            if format['totalQuestions']:
                result['format'][format['format']]['round'] += 1
                result['format'][format['format']]['count'] += format['totalQuestions']
                result['format'][format['format']]['time'] += format['time']
                result['format'][format['format']]['correctTotal'] += format['correctTotal']
                result['format'][format['format']]['incorrectTotal'] += format['incorrectTotal']
                result['format'][format['format']]['partialTotal'] += format['partialTotal']
                result['format'][format['format']]['notAnsweredTotal'] += format['notAnsweredTotal']

        for level in difficultyLevel:
            if level['totalQuestions']:
                result['level'][level['level']]['round'] += 1
                result['level'][level['level']]['count'] += level['totalQuestions']
                result['level'][level['level']]['time'] += level['time']
                result['level'][level['level']]['correctTotal'] += level['correctTotal']
                result['level'][level['level']]['incorrectTotal'] += level['incorrectTotal']
                result['level'][level['level']]['partialTotal'] += level['partialTotal']
                result['level'][level['level']]['notAnsweredTotal'] += level['notAnsweredTotal']

        for concept in concepts:
            if concept['conceptName'] not in result['concept'].keys():
                result['concept'][concept['conceptName']] = {
                    'round':1,
                    'count':concept['totalQuestions'],
                    'time':concept['time'],
                    'correctTotal':concept['correctTotal'],
                    'incorrectTotal':concept['incorrectTotal'],
                    'partialTotal':concept['partialTotal'],
                    'notAnsweredTotal':concept['notAnsweredTotal']
                }
            else:
                result['concept'][concept['conceptName']]['round'] += 1
                result['concept'][concept['conceptName']]['count'] += level['totalQuestions']
                result['concept'][concept['conceptName']]['time'] += level['time']
                result['concept'][concept['conceptName']]['correctTotal'] += level['correctTotal']
                result['concept'][concept['conceptName']]['incorrectTotal'] += level['incorrectTotal']
                result['concept'][concept['conceptName']]['partialTotal'] += level['partialTotal']
                result['concept'][concept['conceptName']]['notAnsweredTotal'] += level['notAnsweredTotal']

        result['overall']['count'] += overall['totalQuestions']
        result['overall']['round'] += 1
        result['overall']['time'] += overall['time']
        result['overall']['correctTotal'] += overall['correctTotal']
        result['overall']['incorrectTotal'] += overall['incorrectTotal']
        result['overall']['partialTotal'] += overall['partialTotal']
        result['overall']['notAnsweredTotal'] += overall['notAnsweredTotal']

    for format in result['format'].keys():
        if result['format'][format]['count']:
            result['format'][format]['time'] = result['format'][format]['time']//result['format'][format]['round'] if result['format'][format]['round'] else 0
            result['format'][format]['correctTotal'] = result['format'][format]['correctTotal']*100//result['format'][format]['count']
            result['format'][format]['incorrectTotal'] = result['format'][format]['incorrectTotal']*100//result['format'][format]['count']
            result['format'][format]['partialTotal'] = result['format'][format]['partialTotal']*100//result['format'][format]['count']
            result['format'][format]['notAnsweredTotal'] = result['format'][format]['notAnsweredTotal']*100//result['format'][format]['count']

    for level in result['level'].keys():
        if result['level'][level]['count']:
            result['level'][level]['time'] = result['level'][level]['time']//result['level'][level]['round'] if result['level'][level]['round'] else 0
            result['level'][level]['correctTotal'] = result['level'][level]['correctTotal']*100//result['level'][level]['count']
            result['level'][level]['incorrectTotal'] = result['level'][level]['incorrectTotal']*100//result['level'][level]['count']
            result['level'][level]['partialTotal'] = result['level'][level]['partialTotal']*100//result['level'][level]['count']
            result['level'][level]['notAnsweredTotal'] = result['level'][level]['notAnsweredTotal']*100//result['level'][level]['count']

    for concept in result['concept'].keys():
        if result['concept'][concept]['count']:
            result['concept'][concept]['time'] = result['concept'][concept]['time']//result['concept'][concept]['round'] if result['concept'][concept]['round'] else 0
            result['concept'][concept]['correctTotal'] = result['concept'][concept]['correctTotal']*100//result['concept'][concept]['count']
            result['concept'][concept]['incorrectTotal'] = result['concept'][concept]['incorrectTotal']*100//result['concept'][concept]['count']
            result['concept'][concept]['partialTotal'] = result['concept'][concept]['partialTotal']*100//result['concept'][concept]['count']
            result['concept'][concept]['notAnsweredTotal'] = result['concept'][concept]['notAnsweredTotal']*100//result['concept'][concept]['count']


    result['overall']['time'] = result['overall']['time']//result['overall']['round']
    result['overall']['correctTotal'] = result['overall']['correctTotal']*100//result['overall']['count']
    result['overall']['incorrectTotal'] = result['overall']['incorrectTotal']*100//result['overall']['count']
    result['overall']['partialTotal'] = result['overall']['partialTotal']*100//result['overall']['count']
    result['overall']['notAnsweredTotal'] = result['overall']['notAnsweredTotal']*100//result['overall']['count']

    print('testResult ========== =========== ============= =================')
    for key, value in result.items():
        print(key, value)
    return render_template('testResults.html', result=result, s=session, error='')


@app.route('/question.html/<iTSId>/<testId>/<userIds>/<userTestId>', methods=['POST', 'GET'])
def question(iTSId, testId, userIds, userTestId):
    if 'adminId' not in session.keys() and 'instructorId' not in session.keys():
        return redirect(url_for('signin'))

    userIds = userIds.split(',')

    testData, errorCode = getTest({'id':testId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+testData)
        return jsonify(error=testData)

    chapterData, errorCode = getChapter({'id':testData.chapterId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+chapterData)
        return jsonify(error=chapterData)

    formatDict = {}
    for format in QuestionFormat.query.all():
        formatDict[format.id] = format.code

    result = {
        'testName':testData.name,
        'testType':'Concept Based',
        'chapter':chapterData.name,
        'question': {}
    }

    iTSData, errorCode = getInstructorTestScheduling({'id':int(iTSId)})
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+iTSData)
        return redirect(url_for('tests'))

    elif errorCode == 404 and userTestId:
        userTestsData, errorCode = getAllUserTests({'ids':[userTestId]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+userTestsData)
            return redirect(url_for('tests'))

        print('=====',userTestsData)
        result['userId'] = userIds[0]
        result['startDate'] = userTestsData[0]['dateTime'].strftime('%m-%d-%Y')
        result['endDate'] = userTestsData[0]['dateTime'].strftime('%m-%d-%Y')

    else:
        userTestsData, errorCode = getAllUserTests({'userIds':userIds, 'testId':testId, 'startEnd':[iTSData.startTime, iTSData.endTime]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+userTestsData)
            return redirect(url_for('tests'))


    if 'adminId' in session.keys():
        instructorData = Admin.query.filter_by(id=session['adminId']).first()
        result['isAdmin'] = True
    else:
        result['instructorId'] = session['instructorId']
        instructorData, errorCode = getInstructor({'id':result['instructorId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(result['instructorId'])+'. error:'+instructorData)
            return render_template('tests.html', result=result, s=session, error=instructorData)

        if instructorData.school:
            result['school'] = instructorData.school
            schoolData, errorCode = getSchool({'id':result['school']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -email:'+ str(result['email'])+'. error:'+schoolData)
                result['error'] = schoolData
                return jsonify(result)

            result['tuition'] = schoolData.tuition

        if instructorData.createdBy:
            result['isOrgHead'] = False

    result['name'] = instructorData.name
    result['email'] = instructorData.email

    questionsData, errorCode = getAllQuestions({'ids':[int(questionId) for questionId in testData.questionIds.split(',')]})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+questionsData)
        return jsonify(error=questionsData)


    for i, question in enumerate(questionsData):
        conceptData, errorCode = getConcept({'id':question['conceptId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+conceptData)
            return jsonify(error=conceptData)

        result['question'][question['id']] = {
            'count':i+1,
            'text':question['text'],
            'format':formatDict[question['format']],
            'level':config2['difficultyLevel'][str(question['difficultyLevel'])],
            'conceptName':conceptData.name,
            'answerExp':question['ansExplanation'],
            'correct':0,
            'incorrect':0,
            'partial':0,
            'notAnswered':0,
            'totalResponses':0,
            'response':None
        }

        if formatDict[question['format']] == 'MCQ' or formatDict[question['format']] == 'MSQ' or formatDict[question['format']] == 'Drag & Drop' or formatDict[question['format']] == 'Sequence':
            questionMcqMsqDadSeqData, errorCode = getQuestionMcqMsqDadSeq({'questionId':question['id']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+questionMcqMsqDadSeqData)
                return jsonify(error=questionMcqMsqDadSeqData)

            # result['question'][question['id']]['questionImagePath'] =  questionMcqMsqDadSeqData.imagePath
            result['question'][question['id']]['choice1'] = questionMcqMsqDadSeqData.choice1
            # result['question'][question['id']]['choice1ImagePath'] = questionMcqMsqDadSeqData.choice1ImagePath
            result['question'][question['id']]['choice2'] = questionMcqMsqDadSeqData.choice2
            # result['question'][question['id']]['choice2ImagePath'] = questionMcqMsqDadSeqData.choice2ImagePath
            result['question'][question['id']]['choice3'] = questionMcqMsqDadSeqData.choice3
            # result['question'][question['id']]['choice3ImagePath'] = questionMcqMsqDadSeqData.choice3ImagePath
            result['question'][question['id']]['choice4'] = questionMcqMsqDadSeqData.choice4
            # result['question'][question['id']]['choice4ImagePath'] = questionMcqMsqDadSeqData.choice4ImagePath
            result['question'][question['id']]['answer'] =  questionMcqMsqDadSeqData.correctChoiceSeq

        elif formatDict[question['format']] == 'Fill' or formatDict[question['format']] == 'True/False':
            questionFillTorFData, errorCode = getQuestionFillTorF({'questionId':question['id']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+questionFillTorFData)
                return jsonify(error=questionFillTorFData)

            # result['question'][question['id']]['questionImagePath'] = questionFillTorFData.imagePath
            result['question'][question['id']]['answer'] = questionFillTorFData.correctAnswer


        for userTest in userTestsData:
            result['question'][question['id']]['totalResponses'] += 1
            userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':userTest['id'], 'questionId':question['id']})
            if errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -instructorId:'+ str(session['instructorId'])+'. error:'+userQuestionTestsData)
                return jsonify(error=userQuestionTestsData)
            elif errorCode == 200:
                if userQuestionTestData.isCorrect:
                    result['question'][question['id']]['correct'] += 1
                elif userQuestionTestData.isPartial:
                    result['question'][question['id']]['partial'] += 1
                elif userQuestionTestData.marks < 0:
                    result['question'][question['id']]['incorrect'] += 1
                    if len(userTestsData) == 1:
                        result['question'][question['id']]['response'] = userQuestionTestData.answer
                else:
                    result['question'][question['id']]['notAnswered'] += 1
            elif errorCode == 404:
                result['question'][question['id']]['notAnswered'] += 1


        if not len(userTestsData):
            result['question'][question['id']]['notAnswered'] = 100
            result['question'][question['id']]['totalResponses'] = 100


    print('questions ========== =========== ============= =================')
    for key, value in result.items():
        print(key, value)
    return render_template('question.html', result=result, s=session, error="")



@app.route('/scheduleTest', methods=['POST', 'GET'])
def scheduleTest():
    data = request.get_json()

    email = data.get('email')
    startDateSel = data.get('startDateSel')
    endDateSel = data.get('endDateSel')
    testSel = data.get('testSel')
    startDateSel = datetime.datetime.strptime(startDateSel, '%d/%m/%y %H:%M')
    endDateSel = datetime.datetime.strptime(endDateSel, '%d/%m/%y %H:%M')
    app.logger.debug(inspect.currentframe().f_code.co_name+ ' -email:'+email+ ' -startDate:'+str(startDateSel)+ ' -endDate:'+str(endDateSel)+' -testId:'+str(testSel))

    instructorData, errorCode = getInstructor({'email':email})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+'. error:'+instructorData)
        return jsonify({'error':instructorData})

    instructorTestScheduling = InstructorTestScheduling(instructorData.id, testSel[0], startDateSel, endDateSel, datetime.datetime.now(indianTime))
    instructorTestSchedulingId, errorCode = insertInstructorTestScheduling(instructorTestScheduling)
    if errorCode != 201:
        app.logger.debug(inspect.currentframe().f_code.co_name+ ' -email:'+email +'. error:'+str(instructorTestSchedulingId))
        return jsonify({'error':str(instructorTestSchedulingId)})

    return jsonify({'error':'success'})


@app.route('/deleteTest', methods=['POST', 'GET'])
def deleteTest():
    data = request.get_json()

    instructorTestId = data.get('instructorTestId')
    app.logger.debug(inspect.currentframe().f_code.co_name+ ' -instructorTestId:'+str(instructorTestId))

    error, errorCode = deleteInstructorScheduling({'id':instructorTestId})
    if errorCode != 204:
        return jsonify({'error':error})

    return jsonify({'error':'success'})



@app.route('/logs1')
def logs1():
    def generate():
        with open('/var/log/syslog') as f:
            # while True:
            yield f.read()
            # time.sleep(1)

    return app.response_class(generate(), mimetype='text/plain')

@app.route('/logs2')
def logs2():
    def generate():
        with open('debug.log') as f:
            # while True:
            yield f.read()
            # time.sleep(1)

    return app.response_class(generate(), mimetype='text/plain')

@app.route('/paymentphonepe/', methods=['GET', 'POST'])
def paymentphonepe():
    string = '''
    <html>
    <head>
    <style>
    body, html {
      height: 100%;
      margin: 0;
    }
    .container {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      font-size: 30px;
    }
    </style>
    </head>
    <body>
        <div class="container">
        <p>Hang on tight, you will be redirected to app</p>
    </div>
    </body>
    </html>
    '''
    return render_template_string(string)

@app.route('/logout')
def logout():
    try:
        session.pop('adminAvailable')
        session.pop('adminName')
        session.pop('adminId')
    except Exception:
        pass
    session.clear()
    print('sads')
    return redirect(url_for('signin'))
