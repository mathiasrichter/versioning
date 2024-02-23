from rdflib import Graph
from versioning import GraphVersionControl, GraphPrettyPrinter    

vc = GraphVersionControl()

# load version 1 of the person graph and commit to version control
g1 = Graph().parse("person_v1.ttl")
vc.commit("person", g1)

# load version 2 of the person graph
g2 = Graph().parse("person_v2.ttl")
vc.commit("person", g2)

GraphPrettyPrinter.print(vc.get_version('person', 1))
GraphPrettyPrinter.print(vc.get_version('person', 2))