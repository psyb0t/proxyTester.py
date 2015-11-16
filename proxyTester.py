#!/usr/bin/python
import sys
import os
import cStringIO
import pycurl
from time import sleep

args = sys.argv[1:]
if len(args) not in [3, 4]:
  sys.exit('Usage: proxyTester.py [proxy_file] [url] [timeout] '
  '[*export_file]')

proxyFile = args[0]
url = args[1]
timeout = args[2]

if not os.path.isfile(proxyFile):
  sys.exit('Proxy list file does not exist')

try:
  timeout = int(timeout)
except:
  sys.exit('Invalid timeout value')

exportFile = False
if len(args) is 4:
  exportFile = args[3]

children = []

def testProxy(pHost, pPort, pType, url, timeout = 15):
  pType = getattr(pycurl, 'PROXYTYPE_' + pType)
  
  hBuff = cStringIO.StringIO()
  cBuff = cStringIO.StringIO()
  userAgent = ('Mozilla/5.0 (Windows NT 6.3; rv:36.0) '
  'Gecko/20100101 Firefox/36.0')
  
  try:
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.PROXY, pHost)
    curl.setopt(curl.PROXYPORT, pPort)
    curl.setopt(curl.PROXYTYPE, pType)
    curl.setopt(curl.TIMEOUT, timeout)
    curl.setopt(curl.USERAGENT, userAgent)
    curl.setopt(curl.SSL_VERIFYHOST, False)
    curl.setopt(curl.SSL_VERIFYPEER, False)
    curl.setopt(curl.HEADERFUNCTION, hBuff.write)
    curl.setopt(curl.WRITEFUNCTION, cBuff.write)
    
    curl.perform()
  except pycurl.error as (errCode, errMsg):
    return (False, errCode, errMsg)
  
  return (True, hBuff.getvalue(), cBuff.getvalue())

def proxyParts(pString):
  if '://' not in pString:
    return False
  
  pType, pAddr = pString.split('://')
  pType = pType.upper()
  if pType not in ['HTTPS', 'HTTP', 'SOCKS5', 'SOCKS4']:
    return False
  
  pHost, pPort = pAddr.split(':')
  try:
    pPort = int(pPort)
  except:
    return False
  
  return (pHost, pPort, pType)

def childProcess(proxy, url, timeout):
  pHost, pPort, pType = proxy
  output = '{}://{}:{}'.format(pType, pHost, pPort)
  
  b, f, s = testProxy(pHost, pPort, pType, url, timeout)
  if not b:
    output += ' [FAIL]'
  else:
    output += ' [SUCCESS]'
    if exportFile:
      with open(exportFile, 'a') as w:
        w.write('{}://{}:{}\n'.format(pType, pHost, pPort))

  print output
  os._exit(0)

def errWrite(err):
  try:
    with open('errs', 'a') as f:
      f.write(err)
  except:
    pass

for line in open(proxyFile, 'r'):
  line = line.strip()
  try:
    proxy = proxyParts(line)
  except Exception as e:
    errWrite(e.strerror)
  
  if proxy and proxy != '':
    pid = os.fork()
    if pid is 0:
      try:
        childProcess(proxy, url, timeout)
      except Exception as e:
        errWrite(e.strerror)
    else:
      children.append(pid)

for child in children:
  try:
    os.waitpid(child, 0)
    children.remove(child)
  except:
    pass

sys.exit('Done!')