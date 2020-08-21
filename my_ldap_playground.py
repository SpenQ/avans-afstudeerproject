#!/usr/bin/env python3

from ldap3 import Server, Connection, ALL

server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL)
with Connection(server, auto_bind=True) as conn:
#for NTLM/AD: conn = Connection(server, user="Domain\\User", password="password", authentication=NTLM)
    print(conn)
    print(conn.extend.standard.who_am_i())

with Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123') as conn:
    # print(conn)
    # print(conn.extend.standard.who_am_i())

    # conn.search('dc=demo1,dc=freeipa,dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn','krbLastPwdChange', 'objectclass'])
    # entry = conn.entries[0]
    # print(entry)
    conn.search('dc=demo1,dc=freeipa,dc=org', '(objectclass=person)')
    print('entries: ' + str(conn.entries))

    conn.search('dc=demo1,dc=freeipa,dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn', 'krbLastPwdChange', 'objectclass'])

    print(conn.entries[0])

    # conn.add('ou=rabe-users=demo1,dc=freeipa,dc=org', 'organizationalUnit')
    # conn.add('cn=b.young,ou=rabe-users,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Beatrix', 'sn': 'Young', 'departmentNumber': 'DEV', 'telephoneNumber': 1111})

print(conn)

# continue here: https://ldap3.readthedocs.io/en/latest/tutorial_searches.html
# and for ou search / AD: https://avleonov.com/2019/08/12/how-to-get-the-organization-units-ou-and-hosts-from-microsoft-active-directory-using-python-ldap3/