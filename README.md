# My Little Puny
A little and ugly Python script that checks for domain names that may be used to perform an [IDN homograph attack](https://en.wikipedia.org/wiki/IDN_homograph_attack).

### Punycode From Wikipedia:
> Punycode is a representation of Unicode with the limited ASCII character subset used for Internet host names.
> Using Punycode, host names containing Unicode characters are transcoded to a subset of ASCII consisting of letters,
> digits, and hyphen, which is called the Letter-Digit-Hyphen (LDH) subset. For example, München (German name for Munich) 
> is encoded as Mnchen-3ya.

> While the Domain Name System (DNS) technically supports arbitrary sequences of octets in domain name labels, 
> the DNS standards recommend the use of the LDH subset of ASCII conventionally used for host names, and require 
> that string comparisons between DNS domain names should be case-insensitive. The Punycode syntax is a method 
> of encoding strings containing Unicode characters, such as internationalized domain names (IDNA), into the LDH subset of 
> ASCII favored by DNS. It is specified in IETF Request for Comments 3492.

## Usage
This script has 2 main arguments. The first argument is a capital letter from A to Z which is used to loops through a list of similar/compatible Unicode characters and convert it to IDN format using Punycode.
The second argument is a "QNAME template" that has an underscore `_` instead of the character you want to check. For Example:

```bash
$ python myLittlePuny.py I tw_tter.com
qname=xn--twtter-xva.com, decoded=twìtter.com, rtype=2, rdata=ns12.domaincontrol.com.
qname=xn--twtter-xva.com, decoded=twìtter.com, rtype=2, rdata=ns11.domaincontrol.com.
qname=xn--twtter-4va.com, decoded=twítter.com, rtype=2, rdata=ns12.domaincontrol.com.
qname=xn--twtter-4va.com, decoded=twítter.com, rtype=2, rdata=ns11.domaincontrol.com.
qname=xn--twtter-cwa.com, decoded=twîtter.com, rtype=2, rdata=dns111.ovh.net.
qname=xn--twtter-cwa.com, decoded=twîtter.com, rtype=2, rdata=ns111.ovh.net.
qname=xn--twtter-jwa.com, decoded=twïtter.com, rtype=2, rdata=ns12.domaincontrol.com.
qname=xn--twtter-jwa.com, decoded=twïtter.com, rtype=2, rdata=ns11.domaincontrol.com.
qname=xn--twtter-j8a.com, decoded=twītter.com, rtype=2, rdata=ns06.domaincontrol.com.
qname=xn--twtter-j8a.com, decoded=twītter.com, rtype=2, rdata=ns05.domaincontrol.com.
qname=xn--twtter-cl8b.com, decoded=twịtter.com, rtype=2, rdata=ns1.transip.nl.
qname=xn--twtter-cl8b.com, decoded=twịtter.com, rtype=2, rdata=ns2.transip.eu.
qname=xn--twtter-cl8b.com, decoded=twịtter.com, rtype=2, rdata=ns0.transip.net.
...
```

The default QTYPE is NS but you can change it using `--qtype`:

```bash
$ python myLittlePuny.py I tw_tter.com --qtype=A
qname=xn--twtter-xva.com, decoded=twìtter.com, rtype=1, rdata=78.153.209.228
qname=xn--twtter-4va.com, decoded=twítter.com, rtype=1, rdata=78.153.209.228
qname=xn--twtter-cwa.com, decoded=twîtter.com, rtype=1, rdata=213.186.33.87
qname=xn--twtter-jwa.com, decoded=twïtter.com, rtype=1, rdata=78.153.209.228
qname=xn--twtter-j8a.com, decoded=twītter.com, rtype=1, rdata=184.168.221.43
qname=xn--twtter-cl8b.com, decoded=twịtter.com, rtype=1, rdata=37.97.254.27
```

## Requirements
- python3
- dnslib

## Install and Run
```bash
$ # install required python modules:
$ pip3 install -r requirements.txt

$ # run myLittlePuny:
$ python3 myLittlePuny.py --help
```


