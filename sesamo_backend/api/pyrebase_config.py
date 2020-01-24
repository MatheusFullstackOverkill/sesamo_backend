import pyrebase

config = {
    "apiKey": "AIzaSyDDp0Kbb1pmL6RDeWPT5SDXQ8hBNMt4FHc",
    "authDomain": "cesamo-162d1e.firebaseapp.com",
    "databaseURL": "https://cesamo-162d1e.firebaseio.com",
    "projectId": "cesamo-162d1e",
    "storageBucket": "cesamo-162d1e.appspot.com",
    "messagingSenderId": "944173613735",
    "appId": "1:944173613735:web:58ac614233b8b421f89182"
}

firebase = pyrebase.initialize_app(config)