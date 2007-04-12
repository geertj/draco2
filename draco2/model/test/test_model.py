# vi: ts=8 sts=4 sw=4 et
#
# test_model.py: test suite for draco2.model
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import py.test

import time
import decimal
import datetime
import threading

from draco2.model import *
from draco2.model.test.support import ModelTest
from draco2.model.test.shopmodel import *


class TestModel(ModelTest):

    model_class = ShopModel

    def new_product(self):
        product = Product()
        product['code'] = 'PR-1'
        product['short_desc'] = 'Product One'
        product['price'] = decimal.Decimal('10.00')
        return product

    def new_user(self):
        user = User()
        user['email'] = 'user@domain.org'
        user['given_name'] = 'first'
        user['surname'] = 'last'
        return user

    def new_order(self):
        order = Order()
        order['order_date'] = datetime.datetime.utcnow()
        order['total'] = decimal.Decimal('20.00')
        return order

    def test_insert_object(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        assert product.has_key('id')
        assert isinstance(product['id'], int)
        result = tnx.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 1
        prod2 = result[0]
        assert prod2 is product

    def test_insert_object_attribute_missing(self):
        tnx = self.model.transaction()
        product = Product()
        tnx.insert(product)
        py.test.raises(ModelIntegrityError, tnx.commit)

    def test_delete_object(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        productid = product['id']
        result = tnx.select(Product, 'id=%s', (productid,))
        assert len(result) == 1
        tnx.delete(product)
        result = tnx.select(Product, 'id=%s', (productid,))
        assert len(result) == 0

    def test_insert_relationship(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        urel = UserOrderRelationship()
        urel.set_role('user', user)
        urel.set_role('order', order)
        tnx.insert(urel)
        prel = ProductOrderRelationship()
        prel.set_role('product', product)
        prel.set_role('order', order)
        prel['count'] = 2
        tnx.insert(prel)
        user2 = urel.role('user')
        assert user2 is user
        order2 = urel.role('order')
        assert order2 is order
        product2 = prel.role('product')
        assert product2 is product
        order2 = prel.role('order')
        assert order2 is order
        result = user2.in_role('user', UserOrderRelationship)
        assert len(result) == 1
        urel2 = result[0]
        assert urel2 == urel
        result = order2.in_role('order', UserOrderRelationship)
        assert len(result) == 1
        urel3 = result[0]
        assert urel3 == urel2
        result = product2.in_role('product', ProductOrderRelationship)
        assert len(result) == 1
        prel2 = result[0]
        assert prel2 == prel
        result = order2.in_role('order', ProductOrderRelationship)
        assert len(result) == 1
        prel3 = result[0]
        assert prel3 == prel2

    def test_insert_relationship_attribute_missing(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        order = self.new_order()
        tnx.insert(order)
        rel = ProductOrderRelationship()
        rel.set_role('product', product)
        rel.set_role('order', order)
        tnx.insert(rel)
        py.test.raises(ModelIntegrityError, tnx.commit)

    def test_insert_relationship_role_missing(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        order = self.new_order()
        tnx.insert(order)
        rel = ProductOrderRelationship()
        rel.set_role('product', product)
        rel['count'] = 2
        py.test.raises(ModelInterfaceError, tnx.insert, rel)

    def test_change_primary_key(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        py.test.raises(ModelInterfaceError, product.__setitem__, 'id', 10)

    def test_change_foreign_key(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        rel = UserOrderRelationship()
        rel.set_role('user', user)
        rel.set_role('order', order)
        tnx.insert(rel)
        py.test.raises(ModelInterfaceError, rel.__setitem__, 'user_id', 10)
 
    def test_set_attribute_null(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        py.test.raises(ModelIntegrityError, product.__setitem__, 'code', None)

    def test_use_entity_after_commit(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        tnx.commit()
        productid = product['id']

    def test_use_entity_after_rollback(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        tnx.commit()
        productid = product['id']

    def test_change_entity_after_commit(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        tnx.commit()
        product['code'] = 'PR2'

    def test_change_entity_after_rollback(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        tnx.rollback()
        py.test.raises(ModelInterfaceError, product.__setitem__, 'code', 'PR2')

    def test_transaction_isolation(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx2 = self.model.transaction()
        tnx.insert(product)
        result = tnx2.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 0
        tnx.commit()
        result = tnx2.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 0
        tnx2.commit()
        result = tnx2.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 1

    def test_cardinality_insert(self):
        return  # XXX: disabled for now
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        # order existentially depends on user
        py.test.raises(ModelIntegrityError, tnx.commit)

    def test_cardinality_delete(self):
        return  # XXX: disabled for now
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        rel = UserOrderRelationship()
        rel.set_role('user', user)
        rel.set_role('order', order)
        tnx.insert(rel)
        tnx.commit()
        tnx = self.model.transaction()
        result = tnx.select(User, 'id=%s', (user['id'],))
        assert len(result) == 1
        user = result[0]
        tnx.delete(user)
        py.test.raises(ModelIntegrityError, tnx.commit)

    def test_view(self):
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        rel = UserOrderRelationship()
        rel.set_role('user', user)
        rel.set_role('order', order)
        tnx.insert(rel)
        result = tnx.select(OrderView)
        assert len(result) == 1
        view = result[0]
        assert view['id'] == order['id']

    def test_persistent_transaction(self):
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        urel = UserOrderRelationship()
        urel.set_role('user', user)
        urel.set_role('order', order)
        tnx.insert(urel)
        data = tnx.dump()
        tnx.rollback()
        tnx2 = self.model.transaction()
        tnx2.load(data)
        result = tnx2.select(User, 'id=%s', (user['id'],))
        assert len(result) == 1
        user2 = result[0]
        assert user2 is not user
        assert user2.items() == user.items()
        result = tnx2.select(Order, 'id=%s', (order['id'],))
        assert len(result) == 1
        order2 = result[0]
        assert order2 is not order
        assert order2.items() == order.items()
        result = tnx2.select(UserOrderRelationship, 'user_id=%s',
                             (user['id'],))
        assert len(result) == 1
        urel2 = result[0]
        assert urel2 is not urel
        assert urel2.items() == urel.items()

    def test_persistent_transaction_delete_entity(self):
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        urel = UserOrderRelationship()
        urel.set_role('user', user)
        urel.set_role('order', order)
        tnx.insert(urel)
        tnx.delete(user)
        data = tnx.dump()
        tnx.rollback()
        tnx2 = self.model.transaction()
        print data
        tnx2.load(data)
        result = tnx2.select(User, 'id=%s', (user['id'],))
        assert len(result) == 0
        result = tnx2.select(Order, 'id=%s', (order['id'],))
        assert len(result) == 1
        order2 = result[0]
        assert order2 is not order
        assert order2.items() == order.items()
        result = tnx2.select(UserOrderRelationship, 'user_id=%s',
                             (user['id'],))
        assert len(result) == 0

    def test_persistent_transaction_revive_entity(self):
        tnx = self.model.transaction()
        user = self.new_user()
        tnx.insert(user)
        order = self.new_order()
        tnx.insert(order)
        urel = UserOrderRelationship()
        urel.set_role('user', user)
        urel.set_role('order', order)
        tnx.insert(urel)
        tnx.commit()
        tnx2 = self.model.transaction()
        result = tnx2.select(Order, 'id=%s', (order['id'],))
        assert len(result) == 1
        order2 = result[0]
        data = tnx2.dump()
        tnx2.delete(order2)
        tnx2.commit()
        tnx3 = self.model.transaction()
        tnx3.load(data)
        result = tnx3.select(Order, 'id=%s', (order['id'],))
        assert len(result) == 1
        order3 = result[0]
        assert order3.items() == order.items()

    class Updater(threading.Thread):

        def run(self):
            self.product['price'] = self.price

    def test_concurrent_update(self):
        tnx = self.model.transaction()
        product = self.new_product()
        tnx.insert(product)
        tnx.commit()
        tnx1 = self.model.transaction()
        result = tnx1.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 1
        prod1 = result[0]
        tnx2 = self.model.transaction()
        result = tnx2.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 1
        prod2 = result[0]
        upd1 = self.Updater()
        upd1.product = prod1
        upd1.price = 100
        upd2 = self.Updater()
        upd2.product = prod2
        upd2.price = 200
        upd1.start()
        upd1.join()
        assert prod1['price'] == 100
        upd2.start()  # Will block
        tnx1.commit() # will raise error in thread 2, which is retried
        upd2.join()
        assert prod2['price'] == 200
        tnx2.commit()
        tnx3 = self.model.transaction()
        result = tnx3.select(Product, 'id=%s', (product['id'],))
        assert len(result) == 1
        prod3 = result[0]
        assert prod3['price'] == 200  # last committed transaction wins

    def _merge(self, ob1, ob2):
        ob1['count'] += ob2['count']

    def test_merge(self):
        tnx = self.model.transaction()
        for i in range(10):
            stat = Stat()
            stat['id'] = 1
            stat['count'] = 2
            tnx.merge(stat, self._merge)
        result = tnx.select(Stat, 'id = %s', (1,))
        assert len(result) == 1
        stat = result[0]
        assert stat['count'] == 20
    
    class Merger(threading.Thread):

        def _merge(self, ob1, ob2):
            print '[%d] merge object %d from %d to %d' % \
                    (self.id, ob1['id'], ob1['count'], ob1['count'] + ob2['count'])
            try:
                ob1['count'] += ob2['count']
            except Exception, err:
                print '[%d] exception' % self.id
                raise

        def run(self):
            tnx = self.transaction
            s1 = Stat()
            s1['id'] = 1
            s1['count'] = 2
            s2 = Stat()
            s2['id'] = 2
            s2['count'] = 3
            if not (self.id % 2):
                tnx.merge(s1, self._merge)
                time.sleep(1)
                tnx.merge(s2, self._merge)
            else:
                tnx.merge(s2, self._merge)
                time.sleep(1)
                tnx.merge(s1, self._merge)
            tnx.commit()

    def test_merge_concurrent(self):
        tnx = self.model.transaction()
        for i in range(2):
            s = Stat()
            s['id'] = i+1
            s['count'] = 0
            tnx.insert(s)
        tnx.commit()
        threads = []
        for i in range(2):
            t = self.Merger()
            t.transaction = self.model.transaction()
            t.id = i
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        tnx = self.model.transaction()
        result = tnx.select(Stat, 'id = %s', (1,))
        assert len(result) == 1
        assert result[0]['count'] == 2 * len(threads)
        result = tnx.select(Stat, 'id = %s', (2,))
        assert len(result) == 1
        assert result[0]['count'] == 3 * len(threads)
