import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("package_log.json")

connection = firebase_admin.initialize_app(cred)