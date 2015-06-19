Usage: python proxyTester.py [proxy_file] [url] [timeout] [*export_file]

* proxy_file - The plain text file containing the list of proxies eg. socks5://127.0.0.1:8080
* url - The URL to check the proxies against
* timeout - The maximum latency a proxy can have before failing the test
* export_file - Optional argument specifying a file in which proxies that pass the test are written to

Requirements:
* pycurl