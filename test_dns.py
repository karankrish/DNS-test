import dns 

def test_DomainExpiry_best():
    assert dns.DomainExpiry((5,"www.yahoo.com")) == {'domainexpiryDate': '01/19/2023',
 'domainDaysLeft': '1372',
 'registrar': 'MarkMonitor Inc.',
 'nameServer': ['NS1.YAHOO.COM',
  'NS2.YAHOO.COM',
  'NS3.YAHOO.COM',
  'NS4.YAHOO.COM',
  'NS5.YAHOO.COM']}
    assert dns.DomainExpiry((5,"yahoo.com")) == {'domainexpiryDate': '01/19/2023',
 'domainDaysLeft': '1372',
 'registrar': 'MarkMonitor Inc.',
 'nameServer': ['NS1.YAHOO.COM',
  'NS2.YAHOO.COM',
  'NS3.YAHOO.COM',
  'NS4.YAHOO.COM',
  'NS5.YAHOO.COM']}
    assert dns.DomainExpiry((5,"startupmission.kerala.gov.in")) =={'domainexpiryDate': '12/31/2019',
 'domainDaysLeft': '257',
 'registrar': 'National Informatics Centre',
 'nameServer': ['ns3.cdit.org', 'ns1.cdit.org', 'ns2.cdit.org']}
def test_DomainExpiry_worst():
    assert dns.DomainExpiry((5,".")) =={'domainexpiryDate': '',
 'domainDaysLeft': '',
 'registrar': '',
 'nameServer': ''}
    assert dns.DomainExpiry((5,"ibm")) == {'domainexpiryDate': '',
 'domainDaysLeft': '',
 'registrar': '',
 'nameServer': ''}
    assert dns.DomainExpiry((5,"www.")) == {'domainexpiryDate': '',
 'domainDaysLeft': '',
 'registrar': '',
 'nameServer': ''}