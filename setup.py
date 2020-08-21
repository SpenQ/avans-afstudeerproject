#!/usr/bin/env python3

# check db for state, if empty do first setup
# call rabe/setup
# {
#     "scheme": "BSW",
#     "attributes": [
#         "admin",
#         "employee",
#         "cust1",
#         "...",
#         "cust100",
#         "warehouse1",
#         "...",
#         "warehouse100",
#     ]
# }
# do setup again when internal state is full, cust or warehouse...
from rabe.model import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ldap3 import Server, Connection, ALL
import rabe_client
import configparser

config = configparser.ConfigParser()
config.read('alembic.ini')

DB_URL = config['alembic']['sqlalchemy.url']

server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL) #TODO should come from config

# engine = create_engine(DB_URL)
# DB_Session = sessionmaker(bind=engine)
# db_session = DB_Session()

# session_data = rabe_client.scheme_setup("bsw", ["TEST1", "TEST2"])
# print('session_data: ' + str(session_data))
# rabe_session = Session(session = session_data)
# print('rabe_session: ' + str(rabe_session))
# db_session.add(rabe_session)
# db_session.commit()

with Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123') as conn: #TODO should come from config
    conn.search('dc=demo1,dc=freeipa,dc=org', '(objectclass=person)', attributes=['uid', 'cn', 'ou', 'sn', 'dc'])

    for entry in conn.entries:
        # print(entry)
        # print(entry.entry_dn)
        # print(str(entry.entry_to_json()))
        print(entry.entry_to_ldif())