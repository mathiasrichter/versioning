from rdflib import Graph, Literal
from rdflib.plugins.sparql import prepareQuery

def strip(s):
    """Helper Function for pretty printing a graph node."""
    s = str(s)
    return s[s.rfind('/')+1:len(s)]

def print_graph(g):
    """Prints the triples of a graph in a somewhat readable manner."""
    i = 1
    r = []
    for s,p,o in g:
        r.append((strip(s),strip(p),strip(o)))
    for s,p,o in sorted(r):
        print('{:<4}{:<25}{:<25}{:<25}'.format(i,s,p,o))
        i += 1

def query_version(graph, version):
    """Takes a graph representing the superset of multiple versions and extracts just the graph for the specified version."""
    result_graph = Graph()
    query = prepareQuery("""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX v: <http://example.org/versioning/>
                SELECT DISTINCT ?s ?p ?o
                WHERE
                { 
                    ?s ?p ?o .
                    ?s v:version ?version .
                    ?o v:version ?version .
                }
            """)
    result = graph.query(query, initBindings={"version": Literal(version)})
    for r in result:
        result_graph.add((r.s, r.p, r.o))
    return result_graph
        
# load version 1 of the person graph
g1 = Graph().parse("person_v1.ttl")

# load version 2 of the person graph
g2 = Graph().parse("person_v2.ttl")

# combine both graphs to show that all versions of a graph can live in the same supergraph
g = g1 + g2

# extract versions 1 and 2 as separate graphs from the combined supergraph and pretty print
print_graph(query_version(g, 1))
print("-------------------------------------------------------------------------------------------")
print_graph(query_version(g, 2))