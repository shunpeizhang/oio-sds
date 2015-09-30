#!/usr/bin/env python

# test_oiosds.py, a script performing functional tests of the OpenIO SDS's C SDK 
# Copyright (C) 2015 OpenIO, original work as part of OpenIO Software Defined Storage
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json, threading, BaseHTTPServer
from ctypes import cdll

class DumbHttpMock (BaseHTTPServer.BaseHTTPRequestHandler):
	def reply (self):
		if len(self.server.expectations) <= 0:
			return
		req, rep = self.server.expectations.pop(0)

		# Check the request
		qpath, qhdr, qbody = req
		if qpath is not None and qpath != self.path:
			raise Exception("unexpected request got:"+str(self.path)+" expected:"+str(qpath))
		if qhdr is not None:
			for k,v in qhdr.items():
				if k not in self.headers:
					raise Exception("missing headers: "+k)
				if self.headers[k] != v:
					raise Exception("invalid header value got:"+str(self.headers[k])+" expected:"+str(v))

		# Reply
		pcode, phdr, pbody = rep
		self.send_response(pcode)
		for k,v in phdr.items():
			self.send_header(k,v)
		if "Content-Length" not in phdr:
			self.send_header("Content-Length", str(len(pbody)))
		self.end_headers()
		self.wfile.write(pbody)
	def do_HEAD (self):
		return self.reply()
	def do_GET (self):
		return self.reply()
	def do_POST (self):
		return self.reply()
	def do_PUT (self):
		return self.reply()
	def do_GET (self):
		return self.reply()
	def do_DELETE (self):
		return self.reply()

def http2url(s):
	return '127.0.0.1:' + str(s.server_port)

class Service (threading.Thread):
	def __init__ (self, srv):
		threading.Thread.__init__(self)
		self.srv = srv
	def run (self):
		self.srv.serve_forever()

def test_get(lib):
	http, services, urls = [], [], []

	http.append(BaseHTTPServer.HTTPServer(("127.0.0.1",0), DumbHttpMock))
	for _ in range(3):
		http.append(BaseHTTPServer.HTTPServer(("127.0.0.1",0), DumbHttpMock))
	for h in http:
		urls.append(http2url(h))
		services.append(Service(h))

	rawx_expectations = [
		(("/0000000000000000000000000000000000000000000000000000000000000000", {"Range":"bytes=0-63"}, ""),
		 (200, {"Content-Range":"bytes=0-63/64"}, "0"*64)),

		(("/0000000000000000000000000000000000000000000000000000000000000001", {"Range":"bytes=0-63"}, ""),
		 (200, {"Content-Range":"bytes=0-63/64"}, "0"*64)),

		(("/0000000000000000000000000000000000000000000000000000000000000004", {"Range":"bytes=0-15"}, ""),
		 (200, {"Content-Range":"bytes=0-15/16"}, "0"*16)),
		(("/0000000000000000000000000000000000000000000000000000000000000005", {"Range":"bytes=0-15"}, ""),
		 (200, {"Content-Range":"bytes=0-15/16"}, "0"*16)),
		(("/0000000000000000000000000000000000000000000000000000000000000006", {"Range":"bytes=0-15"}, ""),
		 (200, {"Content-Range":"bytes=0-15/16"}, "0"*16)),
		(("/0000000000000000000000000000000000000000000000000000000000000007", {"Range":"bytes=0-15"}, ""),
		 (200, {"Content-Range":"bytes=0-15/16"}, "0"*16)),
	]
	for h in http[1:]:
		h.expectations = rawx_expectations
	http[0].expectations = [
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (503, {}, "")),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (200, {}, "[]")),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (200, {}, json.dumps([
			{"url":"http://"+urls[1]+"/0000000000000000000000000000000000000000000000000000000000000000",
			"pos":"0.0", "size":64, "hash":"00000000000000000000000000000000"},
		]))),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (200, {}, json.dumps([
			{"url":"http://"+urls[1]+"/0000000000000000000000000000000000000000000000000000000000000001",
			"pos":"0.0", "size":64, "hash":"00000000000000000000000000000000"},
			{"url":"http://"+urls[2]+"/0000000000000000000000000000000000000000000000000000000000000002",
			"pos":"0.0", "size":64, "hash":"00000000000000000000000000000000"},
			{"url":"http://"+urls[3]+"/0000000000000000000000000000000000000000000000000000000000000003",
			"pos":"0.0", "size":64, "hash":"00000000000000000000000000000000"},
		]))),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (200, {}, json.dumps([
			{"url":"http://"+urls[1]+"/0000000000000000000000000000000000000000000000000000000000000004",
			"pos":"0.0", "size":16, "hash":"00000000000000000000000000000000"},
			{"url":"http://"+urls[2]+"/0000000000000000000000000000000000000000000000000000000000000005",
			"pos":"0.1", "size":16, "hash":"00000000000000000000000000000000"},
			{"url":"http://"+urls[3]+"/0000000000000000000000000000000000000000000000000000000000000006",
			"pos":"0.2", "size":16, "hash":"00000000000000000000000000000000"},
			{"url":"http://"+urls[3]+"/0000000000000000000000000000000000000000000000000000000000000007",
			"pos":"0.3", "size":16, "hash":"00000000000000000000000000000000"},
		]))),
	]
	for s in services:
		s.start()

	cfg = json.dumps({"NS":{"proxy":urls[0]}})
	try:
		lib.test_init(cfg, "NS")
		lib.test_get_fail(cfg, "NS", "NS/ACCT/JFS//plop")
		lib.test_get_fail(cfg, "NS", "NS/ACCT/JFS//plop")
		lib.test_get_success(cfg, "NS", "NS/ACCT/JFS//plop", 64)
		lib.test_get_success(cfg, "NS", "NS/ACCT/JFS//plop", 64)
		lib.test_get_success(cfg, "NS", "NS/ACCT/JFS//plop", 64)
	finally:
		for h in http:
			h.shutdown()
		for s in services:
			s.join()

def test_has(lib):
	proxy = BaseHTTPServer.HTTPServer(("127.0.0.1",0), DumbHttpMock)
	proxy.expectations = [
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (204, {}, "")),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (404, {}, "")),
		(("/v2.0/m2/NS/ACCT/JFS/plop", {}, ""), (500, {}, "")),
	]
	proxy_url = str(proxy.server_name) + ':' + str(proxy.server_port)
	service = Service(proxy)
	service.start()

	cfg = json.dumps({"NS":{"proxy":proxy_url}})
	try:
		lib.test_init(cfg, "NS")
		lib.test_has(cfg, "NS", "NS/ACCT/JFS//plop")
		lib.test_has_not(cfg, "NS", "NS/ACCT/JFS//plop")
		lib.test_has_fail(cfg, "NS", "NS/ACCT/JFS//plop")
	finally:
		proxy.shutdown()
		service.join()

if __name__ == '__main__':
	lib = cdll.LoadLibrary("liboiosds_test.so")
	lib.setup()
	test_has(lib)
	test_get(lib)
