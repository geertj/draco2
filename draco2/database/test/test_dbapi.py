# vi: ts=8 sts=4 sw=4 et
#
# dbapi.py: test support for DB-API tests
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import sys
import random
import datetime
import decimal

from draco2.database import *
from draco2.database.test.support import (DatabaseTest, random_data,
                                          random_string)


class TestTypes(DatabaseTest):
    """Test various aspects of the database."""

    def test_integer(self):
        """Test data insertion and retrieval to integer columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_integer')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_integer ' \
                                  '( value INTEGER NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_integer VALUES (%s)'
        for i in range(100):
            item = random.randrange(-sys.maxint, sys.maxint)
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_integer'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, int) or isinstance(item, long)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_integer')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_integer')
        cursor.execute(query)
        conn.commit()

    def test_numeric(self):
        """Test data insertion and retrieval to numeric columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_numeric')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_numeric ' \
                                  '( value NUMERIC(100,50) NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_numeric VALUES (%s)'
        for i in range(100):
            int = random.getrandbits(150)
            frac = random.getrandbits(150)
            item = decimal.Decimal('%d.%s' % (int, frac))
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_numeric'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, decimal.Decimal)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_numeric')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_numeric')
        cursor.execute(query)
        conn.commit()

    def test_real(self):
        """Test data insertion and retrieval to real columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_real')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_real ' \
                                  '( value REAL NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_real VALUES (%s)'
        for i in range(100):
            item = random.random()
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_real'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, float)
            for i,f in enumerate(data):
                if abs(f - item) < 1e-6:
                    break
            else:
                assert False, 'Item not found'
        query = dialect.translate('DELETE FROM test_real')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_real')
        cursor.execute(query)
        conn.commit()

    def test_double_precision(self):
        """Test data insertion and retrieval to double precision columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_double_precision')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_double_precision ' \
                                  '( value DOUBLE PRECISION NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_double_precision VALUES (%s)'
        for i in range(100):
            item = random.random()
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_double_precision'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, float)
            for i,f in enumerate(data):
                if abs(f - item) < 1e-12:
                    break
            else:
                assert False, 'Item not found'
        query = dialect.translate('DELETE FROM test_double_precision')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_double_precision')
        cursor.execute(query)
        conn.commit()

    def test_char(self):
        """Test data insertion and retrieval to char columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_char')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_char ' \
                                  '( value CHAR(255) NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_char VALUES (%s)'
        for i in range(100):
            item = random_string(255)
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_char'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            padded = item + ((255-len(item)) * ' ')
            assert isinstance(item, unicode)
            assert item in data or padded in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_char')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_char')
        cursor.execute(query)
        conn.commit()

    def test_varchar(self):
        """Test data insertion and retrieval to varchar columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_varchar')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_varchar ' \
                                  '( value VARCHAR(255) NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_varchar VALUES (%s)'
        for i in range(100):
            item = random_string(255)
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_varchar'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, unicode)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_varchar')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_varchar')
        cursor.execute(query)
        conn.commit()

    def test_text(self):
        """Test data insertion and retrieval to text columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_text')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_text ' \
                                  '( value TEXT NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_text VALUES (%s)'
        for i in range(10):
            item = random_string(100000)
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_text'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, unicode)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_text')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_text')
        cursor.execute(query)
        conn.commit()

    def test_blob(self):
        """Test data insertion and retrieval to text columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_blob')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_blob ' \
                                  '( value BLOB NOT NULL )')
        cursor.execute(query)
        data = []
        query = 'INSERT INTO test_blob VALUES (%s)'
        for i in range(10):
            item = buffer(random_data(100000))
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_blob'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, buffer)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_blob')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_blob')
        cursor.execute(query)
        conn.commit()

    def test_date(self):
        """Test data insertion and retrieval to date columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_date')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_date' \
                                  '( value DATE NOT NULL )')
        cursor.execute(query)
        data = []
        rr = random.randrange
        query = 'INSERT INTO test_date VALUES (%s)'
        for i in range(100):
            item = datetime.date(rr(1,10000), rr(1,13), rr(1,29))
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_date'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, datetime.date)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_date')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_date')
        cursor.execute(query)
        conn.commit()
 
    def test_time(self):
        """Test data insertion and retrieval to time columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_time')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_time ' \
                                  '( value TIME NOT NULL )')
        cursor.execute(query)
        data = []
        rr = random.randrange
        query = 'INSERT INTO test_time VALUES (%s)'
        for i in range(100):
            item = datetime.time(rr(0,24), rr(0,60), rr(0,60))
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_time'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, datetime.time)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_time')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_time')
        cursor.execute(query)
        conn.commit()

    def test_datetime(self):
        """Test data insertion and retrieval to datetime columns."""
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_datetime')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_datetime ' \
                                  '( value TIMESTAMP NOT NULL )')
        cursor.execute(query)
        data = []
        rr = random.randrange
        query = 'INSERT INTO test_datetime VALUES (%s)'
        for i in range(100):
            item = datetime.datetime(rr(1,10000), rr(1,13), rr(1,29),
                                     rr(0,24), rr(0,60), rr(0,60))
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_datetime'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, datetime.datetime)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_datetime')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_datetime')
        cursor.execute(query)
        conn.commit()

    def test_interval(self):
        """Test data insertion and retrieval to datetime columns."""
        # Interval is not supported on MySQL
        if self.database.name == 'mysqldb':
            return
        conn = self.database.connection()
        cursor = conn.cursor()
        dialect = self.database.dialect()
        dbapi = self.database.dbapi()
        query = dialect.translate('DROP TABLE test_interval')
        try:
            cursor.execute(query)
        except dbapi.Error:
            conn.rollback()
        query = dialect.translate('CREATE TABLE test_interval ' \
                                  '( value INTERVAL NOT NULL )')
        cursor.execute(query)
        data = []
        rr = random.randrange
        query = 'INSERT INTO test_interval VALUES (%s)'
        for i in range(100):
            ts1 = datetime.datetime(rr(1,10000), rr(1,13), rr(1,29),
                                    rr(0,24), rr(0,60), rr(0,60))
            ts2 = datetime.datetime(rr(1,10000), rr(1,13), rr(1,29),
                                    rr(0,24), rr(0,60), rr(0,60))
            item = ts2 - ts1
            data.append(item)
            cursor.execute(query, (item,))
        query = 'SELECT * FROM test_interval'
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            item = row[0]
            assert isinstance(item, datetime.timedelta)
            assert item in data
            data.remove(item)
        query = dialect.translate('DELETE FROM test_interval')
        cursor.execute(query)
        query = dialect.translate('DROP TABLE test_interval')
        cursor.execute(query)
        conn.commit()
