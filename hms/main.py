from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user


# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='shashank'

login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db=SQLAlchemy(app)



# here we will create db models that is tables


class User(UserMixin ,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50), unique=True)
    password=db.Column(db.String(10000))

class Patients(db.Model):
     pid=db.Column(db.Integer,primary_key=True)
     email=db.Column(db.String(50))
     name=db.Column(db.String(50))
     gender=db.Column(db.String(50))
     slot=db.Column(db.String(50))
     disease=db.Column(db.String(50))
     time=db.Column(db.String(50),nullable=False)
     date=db.Column(db.String(50),nullable=False)
     dept=db.Column(db.String(50))
     number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Roomno(db.Model):
    rid=db.Column(db.Integer,primary_key=True)
    roomno=db.Column(db.Integer)
    email=db.Column(db.String(50))
    doctorpatientname=db.Column(db.String(50))
    


# here we will pass endpoints and run the fuction
@app.route('/')
def index():
    
    return render_template('index.html')
    
    
@app.route('/doctors',methods=['POST','GET'])
@login_required
def doctor():
    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        flash("Information is Stored","primary")



    return render_template('doctor.html')

@app.route('/roomno',methods=['POST','GET'])
@login_required
def roomno():
    if request.method=="POST":

        email=request.form.get('email')
        doctorpatientname=request.form.get('doctorpatientname')
        roomno=request.form.get('roomno')

        query=db.engine.execute(f"INSERT INTO `roomno` (`email`,`doctorpatientname`,`roomno`) VALUES ('{email}','{doctorpatientname}','{roomno}')")
        flash("Room Alloted","primary")



    return render_template('roomno.html')

@app.route('/patients',methods=['POST','GET'])
@login_required
def patient():
    doct=db.engine.execute("SELECT * from `doctors`")
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        query=db.engine.execute( f"INSERT INTO `patients`(`email`,`name`,	`gender`,`slot`,`disease`,`time`,`date`,`dept`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{dept}','{number}')")

        flash("booking confirmed","info")
    return render_template('patient.html',doct=doct)

@app.route('/bookings')
@login_required
def bookings():
    em=current_user.email
    query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}' ")
    
    return render_template('booking.html',query=query)

@app.route('/roomalloted')
@login_required
def roomalloted():
    em=current_user.email
    query=db.engine.execute(f"SELECT * FROM `roomno` WHERE email='{em}' ")
    
    return render_template('roomalloted.html',query=query)
    

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name}', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}', `time` = '{time}', `date` = '{date}', `dept` = '{dept}', `number` = '{number}' WHERE `patients`.`pid` = {pid}")
        flash("Slot is Updates","success")
        return redirect('/bookings')
    
    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    flash("Slot Deleted Successful","danger")
    return redirect('/bookings')




@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
       username=request.form.get('username')
       email=request.form.get('email')
       password=request.form.get('password')
       user= User.query.filter_by(email=email).first()
       if user:
           flash("email already exist","warning")
           return render_template('/signup.html')
       encpassword=generate_password_hash(password)

       new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')" )
           
        
        
       flash("signup success, please login","success")
       return render_template('login.html')


    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
       email=request.form.get('email')
       password=request.form.get('password')
       user=User.query.filter_by(email=email).first()
       if user and check_password_hash(user.password,password):
           login_user(user)
           flash("login success","primary")
           return redirect(url_for('index'))
        
       else:
           flash("invalid credential","danger")
           return render_template('login.html')


    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logout successful","warning")
    return render_template('login.html')



app.run(debug=True)    
