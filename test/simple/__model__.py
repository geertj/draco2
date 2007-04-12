# vi: ts=4 sw=4 et
#
# draco/model/test/shopmodel.py: test model
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.

from draco.model import *


# User Entity

class UserID(IntegerAttribute):
    name = 'id'

class Email(StringAttribute):
    name = 'email'

class GivenName(StringAttribute):
    name = 'given_name'
    width = 64

class SurName(StringAttribute):
    name = 'surname'
    width = 64

class EmailIndex(Index):
    name = 'email_index'
    attributes = [Email]

class User(Entity):
    name = 'users'
    attributes = [UserID, Email, GivenName, SurName ]
    primary_key = [UserID]
    indexes = [EmailIndex]


# Product Entity

class ProductID(IntegerAttribute):
    name = 'id'

class ProductCode(StringAttribute):
    name = 'code'

class ShortDesc(StringAttribute):
    name = 'short_desc'

class LongDesc(StringAttribute):
    name = 'long_desc'
    default = ''

class Price(DecimalAttribute):
    name = 'price'
    precision = 10
    scale = 2

class ProductCodeIndex(Index):
    name = 'code_index'
    attributes = [ProductCode]

class Product(Entity):
    name = 'products'
    attributes = [ProductID, ProductCode, ShortDesc, LongDesc, Price]
    primary_key = [ProductID]
    indexes = [ProductCodeIndex]


# Order Entity

class OrderID(IntegerAttribute):
    name = 'id'

class OrderDate(DateTimeAttribute):
    name = 'order_date'

class OrderTotal(DecimalAttribute):
    name = 'total'

class Order(Entity):
    name = 'orders'
    attributes = [OrderID, OrderDate, OrderTotal]
    primary_key = [OrderID]


# Relationships

class Count(IntegerAttribute):
    name = 'count'

class ProductOrderRelationship(Relationship):
    name = 'product_order'
    roles = [('order', Order, (0, None)),
             ('product', Product, (0, None))]
    attributes = [Count]


class UserOrderRelationship(Relationship):
    name = 'user_order'
    roles = [('order', Order, (0, None)),
             ('user', User, (1, 1)) ]


# Views

class OrderView(View):
    name = 'order_view'
    query = """
            SELECT orders.id AS id,
                   orders.order_date AS date,
                   users.given_name || ' ' || users.surname AS username,
                   orders.total as total
            FROM orders
                 INNER JOIN user_order ON user_order.order_id = orders.id
                 INNER JOIN users ON users.id = user_order.user_id
            """


# The ShopModel

class ShopModel(Model):
    name = 'shopmodel'
    version = 1
    entities = [User, Product, Order]
    relationships = [UserOrderRelationship, ProductOrderRelationship]
    views = [OrderView]
