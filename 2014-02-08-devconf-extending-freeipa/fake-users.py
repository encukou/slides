"""Generate commands to add random users to IPA"""

from faker import Faker
fake = Faker()

for i in range(100):
    first=fake.first_name()
    last=fake.last_name()
    print "ipa user-add {login} --first='{first}' --last='{last}' --stree='{street}' --city='{city}' --state='{state}' --postalcode='{postcode}'".format(
            login=(first[0] + last[:7]).lower(),
            first=first,
            last=last,
            city=fake.city(),
            street=fake.street_address(),
            state=fake.country(),
            postcode=fake.postcode(),
        )
