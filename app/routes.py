from flask import Flask,render_template,request,flash,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'

db = SQLAlchemy(app)

'''
数据库定义部分
'''
# 定义ORM
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


# 创建表格、插入数据
@app.before_first_request
def create_db():
    db.drop_all()  # 每次运行，先删除再创建
    db.create_all()

    admin = User(username='admin', password='root', email='admin@example.com')
    db.session.add(admin)

    guestes = [User(username='guest1', password='guest1', email='guest1@example.com'),
               User(username='guest2', password='guest2', email='guest2@example.com'),
               User(username='guest3', password='guest3', email='guest3@example.com'),
               User(username='guest4', password='guest4', email='guest4@example.com')]
    db.session.add_all(guestes)
    db.session.commit()


'''
辅助函数、装饰器
'''
# 登录检验（用户名、密码验证）
def valid_login(username, password):
    user = User.query.filter(and_(User.username == username, User.password == password)).first()
    if user:
        return True
    else:
        return False


# 注册检验（用户名、邮箱验证）
def valid_regist(username, email):
    user = User.query.filter(or_(User.username == username, User.email == email)).first()
    if user:  # 若已经存在重复的用户名或邮箱
        return False
    else:
        return True




@app.route('/')
# 首页
@app.route('/index')
def index():
    return render_template('index.html', username=session.get('username'))


# 登录页
@app.route('/login',methods=['GET','POST'])
def login():
    # error = None
    if request.method == 'POST':

        name = request.form['username']
        psw = request.form['password']
        if valid_login(name, psw):
            session['username'] = request.form.get('username')
            return redirect(url_for('index'))
        else:
            flash("错误的用户名或密码！")

    # return render_template('login.html',error=error)
    return render_template('login.html')


# 注销
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# 注册
@app.route('/register',methods=['GET','POST'])
def register_form():
    # error = None
    if request.method == 'POST':
        if valid_regist(request.form['username'], request.form['email']):
            user = User(username=request.form['username'], password=request.form['password'],
                        email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            flash("成功注册！")
            return redirect(url_for('login'))
        else:
            flash("该用户名或邮箱已被注册！")

    return render_template('register.html')

