from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime

class NotAVersion(Exception):
    
    def __init__(self, msg:str):
        super().__init__(msg)
        
class GraphNotFound(Exception):
    
    def __init__(self, msg:str):
        super().__init__(msg)
        

class GraphVersionControl:
    
    VERSION_QUERY = """
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX v: <{iri}>
                    
                    SELECT DISTINCT ?s ?p ?o
                    WHERE
                    { 
                        ?vt rdf:type v:VersionedTriple .
                        ?vt v:version ?version .
                        ?vt v:s ?s .
                        ?vt v:p ?p .
                        ?vt v:o ?o .
                    }
                """
    
    def __init__(self, versioning_iri = 'http://example.org/versioning/' ):
        self.versioning_iri = versioning_iri
        self.version_query = prepareQuery(self.VERSION_QUERY.replace('{iri}',self.versioning_iri))
        self.graphs = {}
        if not self.versioning_iri.endswith('/'):
            self.versioning_iri += '/'
        
    def get_id(self) -> str:
        """Generate a unique id based on timestamp."""
        return str(datetime.timestamp(datetime.now())).replace('.','')

    def get_committed_graphs(self) -> list:
        """Return the list of graphs committed to this instance."""
        return self.graphs
    
    def get_entry(self, graph_name:str) -> dict:
        if graph_name in self.graphs.keys():
            return self.graphs[graph_name]
        raise GraphNotFound(graph_name)
    
    def get_latest_version_number(self, graph_name:str) -> int:
        entry = self.get_entry(graph_name)
        return entry['version']
    
    def commit(self, graph_name:str, graph:Graph) -> int:
        """Takes the graph and stores it under the specified name, creating version 1 if the graph has not been stored before,
        or a subsequent version if it has been stored before."""
        try:
            version_record = self.get_entry(graph_name)
            version_record['version'] += 1
            version_record['graph'] += self.create_version(graph, version_record['version'])
            return version_record['version']            
        except GraphNotFound:
            # first version
            self.graphs[graph_name] = {
                'name': graph_name, 
                'graph': self.create_version(graph, 1),
                'version': 1
            }
            return 1

    def create_version(self, graph:Graph, version:int) -> Graph:
        """Takes a graph, stores it under the specified name and tags it with the specified version."""
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
    
    def get_version(self, graph_name:str, version:int=None) -> Graph:
        """Return the graph corresponding to the name and version number specified. If no version is specified, this returns the most recent version."""
        entry = self.get_entry(graph_name)
        if version is None:
            version = entry['version']
        return self.query_version(entry['graph'], version)
        
    def query_version(self, graph:Graph, version:int) -> Graph:
        """Takes a graph representing the superset of multiple versions and extracts just the graph for the specified version."""
        result_graph = Graph()
        result = graph.query(self.version_query, initBindings={"version": Literal(version)})
        if len(result) == 0:
            raise NotAVersion("No version {} for graph.".format(version))
        for r in result:
            result_graph.add((r.s, r.p, r.o))
        return result_graph
