# -*- coding: utf-8 -*-
'''
This module is respnsible for building the html documents of the Milon.
It encapsulates the opening, setup, and closing of the documents, and exposes an API for adding paragraphs to the milon.
'''

import dominate
import dominate.tags as tags
import re
import copy
import HTMLParser
import sizes
from text_segments import MilonTextSegments as TS, fake
import text_segments as ts

html_parser = HTMLParser.HTMLParser()

# dictionary mapping subjects to list of pointers
# each pointer is a tuple of (subject, html_doc's section name, url)
subjects_db = {}
html_docs_l = []

def calc_subject_id(text_orig, cnt):
    # subject_id = "subject_%d" % len(subjects_db)
    text = text_orig.replace(" ", "-")
    if cnt == 0:
        return text
    else:
        return "%s%d" % (text, cnt)

def subject(html_doc, type, text):
    clean_text = clean_name(text.strip())
    new_subject_l = subjects_db.get(clean_text, [])
    subject_id = calc_subject_id(text.strip(), len(new_subject_l))
    new_subject_l.append((text.strip(), html_doc.section, "%s.html#%s" % (html_doc.index, subject_id)))
    subjects_db[clean_text] = new_subject_l

    with tags.span(text, id=subject_id):
        tags.attr(cls=type)

    # with tags.span(tags.a(text, href="#%s" % text.strip(), id=text.strip())):
    #     tags.attr(cls=type)

def regular(type, text):
    if type in [TS.footnote, TS.footnoteRec]:
        with tags.a("(%s)" % text.strip()):
            tags.attr(cls="ptr")
    else:
        if "\n" in text:
            print "New:", text
        if u"°" in text:
            href = re.sub(u"°", "", text)
            href = re.sub(u"־", " ", href)
            with tags.span(tags.a(text, href="#"+href)):
                tags.attr(cls=type)
        else:
            with tags.span(text):
                tags.attr(cls=type)


# return True if updated
def update_values_for_href(child, href):
    values = subjects_db.get(href)
    #TODO: support showing more than 1 result
    if values is None:
        return False
    if len(values) == 1:
        _, _, url = values[0]
        child.children[0]['href'] = url
        return True
    elif len(values) > 1:
        # # tuple of (subject, html_doc's section name, url)
        # subject, section, url = values[]
        child.children[0]['href'] = "search.html?"+href
        return True
    else:
        assert False

def update_href_no_link(child):
    assert len(child.children[0].children) == 1
    text = html_parser.unescape(child.children[0].children[0])
    child.children[0] = tags.span(text)

def fix_links(html_docs_l):
    # fix outbound links
    print "Fixing links"
    for (doc) in html_docs_l:
        for (child) in doc.body.children[0].children:
            if 'definition' in child.attributes.get('class', ()):
                href = ""
                try:
                    href = child.children[0].attributes.get("href")
                except AttributeError as e:
                    pass

                # it's a link - try to update it
                if href:
                    # first, strip it of weird chars
                    try:
                        href = clean_name(href)

                        updated = False
                        if update_values_for_href(child, href):
                            updated = True
                        else:
                            if href[0] in (u"ה", u"ו", u"ש", u"ב", u"כ", u"ל", u"מ"):
                                updated = update_values_for_href(child, href[1:])
                        if not updated:
                            # failed to update - it's not a real link...
                            update_href_no_link(child)

                    except Exception as e:
                        pass
                        print e, "Exception of HREF update", href
                        #TODO - investigate why it happens? (it's a single corner case, I think)


    def sorter(html_doc):
        if html_doc.name in [u"ערכים כלליים",]:
            return "FIRST"
        if html_doc.name in [u"נספחות",]:
            return u"תתתתתתתתתת"    #last
        else:
            return html_doc.name

    # update sections menu
    for (doc) in html_docs_l:
        letters_l = []

        # content_menu = doc.body.children[0].children[1].children[0].children[0].children[-1].children[0].children[1]
        content_menu = doc.body.children[0].children[1].children[0].children[1].children[-1]
        assert content_menu['class'] == 'dropdown-menu dropdown-menu-left scrollable-menu'

        with content_menu:
            with tags.li():
                tags.a(u"אודות", href="index.html")
            with tags.li():
                tags.a(u"הקדמות", href="opening_intros.html")
            with tags.li():
                tags.a(u"הסכמות", href="opening_haskamot.html")
            with tags.li():
                tags.a(u"קיצורים", href="opening_abbrev.html")
            with tags.li():
                tags.a(u"סימנים", href="opening_signs.html")
            # if you add more entries here, please update add_menu_to_apriory_htmls(..)
            with tags.li():
                tags.attr(cls="divider")

            sorted_html_docs_l = sorted(html_docs_l, key=sorter)

            for (html_doc) in sorted_html_docs_l:
                # Only if this a 'high' heading, and not just a letter - include it in the TOC
                if html_doc.name != "NEW_LETTER":
                    with tags.li():
                        tags.a(html_doc.name, href=str(html_doc.index)+".html")
                        if doc.section == html_doc.section:
                            tags.attr(cls="active")
                else:
                    # it's a letter - if it's related to me, save it
                    if doc.section == html_doc.section:
                        letters_l.append(html_doc)

        with doc.body.children[-1]:
            assert doc.body.children[-1]['class'] == 'container-fluid'
            with tags.ul():
                tags.attr(cls="pagination")
                for (html_doc) in letters_l:
                    tags.li(tags.a(html_doc.letter, href=str(html_doc.index)+".html"))



    return html_docs_l

new_lines_in_raw = 0
def add_to_output(html_doc, para, size_kind):
    global new_lines_in_raw
    # we shouldn't accept empty paragraph (?)
    assert len(para) > 0

    with html_doc.body.children[-1]:
        assert html_doc.body.children[-1]['class'] == 'container-fluid';
        for (i, (type, text)) in enumerate(para):
            if 'heading' in type and text.strip():
                # tags.p()
                # tags.p()
                heading = sizes.get_heading_type(size_kind)
                print type, text
                heading(text)
            elif type == TS.newLine:
                new_lines_in_raw += 1
                if new_lines_in_raw == 1:
                    tags.br()
                elif new_lines_in_raw == 2:
                    tags.p()
                else:
                    pass
            elif ts.is_subject(para, i):
                if not ts.is_prev_subject(para, i):
                    # tags.p()
                    #tags.br()
                    pass
                subject(html_doc, type, text)
            else:
                regular(type, text)

            if type != TS.newLine:
                new_lines_in_raw = 0

        # tags.br()

def add_footnote_to_output(paragraphs):
    text = ""
    for (para) in paragraphs:
        text += para.text
    tags.li(text)


def open_html_doc(name, letter=None):
    html_doc = dominate.document(title=u"מילון הראיה")
    html_doc['dir'] = 'rtl'
    with html_doc.head:
        with tags.meta():
            tags.attr(charset="utf-8")
        with tags.meta():
            tags.attr(name="viewport", content="width=device-width, initial-scale=1")

        tags.script(src="jquery/dist/jquery.min.js")
        tags.link(rel='stylesheet', href='bootstrap-3.3.6-dist/css/bootstrap.min.css')
        tags.link(rel='stylesheet', href='style.css')
        tags.script(src="bootstrap-3.3.6-dist/js/bootstrap.min.js")
        tags.link(rel='stylesheet', href="bootstrap-rtl-3.3.4/dist/css/bootstrap-rtl.css")
        tags.link(rel='stylesheet', href='html_demos-gh-pages/footnotes.css')
        tags.script(src="milon.js")
        tags.script(src="html_demos-gh-pages/footnotes.js")
        tags.script(src="subjects_db.json")




    html_doc.footnote_ids_of_this_html_doc = []
    html_doc.name = name
    if letter:
        html_doc.letter = letter
        html_doc.section = html_docs_l[-1].section
    else:
        html_doc.section = name

    html_doc.index = len(html_docs_l) + 1
    with html_doc.body:
        with tags.div():
            tags.attr(cls="container-fluid")
            # TODO: call page_loaded to update saved URL also in other links
            tags.script("page_loaded('%s.html')" % html_doc.index)

            with tags.div():
                tags.attr(cls="fixed_top_left", id="menu_bar")
                with tags.div():
                    with tags.button(type="button"):
                        tags.attr(id="search_icon_button", type="button", cls="btn btn-default")
                        with tags.span():
                            tags.attr(cls="glyphicon glyphicon-search")
                    with tags.span():
                        tags.attr(cls="dropdown")
                        with tags.button(type="button", cls="btn btn-primary") as b:
                            tags.attr(href="#") #, cls="dropdown-toggle")
                            with tags.span():
                                tags.attr(cls="glyphicon glyphicon-menu-hamburger")
                                # b['data-toggle'] = "dropdown"
                        with tags.ul():
                            tags.attr(cls="dropdown-menu dropdown-menu-left scrollable-menu")

    return html_doc


def clean_name(s):
    s = re.sub(u"־", " ", s, flags=re.UNICODE)
    return re.sub(r"[^\w ]", "", s, flags=re.UNICODE)


def close_html_doc(html_doc, word_doc_footnotes):
    with html_doc.body.children[-1]:
        assert html_doc.body.children[-1]['class'] == 'container-fluid'
        with tags.div(id="search_modal"):
            tags.attr(cls="modal fade")


    with html_doc:
        # add footnotes content of this section:
        with tags.ol(id="footnotes"):
            for (id) in html_doc.footnote_ids_of_this_html_doc:
                footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
                assert footnote.id == id
                add_footnote_to_output(footnote.paragraphs)

        # add placeholder for searching
        tags.comment("search_placeholder")

    place_holder = "<!--search_placeholder-->"
    with open("input_web/stub_search.html", 'r') as file:
        search_html = file.read()

    html_doc_name = html_doc.index
    name = "debug_%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=False).encode('utf8'))
    replace_in_file("output/" + name, place_holder, search_html)

    name = "%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=True).encode('utf8'))
        print "Created ", name
    replace_in_file("output/" + name, place_holder, search_html)


heading_back_to_back = False
pattern = re.compile(r"\W", re.UNICODE)

# returns:
#  None - if no need for new html_doc
#  string - with name of new required html_doc
#  ('UPDATE_NAME', string) - to replace the name of newly opened html_doc
#  ('NEW_LETTER', string) - if needs a new html_doc, but w/o putting it in the main TOC
def is_need_new_html_doc(para):
    global heading_back_to_back
    for (type, text) in para:
        if type in ("heading_title", "heading_section"):
            if not heading_back_to_back:
                heading_back_to_back = True
                return text.strip()
            else:
                # the previous, and this, are headings - unite them
                if html_docs_l[-1].name != u"מדורים":
                    result = html_docs_l[-1].name + " " + text.strip()
                else:
                    # in the special case of 'Section' heading - we don't need it
                    result = text.strip()
                return ('UPDATE_NAME', result)
        elif type == "heading_letter":
            return ('NEW_LETTER', text.strip())

    # if we're here - we didn't 'return text' with a heading
    heading_back_to_back = False

def fix_html_doc_name(name):
    if name == u"מילון הראיה":
        return u"ערכים כלליים"
    else:
        return name


def get_active_html_doc(para):
    name = is_need_new_html_doc(para)
    if name:
        if isinstance(name, tuple):
            op, new = name
            if op == 'NEW_LETTER':
                html_docs_l.append(open_html_doc(op, letter=new))
            else:
                assert op == 'UPDATE_NAME'
                print "Updating ", new
                html_docs_l[-1].name = new
                html_docs_l[-1].section = new
        else:
            fixed_name = fix_html_doc_name(name)
            html_docs_l.append(open_html_doc(fixed_name))
    return html_docs_l[-1]

def replace_in_file(file_name, orig_str, new_str):
    with open(file_name, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(orig_str, new_str)

    with open(file_name, 'w') as file:
        file.write(filedata)


def add_menu_to_apriory_htmls(html_docs_l):
    # add menus to index.html and search.html
    menu_bar = copy.deepcopy(html_docs_l[0].body.children[0].children[1])
    assert menu_bar['id'] == 'menu_bar'
    content = menu_bar.children[0].children[-1].children[1].children
    del(content[6].attributes['class'])

    place_holder = "<!--menu_bar-->"

    menu_bar_html = menu_bar.render(inline=True).encode('utf8')

    with open("input_web/stub_search.html", 'r') as file:
        menu_bar_html += file.read()

    replace_in_file('output/search.html', place_holder, menu_bar_html)

    for index, filename in enumerate((
            'index.html',
            "opening_intros.html",
            "opening_haskamot.html",
            "opening_abbrev.html",
            "opening_signs.html",
    )):
        content[index].attributes['class'] = 'active'
        menu_bar_html = menu_bar.render(inline=True).encode('utf8')
        with open("input_web/stub_search.html", 'r') as file:
            menu_bar_html += file.read()

        replace_in_file('output/%s' % filename, place_holder, menu_bar_html)
        del content[index].attributes['class']

def add(para, size_kind): # TODO 'size_kind' should be removed after I'll find a way to not needing it.
	html_doc = get_active_html_doc(para)
	add_to_output(html_doc, para, size_kind)
	return html_doc

def finish(word_doc_footnotes):
	global html_docs_l
	html_docs_l = fix_links(html_docs_l)
	add_menu_to_apriory_htmls(html_docs_l)

	for (html_doc) in html_docs_l:
		close_html_doc(html_doc, word_doc_footnotes)