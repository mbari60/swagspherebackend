# from flask_restful import Resource, reqparse, fields, marshal
# from models import ProductVariantModel, db

# product_variant_fields = {
#     "id": fields.Integer,
#     "product_id": fields.Integer,
#     "color": fields.String,
#     "photo_url": fields.String,
#     "size": fields.String,
#     "other_variant_details": fields.String,
# }

# class ProductVariantResource(Resource):
#     def __init__(self):
#         self.parser = reqparse.RequestParser()
#         self.parser.add_argument('product_id', type=int, required=True, help="Product ID is required")
#         self.parser.add_argument('color', type=str, required=False)
#         self.parser.add_argument('photo_url', type=str, required=True, help="Photo URL is required")
#         self.parser.add_argument('size', type=str, required=False)
#         self.parser.add_argument('other_variant_details', type=str, required=False)

#     def get(self, variant_id=None):
#         if variant_id:
#             variant = ProductVariantModel.query.get(variant_id)
#             if variant:
#                 return marshal(variant, product_variant_fields), 200
#             else:
#                 return {"message": "Product variant not found"}, 404
#         else:
#             variants = ProductVariantModel.query.all()
#             if variants:
#                 return marshal(variants, product_variant_fields)
#             else:
#                 return {"message": "No product variants available"}, 404

#     def post(self):
#         args = self.parser.parse_args()
#         variant = ProductVariantModel(**args)
#         db.session.add(variant)
#         db.session.commit()
#         return marshal(variant, product_variant_fields), 201

#     def put(self, variant_id):
#         args = self.parser.parse_args()
#         variant = ProductVariantModel.query.get(variant_id)
#         if not variant:
#             return {"message": "Product variant not found"}, 404
#         for key, value in args.items():
#             setattr(variant, key, value)
#         db.session.commit()
#         return marshal(variant, product_variant_fields), 200

#     def delete(self, variant_id):
#         variant = ProductVariantModel.query.get(variant_id)
#         if variant:
#             db.session.delete(variant)
#             db.session.commit()
#             return {"message": "Product variant deleted successfully"}, 204
#         else:
#             return {"message": "Product variant not found"}, 404
