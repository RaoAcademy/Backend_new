
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("src/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


def sendPush(title, msg, imagePath, registration_token, dataObject=None):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
            image=imagePath
        ),
        data=dataObject,
        tokens=registration_token,
    )
    response = messaging.send_multicast(message)
