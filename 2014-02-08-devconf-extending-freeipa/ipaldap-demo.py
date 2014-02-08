import ipapython
from pprint import pprint
from ipapython.ipaldap import IPAdmin
from ipapython.dn import DN

dn = DN(('uid', 'jwhite'),
        ('cn', 'users'),
        ('cn', 'accounts'),
        ('dc', 'ipa'),
        ('dc', 'test'))
print 'DN:', dn

ldap = IPAdmin(host='ipa33.ipa.test')
entry = ldap.get_entry(dn)

#####

print 'DN:', entry.dn
print 'Name:', entry['cn']
print 'All attributes:'
pprint.pprint(dict(entry))
