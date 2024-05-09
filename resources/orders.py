from flask_restful import Resource, reqparse, fields, marshal
from models import OrderModel, OrderItemModel, UserModel, ProductVariantModel, db
from flask_mail import Message

order_fields = {
    "id": fields.Integer,
    "user_id": fields.Integer,
    "total_amount": fields.Integer,
    "status": fields.Boolean,
}

order_item_fields = {
    "id": fields.Integer,
    "order_id": fields.Integer,
    "variant_id": fields.Integer,
    "quantity": fields.Integer,
    "unit_price": fields.Integer,
}

class OrderResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', type=int, required=True, help="User ID is required")
        self.parser.add_argument('total_amount', type=int, required=True, help="Total amount is required")
        self.parser.add_argument('status', type=bool, required=False)

    def get(self, order_id=None):
        if order_id:
            order = OrderModel.query.get(order_id)
            if order:
                return marshal(order, order_fields), 200
            else:
                return {"message": "Order not found"}, 404
        else:
            orders = OrderModel.query.all()
            if orders:
                return marshal(orders, order_fields)
            else:
                return {"message": "No orders available"}, 404

    def post(self):
        args = self.parser.parse_args()
        order = OrderModel(**args)
        db.session.add(order)
        db.session.commit()

        # Send confirmation email to user
        user = UserModel.query.get(args['user_id'])
        if user:
            self.send_confirmation_email(user, order)

        return marshal(order, order_fields), 201

    def send_confirmation_email(self, user, order):
        # Here, you would use Flask-Mail or any other email library to send the email
        # Example using Flask-Mail:
        # msg = Message("Order Confirmation", recipients=[user.email])
        # msg.body = f"Dear {user.username}, your order has been received and is being processed. Your order details: {order}"
        # mail.send(msg)
        pass

    def put(self, order_id):
        args = self.parser.parse_args()
        order = OrderModel.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404
        for key, value in args.items():
            setattr(order, key, value)
        db.session.commit()
        return marshal(order, order_fields), 200

    def delete(self, order_id):
        order = OrderModel.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return {"message": "Order deleted successfully"}, 204
        else:
            return {"message": "Order not found"}, 404


class OrderItemResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('order_id', type=int, required=True, help="Order ID is required")
        self.parser.add_argument('variant_id', type=int, required=True, help="Variant ID is required")
        self.parser.add_argument('quantity', type=int, required=True, help="Quantity is required")
        self.parser.add_argument('unit_price', type=int, required=True, help="Unit price is required")

    def get(self, order_item_id=None):
        if order_item_id:
            order_item = OrderItemModel.query.get(order_item_id)
            if order_item:
                return marshal(order_item, order_item_fields), 200
            else:
                return {"message": "Order item not found"}, 404
        else:
            order_items = OrderItemModel.query.all()
            if order_items:
                return marshal(order_items, order_item_fields)
            else:
                return {"message": "No order items available"}, 404

    def post(self):
        args = self.parser.parse_args()
        order_item = OrderItemModel(**args)
        db.session.add(order_item)
        db.session.commit()
        return marshal(order_item, order_item_fields), 201

    def put(self, order_item_id):
        args = self.parser.parse_args()
        order_item = OrderItemModel.query.get(order_item_id)
        if not order_item:
            return {"message": "Order item not found"}, 404
        for key, value in args.items():
            setattr(order_item, key, value)
        db.session.commit()
        return marshal(order_item, order_item_fields), 200

    def delete(self, order_item_id):
        order_item = OrderItemModel.query.get(order_item_id)
        if order_item:
            db.session.delete(order_item)
            db.session.commit()
            return {"message": "Order item deleted successfully"}, 204
        else:
            return {"message": "Order item not found"}, 404
