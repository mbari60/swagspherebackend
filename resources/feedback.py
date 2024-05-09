from flask_restful import Resource, reqparse, fields, marshal
from models import FeedbackModel, db
from datetime import datetime, timedelta
from sqlalchemy import func

feedback_fields = {
    "id": fields.Integer,
    "user_id": fields.Integer,
    "message": fields.String,
    "rating": fields.Integer,
    "created_at": fields.DateTime(dt_format="iso8601"),
}

class FeedbackResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        self.parser.add_argument('message', type=str, required=True, help="Message is required")
        self.parser.add_argument('rating', type=int)

    def get(self, feedback_id=None):
        if feedback_id:
            feedback = FeedbackModel.query.get(feedback_id)
            if feedback:
                return marshal(feedback, feedback_fields), 200
            else:
                return {"message": "Feedback not found"}, 404
        else:
            feedbacks = FeedbackModel.query.all()
            if feedbacks:
                return marshal(feedbacks, feedback_fields)
            else:
                return {"message": "No feedbacks available"}, 404

    def post(self):
        args = self.parser.parse_args()
        feedback = FeedbackModel(**args)
        db.session.add(feedback)
        db.session.commit()
        return marshal(feedback, feedback_fields), 201

    def put(self, feedback_id):
        args = self.parser.parse_args()
        feedback = FeedbackModel.query.get(feedback_id)
        if feedback:
            feedback.user_id = args['user_id']
            feedback.message = args['message']
            feedback.rating = args['rating']
            db.session.commit()
            return marshal(feedback, feedback_fields), 200
        else:
            return {"message": "Feedback not found"}, 404

    def delete(self, feedback_id):
        feedback = FeedbackModel.query.get(feedback_id)
        if feedback:
            db.session.delete(feedback)
            db.session.commit()
            return {"message": "Feedback deleted successfully"}, 204
        else:
            return {"message": "Feedback not found"}, 404
