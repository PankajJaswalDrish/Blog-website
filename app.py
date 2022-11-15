from flask import Flask, render_template, request,session, redirect
import pymongo
from pymongo import MongoClient
from datetime import *
import datetime
from flask_mail import Mail
from model import *
import json
from bson import json_util
from bson.objectid import ObjectId
import uuid
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage



'''
    Access the config file parameters
'''
with open('config.json', 'r') as c:
    params = json.load(c)["params"]
    
    

app = Flask(__name__)

app.secret_key = 'super-secret-key'



app.config['UPLOAD_FOLDER'] = params['upload_location']




'''
    Send Mail from contact page

app.config.update(
    MAIL_SERVER = 'mail.drishinfo.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
'''


#    params['websitename']
    
client = MongoClient('localhost', 27017)
# try:
#     print(client.server_info())
# except Exception:
#     print("Unable to connect to the server.")
# db = MongoClient(app)
# Replace the uri string with your MongoDB deployment's connection string.

#client = MongoClient('localhost', 27017, username='username', password='password')
# set a 5-second connection timeout
#client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

db = client.Blog_test
Contact = db.Contact
Post = db.Post

'''For Contact Page information Update in db'''
def contact_page(_id, name, phone, msg, date, email):
    """
    Inserts a comment into the comments collection, with the following fields:
    - "SrNo", "name", "phone", "msg", "date", "email"
    Name and email must be retrieved from the "user" object.
    """
    comment_doc = { '_id' : _id, 'name' : name, 'phone': phone,'message':msg, 'date' : date, 'email':email}
    return db.Contact.insert_one(comment_doc)

'''For Post Page data save in db '''  
def Post_page(_id, title, slug, content, date, img_file):
    """
    Inserts a comment into the comments collection, with the following fields:
    - "SrNo", "name", "slug", "content", "date"
    Name and email must be retrieved from the "user" object.
    """
    comment_doc = { 'SrNo' : _id, 'title' : title, 'slug':slug, 
                   'content':content, 'date' : date,'img_file':img_file
                   }
    return db.Post.find({"_id":"_id"},{"title":"title"},
                        {"slug":"slug"},{"content":"content"},
                        {"date":"date"},{"img_file":"img_file"})
def Post_page_insert(_id,title, slug, content, date, img_file,tagline):
    """
    Inserts a comment into the comments collection, with the following fields:
    - "SrNo", "name", "slug", "content", "date"
    Name and email must be retrieved from the "user" object.
    """
    comment_doc = { '_id' : _id, 'title' : title, 'slug':slug, 'tagline' : tagline,
                   'content':content, 'date' : date,'img_file':img_file
                   }
    return db.Post.insert_one(comment_doc)

def Post_page_update(_id, post):
    """
    Inserts a comment into the comments collection, with the following fields:
    - "SrNo", "name", "slug", "content", "date"
    Name and email must be retrieved from the "user" object.
    """
    # comment_doc = { '_id' : _id, 'title' : title, 'slug':slug, tagline : 'tagline',
    #                'content':content, 'date' : date,'img_file':img_file
    #              }
    return db.Post.update_one({"_id": _id},{"$set": post})

#################################### Login page #######################################################

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    posts = []
    if ('user' in session and session ['user'] == params['admin_user']):
        for post in Post.find():
            posts.append(post)
        return render_template("dashboard.html",params=params, posts=posts)
    
    if (request.method ==  'POST'):
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            #set session variable
            session['user']=username
            for post in Post.find():
                posts.append(post)
            return render_template("dashboard.html",params=params, posts=posts)
     
    return render_template("login.html",params=params)

#################################### Logout page #######################################################
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


#################################### image upload page #######################################################
@app.route('/uploader', methods = ['POST'])
def uploader():
    if "user" in session and session['user']==params['admin_user']:
        if request.method=='POST':
            print(request.files)
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"

#################################### Edit Post #######################################################

@app.route("/edit/<string:_id>", methods = ['GET','POST'])
def edit(_id):
    post = []
    if ('user' in session and session ['user'] == params['admin_user']):
        if (request.method == 'POST'):
            print("------------")
            #_id = request.form.get('_id')
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.datetime.now()
            print("=====================================================")
            print(_id)
            if _id == '0' :
                ''' ADD POST here'''
                post = Post_page_insert(_id = uuid.uuid4().hex, title = title, slug = slug,
                                        content = content,img_file = img_file, 
                                        tagline = tagline, date = date ) 
                
            else:

                '''Edit Post Here'''
                res_data = json_util._json_convert(post)
                print("=====res_data =====>",res_data)             
                
                post = db.Post.update_one({"_id": _id},{ "$set": {
                    "title": title,
                    "slug": slug,
                    "content": content,
                    "img_file": img_file,
                    "tagline": tagline,
                }})
                print("****************",post)
                return redirect('/edit/'+ _id)

    post = db.Post.find_one(_id)                                              
    return render_template('edit.html',params=params,_id = _id, post=post)
      
          
#################################### Delete post #######################################################
    
@app.route("/delete/<string:_id>" , methods=['GET', 'POST'])
def delete(_id):
    if "user" in session and session['user']==params['admin_user']:
        post = db.Post.find_one(_id)
        db.Post.delete_one(post)
    return redirect("/dashboard","deleted Successfully")
#################################### Home page #######################################################
@app.route("/")
def home():
    a = params['no.-of-post']
    posts = []    
    for post in Post.find().limit(a):
        posts.append(post) 
    return render_template('index.html', params=params, posts=posts,
                           response=json.dumps({"Status": "UP"}),
                           status=200,mimetype='application/json' )


#################################### about page #######################################################

@app.route("/about")
def about():
    return render_template('about.html',params=params)

#################################### post page #######################################################
@app.route("/post/<string:post_slug>", methods=['GET', 'POST'])
def post_route(post_slug):
    data = db.Post.find_one({"slug":post_slug})
    res_data = json_util._json_convert(data)
    if (request.method == 'GET'):
        post={"_id":res_data['_id'],"title": res_data['title'],
        "slug" : res_data['slug'],
        "content": res_data['content'],
        "img_file" :res_data['img_file'],
        "tagline" : res_data['tagline'],
        "date":data['date'].strftime("%b %d %Y %H:%M:%S")
        }
        return render_template('post.html',params=params,post=post)
    elif request.method == 'POST':
        #print(json.loads(request.data))
        data = json.loads(request.data)
        post = {
        '_id' : uuid.uuid4().hex,
        "title" : data['title'],
        "slug" : data['slug'],
        "content" : data['content'],
        "img_file" : data['img_file'],
        "tagline" : data['tagline'],
        "date": datetime.datetime.now()
        
        }
        db.Post.insert_one(post)
        return({"post": post})

#################################### contact page #######################################################
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    #'SrNo' : SrNo, 'name' : name, 'phone': phone,'message':msg, 'date' : date, 'email':email 
    if(request.method=='POST'):
        '''Add entry to the database'''
        # _id = request.form.get('_id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = contact_page(_id=uuid.uuid4().hex, name=name, phone = phone, msg = message, 
                             date = datetime.datetime.now(),email = email )
        # mail.send_message('New message from ' + name,
        #                   sender=email,
        #                   recipients = [params['gmail-user']],
        #                   body = message + "\n" + phone
        #                   )
    return render_template('contact.html',params=params)

#################################### End Functionality #######################################################

app.run(debug=True)

