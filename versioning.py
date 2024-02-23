from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime

class GraphPrettyPrinter:
    
    @classmethod
    def strip(cls, s:str):
        """Helper Function for pretty printing a graph node."""
        s = str(s)
        return s[s.rfind('/')+1:len(s)]

    @classmethod
    def print(cls, g:Graph, strip=True):
        """Prints the triples of a graph in a somewhat readable manner."""
        i = 1
        r = []
        for s,p,o in g:
            if strip is True:
                r.append((GraphPrettyPrinter.strip(s),GraphPrettyPrinter.strip(p),GraphPrettyPrinter.strip(o)))
            else:
                r.append((s,p,o))
        print(">>>> Graph begin >>>>")
        for s,p,o in sorted(r):
            if strip is True:
                print('{:<4}{:<25}{:<25}{:<25}'.format(i,s,p,o))
            else:
                print('{:<4}{:<60}{:<60}{:<60}'.format(i,s,p,o))
            i += 1
        print("<<<< Graph end <<<<")


class GraphVersionControl:
    
    def __init__(self, versioning_iri = 'http://example.org/versioning/' ):
        self.graphs = {}
        self.versioning_iri = versioning_iri
        if not self.versioning_iri.endswith('/'):
            self.versioning_iri += '/'
        
    def get_id(self) -> str:
        return str(datetime.timestamp(datetime.now())).replace('.','')

    def get_committed_graphs(self):
        return self.graphs
    
    def commit(self, graph_name:str, graph:Graph) -> int:
        if graph_name not in self.graphs.keys():
            # first version
            self.graphs[graph_name] = {
                'name': graph_name, 
                'graph': self.create_version(graph, 1),
                'version': 1
            }
            return 1
        else:
            version_record = self.graphs[graph_name]
            version_record['version'] += 1
            version_record['graph'] += self.create_version(graph, version_record['version'])
            return version_record['version']

    def create_version(self, graph:Graph, version:int) -> Graph:
        result = Graph()
        for s,p,o in graph:
            result.add((s,p,o))
            vt = URIRef(self.versioning_iri+'vt_'+str(version)+'_'+self.get_id())
            result.add((vt, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef(self.versioning_iri+'VersionedTriple')))
            result.add((vt, URIRef(self.versioning_iri+'s'), s))
            result.add((vt, URIRef(self.versioning_iri+'p'), p))
            result.add((vt, URIRef(self.versioning_iri+'o'), o))
            result.add((vt, URIRef(self.versioning_iri+'version'), Literal(version)))
        return result
    
    def get_version(self, graph_name:str, version:int) -> Graph:
        return self.query_version(self.graphs[graph_name]['graph'], version)
        
    def query_version(self, graph:Graph, version:int) -> Graph:
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
                        ?vt rdf:type v:VersionedTriple .
                        ?vt v:version ?version .
                        ?vt v:s ?s .
                        ?vt v:p ?p .
                        ?vt v:o ?o .
                    }
                """)
        result = graph.query(query, initBindings={"version": Literal(version)})
        for r in result:
            result_graph.add((r.s, r.p, r.o))
        return result_graph
