# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

# # Prevent multiple initialization
# if not firebase_admin._apps:

#     cred = credentials.Certificate("firebase-key.json")

#     firebase_admin.initialize_app(cred)

# # Firestore database object
# db = firestore.client()
import firebase_admin
from firebase_admin import credentials
 
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)