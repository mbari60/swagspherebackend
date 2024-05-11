import os
from flask import Flask,request, render_template , jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager , jwt_required, get_jwt_identity
from datetime import timedelta
from flask_migrate import Migrate
from flask_restful import Api , marshal
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db , UserOfferModel , UserModel , OfferModel , OrderItemModel , ProductModel , OrderModel

# the resources to create endpoints
from resources.users import userSchema,Login,user_fields
from resources.products import ProductResource
#from resources.variantproducts import ProductVariantResource
#from resources.orders import OrderResource
from resources.offers import OfferResource
from resources.notifications import NotificationResource 
from resources.feedback import FeedbackResource
#from resources.offerbookings import UserOfferModel


app = Flask(__name__)

CORS(app)
api = Api(app)
bcrypt = Bcrypt(app)
JWTManager(app)

# should be at the top b4 the db and migration initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migration = Migrate(app, db)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Setup for JWT
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)



# the routes 
api.add_resource(userSchema, '/registration')
api.add_resource(Login, '/login')
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
#api.add_resource(ProductVariantResource, '/variantproducts', '/variantproducts/<int:product_id>')
#api.add_resource(OrderResource, '/orders', '/orders/<int:order_id>')
api.add_resource(OfferResource, '/offers', '/offers/<int:offer_id>')
api.add_resource(NotificationResource, '/notifications', '/notifications/<int:notification_id>')
api.add_resource(FeedbackResource, '/feedbacks', '/feedbacks/<int:id>')
# api.add_resource(UserOfferResource, '/offerbookings', '/offerbookings/<int:id>')

#admin getting all users 
@app.route('/users', methods=['GET'])
def get_all_users():
    users = UserModel.query.all()
    if users:
        return marshal(users, user_fields), 200
    else:
        return {"message": "No users found"}, 404


# offer bookings 
@app.route('/offerbookings', methods=['POST'])
@jwt_required()
def create_offer_booking():
    args = request.get_json()
    args['user_id'] = get_jwt_identity()
    # Check if the user has already booked this offer
    existing_booking = UserOfferModel.query.filter_by(user_id=args['user_id'], offer_id=args['offer_id']).first()
    if existing_booking:
        return {"message": "You have already booked this offer"}, 400

    user_offer = UserOfferModel(**args)

    # Fetch user and offer details
    user = UserModel.query.filter_by(id=args['user_id']).first()
    #email = user.email if user else None  # Handle potential missing user
    offer = OfferModel.query.filter_by(id=args['offer_id']).first()
    
    if not offer.slots_limit > 0:
        return {"message":"all offer products have been purchased , try your luck next time"}

    if user and offer:
        offer.slots_limit -= 1
        db.session.commit()
        send_offerbookingconfirmation_email(user, offer)
        send_adminbooking_email(user, offer)
        db.session.add(user_offer)
        db.session.commit()
        return {"message":"offer purchase have been received and will be acted upon within the next hours", "status":"success"}, 200
    return {"message":"only registered users can make this offer purchase","status":"fail"},400


def send_offerbookingconfirmation_email(user, offer):
    # Create a message object
    msg = Message('Offer Booking Confirmation Email', sender='kevin.wanjiru600@gmail.com', recipients=[user.email])
    msg.html = render_template('offer_booking_confirmation.html', user = user , offer= offer)
    try:
        # Send the email
        mail.send(msg)
        return {'message': 'Email sent successfully'}, 200
    except:
        return {'message': 'Failed to send email'}, 500    

def send_adminbooking_email(user, offer):
    admin_email = os.environ.get('MAIL_USERNAME')
    # Create a message object
    msg = Message('New Offer Purchase', sender='kevin.wanjiru600@gmail.com', recipients=[admin_email])
    msg.html = render_template('new_offer_booking_notification.html', user = user , offer= offer)
    try:
        # Send the email
        mail.send(msg)
        return {'message': 'Email sent successfully'}, 200
    except:
        return {'message': 'Failed to send email'}, 500    
    


# making orders and cancellations 
@app.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.json
    user_id = get_jwt_identity()
    print(user_id)
    # Check if required fields are provided
    if not 'user_id' or 'order_items' not in data:
        return jsonify({'message': 'User ID and order items are required'}), 400
    
    # Extract user_id from the request data
   
    # Check if the user exists
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Extract order items from the request data
    order_items = data['order_items']
    
    # Calculate total amount for the order
    total_amount = 0
    for item in order_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')
        
        # Fetch product details
        product = ProductModel.query.get(product_id)
        if not product:
            return jsonify({'message': f'Product with ID {product_id} not found'}), 404
        
        unit_price = product.price
        total_amount += unit_price * quantity
    
    # Create the order
    order = OrderModel(user_id=user_id, total_amount=total_amount)
    db.session.add(order)
    db.session.commit()
    
    # Create order items
    for item in order_items:
        product_id = item.get('product_id')
        quantity = item.get('quantity')
        unit_price = ProductModel.query.get(product_id).price
        
        order_item = OrderItemModel(order_id=order.id, product_id=product_id, quantity=quantity, unit_price=unit_price)
        db.session.add(order_item)
    
    send_orderconfimation_email(user,order)
    send_admin_neworder_email(user,order)
    user.merit_points +=1
    db.session.commit()
    
    return jsonify({'message': 'Order created successfully', 'order_id': order.id, 'total_amount': total_amount}), 201


@app.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    # Get the order
    order = OrderModel.query.get(order_id)
    
    # Check if the order exists
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    # Check if the current user is the one who made the order
    current_user_id = request.json.get('user_id')  # Assuming the user ID is sent in the request JSON
    if order.user_id != current_user_id:
        return jsonify({'message': 'You are not authorized to cancel this order'}), 403
    
    user = UserModel.query.filter_by(id = current_user_id).first()
    # Delete order items associated with the order
    OrderItemModel.query.filter_by(order_id=order_id).delete()

    # Send email notification to admin and user
    send_order_cancellation_email_to_user(user, order)
    send_order_cancellation_email_to_admin(user, order)

    # Delete the order
    db.session.delete(order)
    db.session.commit()
    
    return jsonify({'message': 'Order canceled successfully', "status":"success"}), 200

@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = OrderModel.query.all()
    order_list = []
    for order in orders:
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'status': order.status,
            'order_items': []
        }
        
        # Fetch order items for each order
        order_items = OrderItemModel.query.filter_by(order_id=order.id).all()
        for item in order_items:
            product = ProductModel.query.get(item.product_id)
            if product:
                order_data['order_items'].append({
                    'product_id': item.product_id,
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price
                })
        
        order_list.append(order_data)
    
    return jsonify(order_list), 200

# confirmation emails 
def send_admin_neworder_email(user, order):
    msg = Message('Order purchased Confirmation Email', sender='kevin.wanjiru600@gmail.com', recipients=[user.email])
    msg.html = render_template('order_confirmation_user.html', user = user , order =order)
    try:
        # Send the email
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 500   

def send_orderconfimation_email(user,order):
    admin_email = os.environ.get('MAIL_USERNAME')
    msg = Message('Order purchased Confirmation Email', sender='kevin.wanjiru600@gmail.com', recipients=[admin_email])
    msg.html = render_template('new_order_notification_admin.html', user = user , order =order)
    try:
        # Send the email
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 500  

def send_order_cancellation_email_to_user(user, order):
    msg = Message('Order Cancellation Notification', sender='your_email@example.com', recipients=[user.email])
    msg.html = render_template('order_cancellation_notification_user.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 500
    
def send_order_cancellation_email_to_admin(user, order):
    admin_email = os.environ.get('MAIL_USERNAME')
    msg = Message('New Order Cancellation Notification', sender='your_email@example.com', recipients=[admin_email])
    msg.html = render_template('order_cancellation_notification_admin.html', user=user, order=order)
    try:
        mail.send(msg)
        return {'message': 'Email sent successfully', "status":"success"}, 200
    except:
        return {'message': 'Failed to send email', "status":"fail"}, 400

@app.route('/deliverydone/<int:order_id>', methods=['POST'])
def order_delivered(order_id):
    order = OrderModel.query.filter_by(id=order_id).first()
    if order:
        order.status = True
        db.session.commit()
        return {"message":"Successfully delivered" , "status":"Success"},200
    return {'message': 'failed to mark as delivered' , "status":"fail"}, 400


if __name__ == '__main__':
    app.run(debug=True)
