PhEmail
======

PhEmail is a python open source phishing email tool that automates the process of sending phishing emails as part of a social engineering test. The main purpose of PhEmail is to send a bunch of phishing emails and prove who clicked on them without attempting to exploit the web browser or email client but collecting as much information as possible. PhEmail comes with an engine to garther email addresses through LinkedIN, useful during the information gathering phase. Also, this tool supports Gmail authentication which is a valid option in case the target domain has blacklisted the source email or IP address. Finally, this tool can be used to clone corporate login portals in order to steal login credentials.

Further info:
https://www.dionach.com/blog/phemailpy-another-social-engineering-tool
https://www.dionach.com/blog/social-engineering-and-phishing-email-attacks

Installation
=====
You can download the latest version of PhEmail by cloning the GitHub repository:

	git clone https://github.com/Dionach/PhEmail


Usage
=====
	PHishing EMAIL tool v0.13
	Usage: phemail.py [-e <emails>] [-m <mail_server>] [-f <from_address>] [-r <replay_address>] [-s <subject>] [-b <body>]
	          -e    emails: File containing list of emails (Default: emails.txt)
	          -f    from_address: Source email address displayed in FROM field of the email (Default: Name Surname <name_surname@example.com>)
	          -r    reply_address: Actual email address used to send the emails in case that people reply to the email (Default: Name Surname <name_surname@example.com>)
	          -s    subject: Subject of the email (Default: Newsletter)
	          -b    body: Body of the email (Default: body.txt)
	          -p    pages: Specifies number of results pages searched (Default: 10 pages)
	          -v    verbose: Verbose Mode (Default: false)
	          -l    layout: Send email with no embedded pictures 
	          -B    BeEF: Add the hook for BeEF
	          -m    mail_server: SMTP mail server to connect to
	          -g    Google: Use a google account username:password
	          -t    Time delay: Add deleay between each email (Default: 3 sec)
	          -R    Bunch of emails per time (Default: 10 emails)
	          -L    webserverLog: Customise the name of the webserver log file (Default: Date time in format "%d_%m_%Y_%H_%M")
	          -S    Search: query on Google
	          -d    domain: of email addresses
	          -n    number: of emails per connection (Default: 10 emails)
	          -c    clone: Clone a web page
	          -w    website: where the phishing email link points to
	          -o    save output in a file
	          -F    Format (Default: 0): 
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
	          
	Examples: phemail.py -e emails.txt -f "Name Surname <name_surname@example.com>" -r "Name Surname <name_surname@example.com>" -s "Subject" -b body.txt
	          phemail.py -S example -d example.com -F 1 -p 12
	          phemail.py -c https://example.com


Disclaimer
=====
Usage of PhEmail for attacking targets without prior mutual consent is illegal. 
It is the end user's responsibility to obey all applicable local, state and federal laws. 
Developers assume NO liability and are NOT responsible for any misuse or damage caused by this program.
