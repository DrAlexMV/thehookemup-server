from project import database_wrapper, config
from bson.objectid import ObjectId
from project.services.database import Database
from mongokit import Document

Skills = Database['Skills']
connection = Database.connection()


@connection.register
class Skill(Document):
    __collection__ = 'Skills'
    __database__ = config['DATABASE_NAME']
    structure = {
        'name': basestring,
        'occurrences': int
    }
    required_fields = ['name', 'occurrences']

    '''default_values = {
        'occurrences': 1
    }'''

    use_dot_notation = True

    def __repr__(self):
        return '<Skill %r>' % (self.name)


def create_skill(name, occurrences):
    skill = Skills.Skill()
    skill['name'] = name
    skill['occurrences'] = occurrences
    database_wrapper.save_entity(skill)
    return skill


def find_skill_by_id(skill_id):
    # takes a string id
    skill = Skills.Skill.find_one({'_id': ObjectId(skill_id)})
    return skill


def find_skill(map_attributes):
    entry = Skills.Skill.find_one(map_attributes)
    return entry


def increment_skill(skill):
    skill.occurrences += 1
    database_wrapper.save_entity(skill)


# TODO: delete skills from elastic and database if decremented to zero
def decrement_skill(skill):
    if skill.occurrences == 1:
        database_wrapper.remove_entity(skill)
    else:
        skill.occurrences -= 1
        database_wrapper.save_entity(skill)
