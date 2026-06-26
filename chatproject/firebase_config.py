
import os
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "firebase-key.json")

# initialize once
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

# provide a client
def get_firestore_client():
    return firestore.client()
