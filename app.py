import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from form import UserForm  
from flask import flash, render_template, redirect, url_for

app = Flask(__name__)

if os.environ.get("RENDER"):  
    db_path = os.path.join("/tmp", "users.db")  
else:  
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'defaultsecret')

print("Database Path:", db_path)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.name}>"




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 




with app.app_context():
    db.create_all()


@app.route('/', methods=['GET','POST'])
def index():
    form = UserForm()
    
    if form.validate_on_submit():
        
      existing_user =User.query.filter_by(email =form.email.data).first()
    
      if existing_user:  
        
        flash("This email is already registered!", "warning")

        
      else:
          user = User(name=form.name.data, email=form.email.data)
          db.session.add(user)
          db.session.commit()
          return redirect (url_for('index'))
          
     
    users = User.query.all() 
    return render_template('index.html', form=form , users=users)     
          
          
          
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

