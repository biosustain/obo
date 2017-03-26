

class OBOException(object):
    def __init__(self):
        pass


class OBOTagCardinalityException(OBOException):
    def __init__(self, stanza, tag, cardinality=(0, 1)):
        pass


class UnknownTermSubset(OBOException):
    """

    https://oboformat.googlecode.com/svn/trunk/doc/GO.format.obo-1_2.html#S.2.2
    The value of this tag must be a subset name as defined in a subsetdef tag in the file header.
    If the value of this tag is not mentioned in a subsetdef tag, a parse error will be generated.
    A term may belong to any number of subsets.

    """
    def __init__(self):
        pass



class MissingRequiredTag(OBOException):
    pass


