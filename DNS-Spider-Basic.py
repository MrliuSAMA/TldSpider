import re
import subprocess
import pprint
import time
import sched
import os

PREFIX = "/opt/TldSpider"


def spider():
	QueryList = []
#	f = open("/var/ZoneCollect/Data/ZoneGet/root.zone.ori")
	f = open("./root.zone.ori")
	lines = f.readlines()
	for line in lines:
		if line.strip().split()[0] in QueryList:
			pass
		if line.strip().split()[0].lower() in QueryList:
			pass
		else:
			QueryList.append(line.strip().split()[0])
#	print QueryList
	f.close()
	print "total item is %s" % len(QueryList)	
	

	outFileName = time.strftime("%F-%H:%M-")+"res.out"
	f = open("./DataBak/%s" % outFileName,'a')
	for i in QueryList[:]:
		print "current item is %s" % QueryList.index(i)
		ResultNS = fetch(i,"NS")	
		if ResultNS != "NoAnswer":
			f.writelines(ResultNS[1:])

			temp = []			
			if ResultNS[-1] == ";0\n":
				temp = ResultNS[1:-1]
			if ResultNS[-1] == ";1\n":
				temp = ResultNS[1:-2]				

			for j in temp:
				dnsserver = j.strip().split()[-1]
				ResultA = fetch(dnsserver,"A")
				if ResultA != "NoAnswer":
					f.writelines(ResultA[1:])			
			for k in temp:
				dnsserver = j.strip().split()[-1]
				ResultA = fetch(dnsserver,"AAAA")
				if ResultA != "NoAnswer":
					f.writelines(ResultA[1:])			
	f.close()

	
	sort(outFileName)



def sort(sourcefile):
	filenamein = "./DataBak/%s" % sourcefile
	filenameout = filenamein[:-4]+".result"
	f = open(filenamein)
	f1 = open(filenameout,'w') 
	lines = f.readlines()
	last_tag = 0
	now_tag = 0
	WBlines = []
	for linenum in range(len(lines)):
		if lines[linenum] == ";0\n" or lines[linenum] == ";1\n":
			last_tag = now_tag
			now_tag = linenum		
			for line in (lines[(last_tag+1):now_tag]):
				print line
				if line.strip().split()[3] == "RRSIG":
					pass
				elif line.strip().split()[3] == "A":
					WBlines.append(line[:-1]+'\t\t\t\t\t\t'+lines[now_tag][1:])
				elif line.strip().split()[3] == "AAAA":
					WBlines.append(line[:-1]+'\t\t\t\t\t\t'+lines[now_tag][1:])
				elif line.strip().split()[3] == "NS":
					WBlines.append(line[:-1]+'\t\t\t\t\t\t'+lines[now_tag][1:])

	f1.writelines(WBlines)
	f.close()
	f1.close()

	file_name_yse = "./Data/tldspider.dnssec"
	file_name_no = "./Data/tldspider.nodnssec"	
	fyes = open(file_name_yse,'w')
	fno = open(file_name_no, 'w')
	yeslist = []
	nolist = []
	for line in WBlines:
		if line.strip().split()[-1] == '0':
			nolist.append('\t'.join(line.strip().split()[:-1])+'\n')
		elif line.strip().split()[-1] == '1':
			yeslist.append('\t'.join(line.strip().split()[:-1])+'\n')
	fyes.writelines(yeslist)
	fno.writelines(nolist)




def fetch(tldstring, qtype):

#	AnswerList = []	
	ReturnList = []
	ifdnssec = 0

	cmd = "dig @8.8.8.8 %s %s +dnssec" % (tldstring, qtype)
#	cmd = "ls" 
	sub = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	sub.wait()
	digcontent = sub.stdout.readlines()
	pprint.pprint(digcontent)
	
	flags0 = 0
	flags1start = 0
	flags1end = 0
	flags2start = 0
	flags2end = 0


	ifhasanswer = 0
	for i in range(len(digcontent)):
		if "ANSWER SECTION:" not in digcontent[i]:
			continue
		else:
			ifhasanswer = 1
	if ifhasanswer == 0:
		return "NoAnswer"		


	for i in range(len(digcontent)):
		if "flags: qr" in digcontent[i]:
			flags0 = i
		if "ANSWER SECTION:" in digcontent[i]:
			flags1start = i+1
		if "Query time" in digcontent[i] or "AUTHORITY SECTION" in digcontent[i]:
			flags1end = i-1
			break
	
	print flags0
	print flags1start
	print flags1end
#	print flags2start
#	print flags2end

	if "ad" in digcontent[flags0]:
		ifdnssec = 1
	else:
		pass
	
	ReturnList.append(digcontent[flags0])
	ReturnList.extend(digcontent[flags1start:flags1end])
#	ReturnList.extend(AnswerList[flags2start:flags2end])
	ReturnList.append(';'+str(ifdnssec)+'\n')	
	pprint.pprint(ReturnList)
	return ReturnList


def perform_command(schedule,delay_s):
	schedule.enter(delay_s,0,perform_command,(schedule,delay_s))
	spider()

def timing_exe(delay = 14400):
	schedule = sched.scheduler(time.time,time.sleep)
	schedule.enter(0,0,perform_command,(schedule,delay))
	schedule.run()




if __name__ == "__main__":
	os.chdir(PREFIX)
#	timing_exe()
	spider()
#	sort()


