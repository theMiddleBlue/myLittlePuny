# most functions need to be completed
# 

import sys, time, socket, re, argparse, requests, hashlib, json
from dnslib import *

debug = False
version = "0.1"
mypath = os.path.abspath(os.path.dirname(__file__))+'/'

def inlineopts():
	parser = argparse.ArgumentParser()

	parser.add_argument(	"capital",
								metavar="LETTER",
								type=str,
								nargs='+',
								help="Capital letter [A-Z] or ALL")
	parser.add_argument(	"template",
								metavar="TEMPLATE", 
								type=str, 
								nargs='+', 
								help="Domain name template (example: g_oogle.com). Don't use underscore using ALL as letter")
	parser.add_argument(	"--qtype",
								help='QTYPE of DNS query (default: NS)',
								type=str,
								required=False)
	parser.add_argument(	"--http-headers",
								help='Run an HTTP request for each record A (default: off)',
								action="store_true",
								dest="httpheaders",
								default=False)
	parser.add_argument(	"--resolver-ip",
								help='DNS Server to use for query (default: 8.8.8.8)',
								type=str)
	parser.add_argument(	"--resolver-port",
								help='Port of the DNS resolver (default: 53)',
								type=int)
	parser.add_argument(	"--verbose",
								action="store_true",
								dest="verbose",
								default=False,
								help='Verbose (default: off)')
	parser.add_argument(	"--recursive",
								action="store_true",
								dest="recursive",
								default=False,
								help='Check each result for ALL punycode (default: off)')
	parser.add_argument(	"--save-json",
								action="store_true",
								dest="savejson",
								default=False,
								help='Save result in a JSON file <domain>.json (default: off)')

	return parser.parse_args()


opt = inlineopts()

dns_resolver_ip = opt.resolver_ip or '8.8.8.8'
dns_resolver_port = opt.resolver_port or 53
dns_qtype = opt.qtype or "NS"
jobhash = hashlib.md5(str(opt.capital[0]+opt.template[0]+dns_qtype).encode("utf-8")).hexdigest()

class cc:
	HEA = '\033[95m'
	BLU = '\033[1;34m'
	GRN = '\033[92m'
	WRN = '\033[93m'
	FAL = '\033[91m'
	ECL = '\033[0m'
	BLD = '\033[1m'
	UND = '\033[4m'

try:
	unichr
except NameError:
	unichr = chr

def unichar(i):
	try:
		return unichr(i)
	except ValueError:
		return struct.pack('i', i).decode('utf-32')

def qname_decode(char, template=opt.template[0]):
	c = unichar(int(char.strip(), 16))
	return str(template).replace('_', str(c))

def qname_encode(char, template=opt.template[0]):
	c = unichar(int(char.strip(), 16))
	return str(template).replace('_', str(c)).encode("idna")

def make_query(qname, qtype="NS"):
	return DNSRecord.question(qname, qtype)

def send_query(q, daddr="8.8.8.8", dport=53):
	UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	UDPClientSocket.settimeout(10)
	UDPClientSocket.sendto(q.pack(), (daddr, dport) )
	recvdata = UDPClientSocket.recvfrom(1024)[0]

	return DNSRecord.parse(recvdata)

hrequests = {}
hrecursive = {}
results = {}
def parse_answer(qname, decoded_qname, rr):
	answ = ''
	qnamehash = hashlib.md5(str(qname.decode('ascii')).encode("utf-8")).hexdigest()

	if qnamehash not in results:
		results[qnamehash] = {"encoded":str(qname.decode('ascii')), "decoded":decoded_qname, "qtype":dns_qtype, "answer":[]}

		for i in rr:
			if i.rdata is not None and i.rtype > 0:
				sys.stdout.write("\r\033[K")
				answ = str(i.rdata)

				print('| qname='+cc.GRN+str(qname.decode('ascii'))+cc.ECL+', decoded='+cc.BLU+decoded_qname+cc.ECL+', rtype='+str(i.rtype)+', rdata='+cc.HEA+answ+cc.ECL)
				# results[decoded_qname].append({"qname":str(qname.decode('ascii')), "rtype":str(i.rtype), "rdata":answ})
				results[qnamehash]["answer"].append({"rtype": i.rtype, "rdata":answ})
				

				if i.rtype == 1 and opt.httpheaders is True:
					hrequests[answ] = str(qname.decode('ascii'))

				if opt.recursive is True:
					hrecursive[decoded_qname] = str(qname.decode('ascii'))

def enumerate(letter):
	qlist = {}
	with open(mypath+"UnicodeData.txt") as f:
		l = f.readlines()
		for i in l:
			if re.search('^[0-9a-fA-F]{4,5};.*SMALL LETTER '+letter+'(;|\s).*', i.strip()) is not None:

				linearr = i.strip().split(";")
				char = linearr[0]

				decoded_qname = qname_decode(char, opt.template[0])

				try:
					qname = qname_encode(char, opt.template[0])
				except:
					if debug is True:
						print('Warning: Unable to encode '+decoded_qname)
					continue

				try:
					qlist[qname] = decoded_qname
				except:
					if debug is True:
						print("fail to add qlist entry")
					continue

	return qlist

def resolve(qlist):
	print("\n -- letter="+cc.WRN+str(opt.capital[0])+cc.ECL+" template="+cc.FAL+str(opt.template[0])+cc.ECL+" --")
	if opt.verbose is True:
		print("| Version: "+version)
		print("| QNAME List length: "+ str(len(qlist)))
		print("| Compatible unicode: "+str(opt.capital[0]))
		print("| QNAME template: "+str(opt.template[0]))
		print(" -- results --")

	for qname,decoded_qname in qlist.items():
		qnamehash = hashlib.md5(str(qname.decode('ascii')).encode("utf-8")).hexdigest()
		if qnamehash not in results:
			if re.search('xn\-\-', str(qname)) is not None:
				sys.stdout.write(u'Trying to resolve '+ str(qname.decode('ascii')) + ' (' + decoded_qname + ')...')
				sys.stdout.flush()

				q = make_query(qname, qtype=dns_qtype)

				try:
					d = send_query(q, daddr=dns_resolver_ip, dport=53)

				except Exception as e:
					print(" <- Warning: "+str(e))

				parse_answer(qname, decoded_qname, d.rr)
				sys.stdout.write("\r\033[K")
			else:
				if debug is True:
					print("Info: ignoring "+str(qname))
	
	print(" -- end --")

def checkall(domain):
	if re.search('^([^\.]+)\.[a-z0-9\-\.]+$', domain) is not None:
		sld = re.match('^([^\.]+)\.([a-z0-9\-\.]+)$', domain).group(1)
		tld = re.match('^([^\.]+)\.([a-z0-9\-\.]+)$', domain).group(2)

	c=0
	for n in list(sld):
		if re.search('^[A-Z]$', n.upper()) is not None:
			opt.capital = [n.upper()]
			opt.template = [gentemplate(sld, tld, c)]
			qlist = enumerate(opt.capital[0])
			resolve(qlist)
			c=(c+1)

def gentemplate(sld, tld, nchar):
	c=0
	t = ''
	for i in list(sld):
		if nchar == c:
			t=t+'_'
		else:
			t = t+i
		c=(c+1)
	return t+'.'+tld

if opt.capital[0] != "ALL":
	qlist = enumerate(opt.capital[0])
	resolve(qlist)
else:
	checkall(opt.template[0])
	if opt.recursive is True:
		while len(hrecursive) > 0:
			print("\n -- recursive job started -- ")
			for k,v in hrecursive.copy().items():
				checkall(k)
				del hrecursive[k]

if len(results) > 0:
	print("\n")
	print(" -- results --")
	print("| N. domains: "+str(len(results)))
	print(" -- list:")
	for k,v in results.items():
		if len(v["answer"]) > 0:
			#print(k+" -> "+str(json.dumps(v)))
			for i in v["answer"]:
				print('| qname='+cc.GRN+str(v["encoded"])+cc.ECL+', decoded='+cc.BLU+v["decoded"]+cc.ECL+', rtype='+str(i["rtype"])+', rdata='+cc.HEA+i["rdata"]+cc.ECL)
				#print(i)
	print(" -- end --")

# do something with results
# needs to be completed...
# print(results)
if opt.savejson is True:
	fcontent = ''
	for k,v in results.items():
		if len(v["answer"]) > 0:
			# print(k+" -> "+str(json.dumps(v)))
			fcontent += str(json.dumps(v))+"\n"

	if fcontent != '':
		fjson = open(mypath+'json/'+jobhash+'.json', 'w')
		fjson.write(fcontent)

if opt.httpheaders is True and len(hrequests) > 0:
	print("\n"+cc.WRN+"HTTP Response Headers:"+cc.ECL)

	for i in hrequests:
		print(" -- request info --")
		print("| qname: "+cc.WRN+hrequests[i]+cc.ECL+" IP: "+cc.BLU+i+cc.ECL)
		print(" -- response headers --")
		try:
			r = requests.get('http://'+hrequests[i]+'/', timeout=5)
			for h in r.headers:
				print("| "+cc.BLU+h+cc.ECL+': '+cc.WRN+r.headers[h]+cc.ECL)
		except:
			print("| Error: connection reset or request timeout")
		print(" --\n")
