import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db

# the resources to create endpoints
from resources.users import userSchema,Login
from resources.products import ProductResource


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




@app.route('/')
def hello():
    return 'Hello, World!'

# Route to send email confirmation
@app.route('/send_email', methods=['GET'])
def send_email():
    recipient_email = "kevinmbari600@gmail.com"

    # Create a message object
    msg = Message('Confirmation Email', sender='your-email@example.com', recipients=[recipient_email])
    msg.html = render_template('email_template.html', name='Recipient Name')  # HTML email template

    try:
        # Send the email
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to send email'}), 500

if __name__ == '__main__':
    app.run(debug=True)
