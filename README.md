# web-crawler
This program extracts and visualizes course relations in the Northeastern search site (https://wl11gp.neu.edu/udcprod8/NEUCLSS.p_disp_dyn_sched) using Graphviz. BeautifulSoup is used for operated on the HTML documents. After web scraping is performed, a gv document is created with the output in DOT language.

To render DOT as an image: dot -Tpng -ooutput.png input.gv

Queries:
./courses.py --instructor "Derbinsky, Nathaniel L." "Fall 2017 Semester" > derbinsky.gv
./courses.py --subject CS --level UG "Fall 2017 Semester" > cs_undergrad.gv
./courses.py --subject CS --level GR "Fall 2017 Semester" > cs_grad.gv

dot -Tpng -oderbinsky.png derbinsky.gv
dot -Tpng -ocs_undergrad.png cs_undergrad.gv
dot -Tpng -ocs_grad.png cs_grad.gv


Documentation:
http://docs.python-requests.org
http://graphviz.org/

Assignment for CS6220

