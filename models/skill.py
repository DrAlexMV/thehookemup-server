from mongokit import *
from project import Skills
from project import connection
from project import database_wrapper
from bson.objectid import ObjectId


@connection.register
class Skill(Document):
    __collection__ = 'Skills'
    __database__ = 'thehookemup'
    structure = {
        'name': basestring,
        'occurences': int
        }
    required_fields = ['name', 'occurences']

    '''default_values = {
        'occurences': 1
    }'''

    use_dot_notation = True
    def __repr__(self):
        return '<Skill %r>' % (self.name)

def create_skill(name, occurences):
    skill = Skills.Skill()
    skill['name']=name
    skill['occurences']=occurences
    database_wrapper.save_entity(skill)
    return skill

def find_skill_by_id(skill_id):
    #takes a string id
    skill = Skills.Skill.find_one({'_id': ObjectId(skill_id)})
    return skill

def findSingleSkill(mapAttributes):
    entry = Skills.Skill.find_one(mapAttributes)
    return entry

def increment_skill(skill):
    skill.occurences+=1
    database_wrapper.save_entity(skill)

#TODO: delete skills from elastic and database if decremented to zero
def decrement_skill(skill):
    if skill.occurences==1:
        #delete skill
        print 'need to delete skill from elastic and database'
    else:
        skill.occurences-=1
    database_wrapper.save_entity(skill)