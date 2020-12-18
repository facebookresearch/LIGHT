#!/usr/bin/env python3
import json
import os
import sys
import ast
import inspect
import time
import tornado.web
from tornado.ioloop import IOLoop
from tornado import locks
from tornado import gen
from light.data_model.light_database import LIGHTDatabase
from light.graph.builders.starspace_all import StarspaceBuilder

DEFAULT_HOSTNAME = "localhost"
DEFAULT_PORT = 35495
lock = locks.Lock()


def get_handlers(db):
    """ Returns handler array with required arguments """
    here = os.path.abspath(os.path.dirname(__file__))
    path_to_build = here + "/../build/"
    # NOTE: We choose to keep the StaticUIHandler, despite this handler never being
    #       hit in the top level RuleRouter from run_server.py in case this application
    #       is run standalone for some reason.
    return [
        (r"/builder/edits", EntityEditHandler, {"database": db}),
        (
            r"/builder/edits/([0-9]+)/accept/([a-zA-Z_]+)",
            AcceptEditHandler,
            {"database": db},
        ),
        (r"/builder/edits/([0-9]+)/reject", RejectEditHandler, {"database": db}),
        (r"/builder/edits/([0-9]+)", ViewEditWithIDHandler, {"database": db}),
        (r"/builder/entities/([0-9]+)", ViewEntityWithIDHandler, {"database": db}),
        (r"/builder/suggestions/([a-zA-Z_]+)/([0-9]+)", SuggestionHandler, {"database": db}),
        (r"/builder/entities/([a-zA-Z_]+)", EntityHandler, {"database": db}),
        (
            r"/builder/entities/([a-zA-Z_]+)/fields",
            EntityFieldsHandler,
            {"database": db},
        ),
        (r"/builder/interactions", InteractionHandler, {"database": db}),
        (r"/builder/tables/types", TypesHandler, {"database": db}),
        (r"/builder/world/", SaveWorldHandler, {"database": db}),
        (r"/builder/world/autosave/", AutosaveHandler, {"database": db}),
        (r"/builder/world/([0-9]+)", LoadWorldHandler, {"database": db}),
        (r"/builder/world/delete/([0-9]+)", DeleteWorldHandler, {"database": db}),
        (r"/builder/worlds/", ListWorldsHandler, {"database": db}),
        (r"/builder/", MainHandler),
        (r"/builder(.*)", StaticDataUIHandler, {"path": path_to_build}),
        (r"/(.*)", StaticDataUIHandler, {"path": path_to_build}),
    ]


builder = None
def get_builder(database):
    global builder
    if builder is None:
        builder = StarspaceBuilder(
            database, debug=False
        )
    return builder

def get_path(filename):
    """Get the path to an asset."""
    cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    return os.path.join(cwd, filename)


class BuildApplication(tornado.web.Application):
    def __init__(self, handlers, tornado_settings):
        handlers = handlers
        super(BuildApplication, self).__init__(handlers, **tornado_settings)


class AppException(tornado.web.HTTPError):
    """Used to return custom errors"""

    pass


# StaticUIHandler serves static front end, defaulting to builderindex.html served
# if the file is unspecified.
class StaticDataUIHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith("/") or url_path == "":
            url_path = url_path + "builderindex.html"
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
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Acces-Control-Allow-Credentials", "true")
        self.set_header("Content-Type", "*")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(
                json.dumps(
                    {
                        "error": {
                            "code": status_code,
                            "message": self._reason,
                            "traceback": lines,
                        }
                    }
                )
            )
        else:
            self.finish(
                json.dumps({"error": {"code": status_code, "message": self._reason}})
            )


class MainHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Acces-Control-Allow-Credentials", "true")
        self.set_header("Content-Type", "text/html")

    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        here = os.path.abspath(os.path.dirname(__file__))
        self.render(here + "/../build/builderindex.html")


# -------------WorldBuilder Endpoints for World Saving ------------#
class ListWorldsHandler(BaseHandler):
    """Lists the worlds owned by the user"""

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self):
        username = tornado.escape.xhtml_escape(self.current_user)
        with self.db as ldb:
            player = ldb.get_user_id(username)
            worlds = ldb.view_worlds(player_id=player)
            autosave = ldb.get_autosave(player)
        if autosave is not None:
            dat = {"auto": autosave["timestamp"], "data": worlds}
        else:
            dat = {"auto": None, "data": worlds}
        self.write(json.dumps(dat))


class DeleteWorldHandler(BaseHandler):
    """Deletes a world given the user and world id"""

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, id):
        username = tornado.escape.xhtml_escape(self.current_user)
        with (yield lock.acquire()):
            with self.db as ldb:
                player = ldb.get_user_id(username)
                ldb.set_world_inactive(world_id=id, player_id=player)
        self.write(json.dumps(id))


class AutosaveHandler(BaseHandler):
    """Save a world given the player id and world id"""

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        world_dict = json.loads(self.get_argument("data", None))
        curr_time = time.ctime(time.time())
        username = tornado.escape.xhtml_escape(self.current_user)
        with (yield lock.acquire()):
            with self.db as ldb:
                player = ldb.get_user_id(username)
                ldb.set_autosave(json.dumps(world_dict), player, curr_time)
        self.set_status(201)

    @tornado.web.authenticated
    def get(self):
        username = tornado.escape.xhtml_escape(self.current_user)
        with self.db as ldb:
            player = ldb.get_user_id(username)
            world_dump = ldb.get_autosave(player)["world_dump"]
        self.set_status(200)
        self.write(world_dump)


class SaveWorldHandler(BaseHandler):
    """Save a world given the player id and world id"""

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        username = tornado.escape.xhtml_escape(self.current_user)
        dimensions = json.loads(
            self.get_argument(
                "dimensions",
                '{"id": null, "name": null, "height": 3, "width": 3, "floors": 1}',
            )
        )
        world_map = json.loads(self.get_argument("map", '{"tiles": {}, "edges": []}'))
        entities = json.loads(
            self.get_argument("entities", '{"room": {}, "character": {}, "object": {}}')
        )

        name = dimensions["name"]
        if name is None:
            name = "Default " + time.ctime(time.time())
        name = name.strip()

        with (yield lock.acquire()):
            with self.db as ldb:
                player = ldb.get_user_id(username)
                if dimensions["id"] is not None:
                    ldb.set_world_inactive(dimensions["id"], player)
                world_id = ldb.create_world(
                    name,
                    player,
                    dimensions["height"],
                    dimensions["width"],
                    dimensions["floors"],
                )[0]
                # Get DB IDs for all object and store them
                local_id_to_dbid = {}
                for local_id, room in entities["room"].items():
                    room_id = ldb.create_room(
                        room["name"],
                        room["base_id"],
                        room["description"],
                        room["backstory"],
                    )
                    local_id_to_dbid[local_id] = room_id[0]

                for local_id, char in entities["character"].items():
                    char_id = ldb.create_character(
                        char["name"],
                        char["base_id"],
                        char["persona"],
                        char["physical_description"],
                        name_prefix=char["name_prefix"],
                        is_plural=char["is_plural"],
                        char_type=char["char_type"],
                    )
                    local_id_to_dbid[local_id] = char_id[0]

                for local_id, obj in entities["object"].items():
                    obj_id = ldb.create_object(
                        obj["name"],
                        obj["base_id"],
                        obj["is_container"],
                        obj["is_drink"],
                        obj["is_food"],
                        obj["is_gettable"],
                        obj["is_surface"],
                        obj["is_wearable"],
                        obj["is_weapon"],
                        obj["physical_description"],
                        name_prefix=obj["name_prefix"],
                        is_plural=obj["is_plural"],
                    )
                    local_id_to_dbid[local_id] = obj_id[0]

                # Now, go through all the entities and make graph nodes for them, storing a map from the id to the graph id
                dbid_to_nodeid = {}
                for dbid in local_id_to_dbid.values():
                    node_id = ldb.create_graph_node(world_id, dbid)
                    dbid_to_nodeid[dbid] = node_id[0]

                # Make the edges!
                for edge in world_map["edges"]:
                    src_node = dbid_to_nodeid[local_id_to_dbid[str(edge["src"])]]
                    dst_node = dbid_to_nodeid[local_id_to_dbid[str(edge["dst"])]]
                    ldb.create_graph_edge(world_id, src_node, dst_node, edge["type"])

                # Make the tiles!
                for tile in world_map["tiles"]:
                    ldb.create_tile(
                        world_id,
                        dbid_to_nodeid[local_id_to_dbid[str(tile["room"])]],
                        tile["color"],
                        tile["x_coordinate"],
                        tile["y_coordinate"],
                        tile["floor"],
                    )

            # Now return to the user we did all of it!
            self.set_status(201)
            self.write(json.dumps(world_id))


class LoadWorldHandler(BaseHandler):
    """Load a world given the id"""

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self, world_id):
        result = {}
        username = tornado.escape.xhtml_escape(self.current_user)
        with self.db as ldb:
            player_id = ldb.get_user_id(username)

            # Load the world info (dimensions, name, id) and store in "dimensions"
            world = ldb.get_world(world_id, player_id)
            assert len(world) == 1, "Must get a single world back to load it"
            resources = ldb.get_world_resources(world_id, player_id)

        world = world[0]
        result["dimensions"] = {
            x: world[x] for x in world.keys() if x != "owner_id" and x != "in_use"
        }
        result["dimensions"]["floors"] = result["dimensions"]["num_floors"]
        del result["dimensions"]["num_floors"]

        tiles = resources[0]
        tile_list = [
            {x: tile[x] for x in tile.keys() if x != "world_id"} for tile in tiles
        ]
        edges = resources[1]
        edge_list = [{x: edge[x] for x in edge.keys()} for edge in edges]

        # Load the entities
        nextID = 1
        entities = {
            "room": {},
            "character": {},
            "object": {},
        }
        node_to_local_id = {}
        type_to_entities = {
            "room": resources[2],
            "character": resources[3],
            "object": resources[4],
        }
        for type_ in type_to_entities.keys():
            for entity in type_to_entities[type_]:
                entities[type_][nextID] = {key: entity[key] for key in entity.keys()}
                node_to_local_id[entity["id"]] = nextID

                # Modify entires to fit format
                del entities[type_][nextID]["w_id"]
                entities[type_][nextID]["id"] = entities[type_][nextID]["entity_id"]
                del entities[type_][nextID]["entity_id"]
                nextID += 1
        entities["nextID"] = nextID
        result["entities"] = entities

        # Load the edges and tiles
        for tile in tile_list:
            tile["room"] = node_to_local_id[tile["room_node_id"]]
            del tile["id"]
            del tile["room_node_id"]
        edges = []
        for edge in edge_list:
            src = node_to_local_id[edge["src_id"]]
            dst = node_to_local_id[edge["dst_id"]]
            edges.append({"src": src, "dst": dst, "type": edge["edge_type"]})
        result["map"] = {"tiles": tile_list, "edges": edges}

        # Return data
        self.write(json.dumps(result))


# -------------------------------------------------------------#


class EntityEditHandler(BaseHandler):
    """ Submit edits through post request and view edits through get request """

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        id = int(self.get_argument("id"))
        field = self.get_argument("field")
        edited_value = self.get_argument("edited_value")
        player = int(self.get_argument("player"))
        with (yield lock.acquire()):
            with self.db as ldb:
                edit_id = ldb.submit_edit(id, field, edited_value, player)
                # return status 201 when new instance is created
                if ldb.get_edit(edit_id):
                    self.set_status(201)
                self.write(json.dumps({"edit_id": edit_id}))

    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None, True)
        status = self.get_argument("status", None, True)
        player = self.get_argument("player", None, True)
        expand = self.get_argument("expand", False, True)
        with self.db as ldb:
            edits = ldb.get_edit(id=id, player_id=player, status=status)
            ids = [i[0] for i in edits]
            ids_expanded = [ldb.view_edit(i) for i in ids]
        if expand:
            self.write(json.dumps(ids_expanded))
        else:
            self.write(json.dumps(ids))


class AcceptEditHandler(BaseHandler):
    """ Accept edit with given edit_id and accept_type """

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    def post(self, edit_id, accept_type):
        with (yield lock.acquire()):
            with self.db as ldb:
                ldb.accept_edit(edit_id, accept_type)
                id = ldb.get_edit(edit_id=edit_id)[0][1]
        self.write(json.dumps({"id": id}))


class RejectEditHandler(BaseHandler):
    """ Reject edit with given edit_id """

    def initialize(self, database):
        self.db = database

    @gen.coroutine
    def post(self, edit_id):
        with (yield lock.acquire()):
            with self.db as ldb:
                ldb.reject_edit(edit_id)
                id = ldb.get_edit(edit_id=edit_id)[0][1]
        self.write(json.dumps({"id": id}))


class ViewEditWithIDHandler(BaseHandler):
    """ View edit with given edit_id; returns json """

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self, edit_id):
        with self.db as ldb:
            self.write(json.dumps(ldb.view_edit(edit_id)))


class ViewEntityWithIDHandler(BaseHandler):
    """ View entity with given id; returns json """

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self, id):
        with self.db as ldb:
            entity = ldb.get_query(id)
            type = ldb.get_table_name(id, return_type=True)
            columns = ldb.get_columns(type)
        self.write(json.dumps({"entity": dict(zip(columns, entity)), "type": type}))


class EntityHandler(BaseHandler):
    """
    'Type' is specified in the URL because it's mandatory
    GET returns results that match user's search string. expand=True returns
    all information about the entities and expand=False only returns IDs
    POST creates new entities. Depending on the type of entity being created,
    the body of the post request should have all the necessary fields for that
    entity. Call entity/{type}/fields to retrieve the list of fields.
    """

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self, type):
        type = type.replace("_", " ")
        error = False
        with self.db as ldb:
            if type not in list(ldb.table_dict.keys()):
                raise AppException(reason="Type is not valid. ", status_code=400)
            columns = ldb.get_columns(type)
        search = self.get_argument("search", "", True)
        expand = self.get_argument("expand", True, True)
        page = self.get_argument("page", False, True)
        per_page = self.get_argument("per_page", 30, True)
        with self.db as ldb:
            results = ldb.search_database(type, search)
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
                "data": results_json[
                    int(page) * int(per_page) : int(page) * int(per_page)
                    + int(per_page)
                ],
            }
        if expand:
            self.write(json.dumps(results_json))
        else:
            self.write(json.dumps(ids))

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, type):
        with (yield lock.acquire()):
            with self.db as ldb:
                type = type.replace("_", " ")
                # get the column names and types
                fields = ldb.get_columns(type)
                target_func = eval("ldb.create_" + type.replace(" ", "_"))
                parameters = []
                kwargs = {}
                argspec = inspect.getfullargspec(target_func)
                default_args = argspec.defaults
                arg_names = argspec.args
                kw_args = arg_names[-len(default_args) :]
                kw_default_map = {
                    kw_args[i]: default_args[i] for i in range(len(kw_args))
                }
                print(kw_default_map)
                for i in list(fields.keys()):
                    # ignore the ID field since the ID is created by the database
                    if i == "id":
                        continue
                    if i in kw_default_map:
                        if fields[i] == "integer":
                            kwargs[i] = int(self.get_argument(i, kw_default_map.get(i)))
                        else:
                            kwargs[i] = self.get_argument(i, kw_default_map.get(i))
                    else:
                        if fields[i] == "integer":
                            parameters.append(
                                int(self.get_argument(i, kw_default_map.get(i)))
                            )
                        else:
                            parameters.append(
                                self.get_argument(i, kw_default_map.get(i))
                            )
                    # calls db.create_{type}({parameters})
                    # for example, db.create_base_object('name')
                target_func = eval("ldb.create_" + type.replace(" ", "_"))
                id = target_func(*parameters, **kwargs)
                # return (id, boolean) where boolean is whether the attempted
                # insert is unique
            self.write(json.dumps(id))


class EntityFieldsHandler(BaseHandler):
    """
    Given the type of entity, return all its fields in a dictionary where the
    keys are the column names and the values are the types of values they store
    """

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self, type):
        type = type.replace("_", " ")
        error = False
        with self.db as ldb:
            if type not in list(ldb.table_dict.keys()):
                self.set_status(400)
                error = True
            else:
                fields = ldb.get_columns(type)
        if not error:
            self.write(json.dumps(fields))


class SuggestionHandler(BaseHandler):
    """
    Given a type of entity and a related thing to query from, get model
    suggestions for that entity
    """
    def initialize(self, database):
        self.db = database
        self.builder = get_builder(database)

    @tornado.web.authenticated
    def get(self, type, source):
        if type not in ['room', 'object', 'character']:
            raise AppException(reason="Type is not valid. ", status_code=400)
        with self.db as ldb:
            source_objs = ldb.get_id(id=source)
        if len(source_objs) == 0:
            self.write(json.dumps([]))
            return
        source_obj = source_objs[0]
        if type == 'room':
            items = builder.get_neighbor_rooms(source_obj['id'])
        elif type == "object":
            items = builder.get_contained_items(source_obj['id'], source_obj['type'])
        elif type == "character":
            items = builder.get_contained_characters(source_obj['id'])
        with self.db as ldb:
            result_items = [dict(ldb.get_id(id=x.db_id, expand=True)[0]) for x in items]
        self.write(json.dumps(result_items))


class InteractionHandler(BaseHandler):
    """
    Adds/retrieves interactions
    """

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self):
        interaction_id = self.get_argument("interaction_id")
        with self.db as ldb:
            participants = ldb.get_participant(interaction_id=interaction_id)
            turns = ldb.get_turn(interaction_id=interaction_id)
            room = ldb.get_interaction(id=interaction_id)[0][1]
        participant_columns = ["ID", "interaction_id", "character_id", "player_id"]
        turn_columns = [
            "ID",
            "interaction_id",
            "turn_number",
            "turn_time",
            "interaction_type",
            "utterance_id",
            "action",
            "speaker_id",
            "listener_id",
            "participants_lst",
        ]
        participants_lst = []
        turns_lst = []
        for p in participants:
            participants_lst.append(dict(zip(participant_columns, p)))
        for t in turns:
            turns_lst.append(dict(zip(turn_columns, t)))
        self.write(
            json.dumps(
                {"room": room, "participants": participants_lst, "turns": turns_lst}
            )
        )

    @gen.coroutine
    @tornado.web.authenticated
    def post(self):
        room = int(self.get_argument("room"))
        participants = json.loads(self.get_argument("participants"))
        turns = json.loads(self.get_argument("turns"))
        with (yield lock.acquire()):
            with self.db as ldb:
                interaction_id = ldb.add_single_conversation(room, participants, turns)
        self.write(json.dumps(interaction_id))


class TypesHandler(BaseHandler):
    """Returns a list of the types of entities in the database"""

    def initialize(self, database):
        self.db = database

    @tornado.web.authenticated
    def get(self):
        with self.db as ldb:
            self.write(json.dumps(list(ldb.table_dict.keys())))


def main():
    assert sys.argv[1][-3:] == ".db", "Please enter a database path"
    ldb = LIGHTDatabase(sys.argv[1])
    app = BuildApplication(get_handlers(ldb))
    app.listen(DEFAULT_PORT)
    print(f"You can connect to http://{DEFAULT_HOSTNAME}:{DEFAULT_PORT}/builder")
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
