from project import es, DATABASE_NAME, Users, Skills
import requests
import json
from project.config import config
import models

def save_entity(entity):
    """
    All database entities should pass through this method.
    This redirects all database entities to the appropriate handling
    """
    #User specific handling
    if type(entity).__name__ == 'User':
        save_user(entity)

    #Skill specific handling
    if type(entity).__name__ == 'Skill':
        save_skill(entity)


def remove_entity(entity):
    #Skill specific handling
    if type(entity).__name__ == 'Skill':
        remove_skill(entity)


def remove_skill(skill):
    obj_id = str(skill._id)
    headers = {'content-type': 'application/json'}
    r = requests.delete("http://"+config['ELASTIC_HOST']+':'+str(config['ELASTIC_PORT'])+"/skills/skill/"+obj_id, headers=headers)
    skill.delete()


#TODO: Clean this up, use params from project instead of hardcoding
def save_skill(skill):

    skill.save()
    obj_id = str(skill._id)
    headers = {'content-type': 'application/json'}
    r = requests.delete("http://"+config['ELASTIC_HOST']+':'+str(config['ELASTIC_PORT'])+"/skills/skill/"+obj_id, headers=headers)
    #print "first r: " + str(r)+ r.content + '\n'
    searchable_entity = create_simple_skillJSON(skill)
    #print json.dumps(searchable_entity)
    r = requests.put("http://"+config['ELASTIC_HOST']+':'+str(config['ELASTIC_PORT'])+"/skills/skill/"+obj_id, data=json.dumps(searchable_entity), headers=headers)
    #print "second r: " +str(r) + r.content + '\n'
    #es.index(index=DATABASE_NAME, doc_type='Skill', id=obj_id, body=searchable_entity)

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
#TODO: In User enumerate the searchable fields and have this function be malleable in accordance with that
def create_simple_userJSON(user_entity):
    #don't want project dates to be searchable
    for project in user_entity.projects:
        del project['date']
        del project['people']
        print project

    #we want elastic to index users with skills
    skill_names = []
    for skill_id in user_entity.skills:
        skill_names.append(models.skill.find_skill_by_id(skill_id).name)

    searchable_user = {
        "firstName": user_entity.firstName,
        "lastName": user_entity.lastName,
        "roles": user_entity.roles,
        "skills": skill_names,
        "projects": user_entity.projects,
        "email": user_entity.email,
        "major": user_entity.major,
        "graduationYear": user_entity.graduationYear,
        "university": user_entity.university,
        "interests": user_entity.interests
    }

    return searchable_user



def create_simple_skillJSON(skill_entity):
    searchable_skill = {
        "name": skill_entity.name,
        "occurrences":skill_entity.occurrences,
        "name_suggest" : {
            "input":[skill_entity.name],
            "output":skill_entity.name,
            "weight":skill_entity.occurrences
        }
    }
    #print skill_entity.occurrences
    return searchable_skill

#remove a mapping from the database, also removes all associated data
def delete_mapping(doc_type):
    es.indices.delete_mapping(index=DATABASE_NAME,doc_type=doc_type)

#puts everything from the database into elastic
def load_database_to_elastic():
    db_entries=list(Users.User.find())
    for user in db_entries:
        try:
            save_user(user)
            print 'saved successfully'
        except Exception as e:
            print str(e)
            continue

def convert_connection_types():
    db_entries=list(Users.User.find())
    for user in db_entries:
        index = 0
        converted = False
        while index < len(user['edges']['connections']):
            connection = user['edges']['connections'][index]
            if type(connection) != dict:
                converted = True
                user['edges']['connections'][index] = {'user': connection, 'type': 'c'}
            index += 1
        if converted:
            try:
                user.save()
                print 'successfully converted ', user['firstName']
            except Exception as e:
                print 'failed to convert ', user['firstName'], e

