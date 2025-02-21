import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# 設定 MySQL 資料庫
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["JWT_VERIFY_SUB"]=False

db = SQLAlchemy(app)
jwt = JWTManager(app)

# 定義 User 模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# 定義 Course 模型
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# 註冊 API
@app.route("/api/v1/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "使用者名稱存在"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email存在"}), 400
    hashed_password = generate_password_hash(data["password"], method='pbkdf2:sha256')
    user = User(username=data["username"], password=hashed_password, email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "註冊成功"}), 201

# 登入 API
@app.route("/api/v1/auth", methods=["POST"])
def auth():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and check_password_hash(user.password, data["password"]):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "username": user.username})
    return jsonify({"message": "驗證失敗"}), 401

# 新增課程 API
@app.route("/api/v1/courses", methods=["POST"])
@jwt_required()
def add_course():
    user_id = get_jwt_identity()
    data = request.json
    if Course.query.filter_by(course_code=data["course_code"], user_id=user_id).first():
        return jsonify({"message": "課程已存在"}), 400
    course = Course(course_code=data["course_code"], user_id=user_id)
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "課程新增成功"}), 201

# 取得課程 API
@app.route("/api/v1/courses", methods=["GET"])
@jwt_required()
def get_courses():
    user_id = get_jwt_identity()
    courses = Course.query.filter_by(user_id=user_id).all()
    return jsonify([{"course_code": c.course_code} for c in courses])

# 刪除課程 API
@app.route("/api/v1/courses/<string:course_code>", methods=["DELETE"])
@jwt_required()
def delete_course(course_code):
    user_id = get_jwt_identity()
    course = Course.query.filter_by(course_code=course_code, user_id=user_id).first()
    if not course:
        return jsonify({"message": "找不到此課程"}), 404
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "課程刪除成功"}), 200

#前端頁面
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # 在應用程式上下文中創建資料庫表格
    app.run(host="0.0.0.0", port=5000)
