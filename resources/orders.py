# from flask_restful import Resource, reqparse, fields, marshal
# from models import ProductModel, OrderModel, db
# from flask import json

# order_item_fields = {
#     "id": fields.Integer,
#     "product_id": fields.Integer,
#     "quantity": fields.Integer,
# }

# class OrderResource(Resource):
#     order_parser = reqparse.RequestParser()
#     order_parser.add_argument('user_id', type=int, required=True, help="User ID is required")
#     order_parser.add_argument('total_amount', type=int, required=True, help="Total amount is required")
#     order_parser.add_argument('order_items', type=list, required=True, help="Order items are required")

#     def get(self):
#         orders = OrderModel.query.all()
#         if orders:
#             return marshal(orders, order_item_fields), 200
#         else:
#             return {"message": "No orders available"}, 404

#     def post(self):
#         args = self.order_parser.parse_args()
#         user_id = args['user_id']
#         order_items = args['order_items']

#         total_amount = 0

#         order_items = json.loads(order_items)
        
#         for item in order_items:
#             product_id = item.get('product_id')
#             quantity = item.get('quantity')

#             # Query product details by ID
#             product = ProductModel.query.filter_by(id = product_id).first()
#             if product:
#                 total_amount += product.price * quantity
#             else:
#                 return {"message": f"Product with ID {product_id} not found"}, 404

#         order = OrderModel(user_id=user_id, total_amount=total_amount, order_items=order_items)
#         db.session.add(order)
#         db.session.commit()
#         return marshal(order, order_item_fields), 201

#     def delete(self, order_id):
#         order = OrderModel.query.get(order_id)
#         if order:
#             db.session.delete(order)
#             db.session.commit()
#             return {"message": "Order deleted successfully"}, 204
#         else:
#             return {"message": "Order not found"}, 404
