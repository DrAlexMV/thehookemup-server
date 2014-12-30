from flask import jsonify

def mergeFrom(fromData, toData, keysToMerge, require=True):
    for key in keysToMerge:
        data = fromData.get(key)
        if not data is None:
            toData[key] = data
        elif require == True:
            raise Exception('Missing required parameter %s' % key)

# gracefully handles errors with incomplete model data.
def jsonFields(modelInstance, fields):
    entries = {'error' : None}
    for key in fields:
        val = modelInstance.get(key)
        entries[key] = str(val) if (val != None) else None

    ## TODO: reporting of incomplete models
    return jsonify(**entries)
