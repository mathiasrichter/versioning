# Versioning
An exploration of how to version rdf graphs.

## Overview
`versioning.py` contains `GraphVersionControl`, a class providing a simple implementation of how to do version control using rdf-triples (using the vocab in `versioning.ttl`).    

`person_v1.ttl`and `person_v2.ttl` are two versions of the same graph.   

`pretty.py`contains a pretty printer for graphs.   

`sample.py` shows how to tie it all together.   

## Approach
The vocabulary in `verisoning.ttl` defines a `VersionedTriple`. A `VersionedTriple` links a subject, predicate, object with an integer version number. When a graph is versioned, `GraphVersionControl`creates a `VersionedTriple`for each triple in that graph, thus creating a versioned graph for the initial graph. Future versions of the same graph are added with additional versioned triples in the versioned graph maintained by `GraphVersionControl`. So the versioned graph is the "supergraph" of all versions of one graph. Individual versions of the graph are extracted from the versioned graph using SPARQL.  

Let's look at an example graph:

```
@prefix : <http://example.org/sample/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Person rdf:type rdfs:Class .
```

The versioned graph looks like this:

```
@prefix : <http://example.org/sample/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix v: <http://example.org/versioning/> .

:Person rdf:type rdfs:Class .

:vt1 rdf:type v:VersionedTriple  ;
    v:s :Person ;
    v:p rdf:type ;
    v:o rdfs:Class ;
    v:version 1;
.
```

Now let's change the graph:

```
@prefix : <http://example.org/sample/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Person rdf:type rdfs:Class ;
    rdfs:label "Person" ;
.
```

The corresponding versioned graph looks like this:

```
@prefix : <http://example.org/sample/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix v: <http://example.org/versioning/> .

:Person rdf:type rdfs:Class .

:vt1 rdf:type v:VersionedTriple  ;
    v:s :Person ;
    v:p rdf:type ;
    v:o rdfs:Class ;
    v:version 1;
.

:vt2 rdf:type v:VersionedTriple  ;
    v:s :Person ;
    v:p rdf:type ;
    v:o rdfs:Class ;
    v:version 2;
.

:vt3 rdf:type v:VersionedTriple  ;
    v:s :Person ;
    v:p rdfs:label ;
    v:o "Person" ;
    v:version 2;
.
```

This SPARQL query extracts all versioned triples for version 1:

```
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX v: <http://example.org/versioning/>

    SELECT DISTINCT ?s ?p ?o
    WHERE
    { 
        ?vt rdf:type v:VersionedTriple .
        ?vt v:version 1 .
        ?vt v:s ?s .
        ?vt v:p ?p .
        ?vt v:o ?o .
    }
```

`GraphVersionControl` constructs a new graph from the triples returned by this query on the versioned graph.