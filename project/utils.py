from flask import jsonify

def mergeFrom(fromData, toData, keysToMerge, require=True):
    for key in keysToMerge:
        if key in fromData:
            toData[key] = fromData[key]
        elif require == True:
            raise Exception('Missing required parameter %s' % key)

# gracefully handles errors with incomplete model data.
def jsonFields(modelInstance, fields, response=True, extra=None):
    entries = {'error' : None}

    for key in fields:
        val = modelInstance.get(key)
        entries[key] = val if (type(val) in [str, int, float] or val is None) else str(val)

    if not extra is None:
        entries.update(extra)

    ## TODO: reporting of incomplete models
    if response:
        return jsonify(**entries)

    return entries

#This is for helping construct the proper query to send off to the search function
#elastic search term queries can only take single words without spaces
#this function breaks any multi word filters into a group of single word filters
def fix_term_filter(term_filter):
    """
    Makes sure that the term_filter has only a single entry and the term filter doesn't have spaces. If the
    term_filter does have spaces, it returns a list of single word term_filters for the same field. Otherwise
    returns a list with a single term filter
    """
    output = []
    for entry in term_filter:
         if " " in (term_filter[entry]):
             terms = term_filter[entry].split(" ")
             for term in terms:
                 output.append({entry:term.lower()})
         else:
             output.append({entry:term_filter[entry].lower()})
    return output
