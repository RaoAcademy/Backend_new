from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from . models import User, School, Avatar, Admin, Roles, Grade, Board, Subject, Concept, Question,\
QuestionFormat, QuestionMcqMsqDadSeq, QuestionFillTorF, QuestionMatch, Concept,\
Banner, UserQuestionTest, UserQuestion, UserTest, Test, TestCategory, Chapter, SubscriptionActivity,\
Subscription, Coupon, UserCoupon, ReferralActivity, Badges, UserBadges, FAQs, AppVersion, LoginActivity,\
Inits, SplashScreen, Notifications, Analysis, UserConcept
from . dbOps import getGrade, getAllGrades, getBoard, getAllBoards, getSchool, insertSchool,\
getAvatar, getAllAvatars, getUser, updateUser, getSubscription, getAllSubscriptionActivity, insertSubscriptionActivity, \
updateSubscriptionActivity, insertReferralActivity, insertUserBadge, \
getInits, insertInits, updateInits, getSubject, getAllSubjects, getUserTest, getAllUserTests, updateUserTest, insertUserTest, getTest, \
getAllTestsByIds, getAllTests, getAllUserQuestions, getQuestion,\
getAllQuestions, getConcept, getAllConcepts, getQuestionFormat, getAllQuestionFormats, getAnalysis, updateAnalysis, getAllUserConcepts, getChapter,\
getAllChapters, getAllTestCategories, getAllFaqs, getUserQuestionTest, getAllUserQuestionTests, deleteAllUserQuestionTests, \
updateUserQuestionTest, insertUserQuestionTest, getQuestionMcqMsqDadSeq, getQuestionFillTorF, getQuestionMatch
from src import app, db, indianTime
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, extract, and_, or_
import json, ast
from dateutil.relativedelta import relativedelta
import time
from dateutil import rrule
import random, string
from collections import OrderedDict
from . FCMManager import sendPush
import logging, inspect
import requests

configFormat = {}
with app.app_context():
    for id, code in db.session.query(QuestionFormat.id, QuestionFormat.code).all():
        configFormat[id] = code
# configCategory =
with open('src/config') as f:
    lines = f.readlines()
config1 = json.loads(lines[0])  #initialNewUserTestRemaining
config2 = json.loads(lines[1])  #difficultyLevel
config3 = json.loads(lines[2])  #coins
config4 = json.loads(lines[3])  #time
config5 = json.loads(lines[4])  #referral
config6 = json.loads(lines[5])  #marks
config7 = json.loads(lines[6])  #praticeTestDescription
config8 = json.loads(lines[7])  #customTestDescription
config9 = json.loads(lines[8])  #Forfarmance
config10 = json.loads(lines[9])  #suscriptionFields
config11 = json.loads(lines[10])  #analyticsThreshold
config12 = json.loads(lines[11])  #progressBadges
config13 = json.loads(lines[12])  #performanceBadges
config14 = json.loads(lines[13])  #reports
# print(config4['time'][config2['difficultyLevel']['1']])


#collections - > lists of strings/dict
#token in header in postman
import jwt
from functools import wraps
def tokenRequired(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print(request.headers['Token'])
        token = request.headers['Token']
        if not token:
            return jsonify({'alert':'token missing'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            return jsonify(payload)
        except:
            return jsonify({'alert':'invalid token'})
        return decorated
    return decorated


# @app.route('/fnotification/', methods=['POST'])
def fnotification(msg, desc, imagePath, userId, dataObject=None):
    # uId = 31
    # msg = "hi"
    # desc = None
    # imagePath = None
    # print(msg, desc, imagePath, uId, dataObject)
    initsData, errorCode = getInits({'userId':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+initsData)
        return jsonify({'error':initsData}), errorCode

    try:
        sendPush(msg, desc, imagePath, [initsData.fcmToken], dataObject)
        #,{'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'ftestHome', 'userId':'22', 'subjectId':'2'}
        # return jsonify({})
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(initsData.userId)+'. relogin message issued (maybe FCM TOKEN MISSING). error:'+initsData)
        return 'relogin'
    return None


def calExpiryDate(months):
    date = datetime.datetime.strptime(datetime.datetime.now(indianTime).strftime('%Y-%m-%d'), '%Y-%m-%d')
    date += relativedelta(months=months)
    return date


def addStudent(firstname, lastname, gender, dob, board, grade, school, mobile, peerReferral, parentName, parentMobile, city, lastYearResults, fcmToken=None):
    referral = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))    #todo change this to seed mobile

    avatarData, errorCode = getAvatar({'gender':gender})
    if errorCode != 200:
        return avatarData, errorCode

    if peerReferral:
        peerUserData, errorCode = getUser({'peerReferral':peerReferral})
        if errorCode != 200:
            return peerUserData, errorCode

    #free trial
    subscriptionData, errorCode = getSubscription({'id':1})
    if errorCode != 200:
        return subscriptionData, errorCode
    testsRemaining = subscriptionData.numberOfTests
    expiryDate = (calExpiryDate(subscriptionData.validity)).strftime('%Y-%m-%d')

    subjectsData, errorCode = getAllSubjects({'grade':grade, 'board':board})
    if errorCode != 200:
        return subjectData, errorCode

    try:
        user = User(firstname, lastname, gender, dob, None, mobile, grade, None,\
        school, None, board, config1['initialNewUserTestRemaining'], avatarData.id, config5['rewards']['selfCoins'], 1, referral, \
        parentName, parentMobile, city, lastYearResults, datetime.datetime.now(indianTime), 0)
        db.session.add(user)
        db.session.flush()
        userId = user.id

        subscriptionActivity = SubscriptionActivity(userId, 1, 0, None, expiryDate, testsRemaining,\
        True, None, None, None, None, None, datetime.datetime.now(indianTime))
        db.session.add(subscriptionActivity)

        inits = Inits(userId, True, "Your upcoming weekly report will be ready by Monday.", \
        'You will be notified when new tests are added. Finish existing tests', 'Your Free Trial is Active', fcmToken)
        db.session.add(inits)

        userBadges = UserBadges(userId, 1, None, datetime.datetime.now(indianTime))
        db.session.add(userBadges)

        if peerReferral:
            peerReferral = ReferralActivity(peerUserData.id, mobile, datetime.datetime.now(indianTime))
            db.session.add(peerReferral)

        for timeType in ["This week", 'This month', 'This year']:
            db.session.add(Analysis(userId, None, timeType, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
            str([0,0,0,0,0,0]), str([0,0,0,0,0,0,0,0,0,0])))
            for sub in subjectsData:
                db.session.add(Analysis(userId, sub['id'], timeType, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                str([0,0,0,0,0,0]), str([0,0,0,0,0,0,0,0,0,0])))

        db.session.commit()
        return userId, 201
    except Exception as e:
        db.session.rollback()
        return 'failed to add user. error: '+ str(e), 500


def addSchool(name, tuition):
    schoolData, errorCode = getSchool({'name':name})
    if errorCode == 200:
        schoolId = schoolData.id
    elif errorCode == 404:
        school = School(name, None, None, tuition, True, datetime.datetime.now(indianTime))
        schoolId, errorCode = insertSchool(school)
        if errorCode != 201:
            return schoolId, errorCode
    elif errorCode == 500:
        return schoolData, errorCode
    return schoolId, errorCode


@app.route('/fsignup/', methods=['POST'])   #first time user
def fsignup():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    gender = request.form.get('gender') #male, female
    dob = request.form.get('dob')
    board = request.form.get('board')   #boardId
    grade = request.form.get('grade')   #gradeId
    school = request.form.get('school') #schoolName
    mobile = request.form.get('mobile')
    peerReferral = request.form.get('peerReferral') #if given then it is validated or empty
    parentName = request.form.get('parentName')
    parentMobile = request.form.get('parentMobile')
    city = request.form.get('city')
    lastYearResults = request.form.get('lastYearResults')
    fcmToken = request.form.get('fcmToken')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -firstname:'+str(firstname)+' -lastname:'+str(lastname)\
    +' -gender:'+str(gender)+' -dob:'+str(dob)+' -board:'+str(board)+' -grade:'+str(grade)+' -school:'+str(school)\
    +' -mobile:'+str(mobile)+' -peerReferral:'+str(peerReferral)+' -parentName:'+str(parentName)+' -parentMobile:'+str(parentMobile)\
    +' -city:'+str(city)+' -lastYearResults:'+str(lastYearResults)+' -fcmToken:'+str(fcmToken))

    sendObject = {
        'status':1,
        'grades':[],
        'boards':[],
        'Added': False,
        'userId':None,
        'error':None
    }

    gradesData, errorCode = getAllGrades({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+gradesData)
        return jsonify({'error':gradesData}), errorCode

    for g in gradesData:
        sendObject['grades'].append({'id':g['id'],'grade':g['grade']})

    boardsData, errorCode = getAllBoards({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+boardsData)
        return jsonify({'error':boardsData}), errorCode

    for b in boardsData:
        sendObject['boards'].append({'id':b['id'],'board':b['board']})

    if not firstname:
        return jsonify(sendObject), 200

    schoolId, errorCode = addSchool(school, False)
    if errorCode != 200 and errorCode != 201:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+schoolId)
        return jsonify({'error':schoolId}), errorCode

    userId, errorCode = addStudent(firstname, lastname, gender, dob, board, grade, schoolId, mobile, \
    peerReferral, parentName, parentMobile, city, lastYearResults, fcmToken)
    if errorCode != 201:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+userId)
        return jsonify({'error':userId}), errorCode

    # sendObject['token'] = jwt.encode({'userId': userId}, app.config['SECRET_KEY'])
    sendObject['Added'] = True
    sendObject['userId'] = userId
    return jsonify(sendObject), 200


@app.route('/flogin/', methods=['GET', 'POST'])
def flogin():
    mobile = request.form.get('mobile')
    mac = request.form.get('mac') #if device changes then restore ma
    location = request.form.get('location')
    ip = request.form.get('ip')
    fcmToken = request.form.get('fcmToken')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -mobile:'+str(mobile)+' -mac:'+str(mac)\
    +' -location:'+str(location)+' -ip:'+str(ip)+' -fcmToken:'+str(fcmToken))

    sendObject = {
        'status':1,
        'newUser': True,
        'userId': None,
        'error':None,
        'message':None
    }

    userData, errorCode = getUser({'mobile':mobile})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -mobile:'+ str(mobile)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    sendObject['newUser'] = False
    sendObject['userId'] = userData.id

    if userData.status == 0:
        sendObject['message'] = 'your account is not active. contact support'
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(sendObject['userId'])+' . message: user account not active.')
        return jsonify(sendObject), 200

    error, errorCode = updateInits({'userId':userData.id}, {'fcmToken':fcmToken})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(sendObject['userId'])+'. error:'+error)
        return jsonify({'error':error}), errorCode

    #NOT ADDING BELOW TO DBOPS
    loginActivity = db.session.query(LoginActivity).filter_by(userId=userData.id).first()
    # sendObject['token'] = jwt.encode({'userId': user.id}, app.config['SECRET_KEY'])
    if loginActivity:
        loginActivity.deviceInfo = mac
        loginActivity.location = location
        loginActivity.ip = ip
    else:
        db.session.add(LoginActivity(userData.id, mac, location, ip, datetime.datetime.now(indianTime)))
    db.session.commit()
    return jsonify(sendObject), 200


#call this for every 5 mins
@app.route('/fuserActive/', methods=['POST'])
def fuserActive():  #user has logged in to andriod app
    userId = request.form.get('userId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))

    #NOT ADDING BELOW TO DBOPS
    loginActivity = db.session.query(LoginActivity).filter(LoginActivity.userId == userId).\
    order_by(-LoginActivity.id).first()
    if loginActivity and datetime.datetime.now(indianTime).date() - loginActivity.dateTime != datetime.timedelta(0):
        loginActivity.dateTime = datetime.datetime.now(indianTime)
        db.session.commit()
    user = db.session.query(User).filter(User.id == userId).first()
    user.hours += 5
    db.session.commit()
    return jsonify({'status':1}), 200


@app.route('/fvalidateReferral/', methods=['POST'])
def fvalidateReferral():
    referral = request.form.get('referral')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -referral:'+str(referral))

    sendObject = {
        'status':1,
        'valid':False,
        'error': None,
        'ReferrerId': None
    }
    peerUserData, errorCode = getUser({'peerReferral':referral})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+peerUserData)
        return jsonify({'error':peerUserData}), errorCode

    sendObject['valid'] = True
    sendObject['ReferrerId'] = peerUserData.id
    return jsonify(sendObject), 200


@app.route('/fschool/', methods=['POST'])
def fschool():
    school = request.form.get('school')
    tuition = request.form.get('tuition')

    if tuition and tuition.lower() == 'true':
        tuition = True
    else:
        tuition = False

    app.logger.debug(inspect.currentframe().f_code.co_name+' -school:'+str(school)+' -tuition:'+str(tuition))

    sendObject = {
        'error':None,
        'schoolId':None
    }

    schoolId, errorCode = addSchool(school)
    if errorCode != 200 and errorCode != 201:
        app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+schoolId)
        return jsonify({'error':schoolId}), errorCode

    sendObject['schoolId'] = schoolId
    return jsonify(sendObject), 200


@app.route('/favatar/', methods=['POST'])
def favatar():
    userId = request.form.get('userId')
    avatarId = request.form.get('avatarId')
    update = request.form.get('update')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -avatarId:'+str(avatarId)\
    +' -update:'+str(update))

    sendObject = {
        'status':1,
        'updated': False,
        'error':None,
        'avatars':[]
    }

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    avatarsData, errorCode = getAllAvatars({'gender':userData.gender})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+avatarsData)
        return jsonify({'error':avatarsData}), errorCode

    sendObject['avatars'] = avatarsData

    if update:
        avatarData, errorCode = getAvatar({'id':avatarId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+avatarData)
            return jsonify({'error':avatarData}), errorCode

        userUpdateData = {
            'avatarId':avatarId
        }
        error, errorCode = updateUser({'id':userData.id}, userUpdateData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
            return jsonify({'error':error}), errorCode
        sendObject['updated'] = True

    return jsonify(sendObject), 200


@app.route('/fprofile/', methods=['POST'])
def fprofile():
    userId = request.form.get('userId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))

    sendObject = {
        'error':None,
        'status':1,
        'name': None,
        'coins': None,
        'grade': None,
        'avatarImagePath': None,
        'badge': None,
        'defaultSubjectId': None
    }

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    sendObject['name'] =  userData.firstname + ' ' +userData.lastname
    sendObject['coins'] =  userData.coins

    gradeData, errorCode = getGrade({'id':userData.grade})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+gradeData)
        return jsonify({'error':gradeData}), errorCode

    sendObject['grade'] =  gradeData.grade

    avatarData, errorCode = getAvatar({'id':userData.avatarId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+avatarData)
        return jsonify({'error':avatarData}), errorCode

    sendObject['avatarImagePath'] =  avatarData.imagePath

    subjectData, errorCode = getSubject({'grade':userData.grade, 'board':userData.board, 'desc':0})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
        return jsonify({'error':subjectData}), errorCode

    sendObject['defaultSubjectId'] = subjectData.id

    try:
        badge = db.session.query(Badges.imagePath).filter(UserBadges.userId == userId).\
        filter(Badges.id == UserBadges.badgeId).order_by(-UserBadges.id).first()
        if badge:
            sendObject['badge'] = badge[0]
        else:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:No Badge found')
            return jsonify({'error':'No Bagde found for userId '+str(userId)}), 404
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing Badge records, '+str(e))
        return jsonify({'error':'Error in accessing Badge records for userId '+ str(userId)+'. Details:' + str(e)}), 500

    return jsonify(sendObject), 200


@app.route('/fprofileDetailed/', methods=['POST'])
def fprofileDetailed():
    userId = request.form.get('userId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))

    sendObject = {
        'error':None,
        'status':1,
        'avatarImagePath': None,
        'name': None,
        'numberOfTestsTaken':0,
        'numberOfLoopsTaken': 0,
        'numberOfSignedPeople': 0,
        'testsRemaining':0,
        'totalTests':0,
        'profileCompletion': False,
        'badgeActivity': None,
        'badgeActivityUpcoming':None,
        'badgeProgress':None,
        'badgeProgressUpcoming': None,
        'badgePerformance':None,
        'badgePerformanceUpcoming':None
    }

    badgeActivity, badgeProgress1, badgeProgress2, badgePerformance = [], [], [], []
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    sendObject['name'] = userData.firstname
    sendObject['profileCompletion'] = True if userData.parentName and userData.parentMobile and userData.city and userData.lastYearResults \
    else False

    avatarData, errorCode = getAvatar({'id':userData.avatarId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+avatarData)
        return jsonify({'error':avatarData}), errorCode

    sendObject['avatarImagePath'] =  avatarData.imagePath

    testsRemaining, totalTests = 0, 0

    subscriptionActivityData, errorCode = getAllSubscriptionActivity({'userId':userData.id})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionActivityData)
        return jsonify({'error':subscriptionActivityData}), errorCode

    for sA in subscriptionActivityData:
        if sA.expiryDate - datetime.datetime.now(indianTime).date() > datetime.timedelta(0):
            subscriptionData, errorCode = getSubscription({'id':sA.subsId})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionData)
                return jsonify({'error':subscriptionData}), errorCode

            totalTests += subscriptionData.numberOfTests
            testsRemaining += sA.testsRemaining
    sendObject['testsRemaining'] = userData.testsRemaining
    sendObject['totalTests'] = totalTests

    sendObject['numberOfTestsTaken'], errorCode = getAllUserTests({'userId':userId, 'count':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+sendObject['numberOfTestsTaken'])
        return jsonify({'error':sendObject['numberOfTestsTaken']}), errorCode

    try:
        sendObject['numberOfLoopsTaken'] = len(db.session.query(func.count(UserTest.testId)).filter_by(userId=userId).\
        filter(UserTest.target != 0).group_by(UserTest.testId).all())
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing UserTest records, '+str(e))
        return jsonify({'error':'Error in accessing UserTest records for userId '+ str(userId) +'. Details:' + str(e)}), 500
    try:
        sendObject['numberOfSignedPeople'] = ReferralActivity.query.filter_by(userId=userId).count()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing ReferralActivity records'+str(e))
        return jsonify({'error':'Error in accessing ReferralActivity records for userId '+ str(userId) +'. Details:' + str(e)}), 500

    #activity
    try:
        iter = 0
        for badge in db.session.query(Badges.descBefore, Badges.descAfter, Badges.imagePath, UserBadges.achievedDate).\
        filter(Badges.type == 'activity').filter(UserBadges.userId == userId).filter(Badges.id >= UserBadges.badgeId).all():
            badgeActivity.append({
                'imagePath': badge[2],
                'message': badge[1] if iter == 0 else badge[0],
                'date': badge[3] if iter == 0 else None
                })
            iter+=1
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing Activity Badge and UserBadge records,'+str(e))
        return jsonify({'error':'Error in accessing Activity Badge and UserBadge records for userId '+ str(userId)+'. Details:' + str(e)}), 500

    sendObject['badgeActivity'] =  badgeActivity[0]
    sendObject['badgeActivityUpcoming'] = badgeActivity[1:]

    #progress
    try:
        iter = 0
        tempProgressUB = {}
        for uB in UserBadges.query.filter_by(userId=userId).filter(UserBadges.subjectName != None).all():
            badge = Badges.query.filter_by(id=uB.badgeId).first()
            badgeProgress1.append({
                'imagePath': badge.imagePath,
                'message': badge.descAfter if iter == 0 else badge.descBefore,
                'date': uB.achievedDate
            })
            iter+=1
            tempProgressUB[uB.subjectName] = uB.badgeId

        validSubjectNames = [sub.name for sub in Subject.query.filter_by(board=userData.board, grade=userData.grade).all()]

        for badge in db.session.query(Badges.name, Badges.imagePath, Badges.id, Badges.descBefore, Badges.descAfter).\
        filter(Badges.type == 'progress').all():
            subName = badge[0].split('-')[0]
            if subName not in validSubjectNames:
                continue
            if subName not in tempProgressUB.keys() or (subName in tempProgressUB.keys() and tempProgressUB[subName] < badge[2]):
                badgeProgress2.append({
                    'imagePath': badge[1],
                    'message': badge[4] if iter == 0 else badge[3],
                    'date': None
                })
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing Progress and UserBadge records, '+str(e))
        return jsonify({'error':'Error in accessing Progress Badge and UserBadge records for userId '+ str(userId)+'. Details:' + str(e)}), 500

    sendObject['badgeProgress'] = badgeProgress1[0] if badgeProgress1 else {'imagePath':"src/static/img/emptyBadge.png", 'message':'You have no badges yet.', 'date':None}
    sendObject['badgeProgressUpcoming'] = badgeProgress2 if badgeProgress2 else None

    #performance
    try:
        badgePerformance1 = db.session.query(Badges.imagePath, Badges.descAfter, UserBadges.achievedDate).\
        filter(Badges.type == 'performance').filter(UserBadges.userId == userId).filter(UserBadges.badgeId == Badges.id).first()
        if badgePerformance1:
            badgePerformance1 = {
                'imagePath': badge[0],
                'message': badge[1],
                'date': badge[2].date
            }
            for badge in db.session.query(Badges.imagePath, Badges.descBefore).filter(Badges.type == 'performance').\
            filter(UserBadges.userId == userId).filter(Badges.id > UserBadges.badgeId).all():
                badgePerformance.append({
                    'imagePath': badge[0],
                    'message': badge[1],
                    'date': None
                })
        else:
            for badge in Badges.query.filter_by(type='performance').all():
                badgePerformance.append({
                    'imagePath': badge.imagePath,
                    'message': badge.descBefore,
                    'date': None
                })
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing performance and user badge records, '+str(e))
        return jsonify({'error':'Error in accessing Performance Badge and UserBadge records for userId '+ str(userId)+'. Details:' + str(e)}), 500

    sendObject['badgePerformance'] = badgePerformance1 if badgePerformance1 else {'imagePath':"src/static/img/emptyBadge.png", 'message':'You have no badges yet.', 'date':None}
    sendObject['badgePerformanceUpcoming'] = badgePerformance if badgePerformance else None

    return jsonify(sendObject), 200

@app.route('/fprofileUpdate/', methods=['POST'])
def fprofileUpdate():
    userId = request.form.get('userId')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    board = None#request.form.get('board')
    grade = None#request.form.get('grade')
    school = request.form.get('school')
    mobile = None#request.form.get('mobile') #assuming otp verification is done
    email = request.form.get('email')
    parentName = request.form.get('parentName')
    parentMobile = request.form.get('parentMobile')
    city = request.form.get('city')
    lastYearResults = request.form.get('lastYearResults')
    update = request.form.get('update')   #boolean

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -firstname:'+str(firstname)\
    +' -lastname:'+str(lastname)+' -gender:'+str(gender)+' -dob:'+str(dob)+' -board:'+str(board)+' -grade:'+str(grade)\
    +' -school:'+str(school)+' -mobile:'+str(mobile)+' -email:'+str(email)+' -parentName:'+str(parentName)+' -parentMobile:'+str(parentMobile)\
    +' -city:'+str(city)+' -lastYearResults:'+str(lastYearResults)+' -update:'+str(update))

    sendObject = {
        'status':1,
        'error':None,
        'firstname': None,
        'lastname': None,
        'gender': None,
        'dob': None,
        'mobile': None,
        'email': None,
        'Grade': None,
        'school': None,
        'board' : None,
        'Parent Name': None,
        'Parent Mobile': None,
        'city': None,
        'Previous Class Percentage/GPA': None,
        'grades':[],
        'boards':[],
        'updated': False
    }

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    sendObject['firstname'] = userData.firstname
    sendObject['lastname'] = userData.lastname
    sendObject['gender'] = userData.gender
    sendObject['dob'] = userData.dob.strftime('%Y-%m-%d')
    sendObject['mobile'] = userData.mobile
    sendObject['email'] = userData.email
    sendObject['board'] = userData.board
    sendObject['Parent Name'] = userData.parentName
    sendObject['Parent Mobile'] = userData.parentMobile
    sendObject['city'] = userData.city
    sendObject['Previous Class Percentage/GPA'] = userData.lastYearResults

    gradeData, errorCode = getGrade({'id':userData.grade})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+gradeData)
        return jsonify({'error':gradeData}), errorCode

    sendObject['Grade'] = gradeData.grade

    schoolData, errorCode = getSchool({'id':userData.school})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+schoolData)
        return jsonify({'error':schoolData}), errorCode

    sendObject['school'] = schoolData.name

    if update and update.lower()=='true':
        userUpdateData = {}
        if firstname:
            userUpdateData['firstname'] = firstname
        if lastname:
            userUpdateData['lastname'] = lastname
        if gender:
            userUpdateData['gender'] = gender
        if dob:
            userUpdateData['dob'] = dob
        if board:
            userUpdateData['board'] = board
        if grade:
            userUpdateData['grade'] = grade
        if mobile:
            userUpdateData['mobile'] = mobile
        if email:
            userUpdateData['email'] = email
        if parentName:
            userUpdateData['parentName'] = parentName
        if parentMobile:
            userUpdateData['parentMobile'] = parentMobile
        if city:
            userUpdateData['city'] = city
        if lastYearResults:
            userUpdateData['lastYearResults'] = lastYearResults
        if school:
            schoolId, errorCode = addSchool(school, False)
            if errorCode != 200 and errorCode != 201:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+schoolId)
                return jsonify({'error':schoolId}), errorCode
            userUpdateData['school'] = schoolId

        error, errorCode = updateUser({'id':userData.id}, userUpdateData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

        userData, errorCode = getUser({'id':userData.id})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
            return jsonify({'error':userData}), errorCode

        schoolData, errorCode = getSchool({'id':userData.school})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+schoolData)
            return jsonify({'error':schoolData}), errorCode

        gradeData, errorCode = getGrade({'id':userData.grade})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+gradeData)
            return jsonify({'error':gradeData}), errorCode

        sendObject = {
            'status':1,
            'error':None,
            'firstname': userData.firstname,
            'lastname': userData.lastname,
            'gender': userData.gender,
            'dob': userData.dob.strftime('%Y%m%d'),
            'mobile': userData.mobile,
            'email': userData.email,
            'Grade': gradeData.grade,
            'school': schoolData.name,
            'board' : userData.board,
            'Parent Name': userData.parentName,
            'Parent Mobile': userData.parentMobile,
            'city': userData.city,
            'Previous Class Percentage/GPA': userData.lastYearResults,
            'grades':[],
            'boards':[],
            'updated': True
        }

    gradesData, errorCode = getAllGrades({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+gradesData)
        return jsonify({'error':gradesData}), errorCode

    for g in gradesData:
        sendObject['grades'].append({'id':g['id'],'grade':g['grade']})

    boardsData, errorCode = getAllBoards({})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+boardsData)
        return jsonify({'error':boardsData}), errorCode

    for b in boardsData:
        sendObject['boards'].append({'id':b['id'],'board':b['board']})

    return jsonify(sendObject), 200

#default bookmarks test
@app.route('/fbookmarkTest/', methods=['POST'])
def fbookmarkTest():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    subjectId = int(subjectId)

    sendObject = {
        'status':1,
        'subjects':[],
        'userTests':[]
    }

    userData, errorCode = getUser({'id':int(userId)})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    for sub in subjectsData:
        sendObject['subjects'].append({'id':sub['id'],'name':sub['name']})

    userTestsData, errorCode = getAllUserTests({'userId':userData.id, 'bookmark':True, 'desc':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestsData)
        return jsonify({'error':userTestsData}), errorCode

    testIds = [userTest['testId'] for userTest in userTestsData]
    testsData, errorCode = getAllTestsByIds({'ids':testIds})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testsData)
        return jsonify({'error':testsData}), errorCode

    for i, userTest in enumerate(userTestsData):
        testSubjectId, chapterIds, conceptIds, formats, levels, questionIds = None, None, None, None, None, None
        if userTest['testId']:
            text1 = testsData[i]['name']
            text2 = testsData[i]['text2']
            testSubjectId = testsData[i]['subjectId']
            imagePath = testsData[i]['imagePath']
        else:   #custom test
            text1 = userTest['customName']
            text2 = 'Custom Test'
            text3 = None
            imagePath = 'src/static/img/Customtest.png'
            testSubjectId, chapterIds, conceptIds, formats, levels, questionIds = userTest['customSubjectId'], userTest['customTestChapterIds'], \
            userTest['customTestConceptIds'], userTest['customTestFormats'], userTest['customTestLevelIds'], userTest['questionIds']

        if testSubjectId != subjectId:
            continue

        sendObject['userTests'].append({
            'userTestId': userTest['id'],
            'leftTop' : 'Practice' if userTest['practiceTest'] else 'Test',
            'rightTop': None,
            'text1':text1,
            'text2':text2,
            'imagePath':imagePath,
            'coins':userTest['coins'],
            'testId': testsData[i]['id'] if userTest['testId'] else None,
            'subjectId': subjectId,
            'chapterIds': chapterIds,
            'conceptIds': conceptIds,
            'formats': formats,
            'levels': levels,
            'questionIds': questionIds,
            'text3':'Finished'
            })
    return jsonify(sendObject), 200


@app.route('/fbookmarkQuestion/', methods=['POST'])
def fbookmarkQuestion():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    subjectId = int(subjectId)

    sendObject = {
        'status':1,
        'subjects':[],
        'questions':[]
    }

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    for sub in subjectsData:
        sendObject['subjects'].append({'id':sub['id'],'name':sub['name']})

    userQuestionsData, errorCode = getAllUserQuestions({'userId':userData.id, 'bookmark':True, 'desc':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userQuestionsData)
        return jsonify({'error':userQuestionsData}), errorCode

    questionIds = [userQuestion['questionId'] for userQuestion in userQuestionsData]
    questionsData, errorCode = getAllQuestions({'ids':questionIds})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+questionsData)
        return jsonify({'error':questionsData}), errorCode

    conceptIds = [question['conceptId'] for question in questionsData]
    conceptsData, errorCode = getAllConcepts({'ids':conceptIds})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptsData)
        return jsonify({'error':conceptsData}), errorCode

    questionFormatIds = [question['format'] for question in questionsData]
    questionFormatsData, errorCode = getAllQuestionFormats({'ids':questionFormatIds})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+questionFormatsData)
        return jsonify({'error':questionFormatsData}), errorCode

    for i in range(len(userQuestionsData)):
        questionSubjectId = conceptsData[i]['subjectId']
        if questionSubjectId != subjectId:
            continue
        sendObject['questions'].append({
            'questionId' : questionsData[i]['id'],
            'question' : questionsData[i]['text'],
            'format' : questionFormatsData[i]['code'],
            'conceptName' : conceptsData[i]['name']
        })
    return jsonify(sendObject), 200


@app.route('/fsubscription/', methods=['POST'])
def fsubscription():#TODO pastPlans with gst etc
    userId = request.form.get('userId')
    couponId = request.form.get('couponId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -couponId:'+str(couponId))

    sendObject = {}

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    coupon = 0
    if couponId:
        try:
            coupon = Coupon.query.filter_by(id=couponId).first().value
        except Exception as e:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing Coupon records, '+str(e))
            return jsonify({'error':'Error in accessing Coupon records for couponId '+ str(couponId)+'. Details:' + str(e)}), 500

    sendObject = {
        'status':1,
        'userEmail': userData.email,
        'userMobile': userData.mobile,
        'userFirstname': userData.firstname,
        'userLastname': userData.lastname,
        'userCoins': userData.coins,
        'couponAmount': coupon,
        'GST%':config10["subscriptionFields"]["GST%"],
        'internetHandling':config10["subscriptionFields"]["internetHandling"],
        'subscriptions': [],
        'activePlans': [],
        'pastPlans': []
    }

    subscriptionActivityData, errorCode = getAllSubscriptionActivity({'userId':userData.id})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionActivityData)
        return jsonify({'error':subscriptionActivityData}), errorCode

    for sA in subscriptionActivityData:
        subscriptionData, errorCode = getSubscription({'id':sA.subsId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionData)
            return jsonify({'error':subscriptionData}), errorCode

        if sA.expiryDate >= datetime.datetime.now(indianTime).date() and sA.testsRemaining:
            sendObject['activePlans'].append({
                'subsName':subscriptionData.name,
                'numberOfTests':subscriptionData.numberOfTests,
                'testsRemaining':sA.testsRemaining,
                'expiryDate':sA.expiryDate.strftime('%Y-%m-%d'),
            })
        else:
            sendObject['pastPlans'].append({
                'subsName':subscriptionData.name,
                'numberOfTests':subscriptionData.numberOfTests,
                'testsRemaining':sA.testsRemaining,
                'expiryDate':sA.expiryDate.strftime('%Y-%m-%d'),
            })

    try:
        subscriptions = db.session.query(Subscription.id, Subscription.name, Subscription.comment, \
        Subscription.price, Subscription.strikedPrice, Subscription.numberOfTests, Subscription.maxRedeemableCoins,\
        Subscription.validity, Subscription.grade).filter(Subscription.name != 'Free Trial').filter(Subscription.status == True).\
        filter(Subscription.board == userData.board).filter(Subscription.grade == userData.grade).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing subscription records, '+str(e))
        return jsonify({'error':'Error in accessing Subscription records for userId '+ str(userId)+'. Details:' + str(e)}), 500

    for i, sub in enumerate(subscriptions):
        if userData.grade != sub[8]:
            continue
        coins = userData.coins if userData.coins < sub[6] else sub[6]
        # print(sub[3], coins, config10["subscriptionFields"]["coinEquivalentRupees"],coupon,\
        # config10["subscriptionFields"]["internetHandling"], int(config10["subscriptionFields"]["GST%"]*sub[3]/100))
        sendObject['subscriptions'].append({
            'subsId':sub[0],
            'subsName':sub[1],
            'comment':sub[2],
            'price':sub[3],
            'strikedPrice':sub[4],
            'numberOfTests':sub[5],
            'maxRedeemableCoins':sub[6] if sub[6] > 0 else 0,
            'validity':sub[7],
            'yourRedeemableCoins': coins if coins > 0 else 0,
            'gstAmount':int(config10["subscriptionFields"]["GST%"]*sub[3]/100),
            'you pay': sub[3] - coins * config10["subscriptionFields"]["coinEquivalentRupees"] - coupon\
            + config10["subscriptionFields"]["internetHandling"] + int(config10["subscriptionFields"]["GST%"]*sub[3]/100)
        })
    return jsonify(sendObject), 200


@app.route('/fcoupon/', methods=['POST'])
def fcoupon():
    userId = request.form.get('userId')
    coupon = request.form.get('coupon')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -coupon:'+str(coupon))

    sendObject = {
        'status':1,
        'couponId': None,
        'value':None,
        'error':'invalid coupon'
    }

    if coupon:
        coupon = coupon.upper()
        curDatetime = datetime.datetime.now(indianTime).strftime('%Y-%m-%d')
        try:
            couponDetails = db.session.query(Coupon.id, Coupon.maxUses, Coupon.maxPerUser, Coupon.value).\
            filter(Coupon.code == coupon).filter(Coupon.status == True).filter(Coupon.startDate <= curDatetime).\
            filter(Coupon.endDate >= curDatetime).first()
        except Exception as e:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing coupon records, '+str(e))
            return jsonify({'error':'Error in accessing coupon record for coupon '+ str(coupon) +'. Details:' + str(e)}), 500
        # print('1 ',couponDetails)
        if couponDetails:
            try:
                couponCount = db.session.query(func.count(UserCoupon.couponId)).group_by(UserCoupon.couponId).\
                filter(UserCoupon.couponId == couponDetails[0]).first()
            except Exception as e:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing coupons record, '+str(e))
                return jsonify({'error':'Error in accessing coupons record. Details:' + str(e)}), 500
            # print('1 ',couponCount)
            if couponCount:
                try:
                    userCouponCount = db.session.query(func.count(UserCoupon.userId)).group_by(UserCoupon.userId).\
                    filter(UserCoupon.userId == userId).filter(UserCoupon.couponId == couponDetails[0]).first()
                except Exception as e:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing coupon records, '+str(e))
                    return jsonify({'error':'Error in accessing coupons record. Details:' + str(e)}), 500
                # print('1 ',userCouponCount)
                if userCouponCount and couponCount[0] < couponDetails[1] and userCouponCount[0] < couponDetails[2]:
                    sendObject['error'] = None
                    sendObject['couponId'] = couponDetails[0]
                    sendObject['value'] = couponDetails[3]
                elif userCouponCount is None and couponCount[0] < couponDetails[1]:
                    sendObject['error'] = None
                    sendObject['couponId'] = couponDetails[0]
                    sendObject['value'] = couponDetails[3]
                else:
                    sendObject['error'] = 'coupons invalid or reached its usage limit'
            else:
                sendObject['error'] = None
                sendObject['couponId'] = couponDetails[0]
                sendObject['value'] = couponDetails[3]
    return jsonify(sendObject), 200


@app.route('/fproceedToPay/', methods=['POST'])
def fproceedToPay():
    userId = request.form.get('userId')
    amount = request.form.get('amount')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))
    user = User.query.filter_by(id=userId).first()

    #call to ippo pay
    # url = 'https://pk_test_yor2XNSAzGm0:sk_test_4qlwssa8TZIEJ9WWXV9vqEEvNhLctbe5h1LX7gYz@api.ippopay.com/v1/order/create'
    # sendObject1 = {
    #     "amount": amount,
    #     "currency": "INR",
    #     "payment_modes": "cc,dc,nb,upi",
    #     "notify_url":"",
    #     "customer": {
    #             "name": user.firstname,
    #             "email": user.email,
    #             "phone": {
    #                     "country_code": "91" ,
    #                     "national_number": user.mobile
    #                 }
    #             }
    # }
    subsAct = SubscriptionActivity.query.order_by(-SubscriptionActivity.id).first()
    orderId = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

    url = "https://test.cashfree.com/api/v1/order/create"
    sendObject1 = {
            'appId':'308052d571a1064665b5a1e3d5250803',
            'secretKey':'4386c28638919e5448dbb343809fe3f2f0cce36c',
            'orderId': orderId,
            'orderAmount':amount,
            'orderCurrency':"INR",
            'orderNote':None,
            'customerName':user.firstname+' '+user.lastname,
            'customerEmail':user.email,
            'customerPhone':user.mobile,
            'returnUrl':'https://cashfree.com'
    }
    response = requests.post(url, data=sendObject1)
    response = response.json()
    if response.keys():
        return jsonify({'orderId':'order_id', 'status':-1})
    return jsonify({'status':response['status'], 'paymentLink':response['paymentLink'], 'orderId':orderId}), 200


import base64, hashlib
def getPaymentStatus(merchantTransactionId):
    # url = 'https://webhook.site/token/c1769b7d-8273-4100-a560-c98d6aa8cf73/requests'
    # for not losing the token do a cron job daily to send request and delete it.
    toBeSha = "/pg/v1/status/RAOACADEMYONLINE/"+str(merchantTransactionId)+"1b6c088b-0e0c-4fb5-9924-9a8759e606f3"
    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': hashlib.sha256(toBeSha.encode('utf-8')).hexdigest()+"###1",
        'X-MERCHANT-ID': 'RAOACADEMYONLINE'
    }
    url = "https://api.phonepe.com/apis/hermes/pg/v1/status/RAOACADEMYONLINE/"+str(merchantTransactionId)
    response = requests.get(url, headers=headers)
    response = response.json()

    app.logger.debug(inspect.currentframe().f_code.co_name+' -:'+str(response))
    success = True if response['code'] == "PAYMENT_SUCCESS" else False
    message = 'success' if 'successfully' in response['message'] else response['data']['responseCode']
    typeOfMethod = response['data']['paymentInstrument']['type'] if success else None
    paymentInfo = str(response['data']['paymentInstrument']) if success else None

    subscriptionActivity = SubscriptionActivity(None, None, response['data']['amount'], None, None, None,\
    success, message, response['data']['merchantTransactionId'], response['data']['transactionId'],\
    typeOfMethod, paymentInfo, datetime.datetime.now(indianTime))
    subsActivityId, errorCode = insertSubscriptionActivity(subscriptionActivity)
    if errorCode != 201:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -: error:Error in inserting into subscriptionActivity database, ' +str(subsActivityId))
    return response['data']['transactionId']


#after payment is successfully done
@app.route('/fpayment/', methods=['POST'])
def fpayment():
    userId = request.form.get('userId')
    couponId = request.form.get('couponId')
    amount = request.form.get('amount')
    coins = request.form.get('coins')
    subsId = request.form.get('subsId')
    merchantTransactionId = request.form.get('merchantTransactionId')
    transactionId = getPaymentStatus(merchantTransactionId)

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -couponId:'+str(couponId)\
    +' -amount:'+str(amount)+' -coins:'+str(coins)+' -subsId:'+str(subsId)+' -merchantTransactionId:'+str(merchantTransactionId)\
    +' -transactionId:'+str(transactionId))

    sendObject = {
        'success':False,
        'message':'no response from phonepe'
    }
    if couponId == '':
        couponId = None
    if coins == '' or not coins:
        coins = 0

    subscriptionData, errorCode = getSubscription({'id':subsId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionData)
        return jsonify({'error':subscriptionData}), errorCode

    dt, tests = calExpiryDate(subscriptionData.validity), subscriptionData.numberOfTests

    subscriptionActivityData, errorCode = getSubscriptionActivity({'merchantTransactionId':merchantTransactionId, 'transactionId':transactionId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionData)
        return jsonify({'error':subscriptionData}), errorCode

    elif errorCode == 404:
        subscriptionActivity = SubscriptionActivity(userId, subsId, amount//100, couponId, dt, \
        tests, False, 'no response from phonepe', merchantTransactionId, transactionId, None, None, datetime.datetime.now(indianTime))
        subsActivityId, errorCode = insertSubscriptionActivity(subscriptionActivity)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+str(subsActivityId))
            return jsonify({'error':str(subsActivityId)}), errorCode

    else:
        if not subscriptionActivityData.success:
            tests, dt = 0, datetime.datetime.now(indianTime).date()
        error, errorCode = updateSubscriptionActivity({'id':subscriptionActivityData.id}, \
        {'userId':userId, 'subsId':subsId, 'couponId':couponId, 'expiryDate':dt, 'testsRemaining':tests})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

        sendObject['success'] = subscriptionActivityData.success
        sendObject['message'] = subscriptionActivityData.message

    error, errorCode = updateInits({'userId':userId}, {'subscription':'Your Subscription is Active'})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    error, errorCode = updateUser({'id':userId}, {'subtractCoins':int(coins), 'addTests':subscriptionData.numberOfTests})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    try:
        peerUser = ReferralActivity.query.filter_by(peerPhoneNumber=userData.mobile).first()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing ReferralActivity record for mobile '+ \
        str(userData.mobile) +'. Details:' + str(e))
        return jsonify({'error':'Error in accessing ReferralActivity record for mobile '+ str(userData.mobile) +'. Details:' + str(e)}), 500

    if peerUser:
        error, errorCode = updateUser({'id':peerUser.userId}, {'addCoins':config5['rewards']['peerCoins']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

    if couponId:
        try:
            coupon = db.session.query(Coupon).filter_by(id=couponId).first()
            coupon.maxUses -= 1
            db.session.commit()
        except Exception as e:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in updating coupon, '+str(e))
            return jsonify({'error':'Error in updating Coupon for id '+ str(couponId) +'. Details:' + str(e)}), 500

        try:
            db.session.add(UserCoupon(int(userId), int(couponId)))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in inserting into userCoupon, '+str(e))
            return jsonify({'error':'Error in inserting into UserCoupon. Details:' + str(e)}), 500

    return jsonify(sendObject), 200


@app.route('/freferralPage/', methods=['POST'])
def freferralPage():
    userId = request.form.get('userId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))

    sendObject = {
        'rewards':config5['rewards']['peerCoins'],
        'numberOfSignedPeople':0,
        'numberOfPeopleSubscribed':0
    }
    numberOfSignedPeople, numberOfPeopleSubscribed  = 0, 0
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    sendObject['referral'] = userData.referral

    try:
        refAct = db.session.query(ReferralActivity.userId, ReferralActivity.peerPhoneNumber).\
        filter(ReferralActivity.userId == userId).filter(ReferralActivity.peerPhoneNumber == User.mobile).all()
        if refAct:
            sendObject['numberOfSignedPeople'] = len(refAct)
            sendObject['numberOfPeopleSubscribed'] = 0
            for id in [User.query.filter_by(mobile=rA[1]).first().id for rA in refAct]:
                if SubscriptionActivity.query.filter_by(userId=id).filter(SubscriptionActivity.subsId != 1).first():
                    sendObject['numberOfPeopleSubscribed'] += 1
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing referral activity subs activity records, '+str(e))
        return jsonify({'error':'Error in accessing Referral Activity Subscription Activity records. Details:' + str(e)}), 500

    return jsonify(sendObject), 200


def getNewDynamicTest(userId, subjectId, chapterId):
    try:
        test = db.session.query(Test.id, Test.imagePath, Test.name, Test.text2, Test.text3, Test.maxCoins).\
        filter(Test.isStaticTest == False).filter(Test.isLoop == False).\
        filter(Test.subjectId == subjectId).filter(Test.status == True)
        if chapterId:
            test = test.filter(Test.chapterId == chapterId)
        # test = test.outerjoin(UserTest).filter(UserTest.userId == userId).filter(UserTest.id == None)
        return test.order_by(Test.id).all(), 200
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in generating dynamic tests, '+str(e))
        return 'Error in generating dynamic tests. Details: '+str(e), 500


@app.route('/fnoticeClick/', methods=['GET', 'POST'])
def fnoticeClick():
    userId = request.form.get('userId')
    clicked = request.form.get('clicked')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -clicked:'+str(clicked))

    initsUpdateData = {}
    if clicked == 'newBadge':
        initsUpdateData['newBadge'] = False
    elif clicked == 'newWeeklyReports':
        initsUpdateData['newWeeklyReports'] = None
    elif clicked == 'newTests':
        initsUpdateData['newTests'] = None
    elif clicked == 'newSubscription':
        initsUpdateData['subscription'] = None

    error, errorCode = updateInits({'userId':userId}, initsUpdateData)
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    return jsonify({}), 200


# home page - recommendation - initially - physics 2 test (dynamic)
# later - practice test if not then another 2 test # high pritority practiceTest then paused
@app.route('/fhome/', methods=['GET', 'POST'])
def fhome():
    userId = request.form.get('userId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId))

    sendObject = {
        'status':1,
        'recommendations': [],
        'banner': [],
        'message':'good',
        'loops':[]
    }
    initsData, errorCode = getInits({'userId':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+initsData)
        return jsonify({'error':initsData}), errorCode

    notifyForNewTest, notifyForNewBadge, notifyForNewWeeklyReport, notifyForSubscription =\
    True if initsData.newTests else False, True if initsData.newBadge else False, \
    True if initsData.newWeeklyReports else False, True if initsData.subscription else False

    notifyList = [[notifyForNewBadge,"notifyForNewBadge"], [notifyForNewTest,"notifyForNewTest"], \
    [notifyForSubscription,'notifyForSubscription'], [notifyForNewWeeklyReport,'notifyForNewWeeklyReport']]
    notifyList = sorted(notifyList, reverse=True, key=lambda x: x[0])

    sendObject['notifyList'] = notifyList
    sendObject['newBadge'] = 'You earned a new Badge' if initsData.newBadge else "you have no New badges currently"
    sendObject['newWeeklyReports'] = initsData.newWeeklyReports if initsData.newWeeklyReports else "Your upcoming weekly report will be ready by Saturday."
    sendObject['newTests'] = initsData.newTests if initsData.newTests else "You have no New Tests currently"
    sendObject['newSubscription'] = initsData.subscription if initsData.subscription else "You have active subscription currently"

    try:
        for i, banner in enumerate(Banner.query.filter().order_by(Banner.sortOrder).all()):
            sendObject['banner'].append(banner.imagePath)
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing banner records, '+str(e))
        return jsonify({'error':'Error in accessing Banner records. Details: ' + str(e)}), 500

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    if not userData.status:
        sendObject['message'] = 'logout'
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+' . message:logout')
        return jsonify(sendObject), 200

    sendObject['name'] = userData.firstname
    sendObject['referralNumber'] = userData.referral    #for sharing with friends
    subjectData, errorCode = getSubject({'grade':userData.grade, 'board':userData.board, 'sortOrder':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
        return jsonify({'error':subjectData}), errorCode

    sendObject['defaultSubjectId'] = subjectData.id

    homePageTests = 0
    try:
        recommendedUserTests = UserTest.query.filter_by(userId=userId, displayedOnHomePage=True, practiceTest=True).\
        filter(UserTest.progress != 100).order_by(UserTest.paused.desc(), -UserTest.id).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing usertest records for recommendation, '+str(e))
        return jsonify({'error':'Error in accessing UserTest records for recommendations. Details: ' + str(e)}), 500

    for ut in recommendedUserTests:
        testData, errorCode = getTest({'id':ut['testId']})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
            return jsonify({'error':testData}), errorCode

        text1 = ut['customName']
        text2 = 'Custom Test'
        imagePath = None
        if testData: #not custom test
            text1 = testData.name
            text2 = testData.text2
            imagePath = testData.imagePath

        homePageTests += 1
        sendObject['recommendations'].append({
            'leftTop': 'Practice',
            'rightTop': None,
            'imagePath': imagePath,
            'text1': text1,
            'text2': text2,
            'text3': None,
            'coins': ut['coins'],
            'NoOfQs': len((ut['questionIds']).split(',')),
            'time': ut['maxTime'],
            'testId': None,
            'userTestId': ut['id']
        })

    if homePageTests < 2:
        dynamicTests, errorCode = getNewDynamicTest(userId, sendObject['defaultSubjectId'], None)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+dynamicTests)
            return jsonify({'error':dynamicTests}), errorCode

        for test in dynamicTests:
            userTestData, errorCode = getUserTest({'userId':userId, 'testId':test[0]})
            if errorCode == 200:
                continue
            elif errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
                return jsonify({'error':userTestData}), errorCode

            homePageTests += 1
            sendObject['recommendations'].append({
                'leftTop': 'Test',
                'rightTop': 'New',
                'imagePath': test[1],
                'text1': test[2],
                'text2': test[3],
                'text3': test[4],
                'coins': test[5],
                'NoOfQs': None,
                'time': None,
                'testId': test[0],
                'userTestId': None
            })
            if homePageTests == 2:
                break

    try:
        recommendationLoops = db.session.query(Test.id, Test.name, Test.imagePath).filter(Test.isLoop == True).\
        filter(Test.subjectId.in_([sub.id for sub in Subject.query.filter_by(board=userData.board, grade=userData.grade).all()])).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing loop tests, '+str(e))
        return jsonify({'error':'Error in accessing Loop Test records. Details: ' + str(e)}), 500

    i = 0
    for loop in recommendationLoops:
        userTestData, errorCode = getUserTest({'userId':userId, 'testId':loop[0]})
        if errorCode == 200:
            continue
        elif errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
            return jsonify({'error':userTestData}), errorCode

        sendObject['loops'].append({
            'id':loop[0],
            'name':loop[1],
            'imagePath':loop[2]
        })
        i+=1
        if i > 5:
            break
    return jsonify(sendObject), 200


@app.route('/ftestHome/', methods=['POST'])
def ftestHome():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    sendObject = {
        'status':1,
        'subjects': [],
        'testCategories': [],
        'recent': [],
        'recommendations': []
    }
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    for sub in subjectsData:
        sendObject['subjects'].append({'id':sub['id'],'name':sub['name']})

    testCategoriesData, errorCode = getAllTestCategories({
        'subjectId':subjectId,
        'sortOrder':1
    })
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testCategoriesData)
        return jsonify({'error':testCategoriesData}), errorCode

    for i, testCategory in enumerate(testCategoriesData):
        if testCategory['name'] == 'PYQs':
            continue
        sendObject['testCategories'].append({
            'id': testCategory['id'],
            'name': testCategory['name'],
            'caption': testCategory['caption'],
            'imagePath': testCategory['imagePath']
        })

    # testHome Page
    # recommendations - initially - generate dynamic test, untill practice test are present
    recommendationTests = 0
    try:
        recommendedUserTests = UserTest.query.filter_by(userId=userId, practiceTest=True).filter(UserTest.progress != 100).\
        order_by(UserTest.paused.desc(), -UserTest.id).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing usertest records for recommendations, '+str(e))
        return jsonify({'error':'Error in accessing UserTest records for recommendations. Details: ' + str(e)}), 500

    for ut in recommendedUserTests:
        testData, errorCode = getTest({'id':ut.testId, 'subjectId':subjectId})
        if errorCode == 404:
            testData = None
        elif errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
            return jsonify({'error':testData + ' at recommended tests.'}), errorCode

        testId = None
        if testData: #not custom test
            text1 = testData.name
            text2 = testData.text2
            text3 = testData.text3
            testId = testData.id
            imagePath = testData.imagePath
        elif ut.customSubjectId != subjectId:
            continue
        else:   #custom test
            text1 = ut.customName
            text2 = 'Custom Test'
            text3 = None
            chapterData, errorCode = getChapter({'id':ut.customTestChapterIds.split(',')[0]})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData+' at recommended tests.')
                return jsonify({'error':chapterData + ' at recommended tests.'}), errorCode

            imagePath = chapterData.imagePath

        recommendationTests += 1
        sendObject['recommendations'].append({
            'leftTop': 'Practice',
            'rightTop': None,
            'imagePath': imagePath,
            'text1': text1,
            'text2': text2,
            'text3': text3,
            'coins': ut.coins,
            'NoOfQs': len((ut.questionIds).split(',')),
            'time': ut.maxTime,
            'testId': testId,
            'practiceTest': ut.practiceTest,
            'userTestId': ut.id
        })

    if recommendationTests < 2:
        dynamicTests, errorCode = getNewDynamicTest(userId, subjectId, None)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+dynamicTests)
            return jsonify({'error':dynamicTests}), errorCode

        for test in dynamicTests:
            userTestData, errorCode = getUserTest({'userId':userId, 'testId':test[0]})
            if errorCode == 200:
                continue
            elif errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
                return jsonify({'error':userTestData}), errorCode

            recommendationTests += 1
            sendObject['recommendations'].append({
                'leftTop': 'Test',
                'rightTop': 'New',
                'imagePath': test[1],
                'text1': test[2],
                'text2': test[3],
                'text3': test[4],
                'coins': test[5],
                'NoOfQs': None,
                'time': None,
                'testId': test[0],
                'practiceTest':False,
                'userTestId': None
            })
            if recommendationTests == 2:
                break


    # recent - initially - generate dynamic, untill paused top priority(top priority) remain and always show finished tests
    recentTests = 0
    recentUserTests, errorCode = getAllUserTests({'userId':userId, 'paused':True, 'target':0, 'desc':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+recentUserTests)
        return jsonify({'error':recentUserTests}), errorCode

    for ut in recentUserTests:
        testData, errorCode = getTest({'id':ut['testId'], 'subjectId':subjectId})
        if errorCode == 404:
            testData = None
        elif errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData+' at recent tests part 1.')
            return jsonify({'error':testData + ' at recent tests part 1.'}), errorCode

        testId = None
        if testData: #not custom test
            text1 = testData.name
            text2 = testData.text2
            imagePath = testData.imagePath
            testId = testData.id
        elif ut['customSubjectId'] != subjectId:
            continue
        else:   #custom test
            text1 = ut['customName']
            text2 = 'Custom Test'
            text3 = None
            chapterData, errorCode = getChapter({'id':ut['customTestChapterIds'].split(',')[0]})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData+ ' at recent tests part 1')
                return jsonify({'error':chapterData + ' at recent tests part 1.'}), errorCode

            imagePath = chapterData.imagePath

        progress = 'ongoing'
        if ut['customName'] or (testData and testData.isStaticTest):   #static tests
            progress = str(ut['progress']) + '% completed'

        recentTests += 1
        sendObject['recent'].append({
            'leftTop': 'Test' if not ut['practiceTest'] else 'Practice',
            'rightTop': None,
            'imagePath': imagePath,
            'text1': text1,
            'text2': text2,
            'text3': progress,
            'coins': None,
            'testId': testId,
            'practiceTest': ut['practiceTest'],
            'userTestId': ut['id']
        })
        if recentTests > 10:
            break

    #adding recently completed taken tests here
    completedUserTests, errorCode = getAllUserTests({'userId':userId, 'progress':100, 'target':0, 'desc':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+completedUserTests)
        return jsonify({'error':completedUserTests}), errorCode

    for ut in completedUserTests:
        testData, errorCode = getTest({'id':ut['testId'], 'subjectId':subjectId})
        if errorCode == 404:
            testData = None
        elif errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData+' at recent tests part 2')
            return jsonify({'error':testData + ' at recent tests part 2.'}), errorCode

        testId = None
        if testData: #not custom test
            text1 = testData.name
            text2 = testData.text2
            imagePath = testData.imagePath
            testId = testData.id
        elif ut['customSubjectId'] != subjectId:
            continue
        else:   #custom test
            text1 = ut['customName']
            text2 = 'Custom Test'
            text3 = None
            chapterData, errorCode = getChapter({'id':ut['customTestChapterIds'].split(',')[0]})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData+' at recent test part 2')
                return jsonify({'error':chapterData + ' at recent tests part 2.'}), errorCode

            imagePath = chapterData.imagePath

        recentTests += 1
        sendObject['recent'].append({
            'leftTop': 'Test' if not ut['practiceTest'] else 'Practice',
            'rightTop': None,
            'imagePath': imagePath,
            'text1': text1,
            'text2': text2,
            'text3': 'Finished',
            'coins': None,
            'testId': testId,
            'practiceTest': ut['practiceTest'],
            'userTestId': ut['id']
        })
        if recentTests > 10:
            break

    if recentTests < 2:
        dynamicTests, errorCode = getNewDynamicTest(userId, subjectId, None)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+dynamicTests)
            return jsonify({'error':dynamicTests}), errorCode

        for test in dynamicTests:
            userTestData, errorCode = getUserTest({'userId':userId, 'testId':test[0]})
            if errorCode == 200:
                continue
            elif errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData+' at recent tests part 3')
                return jsonify({'error':userTestData + ' at recent tests part 3.'}), errorCode

            recentTests += 1
            sendObject['recent'].append({
                'leftTop': 'Test',
                'rightTop': 'New',
                'imagePath': test[1],
                'text1': test[2],
                'text2': test[3],
                'text3': test[4],
                'coins': test[5],
                'testId': test[0],
                'practiceTest':False,
                'userTestId': None
            })
            if recentTests == 2:
                break
            if recentTests > 10:
                break

    return jsonify(sendObject), 200

@app.route('/fpyq/', methods=['POST'])
def fpyq():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    sendObject = {
        'status':1,
        'test':[]
    }

    try:
        pyqTests = db.session.query(Test.id, Test.imagePath, Test.name, Test.text2, Test.text3, Test.maxCoins).\
        filter(Test.subjectId == subjectId).filter(TestCategory.subjectId == subjectId).filter(TestCategory.name == 'PYQs').\
        filter(Test.categoryId == TestCategory.id).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing pyqTests, '+str(e))
        return jsonify({'error':'Error in accessing pyqTest records. Details: ' + str(e)}), 500

    for test in pyqTests:
        sendObject['test'].append({
            'leftTop': 'Test',
            'rightTop': 'New',
            'testId': test[0],
            'imagePath': test[1],
            'text1': test[2],
            'text2': test[3],
            'text3': test[4],
            'coins': test[5],
            'userTestId': None
        })
    return jsonify(sendObject), 200


@app.route('/ftestChapters/', methods=['POST'])
def ftestChapters():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    sendObject = {
        'status':1,
        'chapter':[]
    }

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectData, errorCode = getSubject({'id':subjectId, 'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectData}), errorCode

    sendObject['subjectName'] = subjectData.name

    chaptersData, errorCode = getAllChapters({'subjectId':subjectId, 'sortOrder':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chaptersData)
        return jsonify({'error':chaptersData}), errorCode

    for i, chapter in enumerate(chaptersData):
        sendObject['chapter'].append({
            'id': chapter['id'],
            'caption': chapter['caption'],
            'imagePath': chapter['imagePath'],
            'name': chapter['name']
        })
    return jsonify(sendObject), 200

@app.route('/ftestChapterConcept/', methods=['POST'])
def ftestChapterConcept():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')
    chapterId = request.form.get('chapterId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId)\
    +' -chapterId:'+str(chapterId))

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectData, errorCode = getSubject({'id':subjectId, 'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
        return jsonify({'error':subjectData}), errorCode

    chapterData, errorCode = getChapter({'id':chapterId, 'subjectId':subjectId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData)
        return jsonify({'error':chapterData}), errorCode

    sendObject = {
        'status':1,
        'name': chapterData.name,
        'imagePath': chapterData.imagePath,
        'tags': chapterData.tags.split(',') if chapterData.tags else None,
        'description': chapterData.description,
        'test':[]
    }
    conceptTests, errorCode = getAllTests({'chapterId':chapterId, 'isStaticTest':False, 'isLoop':False, 'status':True})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chaptersData)
        return jsonify({'error':conceptTests}), errorCode

    for i, test in enumerate(conceptTests):
        userTestData, errorCode = getUserTest({'userId':userId, 'testId':test['id'], 'practiceTest':False, 'rOrder':1})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
            return jsonify({'error':userTestData}), errorCode
        elif errorCode == 404:
            userTestData = None

        text3 = test['text3']
        if userTestData:
            text3 = 'Ongoing'
            if userTestData.progress == 100:
                text3 = 'Finished'

        sendObject['test'].append({
                'testId': test['id'],
                'leftTop': 'Test',
                'rightTop': None if userTestData else 'New',
                'imagePath': test['imagePath'],
                'text1': test['name'],
                'text2': test['text2'],
                'text3': text3,
                'userTestId': userTestData.id if userTestData else None,
                'coins': None if userTestData else test['maxCoins']
        })
    return jsonify(sendObject), 200


#atleast a custom test should have 10 questions
#if selected level has more than 10questions with more than 1 format, ask user to select more formats;
# if selected level has less 10 questions then take questions from another level silently
@app.route('/fcustomTest/', methods=['POST'])
def fcustomTest():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')
    chapterIds = request.form.get('chapterIds')  #comma separated
    conceptIds = request.form.get('conceptIds') #comma separated
    level = request.form.get('level')   #comma separated
    format = request.form.get('format') #comma separated

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId)\
    +' -chapterIds:'+str(chapterIds)+' -conceptIds:'+str(conceptIds)+' -level:'+str(level)+' -format:'+str(format))

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectData, errorCode = getSubject({'id':subjectId, 'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
        return jsonify({'error':subjectData}), errorCode

    # try:
    #     userTest = UserTest.query.filter_by(userId=userId, practiceTest=False).filter(UserTest.customName != None).count()
    # except Exception as e:
    #     app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing custom based usertests, '+str(e))
    #     return jsonify({'error':'Error in accessing Custom based UserTest records. Details: ' + str(e)}), 500
    # customName = 'Custom Test ' + str(userTest+1)

    if not chapterIds:
        chapterData, errorCode = getChapter({'subjectId':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData)
            return jsonify({'error':chapterData}), errorCode

        conceptData, errorCode = getConcept({'chapterId':chapterData.id})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptData)
            return jsonify({'error':conceptData}), errorCode

        chapterIds = str(chapterData.id)
        conceptIds = str(conceptData.id)
    elif not conceptIds:
        chapterData, errorCode = getChapter({'subjectId':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData+ ' with chapterId')
            return jsonify({'error':chapterData + ' with chapterId.'}), errorCode

        conceptData, errorCode = getConcept({'chapterId':chapterIds.split(',')[0]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptData+' with chapterId')
            return jsonify({'error':conceptData + ' with chapterId.'}), errorCode

        conceptIds = str(conceptData.id)

    if not level:
        level = '1,2,3'
    if not format:
        format = '1,2,3,4,5'

    sendObject = {
        'status':1,
        # 'customName':customName,
        'subjectId':subjectId,
        'chapters':[],
        'concepts':[],
        'levels':[],
        'formats':[],
        'chapterIds':chapterIds,
        'conceptIds':conceptIds,
        'level':level,
        'format':format,
        'questionIds':''
    }

    levels, formats = {}, {}
    for chapterId in chapterIds.split(','):
        for concept in conceptIds.split(','):
            try:
                questions = Question.query.filter(Question.conceptId == int(concept)).all()
            except Exception as e:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing question records via conceptId, '+str(e))
                return jsonify({'error':'Error in accessing question records via conceptId. Details: ' + str(e)}), 500

            for ques in questions:
                questionFormatData, errorCode = getQuestionFormat({'id':ques.format})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+questionFormatData)
                    return jsonify({'error':questionFormatData}), errorCode

                formats[ques.format] = questionFormatData.code
                levels[ques.difficultyLevel] = config2['difficultyLevel'][str(ques.difficultyLevel)]
                if str(ques.difficultyLevel) in level.split(',') and str(ques.format) in format.split(','):
                    sendObject['questionIds'] += str(ques.id) + ','

    if sendObject['questionIds'] != '' :
        sendObject['questionIds'] = sendObject['questionIds'][:-1]

    chaptersData, errorCode = getAllChapters({'subjectId':subjectId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chaptersData)
        return jsonify({'error':chaptersData}), errorCode

    for chap in chaptersData:
        sendObject['chapters'].append({
            'id':chap['id'],
            'name':chap['name']
        })

    conceptsData, errorCode = getAllConcepts({'chapterIds':[id for id in chapterIds.split(',')]})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptsData)
        return jsonify({'error':conceptsData}), errorCode

    for con in conceptsData:
        sendObject['concepts'].append({
            'id':con['id'],
            'name':con['name']
        })

    for k,v in levels.items():
        sendObject['levels'].append({
            'id':int(k),
            'level':v
        })
    for k, v in formats.items():
        sendObject['formats'].append({
            'id':int(k),
            'format':v
        })
    return jsonify(sendObject), 200


@app.route('/ftestInstructions/', methods=['POST'])
def ftestInstructions():    #for paused, practice, new, custom #not for loops
    userId = request.form.get('userId')
    testId = request.form.get('testId')
    userTestId = request.form.get('userTestId')
    customName = request.form.get('customName')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -testId:'+str(testId)\
    +' -userTestId:'+str(userTestId)+' -customName:'+str(customName))

    sendObject = {
        'status':1,
        'marksDistribution': config6['marks'],
        'tags':None,
        'preparedBy':None,
        'level': None,
        'format':None
    }
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    isPractice, test, syllabus = False, None, ''
    if userTestId:  #paused or practice
        userTestData, errorCode = getUserTest({'id':userTestId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
            return jsonify({'error':userTestData}), errorCode

        if userTestData.practiceTest:
            isPractice = True
        if userTestData.testId: #not custom test
            testData, errorCode = getTest({'id':userTestData.testId})
            if errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData+' with userTestId')
                return jsonify({'error':testData + ' with userTestId.'}), errorCode
            elif errorCode == 404:
                testData = None
        else:
            customName = userTestData.customName
            customConceptIds = userTestData.customTestConceptIds
            customLevels = userTestData.customTestLevelIds
            customFormats = userTestData.customTestFormats
    else:
        if testId:  #new static or dynamic
            testData, errorCode = getTest({'id':testId})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData+' with testId')
                return jsonify({'error':testData + ' with testId.'}), errorCode

        elif customName:  #new custom test
            # tags = [*set(tags)]
            customConceptIds = request.form.get('customConceptIds') #comma separated
            customLevels = request.form.get('customLevels')   #comma separated
            customFormats = request.form.get('customFormats') #comma separated
            app.logger.debug(inspect.currentframe().f_code.co_name+' continued -customConceptIds:'+str(customConceptIds)\
            +' -customLevels:'+str(customLevels) +' -customFormats:'+str(customFormats))

    if testId:
        sendObject['description'] = testData.description
        syllabus = testData.syllabus
        sendObject['tags'] = testData.tags
        sendObject['preparedBy'] = testData.preparedBy
    elif customName and customConceptIds and customLevels and customFormats:
        sendObject['description'] = config8['customTestDescription']
        level, format = '', ''
        conceptsData, errorCode = getAllConcepts({'ids':[id for id in customConceptIds.split(',')]})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptsData)
            return jsonify({'error':conceptsData}), errorCode

        for con in conceptsData:
            syllabus += con['name'] + ','
        for l in customLevels.split(','):
            level += config2['difficultyLevel'][l] + ','
        for f in customFormats.split(','):
            format += configFormat[int(f)] + ','
        sendObject['level'] = level[:-1]
        sendObject['format'] = format[:-1]

    if userTestId and userTestData.practiceTest:
        sendObject['description'] = config7['praticeTestDescription']
    sendObject['name'] = testData.name if testId else customName
    sendObject['syllabus'] = testData.syllabus if testId else syllabus[:-1]
    sendObject['subscriptionExpired'] = True
    subscriptionActivityData, errorCode = getAllSubscriptionActivity({'userId':userData.id})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subscriptionActivityData)
        return jsonify({'error':subscriptionActivityData}), errorCode

    for sA in subscriptionActivityData:
        if sA.expiryDate - datetime.datetime.now(indianTime).date() > datetime.timedelta(0) and sA.testsRemaining != 0:
            sendObject['subscriptionExpired'] = False
            break
    return jsonify(sendObject), 200


@app.route('/floopsHome/', methods=['POST'])
def floopsHome():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId))

    sendObject = {
        'status':1,
        'FAQs': [],
        'subjects': [],
        'loops': []
    }
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board, 'academics':True, 'sortOrder':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    for sub in subjectsData:
        sendObject['subjects'].append({
            'id': sub['id'],
            'name': sub['name']
        })

    testsData, errorCode = getAllTests({'subjectId':subjectId, 'isLoop':True})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testsData)
        return jsonify({'error':testsData}), errorCode

    for test in testsData:
        sendObject['loops'].append({
            'id': test['id'],
            'imagePath': test['imagePath'],
            'chapterId': test['chapterId'],
            'name': test['name']
        })

    faqsData, errorCode = getAllFaqs({'type':'loops'})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+faqsData)
        return jsonify({'error':faqsData}), errorCode

    for i, faq in enumerate(faqsData):
        sendObject['FAQs'].append({
            'number': i+1,
            'question':faq['question'],
            'answer': faq['answer'],
            'imagePath': faq['imagePath']
        })
    return jsonify(sendObject), 200

#results button will be there if atleast 1 sprint is completed in current loop
#ignore above statement. result andd retake button will appear together always. that means results are of all sprints combined.
#retake is only when current loop target is achieved/accuracy
#resume is only when a sprint is paused
# target can only be changed in bottom sheet and that too it cannot be less than already mentioned target
# target cannot be changed in a sprint set. ignore above comment
#attempted not for now
@app.route('/floopsBottomSheet/', methods=['POST'])
def floopsBottomSheet():
    userId = request.form.get('userId')
    testId = request.form.get('testId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -testId:'+str(testId))

    testData, errorCode = getTest({'id':testId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
        return jsonify({'error':testData}), errorCode

    userTestData, errorCode = getUserTest({'userId':userId, 'testId':testId, 'rOrder':1})
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode
    elif errorCode == 404:
        userTestData = None

    if userTestData:
        _, _, target, achieved = getSprintSetDetails(userId, testId, userTestData.id)
        if not target:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing sprintset')
            return jsonify({'error': 'Error in accessing sprintset details'}), 500

    sendObject = {
        'status':1,
        'imagePath': testData.imagePath,
        'name': testData.name,
        'preparedBy': testData.preparedBy,
        'tags': testData.tags,
        'description': testData.description,
        'target': userTestData.target if userTestData else None,
        'achieved': achieved if userTestData else None,
        'start': True if not userTestData else False,
        'resume': True if userTestData and achieved < userTestData.target else False,
        'results': True if userTestData and achieved >= userTestData.target else False,
        'userTestId': userTestData.id if userTestData else None
    }
    return jsonify(sendObject), 200

def getQuestionSendObject(questionIds, isPractice, resumeQuesId='', userTestId=0):
    sendObject = {
        'status':1,
        'question': []
    }
    for i, qId in enumerate(questionIds.split(',')):
        questionData, errorCode = getQuestion({'id':qId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionData)
            return {'error':questionData}, errorCode

        questionFormatData, errorCode = getQuestionFormat({'id':questionData.format})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionFormatData)
            return {'error':questionFormatData}, errorCode

        format = questionFormatData.code
        questionObject = {
        'questionId':int(qId),
        'questionTags':questionData.tags,
        'format':format,
        'level':int(questionData.difficultyLevel),
        'hints':questionData.hints,
        'ansExplanation':questionData.ansExplanation if isPractice else None,
        'ansExpImage':questionData.ansExpImage if isPractice else None,
        'previousYearApearance':questionData.previousYearApearance,
        'response':None,
        'questionText':questionData.text
        }

        if resumeQuesId != '':
            userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':userTestId, 'questionId':qId})
            if errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+userQuestionTestData)
                return {'error':userQuestionTestData}, errorCode
            elif errorCode == 200:
                questionObject['response'] = userQuestionTestData.answer

        if format == 'MCQ' or format == 'MSQ' or format == 'Drag & Drop' or format == 'Sequence':
            questionMcqMsqDadSeqData, errorCode = getQuestionMcqMsqDadSeq({'questionId':qId})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionMcqMsqDadSeqData)
                return {'error':questionMcqMsqDadSeqData}, errorCode

            questionObject['questionImagePath'] =  questionMcqMsqDadSeqData.imagePath if questionMcqMsqDadSeqData.imagePath else None
            questionObject['choice1'] = questionMcqMsqDadSeqData.choice1
            questionObject['choice1ImagePath'] = questionMcqMsqDadSeqData.choice1ImagePath
            questionObject['choice2'] = questionMcqMsqDadSeqData.choice2
            questionObject['choice2ImagePath'] = questionMcqMsqDadSeqData.choice2ImagePath
            questionObject['choice3'] = questionMcqMsqDadSeqData.choice3
            questionObject['choice3ImagePath'] = questionMcqMsqDadSeqData.choice3ImagePath
            questionObject['choice4'] = questionMcqMsqDadSeqData.choice4
            questionObject['choice4ImagePath'] = questionMcqMsqDadSeqData.choice4ImagePath
            questionObject['answer'] =  questionMcqMsqDadSeqData.correctChoiceSeq if isPractice else None
        elif format == 'Fill' or format == 'True/False':
            questionFillTorFData, errorCode = getQuestionFillTorF({'questionId':qId})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionFillTorFData)
                return {'error':questionFillTorFData}, errorCode

            questionObject['questionImagePath'] = questionFillTorFData.imagePath if questionFillTorFData.imagePath else None
            questionObject['answer'] = questionFillTorFData.correctAnswer if isPractice else None
        elif format == 'Match':
            questionMatchData, errorCode = getQuestionMatch({'questionId':qId})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionMatchData)
                return {'error':questionMatchData}, errorCode

            # questionObject['questionImagePath'] =  questionMatchData.imagePath if questionMatchData.imagePath else None
            questionObject['leftChoice1'] = questionMatchData.leftChoice1
            questionObject['leftChoice1ImagePath'] = questionMatchData.leftChoice1ImagePath
            questionObject['leftChoice2'] = questionMatchData.leftChoice2
            questionObject['leftChoice2ImagePath'] = questionMatchData.leftChoice2ImagePath
            questionObject['leftChoice3'] = questionMatchData.leftChoice3
            questionObject['leftChoice3ImagePath'] = questionMatchData.leftChoice3ImagePath
            questionObject['leftChoice4'] = questionMatchData.leftChoice4
            questionObject['leftChoice4ImagePath'] = questionMatchData.leftChoice4ImagePath
            questionObject['rightChoice1'] = questionMatchData.rightChoice1
            questionObject['rightChoice1ImagePath'] = questionMatchData.rightChoice1ImagePath
            questionObject['rightChoice2'] = questionMatchData.rightChoice2
            questionObject['rightChoice2ImagePath'] = questionMatchData.rightChoice2ImagePath
            questionObject['rightChoice3'] = questionMatchData.rightChoice3
            questionObject['rightChoice3ImagePath'] = questionMatchData.rightChoice3ImagePath
            questionObject['rightChoice4'] = questionMatchData.rightChoice4
            questionObject['rightChoice4ImagePath'] = questionMatchData.rightChoice4ImagePath
            questionObject['answer'] =  questionMatchData.correctChoiceSeq if isPractice else None
        sendObject['question'].append(questionObject)
    return sendObject, 200

@app.route('/fgetQuestionsForDisplay/', methods=['POST'])
def fgetQuestionsForDisplay():
    questionIds = request.form.get('questionIds')
    showAnswer = request.form.get('showAnswer')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -questionIds:'+str(questionIds)+' -showAnswer:'+str(showAnswer))

    if showAnswer.lower() == "false":
        showAnswer = False
    error, errorCode = getQuestionSendObject(questionIds, showAnswer)
    return jsonify(error), errorCode


def getNDynamicQuestionIds(questionIdPool, questionIdsUsed, n, level):
    generatedQuestionIds = ''
    questionIds = set(questionIdPool.split(','))
    questionIds = questionIds.difference(set(questionIdsUsed.split(',')))
    count, initLevel = 0, level
    while count < n or len(questionIds) == 0:
        questionsData, errorCode = getAllQuestions({'ids':questionIds, 'difficultyLevel':level, 'limit':n})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' error:'+questionsData)
            questionsData, errorCode

        count += len(questionsData)
        addedQuestions = ''.join(str(question['id'])+',' for question in questionsData)
        questionIds.difference(set(addedQuestions))
        generatedQuestionIds += addedQuestions
        level = (level + 1) % len(config2['difficultyLevel'].items())
        if initLevel == level:
            break   #no more questions available
    return generatedQuestionIds[:-1], 200


#check max allowed timings for all kinds of tests
@app.route('/ftestStart/', methods=['POST'])
def ftestStart():   #start showing questions
    userId = request.form.get('userId')
    testId = request.form.get('testId')             #new dynamic, static, loop tests
    userTestId = request.form.get('userTestId')     #paused or practice
    displayedOnHomePage = request.form.get('displayedOnHomePage')   #boolean if test started from homepage
    customName = request.form.get('customName') #if new customTest
    loopTarget = request.form.get('loopTarget')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -testId:'+str(testId)\
    +' -userTestId:'+str(userTestId)+' -displayedOnHomePage:'+str(displayedOnHomePage)+' -customName:'+str(customName)\
    +' -loopTarget:'+str(loopTarget))

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    if userData.testsRemaining <= 0:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+' . message:you have no tests remaining')
        return jsonify({'status':1, 'msg':'you have no tests remaining'})

    testType = 'Concept based'
    questionIds, isDynamic, resumeQuesId = '', False, None
    practiceTest = False

    if userTestId:       #for paused or practice  #dynamic/static/custom/loops
        userTestData, errorCode = getUserTest({'id':userTestId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestData)
            return jsonify({'error':userTestData}), errorCode

        practiceTest = userTestData.practiceTest
        questionIds = userTestData.questionIds
        if userTestData.paused:
            resumeQuesId = userTestData.resumeQuesId
        if practiceTest and int(userTestData.customTestLevelIds) > 0:
            error, errorCode = updateUserTest({'id':userTestId}, {'questionIds':userTestData.sprintQuestions, 'progress':0})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
                return jsonify({'error':error}), errorCode

            error, errorCode = deleteAllUserQuestionTests({'userTestId':userTestId})
            if errorCode == 500:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
                return jsonify({'error':error}), errorCode

        if userTestData.target!=0:
            testType= 'Loops'

    elif testId:  #new test static/dynamic/loop   #or retake test
        testData, errorCode = getTest({'id':testId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
            return jsonify({'error':testData}), errorCode

        questionIds = testData.questionIds
        sprintQuestions = ''
        if not testData.isStaticTest:
            questionIds, errorCode = getNDynamicQuestionIds(questionIds, '', 3, 1)
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+questionIds)
                return jsonify({'error':questionIds}), errorCode

        if not loopTarget:
            loopTarget = 0
            sprintNumber = None
        else:
            sprintQuestions = testData.questionIds
            sprintNumber = '1'
        if not displayedOnHomePage:
            displayedOnHomePage = False

        userTest = UserTest(userId, testId, None, None, None, None, None, sprintNumber,\
        False, 0, 0, 0, False, False, 0, questionIds, 0, displayedOnHomePage, loopTarget, sprintQuestions, datetime.datetime.now(indianTime), 0, 0, 0, 0, 0)
        userTestId, errorCode = insertUserTest(userTest)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+str(userTestId))
            return jsonify({'error':str(userTestId)}), errorCode

    elif customName:    #new custom test
        subjectId = request.form.get('subjectId')  #comma separated
        chapterIds = request.form.get('chapterIds')  #comma separated
        conceptIds = request.form.get('conceptIds') #comma separated
        level = request.form.get('level')   #comma separated
        format = request.form.get('format') #comma separated
        questionIds = request.form.get('questionIds')

        app.logger.debug(inspect.currentframe().f_code.co_name+' continued -subjectId:'+str(subjectId)\
        +' -chapterIds:'+str(chapterIds)+' -conceptIds:'+str(conceptIds)+' -level:'+str(level)+' -format:'+str(format)\
        +' -questionIds:'+str(questionIds))

        userTest = UserTest(userId, None, customName, subjectId, chapterIds, conceptIds, level,\
        format, False, 0, 0, 0, False, False, 0, questionIds, 0, False, 0, 0, datetime.datetime.now(indianTime), 0, 0, 0, 0, 0)
        userTestId, errorCode = insertUserTest(userTest)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+str(userTestId))
            return jsonify({'error':str(userTestId)}), errorCode

    sendObject, errorCode = getQuestionSendObject(questionIds, practiceTest, resumeQuesId, userTestId)
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+sendObject)
        jsonify({'error':sendObject}), errorCode

    if loopTarget:
        testType = 'Loops'
    elif customName:
        testType = 'Custom Test'
    sendObject['userTestId'] = userTestId
    sendObject['resumeQuesId'] = resumeQuesId
    sendObject['testType'] = testType
    sendObject['practiceTest'] = practiceTest

    error, errorCode = updateUser({'id':userId}, {'subtractTestsRemaining':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    try:
        subsActivity = db.session.query(SubscriptionActivity).filter_by(userId=userId).\
        filter(SubscriptionActivity.expiryDate>=datetime.datetime.now(indianTime).date()).\
        filter(SubscriptionActivity.testsRemaining>0).first()
        subsActivity.testsRemaining -= 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in updating subsActivity records, '+str(e))
        return jsonify({'error':'Error in updating SubscriptionActivity records. Details: ' + str(e)}), 500

    return jsonify(sendObject), 200


@app.route('/fquestionBookmark/', methods=['POST'])
def fquestionBookmark():
    userId = request.form.get('userId')
    questionId = request.form.get('questionId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -questionId:'+str(questionId))

    errorCode = 500
    try:
        userQuestion = db.session.query(UserQuestion).filter(UserQuestion.userId == userId).\
        filter(UserQuestion.questionId == questionId).first()
        if not userQuestion:
            userQuestion = UserQuestion(userId, questionId, True, False)
            db.session.add(userQuestion)
            db.session.commit()
            userQuestionBookmark = 1
            errorCode = 201
        elif not userQuestion.bookmark and not userQuestion.report:
            db.session.query(userQuestion)
            db.session.commit()
        else:
            userQuestion.bookmark ^= 1
            userQuestionBookmark = userQuestion.bookmark
            db.session.commit()
            errorCode = 200
    except Exception as e:
        db.session.rollback()
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error while adding/updating userQuestion for bookmarks, '+str(e))
        return jsonify({'error':'Error while adding or updating userQuestion for bookmarks. Details:'+str(e)}), errorCode

    return jsonify({'status':1, 'bookmark':userQuestionBookmark}), 200


#dynamic
#1st 3 easy
# if atleast 2 are correct then 3 next level
# if only 1 correct then demote level
#atleast 10 ques ( 3 easy, again 3 easy if(no promotion) or 3 medium, continue untill 10... if easy are done then for 10 completion give medium )
@app.route('/fquestionNext/', methods=['POST'])
def fquestionNext():
    userTestId = request.form.get('userTestId')
    questionId = request.form.get('questionId')
    response = request.form.get('response')     #in particular format
    timetaken = request.form.get('timetaken')
    review = request.form.get('review')     #boolean

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId)+' -questionId:'+str(questionId)\
    +' -response:'+str(response)+' -timetaken:'+str(timetaken)+' -review:'+str(review))

    if timetaken:
        timetaken = int(timetaken)
    else:
        timetaken = 0

    if not review or review == 0 or review == '0' or review == 'false' or review == 'False':
        review = False
    elif review == 'true':
        review = True

    questionData, errorCode = getQuestion({'id':int(questionId)})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionData)
        return jsonify({'error':questionData}), errorCode

    questionFormatData, errorCode = getQuestionFormat({'id':questionData.format})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionFormatData)
        return jsonify({'error':questionFormatData}), errorCode

    format = questionFormatData.code
    #assessing and storing
    if format == 'MCQ' or format == 'MSQ' or format == 'Sequence' or format == 'Drag & Drop':
        questionMcqMsqDadSeqData, errorCode = getQuestionMcqMsqDadSeq({'questionId':int(questionId)})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionMcqMsqDadSeqData)
            return jsonify({'error':questionMcqMsqDadSeqData}), errorCode

        actualAnswer = questionMcqMsqDadSeqData.correctChoiceSeq
    elif format == 'Match':
        questionMatchData, errorCode = getQuestionMatch({'questionId':int(questionId)})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionMatchData)
            return jsonify({'error':questionMatchData}), errorCode

        actualAnswer = questionMatchData.correctChoiceSeq
    elif format == 'Fill' or format == 'True/False':
        questionFillTorFData, errorCode = getQuestionFillTorF({'questionId':int(questionId)})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionFillTorFData)
            return jsonify({'error':questionFillTorFData}), errorCode

        actualAnswer = questionFillTorFData.correctAnswer

    isCorrect, marks, isPartial = False, 0, False
    if response:
        if response == actualAnswer:
            marks = int(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][0])
            isCorrect = True
        elif format == 'MSQ' and response:
            response = response[:-1] if response[-1] == ',' else response
            responseSet = set(sorted(set(response.split(','))))
            response = ",".join(responseSet)
            answerSet = set(sorted(set(actualAnswer.split(','))))
            if len(responseSet&answerSet) == len(answerSet):
                isCorrect = True
            elif len(responseSet&answerSet) > 0:
                isPartial = True
        elif format == 'Sequence' or format == 'Drag & Drop' or format == 'Match':
            for res, aa in zip(response, actualAnswer):
                if res == aa:
                    isPartial = True
                    break

    if isPartial:
        marks = float(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][2])
    elif not isCorrect:
        marks = float(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][1])

    userTestData, errorCode = getUserTest({'id':int(userTestId)})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    testData, errorCode = getTest({'id':userTestData.testId})
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+testData)
        return jsonify({'error':testData}), errorCode
    elif errorCode == 404:
        testData = None

    generateQuestion = False
    questions = userTestData.questionIds.split(',')
    userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':int(userTestId), 'questionId':int(questionId)})
    if errorCode == 200:
        error, errorCode = updateUserQuestionTest({'userTestId':int(userTestId), 'questionId':int(questionId)}, {'review':review, 'answer':response, 'isCorrect':isCorrect, \
        'isPartial':isPartial, 'marks':marks, 'timetaken':timetaken})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

    elif errorCode == 404:
        if testData: #not custom test
            if not testData.isStaticTest and not userTestData.practiceTest:  #for loops and dynamic test
                if questionData.id == int(questions[-1]):
                    generateQuestion = True
        userQuestionTest = UserQuestionTest(int(userTestId), int(questionId), review, True, response, isCorrect,\
        isPartial, marks, timetaken, None)
        userQuestionTestId, errorCode = insertUserQuestionTest(userQuestionTest)
        if errorCode != 201:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+str(userQuestionTestId))
            return jsonify({'error':str(userQuestionTestId)}), errorCode

    else:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestData)
        return jsonify({'error':userQuestionTestData}), errorCode

    if userTestData.target != 0 and userTestData.accuracy * len(userTestData.questionIds.split(','))/len(testData.questionIds.split(',')) > userTestData.target:
        return jsonify({
                    'status':1,
                    'poorPerformanceMessage': 'The loops has successfully stopped as you have achieved your traget score, you can explore the results',
                }), 200

    error, errorCode = updateUserTest({'id':int(userTestId)}, {'paused':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    sendObject = {'poorPerformanceMessage': None}
    poorPerformanceMessage = 'The test stopped due to your poor performance, take practice test and come back'
    if generateQuestion:    #========================================================================================
        numberOfCorrects, numberOfQuestionsToBeGenerated, numberOfQuestionsUsed, highestLevels, level = \
        0, 3, len(questions), len(config2['difficultyLevel'].items()), int(questionData.difficultyLevel)
        if isCorrect:
            numberOfCorrects += 1

        userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':int(userTestId), 'questionId':int(questions[-2])})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestData)
            return jsonify({'error':userQuestionTestData}), errorCode

        if userQuestionTestData.isCorrect:
            numberOfCorrects += 1

        userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':int(userTestId), 'questionId':int(questions[-3])})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestData)
            return jsonify({'error':userQuestionTestData}), errorCode

        if userQuestionTestData.isCorrect:
            numberOfCorrects += 1

        if numberOfCorrects > 1:
            nextLevel = (level + 1) % len(config2['difficultyLevel'].items()) if level < highestLevels else level
        else:
            nextLevel = level - 1 if level > 1 else level

        questionIdPool = testData.questionIds
        if userTestData.sprintQuestions != '':
            poorPerformanceMessage = 'The test stopped due to your poor performance, take a next sprint to achieve the Target Score'
            questionIdPool = userTestData.sprintQuestions

        questionIds, errorCode = getNDynamicQuestionIds(questionIdPool, userTestData.questionIds, numberOfQuestionsToBeGenerated, nextLevel)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionIds)
            return jsonify({'error':questionIds}), errorCode

        questionData, errorCode = getQuestion({'id':int(questionIds.split(',')[0])})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionData)
            return jsonify({'error':questionData}), errorCode

        if questionIds == '':
            return jsonify({
                'poorPerformanceMessage': 'The test has finished, Take a practice test to master the concepts.',
                'status':1
            }), 200

        elif numberOfQuestionsUsed == 10:
            return jsonify({
                    'status':1,
                    'poorPerformanceMessage': poorPerformanceMessage,
                }), 200

        elif numberOfCorrects < 2 and level >= int(questionData.difficultyLevel):
            if numberOfQuestionsUsed == 9:
                questionIds = questionIds.split(',')[0]
            elif numberOfQuestionsUsed > 10:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId)+'Poor Performance')
                return jsonify({
                    'status':1,
                    'poorPerformanceMessage': poorPerformanceMessage,
                }), 200

        sendObject, errorCode = getQuestionSendObject(questionIds, userTestData.practiceTest)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+sendObject)
            jsonify({'error':sendObject}), errorCode

        sendObject['poorPerformanceMessage'] = None
        userTestUpdateData = {'questionIds': userTestData.questionIds}
        for qId in questionIds.split(','):
            userTestUpdateData['questionIds'] += ',' + str(qId)

        error, errorCode = updateUserTest({'id':int(userTestId)}, userTestUpdateData)
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

    return jsonify(sendObject), 200


@app.route('/ftestPaused/', methods=['POST'])
def ftestPaused():
    userTestId = request.form.get('userTestId')
    resumeQuesId = request.form.get('resumeQuesId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId))

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    userQuestionTestsData, errorCode = getAllUserQuestionTests({'userTestId':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestsData)
        return jsonify({'error':userQuestionTestsData}), errorCode

    progress = int(len(userQuestionTestsData)//len(userTestData.questionIds.split(',')) * 100)
    dateTime = datetime.datetime.now(indianTime)
    error, errorCode = updateUserTest({'id':userTestId}, {'paused':True, 'progress':progress, 'dateTime':dateTime, \
    'resumeQuesId':resumeQuesId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    return jsonify({'status':1}), 200


@app.route('/ftestSummary/', methods=['POST'])
def ftestSummary():
    userTestId = request.form.get('userTestId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId))

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    userQuestionTestsData, errorCode = getAllUserQuestionTests({'userTestId':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestsData)
        return jsonify({'error':userQuestionTestsData}), errorCode

    sendObject = {
        'status':1,
        'totalQuestions':len(userQuestionTestsData),
        'answered':0,
        'notAnswered':0,
        'markedForReview':0,
        'answeredAndMarkedForReview':0,
        'notVisited':0
    }
    for uQT in userQuestionTestsData:
        # if not uQT['seen']:
        #     sendObject['notVisited'] += 1
        if uQT['answer']:
            sendObject['answered'] += 1
            if uQT['review']:
                sendObject['answeredAndMarkedForReview'] += 1
        else:
            if uQT['seen']:
                sendObject['notAnswered'] += 1
            if uQT['review']:
                sendObject['markedForReview'] += 1

    testData, errorCode = getTest({'id':userTestData.testId, 'isStaticTest':True})
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+testData)
        return jsonify({'error':testData}), errorCode
    elif errorCode == 404:
        testData = None

    if testData or userTestData.practiceTest or userTestData.customName:
        sendObject['totalQuestions'] = len(testData.questionIds.split(',')) if testData else len(userTestData.questionIds.split(','))
        sendObject['notAnswered'] = sendObject['totalQuestions'] - sendObject['answered']
    sendObject['notVisited'] = sendObject['totalQuestions'] - sendObject['answered'] - sendObject['notAnswered']
    return jsonify(sendObject), 200

def updateBadges(userId, givenSubjectName):   #TODO allrounder performance
    userTestsData, errorCode = getAllUserTests({'userId':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestsData)
        return userTestsData, errorCode

    final, numberOfTests, imagePath = -1, 0, None
    for ut in userTestsData:
        if ut['customName']:
            subjectId = ut['customSubjectId']
        elif ut['testId']:
            testData, errorCode = getTest({'id':ut['testId']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
                return testData, errorCode

            subjectId = testData.subjectId

        subjectData, errorCode = getSubject({'id':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
            return subjectData, errorCode

        if givenSubjectName != subjectData.name:
            continue
        numberOfTests += 1

    try:
        progressBadges = Badges.query.filter_by(type='progress').all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing Badges for progress, '+str(e))
        return 'Error in accessing Badges for progress details:'+str(e), 500

    for i, b in enumerate(progressBadges):
        if b.name.split('-')[0] == givenSubjectName and config12['progressBadges'][i%5] < numberOfTests:
            final = b.id

    if final != -1:
        try:
            userBadges = db.session.query(UserBadges).filter(UserBadges.userId == userId).\
            filter(UserBadges.subjectName == givenSubjectName).first()
            if userBadges:
                userBadges.badgeId = final
            else:
                db.session.add(UserBadges(userId, final, givenSubjectName, datetime.datetime.now(indianTime)))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in updating/inserting userbadges for progress, '+str(e))
            return 'Error in updating/inserting UserBadges for progress details:'+str(e), 500

    testCount = {'P':0, 'A':[]}
    for i, ut in enumerate(userTestsData):
        if ut['practiceTest']:
            testCount['P'] += 1
        else:
            for k,v in config13['performanceBadges'].items():
                if k == 'P' or k == 'A':
                    continue
                if k not in testCount.keys():
                    testCount[k] = {v:0}
                if ut['score'] >= int(k):
                    testCount[k][v] += 1
                elif testCount[k][v] < v:
                    testCount[k][v] = 0

    try:
        performanceBadge = Badges.query.filter_by(type='performance').first()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing badges for performance, '+str(e))
        return 'Error in accessing Badges for performance details:'+str(e), 500

    final, id, temp, i = performanceBadge.id, -1, -1, 0
    for k,v in config13['performanceBadges'].items():
        if k == 'P':
            if testCount[k] >= v:
                temp = i
        elif k =='A':
            None
        elif testCount[k][v] >= v:
            temp = i
        if id < temp:
            id = temp
        i+=1

    if final <= final + id:
        try:
            userBadges = db.session.query(UserBadges).filter(UserBadges.userId == userId).\
            filter(type=='performance').all()
            if userBadges:
                userBadges.badgeId = final + id
            else:
                db.session.add(UserBadges(userId, final+id, datetime.datetime.now(indianTime)))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in updating/inserting userbadges for performance, '+str(e))
            return 'Error in updating/inserting UserBadges for performance details:'+str(e), 500

    return None, 200

@app.route('/ftestSubmit/', methods=['POST'])
def ftestSubmit():
    userTestId = request.form.get('userTestId')
    displayedOnHomePage = request.form.get('displayedOnHomePage')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId)+' -displayedOnHomePage:'+str(displayedOnHomePage))

    if displayedOnHomePage:
        displayedOnHomePage = True
    else:
        displayedOnHomePage = False

    coinsEarned, maxCoins, time, score, questionIds, correctQuestionIds, timetaken, numberOfCorrects, totalEntries  = 0, 0, 0, 0, '', '', 0, 0, 0
    confidence, confidenceTotal, scoreTotal, conceptIdsSet = 0, 0, 0, {}
    difficultyLevelCounts, formatCounts = [0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0]  #easyScore, easyScoreTotal, mediumScore, ......

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    userData, errorCode = getUser({'id':userTestData.userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    testData = None
    if userTestData.testId:
        testData, errorCode = getTest({'id':userTestData.testId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+testData)
            return jsonify({'error':testData}), errorCode

    isGeneralStaticFormat = True if userTestData.practiceTest or (userTestData.testId and testData.isStaticTest) or (userTestData.customName) else 0

    # for uQT in UserQuestionTest.query.filter_by(userTestId=userTestId).all():
    for qId in userTestData.questionIds.split(','):
        correctAnswered, wrongAnswered, notAnswered = False, False, False
        userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':userTestId, 'questionId':qId})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestData)
            return jsonify({'error':userQuestionTestData}), errorCode
        elif errorCode == 404:
            userQuestionTestData = None

        questionData, errorCode = getQuestion({'id':qId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionData)
            return jsonify({'error':questionData}), errorCode

        coin = config3['coins'][config2['difficultyLevel'][questionData.difficultyLevel]]
        allotedTime = config4['time'][config2['difficultyLevel'][questionData.difficultyLevel]]
        if userQuestionTestData:
            score += userQuestionTestData.marks
            timetaken += userQuestionTestData.timetaken
            if userQuestionTestData.isCorrect == True:
                correctQuestionIds += str(qId) + ','
                coinsEarned += coin
                numberOfCorrects += 1
                if userQuestionTestData.timetaken < allotedTime/2:
                    confidence += 1
                correctAnswered = True
            else:
                wrongAnswered = True
                questionIds += str(qId) + ','
                maxCoins += coin
                time += allotedTime

            if userQuestionTestData.seen:
                confidenceTotal += 1
            scoreTotal += int(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][0])

            totalEntries += 1
        else:
            notAnswered = True
            questionIds += str(qId) + ','
            maxCoins += coin
            time += allotedTime

            if isGeneralStaticFormat:
                totalEntries += 1

        if correctAnswered:
            if questionData.conceptId not in conceptIdsSet.keys():
                conceptIdsSet[questionData.conceptId] = [0, 0]

            conceptIdsSet[questionData.conceptId][0] += userQuestionTestData.marks
            conceptIdsSet[questionData.conceptId][1] += int(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][0])

            difficultyLevelCounts[2*(int(questionData.difficultyLevel)-1)]+=1
            difficultyLevelCounts[2*(int(questionData.difficultyLevel)-1)+1]+=1

            formatCounts[2*(questionData.format-1)]+=1
            formatCounts[2*(questionData.format-1)+1]+=1

        elif wrongAnswered or (isGeneralStaticFormat and notAnswered):
            if questionData.conceptId not in conceptIdsSet.keys():
                conceptIdsSet[questionData.conceptId] = [0, 0]
            if userQuestionTestData:
                conceptIdsSet[questionData.conceptId][0] += userQuestionTestData.marks
            conceptIdsSet[questionData.conceptId][1] += int(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][0])

            difficultyLevelCounts[2*(int(questionData.difficultyLevel)-1)]+=1
            difficultyLevelCounts[2*(int(questionData.difficultyLevel)-1)+1]+=1

            formatCounts[2*(questionData.format-1)]+=1
            formatCounts[2*(questionData.format-1)+1]+=1

    userTestUpdateData = {
        'paused':False,
        'progress':100,
        'coinsEarned':coinsEarned,
        'score':score,
        'scoreTotal':scoreTotal,
        'confidence':confidence*100//confidenceTotal if confidenceTotal else 0,
        'timetaken':timetaken,
        'accuracy':(numberOfCorrects*100)//totalEntries if totalEntries else 0,
        'dateTime':datetime.datetime.now(indianTime)
    }

    if userTestData.practiceTest:
        userTestUpdateData['addCustomTestLevelIds'] = 1
        if questionIds == '':
            userTestUpdateData['sprintQuestions'] = ''
    else:
        userTestUpdateData['coins'] = maxCoins + coinsEarned

    error, errorCode = updateUserTest({'id':userTestId}, userTestUpdateData)
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    error, errorCode = updateUser({'id':userTestData.userId}, {'addCoins':coinsEarned})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    customName, customSubjectId, isPracticeTestNeeded = None, None, True
    if testData:
        subjectId = testData.subjectId
        if not testData.isPracticeTestNeeded or testData.isLoop:
            isPracticeTestNeeded = False
    elif userTestData.customName:    #implies custom test
            customName = userTestData.customName
            subjectId = customSubjectId = userTestData.customSubjectId

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    totalTestsOverall, errorCode = getAllTests({'subjectIds':[sub['id'] for sub in subjectsData], 'count':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+totalTestsOverall)
        return jsonify({'error':totalTestsOverall}), errorCode

    totalSubjectTestsOverall, errorCode = getAllTests({'subjectId':subjectId, 'count':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+totalSubjectTestsOverall)
        return jsonify({'error':totalSubjectTestsOverall}), errorCode

    isAnalysisLoop = 1 if userTestData.target and userTestData.customTestFormats == '1' else 0
    isAnalysisStatic = 1 if userTestData.testId and not userTestData.practiceTest and testData.isStaticTest else 0
    isAnalysisCustom = 1 if userTestData.customName and not userTestData.practiceTest else 0
    isAnalysisConcept = 1 if userTestData.testId and not userTestData.practiceTest and not testData.isLoop and not testData.isStaticTest else 0
    isAnalysisOther = 1 if not isAnalysisLoop and not isAnalysisStatic and not isAnalysisCustom and not isAnalysisConcept else 0
    #updating analytics table
    for timeType in ["This week", 'This month', 'This year']:
        error, errorCode = updateAnalysis({'userId':userTestData.userId, 'subjectId':subjectId, 'timeType':timeType}, {
            'confidence':confidence,
            'confidenceTotal':confidenceTotal,
            'score':score,
            'scoreTotal':scoreTotal,
            'totalCorrects':numberOfCorrects,
            'totalQuestions':totalEntries,
            'totalTests':totalSubjectTestsOverall,
            'totalLoopTests':isAnalysisLoop,
            'totalCustomTests':isAnalysisCustom,
            'totalStaticTests':isAnalysisStatic,
            'totalConceptTests':isAnalysisConcept,
            'totalOtherTests':isAnalysisOther,
            'totalUserTests':1,
            'difficultyLevelCounts':difficultyLevelCounts,
            'formatCounts':formatCounts
        })
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

        error, errorCode = updateAnalysis({'userId':userTestData.userId, 'subjectId':None, 'timeType':timeType}, {
            'confidence':confidence,
            'confidenceTotal':confidenceTotal,
            'score':score,
            'scoreTotal':scoreTotal,
            'totalCorrects':numberOfCorrects,
            'totalQuestions':totalEntries,
            'totalTests':totalTestsOverall,
            'totalLoopTests':isAnalysisLoop,
            'totalCustomTests':isAnalysisCustom,
            'totalStaticTests':isAnalysisStatic,
            'totalConceptTests':isAnalysisConcept,
            'totalOtherTests':isAnalysisOther,
            'totalUserTests':1
        })
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
            return jsonify({'error':error}), errorCode

    try:
        for conId, scoreList in conceptIdsSet.items():
            userConcept = db.session.query(UserConcept).filter_by(conceptId=conId).first()
            if userConcept:
                userConcept.score += scoreList[0]
                userConcept.scoreTotal += scoreList[1]
                db.session.commit()
            else:
                db.session.add(UserConcept(userTestData.userId, conId, subjectId, scoreList[0], scoreList[1]))
                db.session.commit()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:Error in inserting/updating UserConcepts, '+str(e))
        return jsonify({'error': 'Error in inserting/updating userConcepts details:'+str(e)}), 500

    sendObject = {}
    if userTestData.target:
        _, _, target, achieved = getSprintSetDetails(userTestData.userId, userTestData.testId, userTestId)
        if not target:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:Error in accessing sprintset')
            return jsonify({'error': 'Error in accessing sprintset details'}), 500

    if (isPracticeTestNeeded or (userTestData.target and target <= achieved)) and questionIds != '':    #creating practice test
        #only 1 pratice test in db per test, append new questions to existing if it exists
        error, errorCode = updateUserTest({'practiceTest':True, 'userId':userTestData.userId, 'testId':userTestData.testId, 'customName':userTestData.customName}, {'sprintQuestions':questionIds[:-1]})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
            return jsonify({'error':error}), errorCode
        elif errorCode == 404:
            practiceTestNumber, sprintNumber, questions, sprintQuestions, isPracticeTest = '0', None, questionIds[:-1], questionIds[:-1], True
            if userTestData.target:
                practiceTestNumber, sprintNumber, isPracticeTest, sprintQuestions, time = None, str(int(userTestData.customTestFormats) + 1), False, '', 0
                if correctQuestionIds == '':
                    sprintQuestions = userTestData.sprintQuestions
                elif userTestData.sprintQuestions:
                    sprintQuestions = ','.join(map(str, set(userTestData.sprintQuestions.split(',')) - set(correctQuestionIds[:-1].split(','))))
                questions, errorCode = getNDynamicQuestionIds(sprintQuestions, '', 3, 1)
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionIds)
                    return jsonify({'error':questionIds}), errorCode

            userTestCreated = UserTest(userTestData.userId, userTestData.testId, customName, customSubjectId, \
            None, None, practiceTestNumber, sprintNumber, False, 0, 0, 0, False, isPracticeTest, maxCoins, questions, \
            time, displayedOnHomePage, userTestData.target, sprintQuestions, datetime.datetime.now(indianTime), 0, 0, 0, 0, 0)
            error, errorCode = insertUserTest(userTestCreated)
            if errorCode != 201:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+str(error))
                return jsonify({'error':str(error)}), errorCode

        # notification practice test
        if not userTestData.target:
            sendObject['message'] = fnotification("Your practice test for the submitted is ready", "", "", userTestData.userId,\
            {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'ftestHome', 'userId':str(userTestData.userId), 'subjectId':str(subjectId)})

    sendObject = {'status':1, 'message':None, 'mobile':userData.mobile}
    if not userTestData.practiceTest:
        subjectData, errorCode = getSubject({'id':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+subjectData)
            return subjectData, errorCode

        updateBadges(userTestData.userId, subjectData.name)

    # Notification - user running out of tests
    testsRemaining = userData.testsRemaining
    if testsRemaining == 0:
        sendObject['message'] = fnotification('You have no tests remaining, subscribe to continue', '', '', userTestData.userId, \
        {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'fsubscription', 'userId':str(userTestData.userId)})
    elif testsRemaining < 3:
        sendObject['message'] = fnotification('You have '+ str(testsRemaining) + ' tests remaining, subscribe to continue', '', '', userTestData.userId,\
        {'click_action': 'FLUTTER_NOTIFICATION_CLICK', 'screen':'fsubscription', 'userId':str(userTestData.userId)})
    return jsonify(sendObject), 200


@app.route('/ftestBookmark/', methods=['POST'])
def ftestBookmark():
    userTestId = request.form.get('userTestId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId))

    error, errorCode = updateUserTest({'id':userTestId}, {'toggleBookmark':1})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+error)
        return jsonify({'error':error}), errorCode

    return jsonify({'status':1}), 200


def ftestResultsFunc(userTestId):
    totalScore = 0
    overall = {
        'time':0,
        'correct': '',
        'correctTotal': 0,
        'incorrect': '',
        'incorrectTotal': 0,
        'partial': '',
        'partialTotal': 0,
        'notAnswered': '',
        'notAnsweredTotal': 0,
        'totalQuestions':0
    }

    concept = []
    difficultyLevel = []
    questionFormat = []

    conceptHelper, conceptCounter, difficultyLevelHelper, difficultyLevelCounter, questionFormatHelper, questionFormatCounter = {}, 0, {}, 0, {}, 0

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    for qId in userTestData.questionIds.split(','):
        questionData, errorCode = getQuestion({'id':qId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionData)
            return jsonify({'error':questionData}), errorCode

        difficultyLevelNumber = config2['difficultyLevel'][questionData.difficultyLevel]
        if difficultyLevelNumber not in difficultyLevelHelper.keys():
            difficultyLevelHelper[difficultyLevelNumber] = difficultyLevelCounter
            difficultyLevelCounter += 1
            difficultyLevel.append({
                'level': difficultyLevelNumber,
                'time':0,
                'accuracy':0,
                'correct': '',
                'correctTotal': 0,
                'incorrect': '',
                'incorrectTotal': 0,
                'partial': '',
                'partialTotal': 0,
                'notAnswered': '',
                'notAnsweredTotal': 0,
                'seenTotalQuestions': 0,
                'totalQuestions': 0
            })
        difficultyLevelIter = difficultyLevelHelper[difficultyLevelNumber]

        totalScore += int(config6['marks'][difficultyLevelNumber][0])

        questionFormatData, errorCode = getQuestionFormat({'id':questionData.format})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionFormatData)
            return jsonify({'error':questionFormatData}), errorCode

        questionFormatCode = questionFormatData.code
        if questionFormatCode not in questionFormatHelper.keys():
            questionFormatHelper[questionFormatCode] = questionFormatCounter
            questionFormatCounter += 1
            questionFormat.append({
                'format': questionFormatCode,
                'time':0,
                'accuracy':0,
                'correct': '',
                'correctTotal': 0,
                'incorrect': '',
                'incorrectTotal': 0,
                'partial': '',
                'partialTotal': 0,
                'notAnswered': '',
                'notAnsweredTotal': 0,
                'seenTotalQuestions': 0,
                'totalQuestions': 0
            })
        questionFormatIter = questionFormatHelper[questionFormatCode]

        conceptData, errorCode = getConcept({'id':questionData.conceptId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+conceptData)
            return jsonify({'error':conceptData}), errorCode

        conceptName = conceptData.name
        if conceptName not in conceptHelper.keys():
            conceptHelper[conceptName] = conceptCounter
            conceptCounter += 1
            concept.append({
                'conceptName': conceptName,
                'time':0,
                'correct': '',
                'correctTotal': 0,
                'incorrect': '',
                'incorrectTotal': 0,
                'partial': '',
                'partialTotal': 0,
                'notAnswered': '',
                'notAnsweredTotal': 0,
                'score': 0,
                'scoreTotal': 0,
                'seenTotalQuestions': 0,
                'totalQuestions': 0
            })
        conceptIter = conceptHelper[conceptName]

        userQuestionTestData, errorCode = getUserQuestionTest({'userTestId':userTestId, 'questionId':qId})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestData)
            return jsonify({'error':userQuestionTestData}), errorCode
        elif errorCode == 404:
            userQuestionTestData = None

        if userQuestionTestData:
            questionFormat[questionFormatIter]['time'] += userQuestionTestData.timetaken
            difficultyLevel[difficultyLevelIter]['time'] += userQuestionTestData.timetaken
            concept[conceptIter]['time'] += userQuestionTestData.timetaken
            overall['time'] += userQuestionTestData.timetaken
            if userQuestionTestData.isCorrect:
                questionFormat[questionFormatIter]['correct'] += qId + ','
                questionFormat[questionFormatIter]['correctTotal'] += 1
                difficultyLevel[difficultyLevelIter]['correct'] += qId + ','
                difficultyLevel[difficultyLevelIter]['correctTotal'] += 1
                concept[conceptIter]['correct'] += qId + ','
                concept[conceptIter]['correctTotal'] += 1
                concept[conceptIter]['score'] += userQuestionTestData.marks
                overall['correct'] += qId + ','
                overall['correctTotal'] += 1
            elif userQuestionTestData.isPartial:
                questionFormat[questionFormatIter]['partial'] += qId + ','
                questionFormat[questionFormatIter]['partialTotal'] += 1
                difficultyLevel[difficultyLevelIter]['partial'] += qId + ','
                difficultyLevel[difficultyLevelIter]['partialTotal'] += 1
                concept[conceptIter]['partial'] += qId + ','
                concept[conceptIter]['partialTotal'] += 1
                concept[conceptIter]['score'] += userQuestionTestData.marks
                overall['partial'] += qId + ','
                overall['partialTotal'] += 1
            elif not userQuestionTestData.answer:
                questionFormat[questionFormatIter]['notAnswered'] += qId + ','
                questionFormat[questionFormatIter]['notAnsweredTotal'] += 1
                difficultyLevel[difficultyLevelIter]['notAnswered'] += qId + ','
                difficultyLevel[difficultyLevelIter]['notAnsweredTotal'] += 1
                concept[conceptIter]['notAnswered'] += qId + ','
                concept[conceptIter]['notAnsweredTotal'] += 1
                overall['notAnswered'] += qId + ','
                overall['notAnsweredTotal'] += 1
            elif userQuestionTestData.marks < 0:
                questionFormat[questionFormatIter]['incorrect'] += qId + ','
                questionFormat[questionFormatIter]['incorrectTotal'] += 1
                difficultyLevel[difficultyLevelIter]['incorrect'] += qId + ','
                difficultyLevel[difficultyLevelIter]['incorrectTotal'] += 1
                concept[conceptIter]['incorrect'] += qId + ','
                concept[conceptIter]['incorrectTotal'] += 1
                concept[conceptIter]['score'] += userQuestionTestData.marks
                overall['incorrect'] += qId + ','
                overall['incorrectTotal'] += 1
            questionFormat[questionFormatIter]['seenTotalQuestions'] += 1
            difficultyLevel[difficultyLevelIter]['seenTotalQuestions'] += 1
            concept[conceptIter]['seenTotalQuestions'] += 1
        else:
            questionFormat[questionFormatIter]['notAnswered'] += qId + ','
            questionFormat[questionFormatIter]['notAnsweredTotal'] += 1
            difficultyLevel[difficultyLevelIter]['notAnswered'] += qId + ','
            difficultyLevel[difficultyLevelIter]['notAnsweredTotal'] += 1
            concept[conceptIter]['notAnswered'] += qId + ','
            concept[conceptIter]['notAnsweredTotal'] += 1
            overall['notAnswered'] += qId + ','
            overall['notAnsweredTotal'] += 1

        questionFormat[questionFormatIter]['totalQuestions'] += 1
        difficultyLevel[difficultyLevelIter]['totalQuestions'] += 1
        concept[conceptIter]['totalQuestions'] += 1
        overall['totalQuestions'] += 1
        concept[conceptIter]['scoreTotal'] += int(config6['marks'][config2['difficultyLevel'][questionData.difficultyLevel]][0])

    for iter, _ in enumerate(questionFormat):
        questionFormat[iter]['time'] = int(questionFormat[iter]['time']/questionFormat[iter]['seenTotalQuestions']) if questionFormat[iter]['seenTotalQuestions'] else 0
        questionFormat[iter]['accuracy'] = int(questionFormat[iter]['correctTotal']*100/questionFormat[iter]['seenTotalQuestions']) if questionFormat[iter]['seenTotalQuestions'] else 0
    for iter, _ in enumerate(difficultyLevel):
        difficultyLevel[iter]['time'] = int(difficultyLevel[iter]['time']/difficultyLevel[iter]['seenTotalQuestions']) if difficultyLevel[iter]['seenTotalQuestions'] else 0
        difficultyLevel[iter]['accuracy'] = int(difficultyLevel[iter]['correctTotal']*100/difficultyLevel[iter]['seenTotalQuestions']) if difficultyLevel[iter]['seenTotalQuestions'] else 0
    for iter, _ in enumerate(concept):
        concept[iter]['time'] = int(concept[iter]['time']/concept[iter]['seenTotalQuestions']) if concept[iter]['seenTotalQuestions'] else 0

    return totalScore, overall, concept, difficultyLevel, questionFormat

@app.route('/ftestResults/', methods=['POST'])
def ftestResults(): #repair format => keep conceptName as value inside and not as dict key
    userTestId = request.form.get('userTestId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId))

    totalScore, overall, concept, difficultyLevel, questionFormat = ftestResultsFunc(userTestId)

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error':userTestData}), errorCode

    performance = config9['Performance']["0"]
    for key, val in config9['Performance'].items():
        if (userTestData.score*100)/totalScore > int(key):
            performance = val

    userTestInputData = {'userId':userTestData.userId, 'practiceTest':True}
    if userTestData.testId:
        userTestInputData['testId'] = userTestData.testId
    else:   #customTest
        userTestInputData['customName'] = userTestData.customName

    practiceTestData, errorCode = getUserTest(userTestInputData)
    if errorCode == 500:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+practiceTestData)
        return jsonify({'error':practiceTestData}), errorCode
    elif errorCode == 404:
        practiceTestData = None

    if practiceTestData and practiceTestData.sprintQuestions != '':
        practiceTestId = practiceTestData.id
    else:
        practiceTestId = None

    sendObject = {
        'status':1,
        'accuracy': userTestData.accuracy,
        'score': str(userTestData.score) + '/' + str(totalScore),
        'performance': performance,
        'questionFormat': questionFormat,
        'difficultyLevel': difficultyLevel,
        'coinsEarned': str(userTestData.coinsEarned) + '/' + str(userTestData.coins),
        'concept': concept,
        'overall': overall,
        'practiceTestId': practiceTestId,
        'practiceTest': True if practiceTestId else False,
        'testId': userTestData.testId
    }
    return jsonify(sendObject), 200

def getSprintSetDetails(userId, testId, userTestId):
    userTestData, errorCode = getUserTest({'userId':userId, 'testId':testId, 'customTestFormats':'1', 'lessThanEqualToId':userTestId, 'rOrder':1})
    if errorCode != 200:
        return None, None, None, None

    lastSprintId = firstSprintId = userTestData.id
    achieved = userTestData.accuracy * len(userTestData.questionIds.split(','))//len(userTestData.sprintQuestions.split(','))
    target = userTestData.target
    totalQuestions = len(userTestData.sprintQuestions.split(','))

    try:
        sprints = UserTest.query.filter_by(userId=userId, testId=testId).filter(UserTest.id>firstSprintId).all()
    except Exception as e:
        return None, None, None, None

    for sprint in sprints:
        if sprint.customTestFormats == '1':
            break
        lastSprintId = sprint.id
        achieved += sprint.accuracy * len(sprint.questionIds.split(','))//totalQuestions

    return firstSprintId, lastSprintId, target, achieved


@app.route('/fsprintHistory/', methods=['POST'])
def fsprintHistory():
    userTestId = request.form.get('userTestId')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+str(userTestId))

    userTestData, errorCode = getUserTest({'id':userTestId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userTestData)
        return jsonify({'error': userTestData}), errorCode

    testData, errorCode = getTest({'id':userTestData.testId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+testData)
        return jsonify({'error':testData}), errorCode

    firstSprintId, lastSprintId, target, achieved = getSprintSetDetails(userTestData.userId, testData.id, userTestId)
    if not target:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:Error in accessing sprintset')
        return jsonify({'error': 'Error in accessing sprintSet details'}), 500

    sendObject = {
        'status':1,
        'sprint':[],
        'loopTarget':target,
        'loopAchieved':achieved
    }
    utId = None
    totalCorrect, cumulativeAchieved, cumulativeTarget = 0, 0, target
    try:
        sprints = UserTest.query.filter_by(testId=userTestData.testId).filter(UserTest.id >= firstSprintId).\
        filter(UserTest.id <= lastSprintId).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:Error in accessing sprints, '+str(e))
        return jsonify({'error': 'Error in accessing sprints details:'+str(e)}), 500

    for i, sprint in enumerate(sprints):
        actualTime = 0
        userQuestionTestsData, errorCode = getAllUserQuestionTests({'userTestId':sprint.id})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+userQuestionTestsData)
            return jsonify({'error':userQuestionTestsData}), errorCode

        for uQT in userQuestionTestsData:
            totalCorrect += uQT['isCorrect']
            questionData, errorCode = getQuestion({'id':uQT['questionId']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+questionData)
                return jsonify({'error':questionData}), errorCode

            actualTime += config4['time'][config2['difficultyLevel'][questionData.difficultyLevel]] * 1.

        achieved = sprint.accuracy * len(sprint.questionIds.split(','))//len(testData.questionIds.split(','))
        cumulativeAchieved += achieved
        cumulativeTarget -= achieved
        if sprint.progress == 0:
            utId = sprint.id
            continue
        sendObject['sprint'].append({
                'coins':sprint.coinsEarned,
                'timetaken':sprint.timetaken,
                'target':cumulativeTarget if cumulativeTarget > 0 else 0,
                'achieved':achieved,
                'userTestId':sprint.id,
            })
    sendObject['nextSprintUserTestId'] = utId
    chapterData, errorCode = getChapter({'id':testData.chapterId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userTestId:'+ str(userTestId)+'. error:'+chapterData)
        return jsonify({'error':chapterData}), errorCode

    sendObject['chapter name'] = chapterData.name
    return jsonify(sendObject), 200

@app.route('/ftestHistory/', methods=['POST'])
def ftestHistory():
    userId = request.form.get('userId')
    time = request.form.get('time')
    search = request.form.get('search')

    startDate = endDate = None
    if request:
        data = request.get_json()
        if data:
            data = data.get('data')
            userId = data['userId']
            startDate = datetime.datetime.strptime(data['startDate'], '%m/%d/%Y').strftime('%Y-%m-%d')
            endDate = datetime.datetime.strptime(data['endDate'], '%m/%d/%Y').strftime('%Y-%m-%d')
            search = data['search']

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -search:'+str(search)+ ' -time:'+str(time))

    sendObject = {
        'status':1,
        'subjects': [],
        'test':[]
    }
    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    for sub in subjectsData:
        sendObject['subjects'].append({'id':sub['id'],'name':sub['name']})

    iter = -1
    prevMonth = None
    if search:
        search = search.lower()
    loopsDict, resumeLoops, lastLoopFirstSprintId = {}, {}, 0

    try:
        if startDate and endDate:
            userTests = UserTest.query.filter_by(userId=userId).filter(or_(UserTest.progress>0, and_(UserTest.target!=0, UserTest.progress==0))).\
            filter(UserTest.dateTime.between(startDate, endDate)).order_by(-UserTest.dateTime).all()
        else:
            if time:
                time = datetime.datetime.strptime(time, "%Y %B").month
            else:
                time = datetime.datetime.now(indianTime).month
            userTests = UserTest.query.filter_by(userId=userId).filter(or_(UserTest.progress>0, and_(UserTest.target!=0, UserTest.progress==0))).\
            filter(extract('month', UserTest.dateTime) == time).order_by(-UserTest.dateTime).all()
    except Exception as e:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing userTest history, '+str(e))
        return jsonify({'error': 'Error in accessing userTest History details:'+str(e)}), 500

    for i, usertest in enumerate(userTests):
        testData, errorCode = getTest({'id':usertest.testId})
        if errorCode == 500:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
            return jsonify({'error':testData}), errorCode
        elif errorCode == 404:
            testData = None

        testType = 'Concept based'    #dynamic

        subjectId, chapterIds, conceptIds, formats, levels, questionIds = None, None, None, None, None, None
        if testData:
            text1 = testData.name
            text2 = testData.text2
            subjectId = testData.subjectId
            if testData.isStaticTest:
                testType = 'Static Test'
            elif testData.isLoop:
                testType = 'Loops'
        else:   #custom test
            text1 = usertest.customName
            testType = text2 = 'Custom Test'
            subjectId, chapterIds, conceptIds, formats, levels, questionIds = usertest.customSubjectId, usertest.customTestChapterIds, \
            usertest.customTestConceptIds, usertest.customTestFormats, usertest.customTestLevelIds, usertest.questionIds

        subjectData, errorCode = getSubject({'id':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
            return jsonify({'error':subjectData}), errorCode

        text3 = subjectData.name

        if search != '':
            if search in testType.lower() or search in text1.lower() or search in text2.lower() or search in text3.lower():
                pass
            else:
                continue

        if testType == 'Loops':
            loopsKey = str(userId)+'-'+str(testData.id)
            if loopsKey not in loopsDict.keys():
                loopsDict[loopsKey] = True
                userTestLoopsData, errorCode = getUserTest({'userId':userId, 'testId':usertest.testId, 'rOrder':1})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestLoopsData)
                    return jsonify({'error':userTestLoopsData}), errorCode

                lastLoopFirstSprintId, lastSprintId, target, achieved = getSprintSetDetails(userId, testData.id, userTestLoopsData.id)
                if not target:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing sprint details')
                    return jsonify({'error': 'Error in accessing sprints details'}), 500

                lastSprintData, errorCode = getUserTest({'id':lastSprintId})
                if errorCode != 200:
                    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+lastSprintData)
                    return jsonify({'error':lastSprintData}), errorCode

                if achieved < lastSprintData.target:
                    resumeLoops[lastSprintId] = 1
            elif usertest.customTestFormats != '1':
                continue
            elif usertest.id == lastLoopFirstSprintId:
                continue

        date = usertest.dateTime.strftime('%d')+','+usertest.dateTime.strftime('%a')+','+usertest.dateTime.strftime("%H:%M")
        # print(usertest.dateTime.strftime('%Y %B'))
        month = str(usertest.dateTime.strftime('%Y %B'))
        if prevMonth != month:
            sendObject['test'].append({
                'month':month,
                'tests':[]
            })
            prevMonth = month
            iter += 1


        sendObject['test'][iter]['tests'].append({
                'date': date,
                'testType': testType,
                'practice': usertest.practiceTest,
                'text1': text1,
                'text2': text2,
                'text3': text3,
                'resume': True if usertest.paused or usertest.id in resumeLoops.keys() else False,
                'userTestId': usertest.id,
                'testId': testData.id if usertest.testId else None,
                'subjectId': subjectId,
                'chapterIds': chapterIds,
                'conceptIds': conceptIds,
                'formats': formats,
                'levels': levels,
                'questionIds': questionIds,
                'results': True if usertest.progress == 100 and not usertest.id in resumeLoops.keys() else False
            })
    print(sendObject)
    return jsonify(sendObject), 200

def getDates(time):
    try:
        startDate = datetime.datetime.strptime(time, '%Y-%m-%d')
        endDate = startDate + datetime.timedelta(days=7)
        return startDate, endDate
    except:
        pass
    time = time.lower()
    today = datetime.datetime.now(indianTime)
    today = datetime.datetime(today.year, today.month, today.day)
    startDate = today - datetime.timedelta(days=((today.weekday()) % 7))
    endDate = startDate + datetime.timedelta(days=7)
    if time == "last week":
        startDate -= datetime.timedelta(days=7)
        endDate -= datetime.timedelta(days=7)
    elif time == "this month":
        startDate = today.replace(day=1)
        endDate = datetime.date(today.year, today.month + 1, 1)
    elif time == "this year":
        startDate = datetime.datetime(today.year, 4, 1, 0, 0, 0)
        endDate = datetime.datetime(today.year+1, 4, 1, 0, 0, 0)
    return startDate, endDate

#confidence - correctans + 1st click timetaken < time(difficultyLevel)/2 for seen questions
#accuracy - correct/seen questions
#for the pie chart - all practice tests are ignored except for loop (sprints). As we mainly want to show user that he is mainly taking these type of tests
@app.route('/fanalytics/', methods=['POST'])
def fanalytics():
    userId = request.form.get('userId')
    time = request.form.get('time')

    if not time:
        time = 'This week'

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -time:'+str(time))

    sendObject = {}

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    startDate, endDate = getDates(time)

    sendObject = {
        "allAccuracy": 75,
        "allCoins": 90,
        "allConfidence": 80,
        "allHours": 90,
        "allPerformance": 75,
        "allScore": 90,
        "allTests": 90,
        'time':time,
        "dateFilter": {
        "This month": "This month",
        "This week": "This week",
        "This year": "This year"
        },
        'subjectList':[]
    }

    analysisData, errorCode = getAnalysis({'userId':userId, 'subjectId':None, 'timeType':time})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+analysisData)
        return jsonify({'error':analysisData}), errorCode

    sendObject['confidence'] = analysisData.confidence*100//analysisData.confidenceTotal if analysisData.confidenceTotal else 0
    sendObject['score'] = analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0
    sendObject['tests'] = (analysisData.totalConceptTests + analysisData.totalLoopTests + analysisData.totalStaticTests)*100//analysisData.totalTests if analysisData.totalTests else 0
    sendObject['performance'] = analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0
    sendObject['accuracy'] = analysisData.totalCorrects*100//analysisData.totalQuestions if analysisData.totalQuestions else 0

    totalTests = analysisData.totalLoopTests + analysisData.totalConceptTests + analysisData.totalCustomTests + analysisData.totalOtherTests
    sendObject['loop'] = analysisData.totalLoopTests*100//totalTests if totalTests else 0
    sendObject['conceptBased'] = analysisData.totalConceptTests*100//totalTests if totalTests else 0
    sendObject['custom'] = analysisData.totalCustomTests*100//totalTests if totalTests else 0
    sendObject['other'] = analysisData.totalOtherTests*100//totalTests if totalTests else 0

    for sub in subjectsData:
        analysisData, errorCode = getAnalysis({'userId':userId, 'subjectId':sub['id'], 'timeType':time})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+analysisData)
            return jsonify({'error':analysisData}), errorCode

        sendObject['subjectList'].append({
            'id':sub['id'],
            'name':sub['name'],
            'confidence' : analysisData.confidence*100//analysisData.confidenceTotal if analysisData.confidenceTotal else 0,
            'score' : analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0,
            'tests' : (analysisData.totalConceptTests + analysisData.totalLoopTests + analysisData.totalStaticTests)*100//analysisData.totalTests if analysisData.totalTests else 0,
            'performance' : analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0,
            'accuracy' : analysisData.totalCorrects*100//analysisData.totalQuestions if analysisData.totalQuestions else 0
        })

    return jsonify(sendObject), 200

#persistance - number of corresponding practice test / tests
#knowledge = accuracy
#3rd part i.e. strong or weak is on the basis of score with threshold 60%
@app.route('/fanalyticsSubject/', methods=['POST'])
def fanalyticsSubject():
    userId = request.form.get('userId')
    subjectId = request.form.get('subjectId')
    time = request.form.get('time')

    subjectId = int(subjectId)
    if not time:
        time = 'This week'

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -subjectId:'+str(subjectId)+' -time:'+str(time))

    sendObject = {}

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    subjectData, errorCode = getSubject({'id':subjectId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
        return jsonify({'error':subjectData}), errorCode

    sendObject = {
        'time': time,
        "dateFilter": {
        "This month": "This month",
        "This week": "This week",
        "This year": "This year"
        },
        'subjects':[]
    }

    for sub in subjectsData:
        sendObject['subjects'].append({
            'id':sub['id'],
            'name':sub['name']
        })

    analysisData, errorCode = getAnalysis({'userId':userId, 'subjectId':subjectId, 'timeType':time})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+analysisData)
        return jsonify({'error':analysisData}), errorCode

    startDate, endDate = getDates(time)
    userTestsData, errorCode = getAllUserTests({'userId':userId, 'startEnd':[startDate, endDate], 'progress':100})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestsData)
        return jsonify({'error':userTestsData}), errorCode

    userConceptsData, errorCode = getAllUserConcepts({'userId':userId, 'subjectId':subjectId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userConceptsData)
        return jsonify({'error':userConceptsData}), errorCode

    totalTests = analysisData.totalLoopTests + analysisData.totalConceptTests + analysisData.totalCustomTests + analysisData.totalOtherTests
    sendObject['values'] = {
        'id':subjectId,
        'name':subjectData.name,
        'confidence' : analysisData.confidence*100//analysisData.confidenceTotal if analysisData.confidenceTotal else 0,
        'score' : analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0,
        'tests' : (analysisData.totalConceptTests + analysisData.totalLoopTests + analysisData.totalStaticTests)*100//analysisData.totalTests if analysisData.totalTests else 0,
        'performance' : analysisData.score*100//analysisData.scoreTotal if analysisData.scoreTotal else 0,
        'accuracy' : analysisData.totalCorrects*100//analysisData.totalQuestions if analysisData.totalQuestions else 0,

        'loop' : analysisData.totalLoopTests*100//totalTests if totalTests else 0,
        'conceptBased' : analysisData.totalConceptTests*100//totalTests if totalTests else 0,
        'custom' : analysisData.totalCustomTests*100//totalTests if totalTests else 0,
        'other' : analysisData.totalOtherTests*100//totalTests if totalTests else 0,

        'testList': [],
        'testsStrong': [],
        'testsWeak': [],
        'difficultyLevelStrong': [],
        'difficultyLevelWeak': [],
        'questionFormatStrong': [],
        'questionFormatWeak': [],
        'conceptsStrong': [],
        'conceptsWeak': [],
        'chaptersStrong': [],
        'chaptersWeak': []
    }

    for userTest in userTestsData:
        testName  = userTest['customName']
        if userTest['testId']:
            testData, errorCode = getTest({'id':userTest['testId']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
                return jsonify({'error':testData}), errorCode

            if subjectId != testData.subjectId:
                continue
            testName = testData.name
        elif subjectId != userTest['customSubjectId']:
            continue
        score = userTest['score']*100//userTest['scoreTotal'] if userTest['scoreTotal'] else 0
        testName = testName if not userTest['practiceTest'] else testName + ' - Practice'
        if score >= config11['analyticsStrongOrWeakThreshold']:
            sendObject['values']['testsStrong'].append(testName)
        else:
            sendObject['values']['testsWeak'].append(testName)
        sendObject['values']['testList'].append({
            'id':userTest['id'],
            'name':testName,
            'accuracy':userTest['accuracy'],
            'confidence':userTest['confidence'],
            'score':userTest['score'],
            'performance':userTest['score']
        })

    difficultyLevelCountsAnalysis = ast.literal_eval(analysisData.difficultyLevelCounts)
    for i, level in enumerate(config2['difficultyLevel'].values()):
        score = difficultyLevelCountsAnalysis[i]*100//difficultyLevelCountsAnalysis[i+1] if difficultyLevelCountsAnalysis[i+1] else 0
        if score >= config11['analyticsStrongOrWeakThreshold']:
            sendObject['values']['difficultyLevelStrong'].append(level.capitalize())
        else:
            sendObject['values']['difficultyLevelWeak'].append(level.capitalize())

    formatCountsAnalysis = ast.literal_eval(analysisData.formatCounts)
    for i, format in enumerate(QuestionFormat.query.all()):
        score = formatCountsAnalysis[i]*100//formatCountsAnalysis[i+1] if formatCountsAnalysis[i+1] else 0
        if score >= config11['analyticsStrongOrWeakThreshold']:
            sendObject['values']['questionFormatStrong'].append(format.code)
        else:
            sendObject['values']['questionFormatWeak'].append(format.code)

    #TODO make concept and chapter analytics timewise. Now showing all time analystics for those two.
    chapterScoreDict = {}
    for userConcept in userConceptsData:
        conceptData, errorCode = getConcept({'id':userConcept['conceptId']})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+conceptData)
            return jsonify({'error':conceptData}), errorCode

        if conceptData.chapterId not in chapterScoreDict.keys():
            chapterScoreDict[conceptData.chapterId] = [0,0]
        else:
            chapterScoreDict[conceptData.chapterId][0] += userConcept['score']
            chapterScoreDict[conceptData.chapterId][1] += userConcept['scoreTotal']
        score = userConcept['score']*100//userConcept['scoreTotal'] if userConcept['scoreTotal'] else 0
        if score >= config11['analyticsStrongOrWeakThreshold']:
            sendObject['values']['conceptsStrong'].append(conceptData.name)
        else:
            sendObject['values']['conceptsWeak'].append(conceptData.name)

    for chapId, scoreList in chapterScoreDict.items():
        chapterData, errorCode = getChapter({'id':chapId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+chapterData)
            return jsonify({'error':chapterData}), errorCode

        score = scoreList[0]*100//scoreList[1] if scoreList[1] else 0
        if score >= config11['analyticsStrongOrWeakThreshold']:
            sendObject['values']['chaptersStrong'].append(chapterData.name)
        else:
            sendObject['values']['chaptersWeak'].append(chapterData.name)
    return jsonify(sendObject), 200

#monday reports
#activity no of tests per day
#performance summation of scores per day
#progress =
#accuracy = correct/attempted   #TODO comes in HOME
#confidence = correctans + 1st click timetaken < time(difficultyLevel)/2 for seen questions
#time - 600 minutes #display in hours
@app.route('/freports/', methods=['POST'])
def freports():
    userId = request.form.get('userId')
    time = request.form.get('time')
    home = request.form.get('home')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+str(userId)+' -time:'+str(time))

    if not time:
        time = 'This week'

    sendObject = {
        'subjectList': [],
        'insights': {
            'bad behaviour':[],
            'good behaviour':[]
        },
        'time':[]
    }

    subjectNamesList = []

    userData, errorCode = getUser({'id':userId})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userData)
        return jsonify({'error':userData}), errorCode

    startDate, endDate = getDates(time)
    userTestsData, errorCode = getAllUserTests({'userId':userId, 'startEnd':[startDate, endDate], 'progress':100})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+userTestsData)
        return jsonify({'error':userTestsData}), errorCode

    subjectsData, errorCode = getAllSubjects({'grade':userData.grade, 'board':userData.board})
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectsData)
        return jsonify({'error':subjectsData}), errorCode

    progressDict, activityDict, performanceDict = {}, {}, {}
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        performanceDict[day] = 0
        activityDict[day] = 0

    NoOfTests, NoOfPracticeTests, timetaken, subjectDict = 0,0,0,{}
    for subject in subjectsData:
        subjectNamesList.append(subject['name'])
        progressDict[subject['name']] = {}
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            progressDict[subject['name']][day] = 0
        subjectDict[subject['id']] = {
            'confidence':0,
            'score':0,
            'tests':0,
            'accuracy':0
        }

    for i, userTest in enumerate(userTestsData):
        # testSubjectId, chapterIds, conceptIds, formats, levels, questionIds = None, None, None, None, None, None
        # if userTest['testId']:
        day = userTest['dateTime'].strftime('%a')
        activityDict[day] += 1  #TODO set count of practice per day and not overall #int(userTest['customTestLevelIds']) if userTest['practiceTest'] else 1
        performanceDict[day] += userTest['score']*100//userTest['scoreTotal'] if userTest['scoreTotal'] else 0
        subjectId = userTest['customSubjectId']

        isDynamicTest = False
        if userTest['testId']:
            testData, errorCode = getTest({'id':userTest['testId']})
            if errorCode != 200:
                app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+testData)
                return jsonify({'error':testData}), errorCode

            NoOfTests += 1
            subjectId = testData.subjectId
            if not testData.isStaticTest and not testData.isLoop:
                isDynamicTest = True

        subjectData, errorCode = getSubject({'id':subjectId})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+subjectData)
            return jsonify({'error':subjectData}), errorCode

        progressDict[subjectData.name][day] += 1 if isDynamicTest else 0
        NoOfPracticeTests += 1 if userTest['practiceTest'] else 0

        try:
            time = db.session.query(func.sum(UserQuestionTest.timetaken)).filter_by(userTestId=userTest['id']).scalar()
            timetaken += int(time) if time else 0
        except Exception as e:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:Error in accessing usertest records, '+str(e))
            return jsonify({'error':'Error in accessing UserTest records for userId '+ str(userId) +' for score. Details:' + str(e)}), 500

        if home == 'home':
            continue

        subjectDict[subjectData.id]['confidence'] += userTest['confidence']
        subjectDict[subjectData.id]['score'] += userTest['score']*100//userTest['scoreTotal'] if userTest['scoreTotal'] else 0
        subjectDict[subjectData.id]['tests'] += 1 if isDynamicTest else 0
        subjectDict[subjectData.id]['accuracy'] += userTest['accuracy']

    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        performanceDict[day] = performanceDict[day]//activityDict[day] if activityDict[day] else 0
        if performanceDict[day] < 0:
            performanceDict[day] = 0
        elif performanceDict[day] > 99:
            performanceDict[day] = 100

    for subject in subjectsData:
        totalSubjectDynamicTests, errorCode = getAllTests({'subjectId':subject['id'], 'isStaticTest':False, 'isLoop':False, 'count':1})
        if errorCode != 200:
            app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+totalSubjectDynamicTests)
            return jsonify({'error':totalSubjectDynamicTests}), errorCode

        subjectDict[subject['id']]['testsCreated'] = totalSubjectDynamicTests
        for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
            progressDict[subject['name']][day] = progressDict[subject['name']][day]*100//totalSubjectDynamicTests if totalSubjectDynamicTests else 0

    sendObject['badge'] = {
            'Activity':activityDict,
            'Progress':progressDict,
            'Performance':performanceDict,
            'subjectList':subjectNamesList,
            'NoOfTests':NoOfTests,
            "NoOfPracticeTests":NoOfPracticeTests,
            'time':timetaken
    }

    if home == 'home':
        return jsonify({'reports':sendObject['badge']})

    totalUserTests = len(userTestsData)
    accuracy, confidence, score, performance, test = 0, 0, 0, 0, 0
    for subject in subjectsData:
        confidence += subjectDict[subject['id']]['confidence']//totalUserTests if totalUserTests else 0
        accuracy += subjectDict[subject['id']]['accuracy']//totalUserTests if totalUserTests else 0
        score += subjectDict[subject['id']]['score']//totalUserTests if totalUserTests else 0
        test += subjectDict[subject['id']]['tests']//subjectDict[subject['id']]['testsCreated'] if subjectDict[subject['id']]['testsCreated'] else 0
        sendObject['subjectList'].append({
            'id':subject['id'],
            'name':subject['name'],
            'confidence': subjectDict[subject['id']]['confidence']//totalUserTests  if totalUserTests else 0,
            'accuracy': subjectDict[subject['id']]['accuracy']//totalUserTests  if totalUserTests else 0,
            'score': subjectDict[subject['id']]['score']//totalUserTests  if subjectDict[subject['id']]['score'] > 0 and totalUserTests else 0,
            'performance': subjectDict[subject['id']]['score']//totalUserTests  if subjectDict[subject['id']]['score'] > 0 and totalUserTests else 0,
            'tests': subjectDict[subject['id']]['tests']//subjectDict[subject['id']]['testsCreated']  if subjectDict[subject['id']]['testsCreated'] else 0
        })

    totalSubjects = len(subjectsData)
    sendObject['confidence'] = confidence//totalSubjects
    sendObject['score'] = score//totalSubjects if score > 0 else 0
    sendObject['tests'] = test//totalSubjects
    sendObject['accuracy'] = accuracy//totalSubjects
    sendObject['performance'] = sendObject['score']

    if config14['reports']['NoOfTests'] > sendObject['badge']['NoOfTests']:
        sendObject['insights']['bad behaviour'].append('Number of Tests')
    else:
        sendObject['insights']['good behaviour'].append('Number of Tests')
    if config14['reports']['NoOfPracticeTests'] > sendObject['badge']['NoOfPracticeTests']:
        sendObject['insights']['bad behaviour'].append('Number of Practice Tests')
    else:
        sendObject['insights']['good behaviour'].append('Number of Practice Tests')
    if config14['reports']['time'] > sendObject['badge']['time']:
        sendObject['insights']['bad behaviour'].append('Time')
    else:
        sendObject['insights']['good behaviour'].append('Time')

    if config14['reports']['confidence'] > sendObject['confidence']:
        sendObject['insights']['bad behaviour'].append('Confidence')
    else:
        sendObject['insights']['good behaviour'].append('Confidence')
    if config14['reports']['Performance'] > sendObject['score']:
        sendObject['insights']['bad behaviour'].append('Performance')
    else:
        sendObject['insights']['good behaviour'].append('Performance')
    if config14['reports']['accuracy'] > sendObject['accuracy']:
        sendObject['insights']['bad behaviour'].append('Accuracy')
    else:
        sendObject['insights']['good behaviour'].append('Accuracy')

    today = datetime.datetime.now(indianTime)
    monday = today - datetime.timedelta(days=((today.weekday()) % 7))
    sendObject['time'].append({'name':'This Week','time':monday.date().strftime('%Y-%m-%d')})
    monday -= datetime.timedelta(days=7)
    sendObject['time'].append({'name':'Last Week','time':monday.date().strftime('%Y-%m-%d')})
    for i in range(2, 20):
        monday -= datetime.timedelta(days=7)
        sendObject['time'].append({'name':monday.date().strftime('%Y-%m-%d'), \
        'time':monday.date().strftime('%Y-%m-%d')})

    return jsonify(sendObject), 200


@app.route('/fappVersion/', methods=['GET', 'POST'])
def fappVersion():
    version = request.form.get('version')
    app.logger.debug(inspect.currentframe().f_code.co_name+' -version:'+str(version))
    appVersion = AppVersion.query.order_by(-AppVersion.id).first()
    if version and appVersion.version != int(version):
        return jsonify({'status':1, 'version':appVersion.version, 'forced':appVersion.forced, 'update':True})
    return jsonify({'status':1, 'version':appVersion.version, 'forced':False, 'updated':False}), 200


@app.route('/ffaq/', methods=['POST'])
#@tokenRequired
def ffaq():
    type = request.form.get('type')

    app.logger.debug(inspect.currentframe().f_code.co_name+' -type:'+str(type))

    sendObject = {
        'status':1,
        'faqs': []
    }
    faqsInputData = {}
    if type != 'all':
         faqsInputData['type'] = type

    faqsData, errorCode = getAllFaqs(faqsInputData)
    if errorCode != 200:
        app.logger.debug(inspect.currentframe().f_code.co_name+' -userId:'+ str(userId)+'. error:'+faqsData)
        return jsonify({'error':faqsData}), errorCode

    for f in faqsData:
        sendObject['faqs'].append({
            'question':f['question'],
            'answer': f['answer'],
            'type':f['type'],
            'imagePath':f['imagePath']
        })
    return jsonify(sendObject), 200

@app.route('/fsplashScreen/', methods=['POST'])
def fsplashScreen():
    sendObject = {
        'status':1,
        'list':[]
    }
    for screen in SplashScreen.query.all():
        sendObject['list'].append({
            'imagePath':screen.imagePath,
            'text1':screen.text1,
            'text2':screen.text2
        })
    return jsonify(sendObject), 200

#TODO add to dbOps
#TODO add auto generated notifications also
@app.route('/fnotificationHistory/', methods=['POST'])
def fnotificationHistory():
    userId = request.form.get('userId')

    sendObject = {
        'status':1,
        'notifications': []
        }
    user = User.query.filter_by(id=userId).first()
    numberOfNotifications = 0
    for n in Notifications.query.order_by(-Notifications.id).all():
        if numberOfNotifications > 10:
            break
        school, board, grade = n.targetUserGroup.split('-')
        if str(user.school) in school.split(',') and str(user.grade) in grade.split(',') and str(user.board) in board.split(','):
            numberOfNotifications += 1
            sendObject['notifications'].append({'title':n.title, 'message':n.message, 'imagePath':n.imagePath})
    return jsonify(sendObject), 200


@app.route('/fgettingStartedVideos/', methods=['POST', 'GET'])
def fgettingStartedVideos():

    sendObject = {
        'videos':[]
    }
    gettingStartedVideos = [[1,1,"Concept"], [2,1, "Loops"], [3,1, "Custom"], [4,1, "Practice"], [5,1, "History"], [6,1, "Analytics"], [7,1, "Reports"], [8,1, "Subscription"], [9,1, "Badges"], [10,1, "Dynamic"], [11,1, "Formats"]]
    gettingStartedVideos = [[1,1,"Concept"], [2,1, "Loops"], [3,1, "Custom"], \
    #[4,1, "Practice"], [5,1, "History"], \
    [6,1, "Analytics"], [7,1, "Reports"], [8,1, "Subscription"], [9,1, "Badges"], [10,1, "Dynamic"], [11,1, "Formats"]]
    path = "src/static/img/"
    localDict = {
        "Concept": ["Concept-based tests", path + "ConceptbasedtestVideo.svg", "https://youtu.be/iVEun2I_eSI"],
        "Loops": ["Loops", path + "LoopsVideo.svg", "https://youtu.be/nnGB53J0_0w"],
        "Custom": ["Custom tests", path + "CustomtestVideo.svg", "https://youtu.be/CTAeZFiiVkk"],
        # "Practice": ["Practice tests", path + "PracticetesttestVideo.svg", url],
        # "History": ["Test History", path + "TesthistorytVideo.svg", url],
        "Analytics": ["Analytics", path + "AnalyticsVideo.svg", "https://youtu.be/nsRsuJLbh6M"],
        "Reports": ["Weekly reports", path + "WeeklyreportVideo.svg", "https://youtu.be/Va5g22hATi4"],
        "Subscription": ["Subscription", path + "SubscriptionVideo.svg", "https://youtu.be/QizdzdMeOJU"],
        "Badges": ["Badges", path + "BadgesVideo.svg", "https://youtu.be/y7JmiEdZIb8"],
        "Dynamic": ["Dynamic leveling", path + "DynamiclevelingVideo.svg", "https://youtu.be/FInpexmEiUI"],
        "Formats": ["5 Question Formats", path + "QuestionformatsVideo.svg", "https://youtu.be/Z4IXc1cmyoQ"],
    }
    for sort, status, name in sorted(gettingStartedVideos):
        if status == 1:
            sendObject['videos'].append({
                'name':localDict[name][0],
                'imagePath':localDict[name][1],
                'url':localDict[name][2]
            })
    return jsonify(sendObject), 200


#number of times a coupon is used and who all used it TODO
@app.route('/run', methods=['GET', 'POST'])
def run():
    path = "src/static/img/"


#badge triggering, results, aws frontend, testing apis, fhome
#reports, analytics




#first get all analytical parameters ready. use all those parameters and save in Usertest
