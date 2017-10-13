#!/usr/bin/env python

import sys
import os
import getopt

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from graphviz import Digraph
from itertools import groupby

PROG_NAME = os.path.splitext(os.path.basename(__file__))[0]

##############################################################################
##############################################################################

_BASE_URL = "https://wl11gp.neu.edu/udcprod8/"

# requests base+endpoint via get/post with provided parameters
# should NOT be called directly
def _call(endpoint, method, params):
    return getattr(requests,method)(urljoin(_BASE_URL, endpoint), data=params)

# get an endpoint with provided parameters
def _get(endpoint, params={}):
    return _call(endpoint, "get", params)

# post to an endpoint with provided parameters
def _post(endpoint, params={}):
    return _call(endpoint, "post", params)

##############################################################################
##############################################################################

# parses all the options in a select
# returns {value:string}
def _parse_select(select):
	return {str(option["value"]):str(option.string).strip() for option in select.find_all("option")}

# an (imperfect) Banner form parser
# provides a dictionary...
#  title: page title
#  action: form action
#  method: form method (e.g. get/post)
#  params: {
#    key: value (hidden fields and selects)
# }
def _parse_form(html):
    retval = { "params":{} }
    soup = BeautifulSoup(html, "html.parser")

    retval["title"] = str(soup.title.string)

    form = soup.find("div", {"class":"pagebodydiv"}).find("form")

    retval["action"] = str(form["action"])
    retval["method"] = str(form["method"])

    for hidden in form.find_all("input", {"type":"hidden"}):
        retval["params"][str(hidden["name"])] = str(hidden["value"])
        
    for select in form.find_all("select"):
        retval["params"][str(select["name"])] = _parse_select(select)
        
    return retval

##############################################################################
##############################################################################

# parses the term-selection form
# params include {term_code:term_name}
def termform():
    return _parse_form(_get("NEUCLSS.p_disp_dyn_sched").text)

# given the output of termform(),
# returns a term code given a term name
def term_to_code(termform, term):
    terms = termform['params']['STU_TERM_IN']
    inv_terms = {v:k for k,v in terms.items()}
    if term in inv_terms:
        return inv_terms[term]
    else:
        return None

##############################################################################
##############################################################################

# parses the empy course-search form
# for a particular term
def searchform(termcode):
    return _parse_form(_post("NEUCLSS.p_class_select", {"STU_TERM_IN":termcode}).text)

# given the output of searchform(),
# returns an instructor code given an instructor name
def instructor_to_code(searchform, instructor):
    instructors = searchform['params']['sel_instr']
    inv_instructors = {v:k for k,v in instructors.items()}
    if instructor in inv_instructors:
        return inv_instructors[instructor]
    else:
        return None

##############################################################################
##############################################################################

def str_join(*args):
    return ''.join(map(str, args))

# parses the html of a course search, returns...
# TODO: DOCUMENT RETURN WITH EXAMPLES HERE (must be a tuple)
def _parse_course_listing(html):
    retval = { "params":{} }
    soup = BeautifulSoup(html, "html.parser")
    retval["title"] = str(soup.title.string)
    form = soup.find("div", {"class":"pagebodydiv"}).find("table")
    key = ""
    for atag in form.find_all('a'):
        atext = str(atag.text).split(" - ")
        if len(atext) > 1:
            num = str(atext[2]).strip()
            courseNodeLabel = str_join(num, '\n', str(atext[0]).strip())
            key = num.replace(" ", "_")
            if key not in retval["params"]:
                retval["params"].setdefault(key, [])
                retval["params"][key].append(courseNodeLabel)
        else:
            if 'Syllabus Available' not in atext[0]:
                underscoreText = atext[0].replace(" ", "_")
                if (key is not underscoreText and underscoreText not in retval["params"][key] and underscoreText not in retval["params"]):
                    retval["params"][key].append(underscoreText)
                    retval["params"].setdefault(underscoreText, [])
                    prereqLabel = str_join(atext[0], '\n')
                    retval["params"][underscoreText].append(prereqLabel)
    
    #d = [x for x, y in groupby(retval["params"])]
    #finalInfo = dict(zip(sorted(retval["params"].items()), d))
    print(retval)
    return (None, None, None) # TODO: replace with your code (course numbers, titles, prereqs)

# execute a course search request
# returns the parsed result: format of your choice (must be a tuple)
# (see _parse_course_listing for details)
def coursesearch(termcode, 
                 sel_day=[], sel_subj=["%"], sel_attr=["%"],
                 sel_schd=["%"], sel_camp=["%"], sel_insm=["%"], 
                 sel_ptrm=["%"], sel_levl=["%"], sel_instr=["%"], sel_seat=[],
                 sel_crn="", sel_crse="", sel_title="", sel_from_cred="", sel_to_cred="",
                 begin_hh="0", begin_mi="0", begin_ap="a",
                 end_hh="0", end_mi="0", end_ap="a"):
    
    # required parameters
    # (or Banner gets unhappy)
    params = [
        ("STU_TERM_IN", termcode),
        ("sel_day", "dummy"),
        ("sel_subj", "dummy"),
        ("sel_attr", "dummy"),
        ("sel_schd", "dummy"),
        ("sel_camp", "dummy"),
        ("sel_insm", "dummy"),
        ("sel_ptrm", "dummy"),
        ("sel_levl", "dummy"),
        ("sel_instr", "dummy"),
        ("sel_seat", "dummy"),
        ("p_msg_code", "UNSECURED"),
        ("sel_crn", sel_crn),
        ("sel_subj", sel_subj), # CS
        ("sel_crse", sel_crse),
        ("sel_title", sel_title),
        ("sel_attr", sel_attr),
        ("sel_levl", sel_levl), # UG G
        ("sel_schd", sel_schd),
        ("sel_insm", sel_insm),
        ("sel_from_cred", sel_from_cred),
        ("sel_to_cred", sel_to_cred),
        ("sel_camp", sel_camp),
        ("sel_ptrm", sel_ptrm),
        ("sel_instr", sel_instr),
        ("begin_hh", begin_hh),
        ("begin_mi", begin_mi),
        ("begin_ap", begin_ap),
        ("end_hh", end_hh),
        ("end_mi", end_mi),
        ("end_ap", end_ap)
    ]
    
    # @TODO
    # 1. Take function parameters and add to params
    # 2. Submit form with parameters
    # 3. Call _parse_course_listing to parse, return
    return _parse_course_listing(_post("NEUCLSS.p_class_search", params).text)

##############################################################################
##############################################################################

# takes in output of coursesearch
# and outputs to the console a digraph of related courses
# in DOT format
def print_course_dot(courseinfo):
    # @TODO check height and width
    g = Digraph('G', filename='test_dot.gv', node_attr={'width': '5', 'height': '1'})
    dot = Digraph(name='G')
    dot.graph_attr['rankdir'] = 'LR'

    # @TODO sort course number for nodes

    # @TODO sort course number w/ prereq sorted too

    # @TODO
    # for each course number create a node
    # dot.node('CS_5001', 'CS 5001\nIntensive Foundations of Computer Science')

    # for each course number with prereq(s) create an edge
    # dot.edges(['CS_5001', 'CS_5003'])

    print(dot.source)

##############################################################################
##############################################################################

# outputs usage statement and exits
def usage():
    print("usage:", PROG_NAME, "(--level)*", "(--instructor)*", "(--subject)*", "[--course]", "<term code>")
    print(" ()* can occur 0 or more times")
    print(" [] can occur 0 or 1 time")
    print(" <> must be provided")
    sys.exit(2)

# 1. parses command-line parameters
#    - uses term form to validate term
#    - uses search form to validate level, instructor, subject
# 2. performs a course search
# 3. outputs information in DOT format
def main(argv):
    opts,args = getopt.getopt(argv,"",["level=", "instructor=", "subject=", "course="])
    
    #####
    
    if len(args) != 1:
        usage()
        
    term = args[0]
    termcode = term_to_code(termform(), term)
    if termcode is None:
        print("ERROR: invalid term")
        usage()
        
    #####
        
    sform = searchform(termcode)
        
    levels = []
    instructors = []
    subjects = []
    course = None
    
    for opt in opts:
        if opt[0] == "--course":
            if course is not None:
                print("ERROR: only one course allowed")
                usage()
            else:
                course = opt[1]
                
        elif opt[0] == "--level":
            if opt[1] in sform['params']['sel_levl'].keys():
                levels.append(opt[1])
            else:
                print("ERROR: invalid level '{}'".format(opt[1]))
                usage()
                
        elif opt[0] == "--instructor":
            instructorcode = instructor_to_code(sform, opt[1])
            if instructorcode is not None:
                instructors.append(instructorcode)
            else:
                print("ERROR: invalid instructor '{}'".format(opt[1]))
                usage()
                
        elif opt[0] == "--subject":
            if opt[1] in sform['params']['sel_subj'].keys():
                subjects.append(opt[1])
            else:
                print("ERROR: invalid subject '{}'".format(opt[1]))
                usage()
    
    if not len(levels):
        levels = ["%"]
        
    if not len(instructors):
        instructors = ["%"]
        
    if not len(subjects):
        subjects = ["%", "%"]
        
    if course is None:
        course = ""
        
    info = coursesearch(termcode,
        sel_levl=levels,
        sel_instr=instructors,
        sel_subj=subjects,
        sel_crse=course
    )
    
    #####
    
    print_course_dot(*info)
    
if __name__ == "__main__":
    main(sys.argv[1:])
