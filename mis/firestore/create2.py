import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "許芷嫙",
  "mail": "a0966086485@gmail.com",
  "lab": 888
}

doc_ref = db.collection("靜宜資管2026a").document("zhixx")
doc_ref.set(doc)
