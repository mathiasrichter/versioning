from rdflib import Graph

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

