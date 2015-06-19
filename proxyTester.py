#!/usr/bin/python
import sys
import os
import cStringIO
import pycurl

args = sys.argv[1:]
if len(args) not in [3, 4]:
  sys.exit('Usage: proxyTester.py [proxy_file] [url] [timeout] '
  '[*export_file]')

proxyFile = args[0]
url = args[1]
timeout = args[2]

exportFile = False
if len(args) is 4:
  exportFile = args[3]

def testProxy(pHost, pPort, pType, url, timeout = 15):
  pType = getattr(pycurl, 'PROXYTYPE_' + pType)
  
  hBuff = cStringIO.StringIO()
  cBuff = cStringIO.StringIO()
  userAgent = ('Mozilla/5.0 (Windows NT 6.3; rv:36.0) '
  'Gecko/20100101 Firefox/36.0')
  
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
  
  try:
    curl.perform()
  except pycurl.error as (errCode, errMsg):
    return (False, errCode, errMsg)
  
  return (True, hBuff.getvalue(), cBuff.getvalue())

def proxyParts(pString):
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

def run(proxyFile, timeout, url):
  if not os.path.isfile(proxyFile):
    sys.exit('Proxy list file does not exist')
  
  try:
    timeout = int(timeout)
  except:
    sys.exit('Invalid timeout value')
  
  with open(proxyFile, 'r') as f:
    for line in f:
      line = line.strip()
      proxy = proxyParts(line)
      
      if proxy:
        pHost, pPort, pType = proxy
        sys.stdout.write('Testing {} proxy {}:{}'.format(pType, pHost, pPort))
        sys.stdout.flush()
        
        b, f, s = testProxy(pHost, pPort, pType, url, timeout)
        if not b:
          print ' - FAIL'
          continue
        print ' - SUCCESS'
        
        if exportFile:
          with open(exportFile, 'a') as w:
            w.write('{}://{}:{}\n'.format(pType, pHost, pPort))

run(proxyFile, timeout, url)
