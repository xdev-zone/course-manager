######## API #########
from flask import jsonify
from app import app, db
from app.models import User, Course


@app.route('/api/courses', methods=['GET'])
def get_courses():
    data = Course.to_collection()
    return jsonify(data)

@app.route('/api/courses/<int:id>', methods=['GET'])
def get_course(id):
    data = Course.query.get_or_404(id).to_dict()
    return jsonify(data)

@app.route('/api/courses/<int:id>/register/<int:userid>', methods=['POST'])
def registrate(id, userid):
    course = Course.query.get_or_404(id)
    user = User.query.get_or_404(userid)
    course.register(user)
    db.session.commit()
    return jsonify(course.to_dict())

@app.route('/api/courses/<int:id>/unregister/<int:userid>', methods=['POST'])
def unregistrate(id, userid):
    course = Course.query.get_or_404(id)
    user = User.query.get_or_404(userid)
    course.unregister(user)
    db.session.commit()
    return jsonify(course.to_dict())
