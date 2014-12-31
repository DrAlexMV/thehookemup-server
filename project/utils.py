from flask import jsonify

def mergeFrom(fromData, toData, keysToMerge, require=True):
    for key in keysToMerge:
        if key in fromData:
            toData[key] = fromData[key]
        elif require == True:
            raise Exception('Missing required parameter %s' % key)

# gracefully handles errors with incomplete model data.
def jsonFields(modelInstance, fields, response=True):
    entries = {'error' : None}
    for key in fields:
        val = modelInstance.get(key)
        entries[key] = val if (type(val) in [str, int, float] or val is None) else str(val)

    ## TODO: reporting of incomplete models
    if response:
        return jsonify(**entries)

    return entries
