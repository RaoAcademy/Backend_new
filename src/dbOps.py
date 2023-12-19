from . models import User, School, Avatar, Admin, Roles, Grade, \
Board, Subject, Concept, Question,\
QuestionFormat, QuestionMcqMsqDadSeq, QuestionFillTorF, Coupon,\
QuestionMatch, Chapter, TestCategory, Test, Notifications, Subscription, \
SubscriptionActivity, LoginActivity, Inits, UserTest, UserQuestion, Analysis,\
UserConcept, FAQs, UserQuestionTest, Instructor, InstructorAssignment, InstructorTestScheduling
from src import db, indianTime
from sqlalchemy import func, exc, or_, and_
from sqlalchemy.exc import IntegrityError
import ast, datetime

#grade
def getGrade(gradeInputData):
    try:
        grade = Grade.query.filter_by(id=gradeInputData['id']).first()
        if grade:
            return grade, 200
        else:
            return 'Grade not found for id '+str(id) , 404
    except Exception as e:
        return 'Error in accessing Grade record for id '+str(id)+ '. Details:'+str(e), 500

def getAllGrades(gradeInputData):
    try:
        grades = Grade.query
        if 'ids' in gradeInputData.keys():
            grades = grades.filter(Grade.id.in_(gradeInputData['ids']))
        grades = grades.all()
        gradesData = []
        for grade in grades:
            gradesData.append({
                "id": grade.id,
                "grade": grade.grade
            })
        return gradesData, 200
    except Exception as e:
        return 'Error in accessing grades records. Details: '+ str(e), 500


#board
def getBoard(boardInputData):
    try:
        board = Board.query.filter_by(id=boardInputData['id']).first()
        if board:
            return board, 200
        else:
            return 'Board not found for name '+str(name) , 404
    except Exception as e:
        return 'Error in accessing Board record for name '+str(name)+ '. Details:'+str(e), 500

def getAllBoards(boardInputData):
    try:
        boards = Board.query
        if 'ids' in boardInputData.keys():
            boards = boards.filter(Board.id.in_(boardInputData['ids']))
        boards = boards.all()
        boardsData = []
        for board in boards:
            boardsData.append({
                "id": board.id,
                "board": board.name
            })
        return boardsData, 200
    except Exception as e:
        return 'Error in accessing boards records. Details: '+str(e), 500


#school
def getSchool(schoolInputData):
    try:
        school = School.query
        if 'name' in schoolInputData.keys():
            school = school.filter_by(name=schoolInputData['name'])
        if 'id' in schoolInputData.keys():
            school = school.filter_by(id=schoolInputData['id'])
        school = school.first()
        if school:
            return school, 200
        else:
            return 'School not found for '+ str(schoolInputData), 404
    except Exception as e:
        return 'Error in accessing school record for '+ str(schoolInputData)+'. Details:' + str(e), 500

def insertSchool(school):
    try:
        db.session.add(school)
        db.session.flush()
        schoolId = school.id
        db.session.commit()
        return schoolId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertSchool', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to add school. error: ' + str(e), 500


#avatar
def getAvatar(avatarInputData):
    try:
        avatar = Avatar.query
        if 'id' in avatarInputData.keys():
            avatar = avatar.filter_by(id=avatarInputData['id'])
        if 'gender' in avatarInputData.keys():
            avatar = avatar.filter_by(gender=avatarInputData['gender'])
        avatar = avatar.first()
        if avatar:
            return avatar, 200
        else:
            return 'Avatar not found for '+str(avatarInputData), 404
    except Exception as e:
        return 'Error in accessing avatar record for '+str(avatarInputData)+ '. Details:'+str(e), 500

def getAllAvatars(avatarInputData):
    try:
        avatars = Avatar.query
        if 'gender' in avatarInputData.keys():
            avatars = avatars.filter_by(gender=avatarInputData['gender'])
        avatars = avatars.all()
        avatarsData = []
        for avatar in avatars:
            avatarsData.append({
                "id": avatar.id,
                "imagePath": avatar.imagePath
            })
        return avatarsData, 200
    except Exception as e:
        return 'Error in accessing avatars records for '+str(avatarInputData)+ '. Details: '+str(e), 500


#user
def getUser(userInputData):
    try:
        user = User.query
        if 'id' in userInputData.keys():
            user = user.filter_by(id=userInputData['id'])
        if 'mobile' in userInputData.keys():
            user = user.filter_by(mobile=userInputData['mobile'])
        if 'peerReferral' in userInputData.keys():
            user = user.filter_by(referral=userInputData['peerReferral'])
        if 'parentMobile' in userInputData.keys():
            user = user.filter_by(parentMobile=userInputData['parentMobile'])
        user = user.first()
        if user:
            return user, 200
        else:
            return 'User not found for '+str(userInputData) , 404
    except Exception as e:
        return 'Error in accessing User record for '+str(userInputData)+ '. Details:'+str(e), 500

def getAllUsers(userInputData):
    try:
        users = User.query
        if 'ids' in userInputData.keys():
            users = users.filter(User.id.in_(userInputData['ids']))
        if 'school' in userInputData.keys():
            users = users.filter_by(school=userInputData['school'])
        if 'schools' in userInputData.keys():
            users = users.filter(User.school.in_(userInputData['schools']))
        if 'gender' in userInputData.keys():
            users = users.filter_by(gender=userInputData['gender'])
        if 'grades' in userInputData.keys():
            users = users.filter(User.grade.in_(userInputData['grades']))
        if 'boards' in userInputData.keys():
            users = users.filter(User.board.in_(userInputData['boards']))
        if 'sections' in userInputData.keys():
            users = users.filter(User.section.in_(userInputData['sections']))
        if 'boardGradeSectionPair' in userInputData.keys():
            users = users.filter(or_(*[and_(User.board == board, User.grade == grade, User.section == section) \
            for board, grade, section in userInputData['boardGradeSectionPair']]))
        if 'tuitionId' in userInputData.keys():
            tuitionId = userInputData['tuitionId']
            users = users.filter(or_(User.tuitions == tuitionId, User.tuitions.like(f'{tuitionId},%'), User.tuitions.like(f'%,{tuitionId}'), User.tuitions.like(f'%,{tuitionId},%')))
        if 'count' in userInputData.keys():
            return users.count(), 200
        users = users.all()
        usersData = []
        for user in users:
            usersData.append({
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "gender": user.gender,
                "dob": user.dob,
                "email": user.email,
                "mobile": user.mobile,
                "grade": user.grade,
                "section": user.section,
                "school": user.school,
                "tuitions": user.tuitions,
                "board": user.board,
                "testsRemaining": user.testsRemaining,
                "avatarId": user.avatarId,
                "coins": user.coins,
                "status": user.status,
                "referral": user.referral,
                "parentName": user.parentName,
                "parentMobile": user.parentMobile,
                "city": user.city,
                "lastYearResults": user.lastYearResults,
                "datetime": user.datetime,
                "hours": user.hours
            })
        return usersData, 200
    except Exception as e:
        return 'Error in accessing users records for '+str(userInputData)+ '. Details: '+str(e), 500

def updateUser(userInputData, userUpdateData):
    try:
        user = db.session.query(User)
        if 'id' in userInputData.keys():
            user = user.filter_by(id=userInputData['id'])
        user = user.first()
        if user is None:
            return 'user not found for id '+str(id), 404
        if 'avatarId' in userUpdateData.keys():
            user.avatarId = userUpdateData['avatarId']
        if 'firstname' in userUpdateData.keys():
            user.firstname = userUpdateData['firstname']
        if 'lastname' in userUpdateData.keys():
            user.lastname = userUpdateData['lastname']
        if 'gender' in userUpdateData.keys():
            user.gender = userUpdateData['gender']
        if 'dob' in userUpdateData.keys():
            user.dob = userUpdateData['dob']
        if 'board' in userUpdateData.keys():
            user.board = userUpdateData['board']
        if 'grade' in userUpdateData.keys():
            user.grade = userUpdateData['grade']
        if 'school' in userUpdateData.keys():
            user.school = userUpdateData['school']
        if 'mobile' in userUpdateData.keys():
            user.mobile = userUpdateData['mobile']
        if 'email' in userUpdateData.keys():
            user.email = userUpdateData['email']
        if 'parentName' in userUpdateData.keys():
            user.parentName = userUpdateData['parentName']
        if 'parentMobile' in userUpdateData.keys():
            user.parentMobile = userUpdateData['parentMobile']
        if 'city' in userUpdateData.keys():
            user.city = userUpdateData['city']
        if 'lastYearResults' in userUpdateData.keys():
            user.lastYearResults = int(userUpdateData['lastYearResults'])
        if 'subtractCoins' in userUpdateData.keys():
            user.coins -= int(userUpdateData['subtractCoins'])
        if 'addCoins' in userUpdateData.keys():
            user.coins += int(userUpdateData['addCoins'])
        if 'addTests' in userUpdateData.keys():
            user.testsRemaining += userUpdateData['addTests']
        if 'subtractTestsRemaining' in userUpdateData.keys():
            user.testsRemaining -= userUpdateData['subtractTestsRemaining']
        db.session.commit()
        return 'updateUser details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at update user', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update user record '+str(userInputData) +' with '+str(userUpdateData)+ '. Details: '+ str(e), 500
    

#subscription
def getSubscription(subscriptionInputData):
    try:
        subscription = Subscription.query
        if 'id' in subscriptionInputData.keys():
            subscription = subscription.filter_by(id=subscriptionInputData['id'])
        subscription = subscription.first()
        if subscription:
            return subscription, 200
        else:
            return 'Subscription not found for '+str(subscriptionInputData), 404
    except Exception as e:
        return 'Error in accessing Subscription record for '+str(subscriptionInputData) +'. Details:' + str(e), 500


#subscriptionActivity
def getSubscriptionActivity(subscriptionActivityInputData):
    try:
        subscriptionActivity = SubscriptionActivity.query
        if 'id' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(id=subscriptionActivityInputData['id'])
        if 'userId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(userId=subscriptionActivityInputData['userId'])
        if 'merchantTransactionId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(merchantTransactionId=subscriptionActivityInputData['merchantTransactionId'])
        if 'transactionId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(transactionId=subscriptionActivityInputData['transactionId'])
        if 'active' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter(SubscriptionActivity.expiryDate >= datetime.datetime.now(indianTime).date()).filter(SubscriptionActivity.testsRemaining!=0)
        subscriptionActivity = subscriptionActivity.first()
        if subscriptionActivity:
            return subscriptionActivity, 200
        else:
            return 'SubscriptionActivity not found for '+str(subscriptionActivityInputData), 404
    except Exception as e:
        return 'Error in accessing SubscriptionActivity record for '+str(subscriptionActivityInputData) +'. Details:' + str(e), 500

def getAllSubscriptionActivity(subscriptionActivityInputData):
    try:
        subscriptionActivity = SubscriptionActivity.query
        if 'userId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(userId=subscriptionActivityInputData['userId'])
        subscriptionActivityData = subscriptionActivity.all()
        return subscriptionActivityData, 200
    except Exception as e:
        return 'Error in accessing avatars records for '+str(subscriptionActivityInputData) +'. Details: '+str(e), 500

def insertSubscriptionActivity(subscriptionActivity):
    try:
        db.session.add(subscriptionActivity)
        db.session.flush()
        subscriptionActivityId = subscriptionActivity.id
        db.session.commit()
        return subscriptionActivityId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertSubscriptionActivity', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to add SubscriptionActivity. error: ' + str(e), 500

def updateSubscriptionActivity(subscriptionActivityInputData, subscriptionActivityUpdateData):
    try:
        subscriptionActivity = db.session.query(SubscriptionActivity)
        if 'id' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(id=subscriptionActivityInputData['id'])
        if 'merchantTransactionId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(merchantTransactionId=subscriptionActivityInputData['merchantTransactionId'])
        if 'transactionId' in subscriptionActivityInputData.keys():
            subscriptionActivity = subscriptionActivity.filter_by(transactionId=subscriptionActivityInputData['transactionId'])
        subscriptionActivity = subscriptionActivity.first()
        if subscriptionActivity is None:
            return 'subscriptionActivity not found for merchantTransactionId '+str(merchantTransactionId), 404
        if 'userId' in subscriptionActivityUpdateData.keys():
            subscriptionActivity.userId = subscriptionActivityUpdateData['userId']
        if 'subsId' in subscriptionActivityUpdateData.keys():
            subscriptionActivity.subsId = subscriptionActivityUpdateData['subsId']
        if 'couponId' in subscriptionActivityUpdateData.keys():
            subscriptionActivity.couponId = subscriptionActivityUpdateData['couponId']
        if 'expiryDate' in subscriptionActivityUpdateData.keys():
            subscriptionActivity.expiryDate = subscriptionActivityUpdateData['expiryDate']
        if 'testsRemaining' in subscriptionActivityUpdateData.keys():
            subscriptionActivity.testsRemaining = subscriptionActivityUpdateData['testsRemaining']
        db.session.commit()
        return 'updateSubsAct details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateSubscriptionActivity', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update subscriptionActivity record '+str(subscriptionActivityInputData) +' with '+str(subscriptionActivityUpdateData)+ '. Details: '+ str(e), 500


#ReferralActivity
def insertReferralActivity(referralActivity):
    try:
        db.session.add(referralActivity)
        db.session.flush()
        referralActivityId = referralActivity.id
        db.session.commit()
        return referralActivityId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertReferralActivity', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add ReferralActivity. error: ' + str(e), 500


#userBadges
def insertUserBadge(userBadge):
    try:
        db.session.add(userBadge)
        db.session.flush()
        userBadgeId = userBadge.id
        db.session.commit()
        return userBadgeId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertUserBadge', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add UserBadge. error: ' + str(e), 500
    

#inits
def getInits(initsInputData):
    try:
        inits = Inits.query.filter_by(userId=initsInputData['userId']).first()
        if inits:
            return inits, 200
        else:
            return 'UserInits not found for '+str(initsInputData), 404
    except Exception as e:
        return 'Error in accessing UserInits record for '+str(initsInputData)+ '. Details:'+str(e), 500

def insertInits(inits):
    try:
        db.session.add(inits)
        db.session.flush()
        initsId = inits.id
        db.session.commit()
        return initsId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertInits', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add Inits. error: ' + str(e), 500

def updateInits(initsInputData, initsUpdateData):
    try:
        inits = db.session.query(Inits).filter_by(userId=initsInputData['userId']).first()
        if inits is None:
            return 'userInits not found for '+str(initsInputData), 404
        if 'fcmToken' in initsUpdateData.keys():
            inits.fcmToken = initsUpdateData['fcmToken']
        if 'subscription' in initsUpdateData.keys():
            inits.subscription = initsUpdateData['subscription']
        if 'newBadge' in initsUpdateData.keys():
            inits.newBadge = initsUpdateData['newBadge']
        if 'newWeeklyReports' in initsUpdateData.keys():
            inits.newWeeklyReports = initsUpdateData['newWeeklyReports']
        if 'newTests' in initsUpdateData.keys():
            inits.newTests = initsUpdateData['newTests']
        db.session.commit()
        return 'userInits details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateInits', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update userInits record '+str(initsInputData) +' with '+str(initsUpdateData)+ '. Details: '+ str(e), 500


#subject
def getSubject(subjectInputData):
    try:
        subject = Subject.query
        if 'id' in subjectInputData.keys():
            subject = subject.filter_by(id=subjectInputData['id'])
        if 'name' in subjectInputData.keys():
            subject = subject.filter_by(name=subjectInputData['name'])
        if 'grade' in subjectInputData.keys():
            subject = subject.filter_by(grade=subjectInputData['grade'])
        if 'board' in subjectInputData.keys():
            subject = subject.filter_by(board=subjectInputData['board'])
        if 'desc' in subjectInputData.keys():
            subject = subject.order_by(-Subject.id)
        if 'sortOrder' in subjectInputData.keys():
            subject = subject.order_by(Subject.sortOrder)
        subject = subject.first()
        if subject:
            return subject, 200
        else:
            return 'Subject not found for '+str(subjectInputData) , 404
    except Exception as e:
        return 'Error in accessing subject record for '+str(subjectInputData)+ '. Details:'+str(e), 500

def getAllSubjects(subjectInputData):
    try:
        subjects = Subject.query
        if 'grade' in subjectInputData.keys():
            subjects = subjects.filter_by(grade=subjectInputData['grade'])
        if 'board' in subjectInputData.keys():
            subjects = subjects.filter_by(board=subjectInputData['board'])
        if 'grades'and 'boards' in subjectInputData.keys():
            subjects = subjects.filter(Subject.board.in_(subjectInputData['boards']), Subject.grade.in_(subjectInputData['grades']))
        if 'grades' in subjectInputData.keys():
            subjects = subjects.filter(Subject.grade.in_(subjectInputData['grades']))
        if 'boards' in subjectInputData.keys():
            subjects = subjects.filter(Subject.board.in_(subjectInputData['boards']))
        if 'academics' in subjectInputData.keys():
            subjects = subjects.filter_by(academics=subjectInputData['academics'])
        if 'desc' in subjectInputData.keys():
            subjects = subjects.order_by(-Subject.id)
        if 'sortOrder' in subjectInputData.keys():
            subjects = subjects.order_by(Subject.sortOrder)
        subjects = subjects.all()
        subjectsData = []
        for subject in subjects:
            subjectsData.append({
                "id": subject.id,
                "name": subject.name,
                "code": subject.code,
                "grade": subject.grade,
                "board": subject.board,
                "academics": subject.academics,
                "sortOrder": subject.sortOrder
            })
        return subjectsData, 200
    except Exception as e:
        return 'Error in accessing subjects records for '+str(subjectInputData)+ '. Details: '+str(e), 500


#userTest
def getUserTest(userTestInputData):
    try:
        userTest = UserTest.query
        if 'id' in userTestInputData.keys():
            userTest = userTest.filter_by(id=userTestInputData['id'])
        if 'userId' in userTestInputData.keys():
            userTest = userTest.filter_by(userId=userTestInputData['userId'])
        if 'testId' in userTestInputData.keys():
            userTest = userTest.filter_by(testId=userTestInputData['testId'])
        if 'customName' in userTestInputData.keys():
            userTest = userTest.filter_by(customName=userTestInputData['customName'])
        if 'paused' in userTestInputData.keys():
            userTest = userTest.filter_by(paused=userTestInputData['paused'])
        if 'practiceTest' in userTestInputData.keys():
            userTest = userTest.filter_by(practiceTest=userTestInputData['practiceTest'])
        if 'customTestFormats' in userTestInputData.keys():
            userTest = userTest.filter_by(customTestFormats=userTestInputData['customTestFormats'])
        if 'lessThanEqualToId' in userTestInputData.keys():
            userTest = userTest.filter(UserTest.id <= userTestInputData['lessThanEqualToId'])
        if 'rOrder' in userTestInputData.keys():
            userTest = userTest.order_by(-UserTest.id)
        userTest = userTest.first()
        if userTest:
            return userTest, 200
        else:
            return 'userTest not found for '+str(userTestInputData) , 404
    except Exception as e:
        return 'Error in accessing userTest record for '+str(userTestInputData)+ '. Details:'+str(e), 500

def getAllUserTests(userTestInputData):
    try:
        userTests = UserTest.query
        if 'userId' in userTestInputData.keys():
            userTests = userTests.filter_by(userId=userTestInputData['userId'])
        if 'userIds' in userTestInputData.keys():
            userTests = userTests.filter(UserTest.userId.in_(userTestInputData['userIds']))
        if 'testIds' in userTestInputData.keys():
            userTests = userTests.filter(UserTest.testId.in_(userTestInputData['testIds']))
        if 'ids' in userTestInputData.keys():
            userTests = userTests.filter(UserTest.id.in_(userTestInputData['ids']))
        if 'progress' in userTestInputData.keys():
            userTests = userTests.filter_by(progress=userTestInputData['progress'])
        if 'target' in userTestInputData.keys():
            userTests = userTests.filter_by(target=userTestInputData['target'])
        if 'paused' in userTestInputData.keys():
            userTests = userTests.filter_by(paused=userTestInputData['paused'])
        if 'bookmark' in userTestInputData.keys():
            userTests = userTests.filter_by(bookmark=userTestInputData['bookmark'])
        if 'startEnd' in userTestInputData.keys():
            userTests = userTests.filter(UserTest.dateTime.between(userTestInputData['startEnd'][0], userTestInputData['startEnd'][1]))
        if 'desc' in userTestInputData.keys():
            userTests = userTests.order_by(-UserTest.id)
        if 'count' in userTestInputData.keys():
            return userTests.count(), 200

        userTests = userTests.all()
        userTestsData = []
        for userTest in userTests:
            userTestsData.append({
                "id": userTest.id,
                "userId": userTest.userId,
                "testId": userTest.testId,
                "customName": userTest.customName,
                "customSubjectId": userTest.customSubjectId,
                "customTestChapterIds": userTest.customTestChapterIds,
                "customTestConceptIds": userTest.customTestConceptIds,
                "customTestLevelIds": userTest.customTestLevelIds,
                "customTestFormats": userTest.customTestFormats,
                "paused": userTest.paused,
                "progress": userTest.progress,
                "coinsEarned": userTest.coinsEarned,
                "timetaken": userTest.timetaken,
                "bookmark": userTest.bookmark,
                "practiceTest": userTest.practiceTest,
                "coins": userTest.coins,
                "questionIds": userTest.questionIds,
                "maxTime": userTest.maxTime,
                "displayedOnHomePage": userTest.displayedOnHomePage,
                "target": userTest.target,
                "sprintQuestions": userTest.sprintQuestions,
                "dateTime": userTest.dateTime,
                "accuracy": userTest.accuracy,
                "score": userTest.score,
                "scoreTotal": userTest.scoreTotal,
                "confidence": userTest.confidence,
                "resumeQuesId": userTest.resumeQuesId
            })
        return userTestsData, 200
    except Exception as e:
        return 'Error in accessing userTests records for '+str(userTestInputData)+ '. Details: '+str(e), 500

def updateUserTest(userTestInputData, userTestUpdateData):
    try:
        userTest = db.session.query(UserTest)
        if 'userId' in userTestInputData.keys():
            userTest = userTest.filter_by(userId=userTestInputData['userId'])
        if 'testId' in userTestInputData.keys():
            userTest = userTest.filter_by(testId=userTestInputData['testId'])
        if 'practiceTest' in userTestInputData.keys():
            userTest = userTest.filter_by(practiceTest=userTestInputData['practiceTest'])
        if 'customName' in userTestInputData.keys():
            userTest = userTest.filter_by(customName=userTestInputData['customName'])
        if 'id' in userTestInputData.keys():
            userTest = userTest.filter_by(id=userTestInputData['id'])
        userTest = userTest.first()
        if userTest is None:
            return 'userTest not found for '+str(userTestInputData), 404
        if 'paused' in userTestUpdateData.keys():
            userTest.paused = userTestUpdateData['paused']
        if 'progress' in userTestUpdateData.keys():
            userTest.progress = userTestUpdateData['progress']
        if 'dateTime' in userTestUpdateData.keys():
            userTest.dateTime = userTestUpdateData['dateTime']
        if 'resumeQuesId' in userTestUpdateData.keys():
            userTest.resumeQuesId = userTestUpdateData['resumeQuesId']
        if 'questionIds' in userTestUpdateData.keys():
            userTest.questionIds = userTestUpdateData['questionIds']
        if 'toggleBookmark' in userTestUpdateData.keys():
            userTest.bookmark ^= 1
        if 'coinsEarned' in userTestUpdateData.keys():
            userTest.coinsEarned = userTestUpdateData['coinsEarned']
        if 'score' in userTestUpdateData.keys():
            userTest.score = userTestUpdateData['score']
        if 'confidence' in userTestUpdateData.keys():
            userTest.confidence = userTestUpdateData['confidence']
        if 'timetaken' in userTestUpdateData.keys():
            userTest.timetaken = userTestUpdateData['timetaken']
        if 'accuracy' in userTestUpdateData.keys():
            userTest.accuracy = userTestUpdateData['accuracy']
        if 'addCustomTestLevelIds' in userTestUpdateData.keys():
            userTest.customTestLevelIds = str(int(userTest.customTestLevelIds) + userTestUpdateData['addCustomTestLevelIds'])
        if 'sprintQuestions' in userTestUpdateData.keys():
            userTest.sprintQuestions = userTestUpdateData['sprintQuestions']
        if 'coins' in userTestUpdateData.keys():
            userTest.coins = userTestUpdateData['coins']

        db.session.commit()
        return 'userTest details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateUserTest', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update userTest record '+str(userTestInputData) +' with '+str(userTestUpdateData)+ '. Details: '+ str(e), 500

def insertUserTest(userTest):
    try:
        db.session.add(userTest)
        db.session.flush()
        userTestId = userTest.id
        db.session.commit()
        return userTestId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertUserTest', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add UserTest. error: ' + str(e), 500


#test
def getTest(testInputData):
    try:
        test = Test.query
        if 'id' in testInputData.keys():
            test = test.filter_by(id=testInputData['id'])
        if 'subjectId' in testInputData.keys():
            test = test.filter_by(subjectId=testInputData['subjectId'])
        if 'isStaticTest' in testInputData.keys():
            test = test.filter_by(isStaticTest=testInputData['isStaticTest'])
        test = test.first()
        if test:
            return test, 200
        else:
            return 'Test not found for '+str(testInputData) , 404
    except Exception as e:
        return 'Error in accessing test record for '+str(testInputData)+ '. Details:'+str(e), 500

def getAllTestsByIds(testInputData):
    try:
        tests = Test.query
        # if 'id' in testInputData.keys():
        #     tests = tests.filter_by(id=testInputData['id'])
        if 'ids' in testInputData.keys():
            tests = tests.filter(Test.id.in_(testInputData['ids']))
        tests = tests.all()
        testsData1, testsData = {}, []
        for test in tests:
            testsData1[test.id] = {
                "id": test.id,
                "name": test.name,
                "text2": test.text2,
                "text3": test.text3,
                "conceptId": test.conceptId,
                "chapterId": test.chapterId,
                "subjectId": test.subjectId,
                "categoryId": test.categoryId,
                "imagePath": test.imagePath,
                "description": test.description,
                "preparedBy": test.preparedBy,
                "syllabus": test.syllabus,
                "tags": test.tags,
                "maxCoins": test.maxCoins,
                "isStaticTest": test.isStaticTest,
                "isLoop": test.isLoop,
                "isPracticeTestNeeded": test.isPracticeTestNeeded,
                "questionIds": test.questionIds,
                "maxTime": test.maxTime,
                "status": test.status,
                "testBasedOn": test.testBasedOn,
                "addedBy": test.addedBy,
                "datetime": test.datetime
            }
        for testId in testInputData['ids']:
            if testId in testsData1.keys():
                testsData.append(testsData1[testId])
            else:
                testsData.append(None)
        return testsData, 200
    except Exception as e:
        return 'Error in accessing tests by ids records for '+str(testInputData)+ '. Details: '+str(e), 500

def getAllTests(testInputData):
    try:
        tests = Test.query
        if 'ids' in testInputData.keys():
            tests = tests.filter(Test.id.in_(testInputData['ids']))
        if 'subjectId' in testInputData.keys():
            tests = tests.filter_by(subjectId=testInputData['subjectId'])
        if 'subjectIds' in testInputData.keys():
            tests = tests.filter(Test.subjectId.in_(testInputData['subjectIds']))
        if 'chapterId' in testInputData.keys():
            tests = tests.filter_by(chapterId=testInputData['chapterId'])
        if 'chapterIds' in testInputData.keys():
            tests = tests.filter(Test.chapterId.in_(testInputData['chapterIds']))
        if 'conceptIds' in testInputData.keys():
            tests = tests.filter(Test.conceptId.in_(testInputData['conceptIds']))
        if 'isLoop' in testInputData.keys():
            tests = tests.filter_by(isLoop=testInputData['isLoop'])
        if 'isStaticTest' in testInputData.keys():
            tests = tests.filter_by(isStaticTest=testInputData['isStaticTest'])
        if 'status' in testInputData.keys():
            tests = tests.filter_by(status=testInputData['status'])
        if 'startEnd' in testInputData.keys():
            tests = tests.filter(Test.datetime.between(testInputData['startEnd'][0], testInputData['startEnd'][1]))
        if 'desc' in testInputData.keys():
            tests = tests.order_by(-Test.id)
        if 'count' in testInputData.keys():
            return tests.count(), 200

        tests = tests.all()
        testsData = []
        for test in tests:
            testsData.append({
                "id": test.id,
                "name": test.name,
                "text2": test.text2,
                "text3": test.text3,
                "conceptId": test.conceptId,
                "chapterId": test.chapterId,
                "subjectId": test.subjectId,
                "categoryId": test.categoryId,
                "imagePath": test.imagePath,
                "description": test.description,
                "preparedBy": test.preparedBy,
                "syllabus": test.syllabus,
                "tags": test.tags,
                "maxCoins": test.maxCoins,
                "isStaticTest": test.isStaticTest,
                "isLoop": test.isLoop,
                "isPracticeTestNeeded": test.isPracticeTestNeeded,
                "questionIds": test.questionIds,
                "maxTime": test.maxTime,
                "status": test.status,
                "testBasedOn": test.testBasedOn,
                "addedBy": test.addedBy,
                "datetime": test.datetime
            })
        return testsData, 200
    except Exception as e:
        return 'Error in accessing tests records for '+str(testInputData)+ '. Details: '+str(e), 500

#userQuestion
def getAllUserQuestions(userQuestionInputData):
    try:
        userQuestions = UserQuestion.query
        if 'userId' in userQuestionInputData.keys():
            userQuestions = userQuestions.filter_by(userId=userQuestionInputData['userId'])
        if 'bookmark' in userQuestionInputData.keys():
            userQuestions = userQuestions.filter_by(bookmark=userQuestionInputData['bookmark'])
        if 'desc' in userQuestionInputData.keys():
            userQuestions = userQuestions.order_by(-UserQuestion.id)
        userQuestions = userQuestions.all()
        userQuestionsData = []
        for userQuestion in userQuestions:
            userQuestionsData.append({
                "id": userQuestion.id,
                "questionId": userQuestion.questionId,
                "bookmark": userQuestion.bookmark,
                "report": userQuestion.report
            })
        return userQuestionsData, 200
    except Exception as e:
        return 'Error in accessing userQuestions records for '+str(userQuestionInputData)+ '. Details: '+str(e), 500


#question
def getQuestion(questionInputData):
    try:
        question = Question.query
        if 'id' in questionInputData.keys():
            question = question.filter_by(id=questionInputData['id'])
        if 'text' in questionInputData.keys():
            question = question.filter_by(text=questionInputData['text'])
        if 'conceptId' in questionInputData.keys():
            question = question.filter_by(conceptId=questionInputData['conceptId'])
        question = question.first()
        if question:
            return question, 200
        else:
            return 'Question not found for '+str(questionInputData) , 404
    except Exception as e:
        return 'Error in accessing question record for '+str(questionInputData)+ '. Details:'+str(e), 500

def getAllQuestions(questionInputData):
    try:
        questions = Question.query
        # if 'id' in questionInputData.keys():
        #     questions = questions.filter_by(id=questionInputData['id'])
        if 'ids' in questionInputData.keys():
            questions = questions.filter(Question.id.in_(questionInputData['ids']))
        if 'difficultyLevel' in questionInputData.keys():
            questions = questions.filter_by(difficultyLevel=questionInputData['difficultyLevel'])
        if 'limit' in questionInputData.keys():
            questions = questions.limit(questionInputData['limit'])
        questions = questions.all()
        questionsData = []
        for question in questions:
            questionsData.append({
                "id": question.id,
                "text": question.text,
                "conceptId": question.conceptId,
                "addedBy": question.addedBy,
                "datetime": question.datetime,
                "difficultyLevel": question.difficultyLevel,
                "format": question.format,
                "category": question.category,
                "hints": question.hints,
                "hintsImagePath": question.hintsImagePath,
                "description": question.description,
                "tags": question.tags,
                "maxSolvingTime": question.maxSolvingTime,
                "ansExplanation": question.ansExplanation,
                "ansExpImage": question.ansExpImage,
                "previousYearApearance": question.previousYearApearance,
                "status": question.status
            })
        return questionsData, 200
    except Exception as e:
        return 'Error in accessing questions records for '+str(questionInputData)+ '. Details: '+str(e), 500


#concept
def getConcept(conceptInputData):
    try:
        concept = Concept.query
        if 'id' in conceptInputData.keys():
            concept = concept.filter_by(id=conceptInputData['id'])
        if 'name' in conceptInputData.keys():
            concept = concept.filter_by(name=conceptInputData['name'])
        if 'chapterId' in conceptInputData.keys():
            concept = concept.filter_by(chapterId=conceptInputData['chapterId'])
        concept = concept.first()
        if concept:
            return concept, 200
        else:
            return 'Concept not found for '+str(conceptInputData) , 404
    except Exception as e:
        return 'Error in accessing concept record for '+str(conceptInputData)+ '. Details:'+str(e), 500

def getAllConcepts(conceptInputData):
    try:
        concepts = Concept.query
        if 'ids' in conceptInputData.keys():
            concepts = concepts.filter(Concept.id.in_(conceptInputData['ids']))
        if 'chapterIds' in conceptInputData.keys():
            concepts = concepts.filter(Concept.chapterId.in_(conceptInputData['chapterIds']))
        concepts = concepts.all()
        conceptsData = []
        for concept in concepts:
            conceptsData.append({
                "id": concept.id,
                "name": concept.name,
                "chapterId": concept.chapterId,
                "subjectId": concept.subjectId,
                "status": concept.status,
                "addedBy": concept.addedBy,
                "datetime": concept.datetime
            })
        return conceptsData, 200
    except Exception as e:
        return 'Error in accessing concepts records for '+str(conceptInputData)+ '. Details: '+str(e), 500

def insertConcept(concept):
    try:
        db.session.add(concept)
        db.session.flush()
        conceptId = concept.id
        db.session.commit()
        return conceptId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertConcept', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add Concept. error: ' + str(e), 500


#questionFormat
def getQuestionFormat(questionFormatInputData):
    try:
        questionFormat = QuestionFormat.query
        if 'id' in questionFormatInputData.keys():
            questionFormat = questionFormat.filter_by(id=questionFormatInputData['id'])
        questionFormat = questionFormat.first()
        if questionFormat:
            return questionFormat, 200
        else:
            return 'QuestionFormat not found for '+str(questionFormatInputData) , 404
    except Exception as e:
        return 'Error in accessing questionFormat record for '+str(questionFormatInputData)+ '. Details:'+str(e), 500

def getAllQuestionFormats(questionFormatInputData):
    try:
        questionFormats = QuestionFormat.query
        if 'ids' in questionFormatInputData.keys():
            questionFormats = questionFormats.filter(QuestionFormat.id.in_(questionFormatInputData['ids']))
        questionFormats = questionFormats.all()
        questionFormatsData1, questionFormatsData = {}, []
        for questionFormat in questionFormats:
            questionFormatsData1[questionFormat.id] = {
                "id": questionFormat.id,
                "name": questionFormat.name,
                "code": questionFormat.code
        }
        for format in questionFormatInputData['ids']:
            if format in questionFormatsData1.keys():
                questionFormatsData.append(questionFormatsData1[format])
            else:
                questionFormatsData.append(None)
        return questionFormatsData, 200
    except Exception as e:
        return 'Error in accessing questionFormats records for '+str(questionFormatInputData)+ '. Details: '+str(e), 500


#analysis
def getAnalysis(analysisInputData):
    try:
        analysis = Analysis.query
        if 'userId' in analysisInputData.keys():
            analysis = analysis.filter_by(userId=analysisInputData['userId'])
        if 'subjectId' in analysisInputData.keys():
            analysis = analysis.filter_by(subjectId=analysisInputData['subjectId'])
        if 'timeType' in analysisInputData.keys():
            analysis = analysis.filter_by(timeType=analysisInputData['timeType'])
        analysis = analysis.first()
        if analysis:
            return analysis, 200
        else:
            return 'Analysis not found for '+str(analysisInputData) , 404
    except Exception as e:
        return 'Error in accessing analysis record for '+str(analysisInputData)+ '. Details:'+str(e), 500

def updateAnalysis(analysisInputData, analysisUpdateData):
    try:
        analysis = db.session.query(Analysis).filter_by(userId=analysisInputData['userId'], \
        subjectId=analysisInputData['subjectId'], timeType=analysisInputData['timeType']).first()
        if analysis is None:
            return 'analysis not found for '+str(analysisInputData), 404

        if 'confidence' in analysisUpdateData.keys():
            analysis.confidence += analysisUpdateData['confidence']
        if 'confidenceTotal' in analysisUpdateData.keys():
            analysis.confidenceTotal += analysisUpdateData['confidenceTotal']
        if 'score' in analysisUpdateData.keys():
            analysis.score += analysisUpdateData['score']
        if 'scoreTotal' in analysisUpdateData.keys():
            analysis.scoreTotal += analysisUpdateData['scoreTotal']
        if 'totalCorrects' in analysisUpdateData.keys():
            analysis.totalCorrects += analysisUpdateData['totalCorrects']
        if 'totalQuestions' in analysisUpdateData.keys():
            analysis.totalQuestions += analysisUpdateData['totalQuestions']
        if 'totalTests' in analysisUpdateData.keys():
            analysis.totalTests = analysisUpdateData['totalTests']
        if 'totalLoopTests' in analysisUpdateData.keys():
            analysis.totalLoopTests += analysisUpdateData['totalLoopTests']
        if 'totalCustomTests' in analysisUpdateData.keys():
            analysis.totalCustomTests += analysisUpdateData['totalCustomTests']
        if 'totalStaticTests' in analysisUpdateData.keys():
            analysis.totalStaticTests += analysisUpdateData['totalStaticTests']
        if 'totalConceptTests' in analysisUpdateData.keys():
            analysis.totalConceptTests += analysisUpdateData['totalConceptTests']
        if 'totalOtherTests' in analysisUpdateData.keys():
            analysis.totalOtherTests += analysisUpdateData['totalOtherTests']
        if 'totalUserTests' in analysisUpdateData.keys():
            analysis.totalUserTests += analysisUpdateData['totalUserTests']
        if 'difficultyLevelCounts' in analysisUpdateData.keys():
            difficultyLevelCountsAnalysis = ast.literal_eval(analysis.difficultyLevelCounts)
            analysis.difficultyLevelCounts = str([x + y for x, y in zip(difficultyLevelCountsAnalysis, analysisUpdateData['difficultyLevelCounts'])])
        if 'formatCounts' in analysisUpdateData.keys():
            formatCountsAnalysis = ast.literal_eval(analysis.formatCounts)
            analysis.formatCounts = str([x + y for x, y in zip(formatCountsAnalysis, analysisUpdateData['formatCounts'])])

        db.session.commit()
        return 'analysis details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateAnalysis', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update analysis record '+str(analysisInputData) +' with '+str(analysisUpdateData)+ '. Details: '+ str(e), 500

#userConcept
def getAllUserConcepts(userConceptInputData):
    try:
        userConcepts = UserConcept.query
        if 'userId' in userConceptInputData.keys():
            userConcepts = userConcepts.filter_by(userId=userConceptInputData['userId'])
        if 'subjectId' in userConceptInputData.keys():
            userConcepts = userConcepts.filter_by(subjectId=userConceptInputData['subjectId'])
        userConcepts = userConcepts.all()
        userConceptsData = []
        for userConcept in userConcepts:
            userConceptsData.append({
                "id": userConcept.id,
                "conceptId": userConcept.conceptId,
                "score": userConcept.score,
                "scoreTotal": userConcept.scoreTotal
        })
        return userConceptsData, 200
    except Exception as e:
        return 'Error in accessing userConcepts records for '+str(userConceptInputData)+ '. Details: '+str(e), 500


#chapter
def getChapter(chapterInputData):
    try:
        chapter = Chapter.query
        if 'id' in chapterInputData.keys():
            chapter = chapter.filter_by(id=chapterInputData['id'])
        if 'subjectId' in chapterInputData.keys():
            chapter = chapter.filter_by(subjectId=chapterInputData['subjectId'])
        chapter = chapter.first()
        if chapter:
            return chapter, 200
        else:
            return 'Chapter not found for '+str(chapterInputData) , 404
    except Exception as e:
        return 'Error in accessing chapter record for '+str(chapterInputData)+ '. Details:'+str(e), 500

def getAllChapters(chapterInputData):
    try:
        chapters = Chapter.query
        if 'subjectId' in chapterInputData.keys():
            chapters = chapters.filter_by(subjectId=chapterInputData['subjectId'])
        if 'subjectIds' in chapterInputData.keys():
            chapters = chapters.filter(Chapter.subjectId.in_(chapterInputData['subjectIds']))
        if 'sortOrder' in chapterInputData.keys():
            chapters = chapters.order_by(Chapter.sortOrder)
        chapters = chapters.all()
        chaptersData = []
        for chapter in chapters:
            chaptersData.append({
                "id": chapter.id,
                "name": chapter.name,
                'caption': chapter.caption,
                'imagePath': chapter.imagePath
            })
        return chaptersData, 200
    except Exception as e:
        return 'Error in accessing chapters records for '+str(chapterInputData)+ '. Details: '+str(e), 500


#testCategory
def getAllTestCategories(testCategoriesInputData):
    try:
        testCategories = TestCategory.query
        if 'subjectId' in testCategoriesInputData.keys():
            testCategories = testCategories.filter_by(subjectId=testCategoriesInputData['subjectId'])
        if 'sortOrder' in testCategoriesInputData.keys():
            testCategories = testCategories.order_by(TestCategory.sortOrder)
        testCategories = testCategories.all()
        testCategoriesData = []
        for testCategory in testCategories:
            testCategoriesData.append({
                "id": testCategory.id,
                "name": testCategory.name,
                "caption": testCategory.caption,
                "imagePath": testCategory.imagePath,
                "sortOrder": testCategory.sortOrder,
                "subjectId": testCategory.subjectId,
                "datetime": testCategory.datetime
        })
        return testCategoriesData, 200
    except Exception as e:
        return 'Error in accessing testCategories records for '+str(testCategoriesInputData)+ '. Details: '+str(e), 500


#FAQs
def getAllFaqs(faqsInputData):
    try:
        faqs = FAQs.query
        if 'type' in faqsInputData.keys():
            faqs = faqs.filter_by(type=faqsInputData['type'])
        faqs = faqs.all()
        faqsData = []
        for faq in faqs:
            faqsData.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "imagePath": faq.imagePath,
                "type": faq.type,
                "addedBy": faq.addedBy,
                "datetime": faq.datetime
            })
        return faqsData, 200
    except Exception as e:
        return 'Error in accessing faqs records for '+str(faqsInputData)+ '. Details: '+str(e), 500


#UserQuestionTest
def getUserQuestionTest(userQuestionTestInputData):
    try:
        userQuestionTest = UserQuestionTest.query
        if 'userTestId' in userQuestionTestInputData.keys():
            userQuestionTest = userQuestionTest.filter_by(userTestId=userQuestionTestInputData['userTestId'])
        if 'questionId' in userQuestionTestInputData.keys():
            userQuestionTest = userQuestionTest.filter_by(questionId=userQuestionTestInputData['questionId'])
        userQuestionTest = userQuestionTest.first()
        if userQuestionTest:
            return userQuestionTest, 200
        else:
            return 'UserQuestionTest not found for '+str(userQuestionTestInputData) , 404
    except Exception as e:
        return 'Error in accessing userQuestionTest record for '+str(userQuestionTestInputData)+ '. Details:'+str(e), 500

def getAllUserQuestionTests(userQuestionTestInputData):
    try:
        userQuestionTests = UserQuestionTest.query
        if 'userTestId' in userQuestionTestInputData.keys():
            userQuestionTests = userQuestionTests.filter_by(userTestId=userQuestionTestInputData['userTestId'])
        userQuestionTests = userQuestionTests.all()
        userQuestionTestsData = []
        for userQuestionTest in userQuestionTests:
            userQuestionTestsData.append({
                "id": userQuestionTest.id,
                "userTestId": userQuestionTest.userTestId,
                "questionId": userQuestionTest.questionId,
                "review": userQuestionTest.review,
                "seen": userQuestionTest.seen,
                "answer": userQuestionTest.answer,
                "isCorrect": userQuestionTest.isCorrect,
                "isPartial": userQuestionTest.isPartial,
                "marks": userQuestionTest.marks,
                "timetaken": userQuestionTest.timetaken,
                "category": userQuestionTest.category
            })
        return userQuestionTestsData, 200
    except Exception as e:
        return 'Error in accessing userQuestionTests records for '+str(userQuestionTestInputData)+ '. Details: '+str(e), 500

def deleteAllUserQuestionTests(userQuestionTestInputData):
    try:
        userQuestionTests = UserQuestionTest.query
        if 'userTestId' in userQuestionTestInputData.keys():
            userQuestionTests = userQuestionTests.filter_by(userTestId=userQuestionTestInputData['userTestId'])
        userQuestionTests = userQuestionTests.all()
        if not userQuestionTests:
            return " No userQuestionTests records found for "+ str(userQuestionTestInputData), 404

        for userQuestionTest in userQuestionTests:
            db.session.delete(userQuestionTest)
        db.session.commit()
        return "userQuestionTests with "+ str(userQuestionTestInputData) + " are deleted. ", 204
    except Exception as e:
        db.session.rollback()
        return 'Error in accessing userQuestionTests records for '+str(userQuestionTestInputData)+ '. Details: '+str(e), 500

def updateUserQuestionTest(userQuestionTestInputData, userQuestionTestUpdateData):
    try:
        userQuestionTest = db.session.query(UserQuestionTest)
        if 'userTestId' in userQuestionTestUpdateData.keys():
            userQuestionTest.userTestId = userQuestionTestUpdateData['userTestId']
        if 'questionId' in userQuestionTestUpdateData.keys():
            userQuestionTest.questionId = userQuestionTestUpdateData['questionId']
        userQuestionTest = userQuestionTest.first()
        if userQuestionTest is None:
            return 'userQuestionTest not found for '+str(userQuestionTestInputData), 404

        if 'review' in userQuestionTestUpdateData.keys():
            userQuestionTest.review = userQuestionTestUpdateData['review']
        if 'answer' in userQuestionTestUpdateData.keys():
            userQuestionTest.answer = userQuestionTestUpdateData['answer']
        if 'isCorrect' in userQuestionTestUpdateData.keys():
            userQuestionTest.isCorrect = userQuestionTestUpdateData['isCorrect']
        if 'isPartial' in userQuestionTestUpdateData.keys():
            userQuestionTest.isPartial = userQuestionTestUpdateData['isPartial']
        if 'marks' in userQuestionTestUpdateData.keys():
            userQuestionTest.marks = userQuestionTestUpdateData['marks']
        if 'timetaken' in userQuestionTestUpdateData.keys():
            userQuestionTest.timetaken = userQuestionTestUpdateData['timetaken']
        db.session.commit()
        return 'userQuestionTest details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateUserQuestionTest', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update userQuestionTest record '+str(userQuestionTestInputData)+' with '+str(userQuestionTestUpdateData)+ '. Details: '+ str(e), 500

def insertUserQuestionTest(userQuestionTest):
    try:
        db.session.add(userQuestionTest)
        db.session.flush()
        userQuestionTestId = userQuestionTest.id
        db.session.commit()
        return userQuestionTestId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertUserQuestionTest', 400
    except Exception as e:
        db.session.rollback()
        return 'failed to add UserQuestionTest. error: ' + str(e), 500


#QuestionMcqMsqDadSeq
def getQuestionMcqMsqDadSeq(questionMcqMsqDadSeqInputData):
    try:
        questionMcqMsqDadSeq = QuestionMcqMsqDadSeq.query
        if 'questionId' in questionMcqMsqDadSeqInputData.keys():
            questionMcqMsqDadSeq = questionMcqMsqDadSeq.filter_by(questionId=questionMcqMsqDadSeqInputData['questionId'])
        questionMcqMsqDadSeq = questionMcqMsqDadSeq.first()
        if questionMcqMsqDadSeq:
            return questionMcqMsqDadSeq, 200
        else:
            return 'QuestionMcqMsqDadSeq not found for '+str(questionMcqMsqDadSeqInputData) , 404
    except Exception as e:
        return 'Error in accessing questionMcqMsqDadSeq record for '+str(questionMcqMsqDadSeqInputData)+ '. Details:'+str(e), 500


#QuestionFillTorF
def getQuestionFillTorF(questionFillTorFInputData):
    try:
        questionFillTorF = QuestionFillTorF.query
        if 'questionId' in questionFillTorFInputData.keys():
            questionFillTorF = questionFillTorF.filter_by(questionId=questionFillTorFInputData['questionId'])
        questionFillTorF = questionFillTorF.first()
        if questionFillTorF:
            return questionFillTorF, 200
        else:
            return 'QuestionFillTorF not found for '+str(questionFillTorFInputData) , 404
    except Exception as e:
        return 'Error in accessing questionFillTorF record for '+str(questionFillTorFInputData)+ '. Details:'+str(e), 500


#QuestionMatch
def getQuestionMatch(questionMatchInputData):
    try:
        questionMatch = QuestionMatch.query
        if 'questionId' in questionMatchInputData.keys():
            questionMatch = questionMatch.filter_by(questionId=questionMatchInputData['questionId'])
        questionMatch = questionMatch.first()
        if questionMatch:
            return questionMatch, 200
        else:
            return 'QuestionMatch not found for '+str(questionMatchInputData) , 404
    except Exception as e:
        return 'Error in accessing questionMatch record for '+str(questionMatchInputData)+ '. Details:'+str(e), 500

#Instructor
def getInstructor(instructorInputData):
    try:
        instructor = Instructor.query
        if 'id' in instructorInputData.keys():
            instructor = instructor.filter_by(id=instructorInputData['id'])
        if 'email' in instructorInputData.keys():
            instructor = instructor.filter_by(email=instructorInputData['email'])
        if 'token' in instructorInputData.keys():
            instructor = instructor.filter_by(token=instructorInputData['token'])
        instructor = instructor.first()
        if instructor:
            return instructor, 200
        else:
            return 'Instructor not found for '+str(instructorInputData) , 404
    except Exception as e:
        return 'Error in accessing instructor record for '+str(instructorInputData)+ '. Details:'+str(e), 500

def getAllInstructors(instructorsInputData):
    try:
        instructors = Instructor.query
        if 'schools' in instructorsInputData.keys():
            instructors = instructors.filter(Instructor.school.in_(instructorsInputData['schools']))
        if 'school' in instructorsInputData.keys():
            instructors = instructors.filter_by(school=instructorsInputData['school'])
        instructors = instructors.all()

        instructorsData = []
        for instructor in instructors:
            instructorsData.append({
                "id": instructor.id,
                "name": instructor.name,
                "email": instructor.email,
                "mobile": instructor.mobile,
                "password": instructor.password,
                "school": instructor.school,
                "status": instructor.status,
                "createdBy": instructor.createdBy,
                "datetime": instructor.datetime
            })
        return instructorsData, 200
    except Exception as e:
        return 'Error in accessing instructors records for '+str(instructorsInputData)+ '. Details: '+str(e), 500

def updateInstructor(instructorInputData, instructorUpdateData):
    try:
        instructor = db.session.query(Instructor)
        if 'email' in instructorInputData.keys():
            instructor = instructor.filter_by(email=instructorInputData['email'])
        if 'token' in instructorInputData.keys():
            instructor = instructor.filter_by(token=instructorInputData['token'])
        instructor = instructor.first()
        if instructor is None:
            return 'instructor not found for '+str(instructorInputData), 404
        if 'token' in instructorUpdateData.keys():
            instructor.token = instructorUpdateData['token']
        if 'password' in instructorUpdateData.keys():
            instructor.password = instructorUpdateData['password']
        db.session.commit()
        return 'instructor details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateInstructor', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update instructor record '+str(instructorInputData) +' with '+str(instructorUpdateData)+ '. Details: '+ str(e), 500

def insertInstructor(instructor):
    try:
        db.session.add(instructor)
        db.session.flush()
        instructorId = instructor.id
        db.session.commit()
        return instructorId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertInstructor', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to add instructor. error: ' + str(e), 500


#Admin
def getAdmin(adminInputData):
    try:
        admin = Admin.query
        if 'id' in adminInputData.keys():
            admin = admin.filter_by(id=adminInputData['id'])
        if 'email' in adminInputData.keys():
            admin = admin.filter_by(email=adminInputData['email'])
        if 'token' in adminInputData.keys():
            admin = admin.filter_by(token=adminInputData['token'])
        admin = admin.first()
        if admin:
            return admin, 200
        else:
            return 'Admin not found for '+str(adminInputData) , 404
    except Exception as e:
        return 'Error in accessing admin record for '+str(adminInputData)+ '. Details:'+str(e), 500

def updateAdmin(adminInputData, adminUpdateData):
    try:
        admin = db.session.query(Admin)
        if 'email' in adminInputData.keys():
            admin = admin.filter_by(email=adminInputData['email'])
        if 'token' in adminInputData.keys():
            admin = admin.filter_by(token=adminInputData['token'])
        admin = admin.first()
        if admin is None:
            return 'admin not found for '+str(adminInputData), 404
        if 'token' in adminUpdateData.keys():
            admin.token = adminUpdateData['token']
        if 'password' in adminUpdateData.keys():
            admin.password = adminUpdateData['password']
        db.session.commit()
        return 'admin details updated successfully', 200
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at updateAdmin', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to update admin record '+str(adminInputData) +' with '+str(adminUpdateData)+ '. Details: '+ str(e), 500


#InstructorAssignment
def getInstructorAssignment(instructorAssignmentInputData):
    try:
        instructorAssignment = InstructorAssignment.query
        if 'id' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter_by(id=instructorAssignmentInputData['id'])
        instructorAssignment = instructorAssignment.first()
        if instructorAssignment:
            return instructorAssignment, 200
        else:
            return 'InstructorAssignment not found for '+str(instructorAssignmentInputData) , 404
    except Exception as e:
        return 'Error in accessing instructorAssignment record for '+str(instructorAssignmentInputData)+ '. Details:'+str(e), 500

def getAllInstructorAssignments(instructorAssignmentInputData):
    try:
        instructorAssignment = InstructorAssignment.query
        if 'ids' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.id.in_(instructorAssignmentInputData['ids']))
        if 'instructorId' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter_by(instructorId=instructorAssignmentInputData['instructorId'])
        if 'instructorIds' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.instructorId.in_(instructorAssignmentInputData['instructorIds']))
        if 'boards' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.board.in_(instructorAssignmentInputData['boards']))
        if 'grades' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.grade.in_(instructorAssignmentInputData['grades']))
        if 'sections' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.section.in_(instructorAssignmentInputData['sections']))
        if 'subjects' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter(InstructorAssignment.subject.in_(instructorAssignmentInputData['subjects']))
        instructorAssignment = instructorAssignment.all()
        if instructorAssignment:
            return instructorAssignment, 200
        else:
            return 'InstructorAssignment not found for '+str(instructorAssignmentInputData) , 404
    except Exception as e:
        return 'Error in accessing instructorAssignment record for '+str(instructorAssignmentInputData)+ '. Details:'+str(e), 500

def insertInstructorAssignment(instructorAssignment):
    try:
        db.session.add(instructorAssignment)
        db.session.flush()
        instructorId = instructorAssignment.id
        db.session.commit()
        return instructorId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertInstructorAssignment', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to add instructorAssignment. error: ' + str(e), 500

def deleteInstructorAssignment(instructorAssignmentInputData):
    try:
        instructorAssignment = InstructorAssignment.query
        if 'id' in instructorAssignmentInputData.keys():
            instructorAssignment = instructorAssignment.filter_by(id=instructorAssignmentInputData['id'])
        instructorAssignment = instructorAssignment.first()
        if not instructorAssignment:
            return " No instructorAssignment records found for "+ str(instructorAssignmentInputData), 404

        db.session.delete(instructorAssignment)
        db.session.commit()
        return "instructorAssignment with "+ str(instructorAssignmentInputData) + " are deleted. ", 204
    except Exception as e:
        db.session.rollback()
        return 'Error in accessing instructorAssignment records for '+str(instructorAssignmentInputData)+ '. Details: '+str(e), 500


#InstructorTestScheduling
def getInstructorTestScheduling(instructorTestSchedulingInputData):
    try:
        instructorTestScheduling = InstructorTestScheduling.query
        if 'id' in instructorTestSchedulingInputData.keys():
            instructorTestScheduling = instructorTestScheduling.filter_by(id=instructorTestSchedulingInputData['id'])
        instructorTestScheduling = instructorTestScheduling.first()
        if instructorTestScheduling:
            return instructorTestScheduling, 200
        else:
            return 'InstructorTestScheduling not found for '+str(instructorTestSchedulingInputData) , 404
    except Exception as e:
        return 'Error in accessing instructorTestScheduling record for '+str(instructorTestSchedulingInputData)+ '. Details:'+str(e), 500

def getAllInstructorTestSchedulings(instructorTestSchedulingInputData):
    try:
        instructorTestScheduling = InstructorTestScheduling.query
        if 'instructorId' in instructorTestSchedulingInputData.keys():
            instructorTestScheduling = instructorTestScheduling.filter_by(instructorId=instructorTestSchedulingInputData['instructorId'])
        if 'instructorIds' in instructorTestSchedulingInputData.keys():
            instructorTestScheduling = instructorTestScheduling.filter(InstructorTestScheduling.instructorId.in_(instructorTestSchedulingInputData['instructorIds']))
        if 'startEnd' in instructorTestSchedulingInputData.keys():
            instructorTestScheduling = instructorTestScheduling.filter(InstructorTestScheduling.startTime.between(instructorTestSchedulingInputData['startEnd'][0], \
            instructorTestSchedulingInputData['startEnd'][1]))
        instructorTestScheduling = instructorTestScheduling.all()
        if instructorTestScheduling:
            return instructorTestScheduling, 200
        else:
            return 'InstructorTestScheduling not found for '+str(instructorTestSchedulingInputData) , 404
    except Exception as e:
        return 'Error in accessing instructorTestScheduling record for '+str(instructorTestSchedulingInputData)+ '. Details:'+str(e), 500

def insertInstructorTestScheduling(instructorTestScheduling):
    try:
        db.session.add(instructorTestScheduling)
        db.session.flush()
        instructorId = instructorTestScheduling.id
        db.session.commit()
        return instructorId, 201
    except IntegrityError:
        db.session.rollback()
        return 'Duplicate entry or integrity violation at insertInstructorTestScheduling', 400
    except Exception as e:
        db.session.rollback()
        return 'Failed to add instructorTestScheduling. error: ' + str(e), 500

def deleteInstructorScheduling(instructorSchedulingInputData):
    try:
        instructorScheduling = InstructorTestScheduling.query
        if 'id' in instructorSchedulingInputData.keys():
            instructorScheduling = instructorScheduling.filter_by(id=instructorSchedulingInputData['id'])
        instructorScheduling = instructorScheduling.first()
        if not instructorScheduling:
            return " No instructorScheduling records found for "+ str(instructorSchedulingInputData), 404

        db.session.delete(instructorScheduling)
        db.session.commit()
        return "instructorScheduling with "+ str(instructorSchedulingInputData) + " are deleted. ", 204
    except Exception as e:
        db.session.rollback()
        return 'Error in accessing instructorScheduling records for '+str(instructorSchedulingInputData)+ '. Details: '+str(e), 500


#school
def getAllSchools(schoolsInputData):
    try:
        schools = School.query
        if 'id' in schoolsInputData.keys():
            schools = schools.filter_by(id=schoolsInputData['id'])
        schools = schools.all()
        schoolsData = []
        for school in schools:
            schoolsData.append({
                "id": school.id,
                "name": school.name,
                "address": school.address,
                "city": school.city,
                "tuition": school.tuition,
                "status": school.status,
                "datetime": school.datetime
            })
        return schoolsData, 200
    except Exception as e:
        return 'Error in accessing schools records for '+str(schoolsInputData)+ '. Details: '+str(e), 500
