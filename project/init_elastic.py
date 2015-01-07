def generate_search_structure(es):
    #tell elastic search what the structure of the user is
    es.indices.put_mapping(index='thehookemup',doc_type='User',body={
        "User":{
            "_all" : {"enabled" : True},
            "properties":{
                "email":{"type":"string"},
                "firstName":{"type":"string"},
                "lastName":{"type":"string"},
                "role":{"type":"string"},
                "details": {
                    "type": "nested",
                    "properties":{
                    "title":{"type":"string"},
                    "content":{
                        "type":"nested",
                        "properties":{
                            "title":{"type":"string"},
                            "description":{"type":"string"},
                            "subpoints":{
                                "type":"nested",
                                "properties":{
                                    "title":{"type":"string"},
                                    "description":{"type":"string"}
                                }
                            }
                        }

                    }
                }
            },
                "jobs":{
                    "type":"nested",
                    "properties":{
                        "companyName": {"type":"string"},
                        "startDate":{"type":"string"},
                        "endDate":{"type":"string"},
                        "description":{"type":"string"},
                        "currentlyWorking":{"type":"boolean"}
                    }
                }
            }
        }
    })

