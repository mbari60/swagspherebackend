from flask import render_template , request , jsonify, current_app
from flask_restful import Resource
from models import UserModel, ProductModel , OrderModel , OrderItemModel , db , OfferModel
from app import mail


class Offers(Resource):

    def post(self):
        data = request.get_json()

        # Validate required fields
        if not all([data.get("user_id"), data.get("offer_id"), data.get("offer_price"), data.get("offer_name")]):
            return {"message": "Missing required fields"}, 400

        user_id = data.get("user_id")
        offer_id = data.get("product_id")
        offer_price = data.get("offer_price")

        # Check if user exists
        user = UserModel.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        # Check if product exists
        offer_product = OfferModel.query.get(offer_id)
        if not offer_product:
            return {"message": "Product not found"}, 404

        # Check if user has already bought this offer
        past_orders = OfferModel.query.filter_by(user_id=user_id).all()
        for order in past_orders:
            for item in order.order_items:
                if item.variant_id == product_id:
                    return jsonify({"message": "You have already purchased this offer"}), 400

        # Calculate total price
        total_price = product.price * quantity

        # Create order and order item
        new_order = OrderModel(user_id, total_price)
        new_order_item = OrderItemModel(new_order.id, product_id, quantity, product.price)

        db.session.add(new_order)
        db.session.add(new_order_item)
        db.session.commit()

        # Send confirmation emails
        self.send_email(user.email, "Order Confirmation - Your order is being processed!",
                        render_template("order_confirmation.html", username=user.username,
                                        order_id=new_order.id, product_name=product.name,
                                        quantity=quantity, total_price=total_price))

        self.send_email(current_app.config["ADMIN_EMAIL"], "New Order Notification",
                        render_template("new_order_notification.html", order_id=new_order.id,
                                        username=user.username, user_email=user.email,
                                        product_name=product.name, quantity=quantity,
                                        total_price=total_price))

        return jsonify(new_order.serialize()), 201  # Created

    def send_email(self, recipient, subject, html_content):
        try:
            mail.send_message(
                sender=current_app.config["MAIL_USERNAME"],
                recipients=[recipient],
                subject=subject,
                html=html_content,
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {recipient}: {e}")
