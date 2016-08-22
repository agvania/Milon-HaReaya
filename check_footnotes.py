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
	if isinstance(elem, ET.Element):
		return reduce(lambda a,b: a+b, elem.itertext(), '')
	elif isinstance(elem, type([])):
		return reduce(lambda e1,e2: text(e1)+text(e2), elem, '')
	else:
		return elem

def docxtext(docx_elements):
	return reduce(lambda e1,e2: e1.text+e2.text, docx_elements)

reffed_fns = {}

with zipfile.ZipFile(milon, 'r') as docxzip:
	tree = ET.ElementTree(ET.fromstring(docxzip.open('word/document.xml', 'r').read()))
	for n in note:
		# find the xml element representing the note
		ref = tree.find(".//%s[@%s='%d'].." % (dtag.footnoteReference, dtag.id, n.id))
		if ref is not None:
			# find the paragraph containing the footnote
			p = tree.find(".//%s[@%s='%d']../.." % (dtag.footnoteReference, dtag.id, n.id))
			# find the next element right after the footnote
			next = findNext(p, ref)
			# if it's a 'bookmarkEnd' element, it means this footnote is referenced somewhere along the rest of the document
			if next.tag == dtag.bookmarkEnd:
				# get the bookmark's unique name from its 'bookmarkStart' element
				ref_name = p.find(".//%s[@%s='%s']" % (dtag.bookmarkStart, dtag.id, next.attrib[dtag.id])).attrib[dtag.name][1:]
				# find the elements referencing this footnote
				ref_elems = tree.findall(".//*/[%s='%s']" % (dtag.instrText , ref_name + ' \h'))
				if ref_elems: # not empty
					text_list = []
					# for each element, find the next textual element after it, and get its text,
					# which is (or should be at least), the footnote number of the referring footnote
					for e in ref_elems:
						pp = findParagraph(tree, e)
						next_textual = findNextTextual(pp, e)
						recurring_fn_n = text(next_textual).strip()
						p_r = list(pp.iter(dtag.r))
						text_list.append(text(p_r))
					reffed_fns[n.id] = (ref_name, text_list)

for k,v in reffed_fns.iteritems():
	print k, v[0]
	for u in v[1]:
		print u




'''
TODO:
There's a problem here yet: all I do is to find the paragraphs referring to each footnote.
But what we really want is the places where the referring footnote number is not the same as the original footnote.
The original footnote's number is not written in the xml. It is determined by word when processing the xml.
That's why the number is changing automatically when new footnotes are added.
But the number of the referring footnotes ARE written in the xml.
So to really know if the referring footnote's number differs from the original,
we need to calculate the number of the original with the same logic of word.
I don't know how word knows when to start a new numbering. That's what we need to find out.
My guess is that it has a special element in the xml to tell that a new section has started,
and thus the following footnotes will start with a new number.
'''