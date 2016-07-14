# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from pprint import pprint
import zipfile
import sys
#sys.path.insert(0, r'C:\Users\zharamax\PycharmProjects\python-docx')
#sys.path.insert(0, r'C:\Users\sdaudi\Github\python-docx')
#import docx as dx

#milon = 'dict.docx'
milon = 'dict_start.docx'
#milon = 'orayta.docx'

import docx_fork_ludoo as docx
doc = docx.Document(milon)
note = doc.footnotes_part.notes

def docxtag(tag=None):
	# TODO make it more general, meaning that the string is taken from the document's definitions
	return "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + tag

class dtag:
	r = docxtag('r')
	t = docxtag('t')
	p = docxtag('p')
	bookmarkStart = docxtag('bookmarkStart')
	bookmarkEnd = docxtag('bookmarkEnd')
	footnoteReference = docxtag('footnoteReference')
	id = docxtag('id')
	name = docxtag('name')
	instrText = docxtag('instrText')


def findNext(elem, child):
	child_found = False
	for e in list(elem):
		if e is child:
			child_found = True
		elif child_found:
			return e

def findNextTextual(elem, child):
	child_found = False
	for e in list(elem):
		if e is child:
			child_found = True
		elif child_found:
			text_elem = e.find(dtag.t)
			if text_elem is not None:
				return e

	return None

def findParagraph(tree, child):
	p = None
	for e in tree.iter():
		if e.tag == dtag.p:
			p = e
		elif e is child:
			return p

	return None

def text(elem):
	return reduce(lambda a,b: a+b, next_textual.itertext())

reffed_fns = {}

with zipfile.ZipFile(milon, 'r') as docxzip:
	tree = ET.ElementTree(ET.fromstring(docxzip.open('word/document.xml', 'r').read()))
	for n in note:
		ref = tree.find(".//%s[@%s='%d'].." % (dtag.footnoteReference, dtag.id, n.id))
		if ref is not None:
			p = tree.find(".//%s[@%s='%d']../.." % (dtag.footnoteReference, dtag.id, n.id))
			next = findNext(p, ref)
			if next.tag == dtag.bookmarkEnd:
				ref_name = p.find(".//%s[@%s='%s']" % (dtag.bookmarkStart, dtag.id, next.attrib[dtag.id])).attrib[dtag.name][1:]
				ref_elems = tree.findall(".//*/[%s='%s']" % (dtag.instrText , ref_name + ' \h'))
				if ref_elems: # not empty
					#print "%d: %s" % (n.id, ref_name)
					text_list = []
					for e in ref_elems:
						pp = findParagraph(tree, e)
						next_textual = findNextTextual(pp, e)
						text_list.append(text(next_textual))
					reffed_fns[n.id] = (ref_name, text_list)

pprint(reffed_fns)
