from project import es, DATABASE_NAME


#TODO: write handling for images (if we want it?)
def save_entity(entity):
    """All database entities should pass through this method.
    This redirects all database entities to the appropriate handling
    """
    #User specific handling
    if type(entity).__name__ == 'User':
        save_user(entity)



def save_user(user):
    """
    Saves a user to the user mongo database,
    puts the relevant data into elastic,
    overwriting the existing data in elastic for the user
    """
    #save to mongo
    user.save()
    obj_id = str(user._id)
    #delete the entity from elastic search if it already exists
    es.delete(index=DATABASE_NAME,doc_type='User', id=obj_id, ignore=[400, 404])
    #get json user object with some fields removed for saving into elastic
    searchable_entity = create_simple_userJSON(user)
    #resave the entity into elastic search
    es.index(index=DATABASE_NAME, doc_type='User', id=obj_id, body=searchable_entity)

#turns the user json into something indexable by elastic search, removes fields like image and password
def create_simple_userJSON(user_entity):
    searchable_user = {
        "firstName": user_entity.firstName,
        "lastName": user_entity.lastName,
        "role": user_entity.role,
        "email": user_entity.email,
        "major": user_entity.major,
        "graduationYear": user_entity.graduationYear,
        "university": user_entity.university,
        "details": user_entity.details,
        "jobs": user_entity.jobs
    }
    return searchable_user


#remove a mapping from the database, also removes all associated data
def delete_mapping(doc_type):
    es.indices.delete_mapping(index=DATABASE_NAME,doc_type=doc_type)