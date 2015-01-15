def generate_search_structure(es):
    # create if not already there
    es.indices.create(index='thehookemup', ignore=400)

    # tell elastic search what the structure of the user is
    es.indices.put_mapping(index='thehookemup',doc_type='User',body={
        "User":{
            "_all" : {"enabled" : True},
            "properties":{
                "email":{"type":"string"},
                "firstName":{"type":"string"},
                "lastName":{"type":"string"},
                "role":{"type":"string"},
                "interests":{
                    "type":"nested",
                    "properties":{
                        "title":{"type":"string"},
                        "description":{"type":"string"}
                    }
                },
                "skills":{"type":"string"},
                "projects": {
                    "type": "nested",
                    "properties":{
                    "title":{"type":"string"},
                    "description":{"type":"string"},
                    "details":{
                        "type":"nested",
                        "properties":{
                            "title":{"type":"string"},
                            "description":{"type":"string"},
                            }
                        }
                    }
                }



            }


        }

    })

