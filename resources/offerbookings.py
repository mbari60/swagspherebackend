from flask_restful import Resource, fields, reqparse
from models import UserModel, OfferModel

user_offer_fields = {
    "id": fields.Integer,
    "user_id": fields.Integer,
    "username": fields.String(attribute=lambda user_id: UserModel.query.get(user_id).username if user_id else None),
    "offer_id": fields.Integer,
    "offer_name": fields.String(attribute=lambda offer_id: OfferModel.query.get(offer_id).offer_name if offer_id else None),
}


class UserOfferResource(Resource):
        
        offer_parser = reqparse.RequestParser()
        offer_parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        offer_parser.add_argument('offer_id', type=int, required=True, help="Offer ID is required")

#     def post(self):
#         from app import mail  # Import mail locally inside the function
#         args = self.parser.parse_args()

#         # Check if the user has already booked this offer
#         existing_booking = UserOfferModel.query.filter_by(user_id=args['user_id'], offer_id=args['offer_id']).first()
#         if existing_booking:
#             return {"message": "You have already booked this offer"}, 400

#         user_offer = UserOfferModel(**args)
#         db.session.add(user_offer)
#         db.session.commit()

#         # Fetch user and offer details
#         user = UserModel.query.get(args['user_id'])
#         offer = OfferModel.query.get(args['offer_id'])

#         # Send confirmation email to user
#         if user and offer:
#             subject = "Offer Booking Confirmation"
#             send_email(user.email, subject, "offer_booking_confirmation.html", user=user, offer=offer)

#             # Send notification email to admin
#             admin_email = os.environ.get("MAIL_USERNAME")  # Fix the syntax error here
#             admin_subject = "New Offer Booking"
#             send_email(admin_email, admin_subject, "new_offer_booking_notification.html", user=user, offer=offer)

#         return marshal(user_offer, user_offer_fields), 201

# def send_email(recipient, subject, template, **kwargs):
#     try:
#         msg = Message(subject=subject, recipients=[recipient])
#         msg.html = render_template(template, **kwargs)
#         mail.send(msg)
#     except Exception as e:
#         return {"message": "failed to send email", "status": "error"}, 400
