#!/usr/bin/env python3
import json
import os
import sys
import ast
import inspect
import tornado.web
from tornado.ioloop import IOLoop
from tornado import locks
from tornado import gen
from light.data_model.light_database import LIGHTDatabase

# Conflicts with game UI port
HOSTNAME = 'localhost'
PORT = 35495 
lock = locks.Lock()


def get_handlers(db):
    ''' Returns handler array with required arguments '''
    here = os.path.abspath(os.path.dirname(__file__))
    path_to_build = here + "/../build/"
    return [
        (r"/builder/edits", EntityEditHandler, {'dbpath': db}),
        (r"/builder/edits/([0-9]+)/accept/([a-zA-Z_]+)", AcceptEditHandler, {'dbpath': db}),
        (r"/builder/edits/([0-9]+)/reject", RejectEditHandler, {'dbpath': db}),
        (r"/builder/edits/([0-9]+)", ViewEditWithIDHandler, {'dbpath': db}),
        (r"/builder/edges", EdgesHandler, {'dbpath': db}),
        (r"/builder/entities/([0-9]+)", ViewEntityWithIDHandler, {'dbpath': db}),
        (r"/builder/entities/([a-zA-Z_]+)", EntityHandler, {'dbpath': db}),
        (r"/builder/entities/([a-zA-Z_]+)/fields", EntityFieldsHandler, {'dbpath': db}),
        (r"/builder/interactions", InteractionHandler, {'dbpath': db}),
        (r"/builder/tables/types", TypesHandler, {'dbpath': db}),
        (r"/builder/", MainHandler),
        (r"/builder/(.*)", StaticDataUIHandler, {'path': path_to_build}),
        (r"/(.*)", StaticDataUIHandler, {'path': path_to_build}),
    ]

def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)

tornado_settings = {
    "autoescape": None,
    "cookie_secret": "0123456789", #TODO: Placeholder, do not include in repo when deploy!!!
    "compiled_template_cache": False,
    "login_url": "/login",
    "template_path": get_path('static'),
}

class BuildApplication(tornado.web.Application):
    def __init__(self, handlers):
        handlers = handlers
        super(BuildApplication, self).__init__(handlers, **tornado_settings)


class AppException(tornado.web.HTTPError):
    '''Used to return custom errors'''
    pass

# StaticUIHandler serves static front end, defaulting to builder_index.html served
# if the file is unspecified.
class StaticDataUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + 'builder_index.html'
        return url_path

class BaseHandler(tornado.web.RequestHandler):
    def options(self, *args, **kwargs):
        pass

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(
                json.dumps(
                    {
                        'error': {
                            'code': status_code,
                            'message': self._reason,
                            'traceback': lines,
                        }
                    }
                )
            )
        else:
            self.finish(
                json.dumps({'error': {'code': status_code, 'message': self._reason}})
            )

class MainHandler(BaseHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'text/html')


    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        here = os.path.abspath(os.path.dirname(__file__))
        self.render(here + "/../build/builderindex.html")
        
class EntityEditHandler(BaseHandler):
    ''' Submit edits through post request and view edits through get request '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    @gen.coroutine
    def post(self):
        with (yield lock.acquire()):
            with LIGHTDatabase(self.dbpath) as db:
                id = int(self.get_argument('id'))
                field = self.get_argument('field')
                edited_value = self.get_argument('edited_value')
                player = int(self.get_argument('player'))
                edit_id = db.submit_edit(id, field, edited_value, player)
                # return status 201 when new instance is created
                if db.get_edit(edit_id):
                    self.set_status(201)
                self.write(json.dumps({'edit_id': edit_id}))

    def get(self):
        with LIGHTDatabase(self.dbpath) as db:
            id = self.get_argument("id", None, True)
            status = self.get_argument("status", None, True)
            player = self.get_argument("player", None, True)
            expand = self.get_argument("expand", False, True)
            edits = db.get_edit(id=id, player_id=player, status=status)
            ids = [i[0] for i in edits]
            ids_expanded = [db.view_edit(i) for i in ids]
            if expand:
                self.write(json.dumps(ids_expanded))
            else:
                self.write(json.dumps(ids))


class AcceptEditHandler(BaseHandler):
    ''' Accept edit with given edit_id and accept_type '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    @gen.coroutine
    def post(self, edit_id, accept_type):
        with (yield lock.acquire()):
            with LIGHTDatabase(self.dbpath) as db:
                db.accept_edit(edit_id, accept_type)
                id = db.get_edit(edit_id=edit_id)[0][1]
        self.write(json.dumps({'id': id}))


class RejectEditHandler(BaseHandler):
    ''' Reject edit with given edit_id '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    @gen.coroutine
    def post(self, edit_id):
        with (yield lock.acquire()):
            with LIGHTDatabase(self.dbpath) as db:
                db.reject_edit(edit_id)
                id = db.get_edit(edit_id=edit_id)[0][1]
        self.write(json.dumps({'id': id}))


class ViewEditWithIDHandler(BaseHandler):
    ''' View edit with given edit_id; returns json '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self, edit_id):
        with LIGHTDatabase(self.dbpath) as db:
            self.write(json.dumps(db.view_edit(edit_id)))


class ViewEntityWithIDHandler(BaseHandler):
    ''' View entity with given id; returns json '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self, id):
        with LIGHTDatabase(self.dbpath) as db:
            entity = db.get_query(id)
            type = db.get_table_name(id, return_type=True)
            columns = db.get_columns(type)
            self.write(json.dumps({
                'entity': dict(zip(columns, entity)),
                'type': type
            }))


class EntityHandler(BaseHandler):
    '''
    'Type' is specified in the URL because it's mandatory
    GET returns results that match user's search string. expand=True returns
    all information about the entities and expand=False only returns IDs
    POST creates new entities. Depending on the type of entity being created,
    the body of the post request should have all the necessary fields for that
    entity. Call entity/{type}/fields to retrieve the list of fields.
    '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    @tornado.web.authenticated
    def get(self, type):
        type = type.replace('_', ' ')
        error = False
        with LIGHTDatabase(self.dbpath) as db:
            if type not in list(db.table_dict.keys()):
                raise AppException(reason='Type is not valid. ', status_code=400)
            columns = db.get_columns(type)
        search = self.get_argument('search', '', True)
        expand = self.get_argument('expand', True, True)
        page = self.get_argument('page', False, True)
        per_page = self.get_argument('per_page', 30, True)
        with LIGHTDatabase(self.dbpath) as db:
            results = db.search_database(type, search)
        ids = [i[0] for i in results]
        results_json = []
        for r in results:
            results_json.append(dict(zip(columns, r)))
        if page:
            total = len(results_json)
            results_json = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": int((total + int(per_page) - 1) / per_page),
                "data": results_json[int(page) * int(per_page): int(page) * int(per_page) + int(per_page)]
            }
        if expand:
            self.write(json.dumps(results_json))
        else:
            self.write(json.dumps(ids))

    @gen.coroutine
    def post(self, type):
        with (yield lock.acquire()):
            type = type.replace('_', ' ')
            # get the column names and types
            with LIGHTDatabase(self.dbpath) as db:
                fields = db.get_columns(type)
                target_func = eval('db.create_' + type.replace(' ', '_'))
            parameters = []
            kwargs = {}
            argspec = inspect.getfullargspec(target_func)
            default_args = argspec.defaults
            arg_names = argspec.args
            kw_args = arg_names[-len(default_args) :]
            kw_default_map = {kw_args[i]: default_args[i] for i in range(len(kw_args))}
            print(kw_default_map)
            for i in list(fields.keys()):
                # ignore the ID field since the ID is created by the database
                if i == 'id':
                    continue
                if i in kw_default_map:
                    if fields[i] == 'integer':
                        kwargs[i] = int(self.get_argument(i, kw_default_map.get(i)))
                    else:
                        kwargs[i] = self.get_argument(i, kw_default_map.get(i))
                else:
                    if fields[i] == 'integer':
                        parameters.append(
                            int(self.get_argument(i, kw_default_map.get(i)))
                        )
                    else:
                        parameters.append(self.get_argument(i, kw_default_map.get(i)))
            with LIGHTDatabase(self.dbpath) as db:
                # calls db.create_{type}({parameters})
                # for example, db.create_base_object('name')
                target_func = eval('db.create_' + type.replace(' ', '_'))
                id = target_func(*parameters, **kwargs)
                # return (id, boolean) where boolean is whether the attempted
                # insert is unique
                self.write(json.dumps(id))


class EntityFieldsHandler(BaseHandler):
    '''
    Given the type of entity, return all its fields in a dictionary where the
    keys are the column names and the values are the types of values they store
    '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self, type):
        type = type.replace('_', ' ')
        error = False
        with LIGHTDatabase(self.dbpath) as db:
            if type not in list(db.table_dict.keys()):
                self.set_status(400)
                error = True
            else:
                fields = db.get_columns(type)
        if not error:
            self.write(json.dumps(fields))


class InteractionHandler(BaseHandler):
    '''
    Adds/retrieves interactions
    '''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self):
        interaction_id = self.get_argument('interaction_id')
        with LIGHTDatabase(self.dbpath) as db:
            participants = db.get_participant(interaction_id=interaction_id)
            turns = db.get_turn(interaction_id=interaction_id)
            room = db.get_interaction(id=interaction_id)[0][1]
        participant_columns = ['ID', 'interaction_id', 'character_id', 'player_id']
        turn_columns = [
            'ID',
            'interaction_id',
            'turn_number',
            'turn_time',
            'interaction_type',
            'utterance_id',
            'action',
            'speaker_id',
            'listener_id',
            'participants_lst',
        ]
        participants_lst = []
        turns_lst = []
        for p in participants:
            participants_lst.append(dict(zip(participant_columns, p)))
        for t in turns:
            turns_lst.append(dict(zip(turn_columns, t)))
        self.write(
            json.dumps(
                {'room': room, 'participants': participants_lst, 'turns': turns_lst}
            )
        )

    @gen.coroutine
    def post(self):
        room = int(self.get_argument('room'))
        participants = json.loads(self.get_argument('participants'))
        turns = json.loads(self.get_argument('turns'))
        with (yield lock.acquire()):
            with LIGHTDatabase(self.dbpath) as db:
                interaction_id = db.add_single_conversation(room, participants, turns)
        self.write(json.dumps(interaction_id))


class TypesHandler(BaseHandler):
    '''Returns a list of the types of entities in the database'''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self):
        with LIGHTDatabase(self.dbpath) as db:
            self.write(json.dumps(list(db.table_dict.keys())))


class EdgesHandler(BaseHandler):
    '''Create edges between entities'''

    def initialize(self, dbpath):
        self.dbpath = dbpath

    def get(self):
        room = int(self.get_argument('room'))
        with LIGHTDatabase(self.dbpath) as db:
            potential_entities = db.find_database_entities_in_rooms(room)
            self.write(json.dumps(potential_entities))

    def post(self):
        '''displays/creates edges'''
        with LIGHTDatabase(self.dbpath) as db:
            room = int(self.get_argument('room'))
            objs = json.loads(self.get_argument('objs', '[]', True))
            chars = json.loads(self.get_argument('chars', '[]', True))
            neighbors = json.loads(self.get_argument('neighbors', '[]', True))

            # convert to boolean
            dry_run = eval(self.get_argument('dry_run', 'False', 'True'))
            edges = db.create_edges(room, chars, objs, neighbors, dry_run)
            ids = [i[0] for i in edges]
            edges_json = json.dumps(edges)
            self.write(json.dumps(edges))


def main():
    assert sys.argv[1][-3:] == '.db', 'Please enter a database path'
    app = BuildApplication(get_handlers(sys.argv[1]))
    app.listen(PORT)
    print(f'You can connect to http://{HOSTNAME}:{PORT}/builder')
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
