import requests,os,warnings,time,sys,re,shutil

if len(sys.argv)>1 and sys.argv[1]:
    ip = sys.argv[1]
else:
    ip = '10.0.0.10'
if len(sys.argv)>2 and sys.argv[2]:
    login=sys.argv[2]
else:
    login = 'root'
if len(sys.argv)>3 and sys.argv[3]:
    password=sys.argv[3]
else:
    password='Huawei12#$'

print('Try iKVM %s, login: %s, password: %s' %(ip,login,password))
session = requests.Session()
session.verify = False
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
headers=session.headers.update(
    {
        'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/102.0',
    }
)

def getData(ip,login,password):
    session.get('https://' + ip + '/')
    res = session.get('https://'+ip+'/login.asp?lang=en', headers=headers)
    if res.status_code==200:
        res = session.post('https://'+ip+'/goform/Login', headers=headers,data={'lang':'end','UserName':login,
                                                            'Password':password,'authenticateType':'0','domain':'0'})
        if not 'index.asp' in res.text:
            print('No loggined, try again')
            res = session.post('https://' + ip + '/goform/Login', headers=headers,
                               data={'lang': 'end', 'UserName': login, 'Password': password, 'authenticateType': '0',
                                     'domain': '0'})

        if 'index.asp' in res.text:
            print('Loggined')
            res = session.get('https://' + ip + '/index.asp', headers=headers)
            if 'bottom.asp' in res.text:
                res = session.get('https://' + ip + '/kvmvmm.asp?kvmmode=1', headers=headers)
                if ('verifyValue' in res.text or 'VERIFYVALUE' in res.text) and ('typeData' in res.text or 'TYPEDATA' in res.text):
                    if m := re.search(r'verifyvalue*.+value*.+=*.+(\'|\")(.+)(\'|\")', res.text,re.I):
                        print('Finded First Key')
                        if m.group(2):
                            fkey=m.group(2)
                    if m := re.search(r'typedata*.+value*.+=*.+(\'|\")(.+)(\'|\")', res.text,re.I):
                        print('Finded Second Key')
                        if m.group(2):
                            lkey=m.group(2)
                    #fkey=res.text.split('verifyValue" VALUE="')[1].split('">')[0]
                    #lkey = res.text.split('typeData" VALUE="')[1].split('">')[0]
                    dwnld='jar'
                    file='vconsole.jar'
                    if m := re.search(r'codebase*.+value*.+=*.+(\'|\")(.+)(\'|\")', res.text,re.I):
                        print('Finded path KVM')
                        if m.group(2):
                            dwnld=m.group(2)
                    else:
                        print('No finded path KVM')
                    if m := re.search(r'archive*.value*.=*.(\'|\")(.+)(\'|\")', res.text,re.I):
                        print('Finded file KVM')
                        if m.group(2):
                            file=m.group(2)
                    else:
                        print('No finded path KVM')
                    print('Try get '+'https://' + ip + '/'+dwnld+'/'+file)
                    response = session.get('https://' + ip + '/'+dwnld+'/'+file, stream=True)
                    with open(file, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                    print(fkey)
                    print(lkey)
                    return {'ip':ip,'fkey':fkey,'lkey':lkey,'file':file}
        else:
            print('No loggined, tryed')
    return False

def setFile(ip,fkey,lkay,finame):
    with open('kvm.jnlp', 'w') as fp:
        fp.write('''<?xml version="1.0" encoding="UTF-8"?>
		<jnlp spec="1.0+" codebase="">
			<information>
			<title>Remote Virtual Console   IP : %s</title>
				<vendor>iBMC</vendor>
			</information>
			<resources>
				<j2se version="1.6" />
				<jar href="%s" main="true"/>
			</resources>
			<applet-desc name="Remote Virtual Console(%s)" main-class="com.kvm.KVMApplet" width="950" height="700" >
				<param name="verifyValue" value="%s"/>
				<param name="mmVerifyValue" value="%s"/>
				<param name="typeData" value="%s"/>
				<param name="java_arguments" value="-Xmx256m -Dcom.sun.net.ssl.checkRevocation=false">
				<param name="local" value="en"/>
				<param name="compress" value="0"/>
				<param name="vmm_compress" value="0"/>
				<param name="port" value="2198"/>
				<param name="vmmPort" value="8208"/>
				<param name="privilege" value="4"/>
				<param name="bladesize" value="1">
				<param name="productType" value="BMC">
				<param name="ietype" value="i586">
				<param name="IPA" value="%s"/>
				<param name="IPB" value="%s"/>
				<param name="title" value="   IP : %s"/>
				
			</applet-desc>
			<security>
				<all-permissions/>
			</security>
		</jnlp>''' %(ip,finame,ip,fkey,fkey,lkay,ip,ip,ip))
        fp.close()
        return 'kvm.jnlp'
    return False

dt=getData(ip,login,password)
while not dt:
    dt = getData(ip, login, password)
if dt and 'fkey' in dt.keys():
    setFile(ip, dt['fkey'], dt['lkey'], dt['file'])
    if os.path.isfile('kvm.jnlp'):
        os.system('javaws ./kvm.jnlp')
        os.remove('kvm.jnlp')
