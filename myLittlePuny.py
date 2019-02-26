import sys, time, socket, re, argparse
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
								help="Capital letter [A-Z]")
	parser.add_argument(	"template",
								metavar="TEMPLATE", 
								type=str, 
								nargs='+', 
								help="Domain name template (example: g_oogle.com)")
	parser.add_argument(	"--qtype",
								help='QTYPE of DNS query (default: NS)',
								type=str,
								required=False)
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

	return parser.parse_args()


opt = inlineopts()

dns_resolver_ip = opt.resolver_ip or '8.8.8.8'
dns_resolver_port = opt.resolver_port or 53
dns_qtype = opt.qtype or "NS"

class cc:
	HEA = '\033[95m'
	BLU = '\033[94m'
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
	# return str(template).replace('_', str(c))

def qname_encode(char, template=opt.template[0]):
	c = unichar(int(char.strip(), 16))
	return str(template).replace('_', str(c)).encode("idna")
	# return str(template).replace('_', str(c)).encode("idna")

def make_query(qname, qtype="NS"):
	return DNSRecord.question(qname, qtype)

def send_query(q, daddr="8.8.8.8", dport=53):
	UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	UDPClientSocket.settimeout(10)
	UDPClientSocket.sendto(q.pack(), (daddr, dport) )
	recvdata = UDPClientSocket.recvfrom(1024)[0]

	return DNSRecord.parse(recvdata)

def parse_answer(qname, decoded_qname, rr):
	answ = ''
	for i in rr:
		sys.stdout.write("\r\033[K")
		answ = str(i.rdata)
		print('qname='+cc.GRN+str(qname)+cc.ECL+', decoded='+cc.BLU+decoded_qname+cc.ECL+', rtype='+str(i.rtype)+', rdata='+cc.HEA+answ+cc.ECL)


qlist = {}
with open(mypath+"UnicodeData.txt") as f:
	l = f.readlines()
	for i in l:
		if re.search('^[0-9a-fA-F]{4,5};.*SMALL LETTER '+opt.capital[0]+' .*', i.strip()) is not None:

			linearr = i.strip().split(";")
			char = linearr[0]

			decoded_qname = qname_decode(char)

			try:
				qname = qname_encode(char)
			except:
				if debug is True:
					print('Warning: Unable to encode '+decoded_qname)
					continue

			qlist[qname] = decoded_qname

if opt.verbose is True:
	print(" -")
	print("| Version: "+version)
	print("| QNAME List length: "+ str(len(qlist)))
	print("| Compatible unicode: "+str(opt.capital[0]))
	print("| QNAME template: "+str(opt.template[0]))
	print(" -\n")

for qname,decoded_qname in qlist.items():
	if True:
		if True:
			if re.search('xn\-\-', str(qname)) is not None:
				sys.stdout.write(u'Trying to resolve '+ str(qname) + ' (' + decoded_qname + ')...')
				sys.stdout.flush()

				q = make_query(qname, qtype=dns_qtype)

				try:
					d = send_query(q, daddr=dns_resolver_ip, dport=53)

				except Exception as e:
					print(" <- Warning: "+str(e))

				parse_answer(qname, decoded_qname, d.rr)

				# time.sleep(0.5)
				sys.stdout.write("\r\033[K")
			else:
				if debug is True:
					print("Info: ignoring "+str(qname))
