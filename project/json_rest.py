from flask.json import JSONEncoder
from datetime import datetime
from bson.objectid import ObjectId

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
        	return str(obj)

        return JSONEncoder.default(self, obj)
