#!/usr/bin/env python3
import unittest.mock as mock
import json
import re
import os
import ast
import asyncio
from tornado import gen, httpclient, ioloop, testing, escape
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.ioloop import IOLoop
import shutil, tempfile
import unittest
import os
import urllib
from urllib import parse
from light.data_model.light_database import (
    LIGHTDatabase,
    DB_EDGE_IN_CONTAINED,
    DB_EDGE_EX_CONTAINED,
    DB_EDGE_WORN,
    DB_EDGE_WIELDED,
    DB_EDGE_NEIGHBOR,
    EDGE_TYPES,
    DB_TYPE_BASE_CHAR,
    DB_TYPE_CHAR,
    DB_TYPE_BASE_OBJ,
    DB_TYPE_OBJ,
    DB_TYPE_BASE_ROOM,
    DB_TYPE_ROOM,
    DB_TYPE_GRAPH_EDGE,
    DB_TYPE_GRAPH_NODE,
    DB_TYPE_EDGE,
    DB_TYPE_TEXT_EDGE,
    DB_TYPE_TILE,
    DB_TYPE_INTERACTION,
    DB_TYPE_UTTERANCE,
    DB_TYPE_PARTICIPANT,
    DB_TYPE_TURN,
    DB_TYPE_PLAYER,
    DB_TYPE_WORLD,
    ENTITY_TYPES,
    DB_STATUS_PROD,
    DB_STATUS_REVIEW,
    DB_STATUS_REJECTED,
    DB_STATUS_QUESTIONABLE,
    DB_STATUS_ACCEPTED,
    DB_STATUS_ACCEPT_ONE,
    DB_STATUS_ACCEPT_ALL,
    CONTENT_STATUSES,
    EDIT_STATUSES,
)
from deploy.web.server.tests.config import TEST_TORNADO_SETTINGS
from deploy.web.server.builder_server import (
    BuildApplication,
    get_handlers,
)
from deploy.web.server.tornado_server import (
    LandingApplication,
    Application,
)
from deploy.web.server.registry import RegistryApplication

PORT = 35494
URL = f"http://localhost:{PORT}"


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


class MockFlags:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port


@mock.patch(
    "deploy.web.server.registry.BaseHandler.get_current_user", return_value="user"
)
@mock.patch("light.graph.builders.starspace_all.StarspaceBuilder")
class TestRegistryApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        # Need to fix this somehow...
        self.db_path = os.path.join(self.data_dir, "test_server.db")
        self.db = LIGHTDatabase(self.db_path)
        self.FLAGS = MockFlags("localhost", PORT)
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = RegistryApplication(
            self.FLAGS, self.db, {}, tornado_settings=TEST_TORNADO_SETTINGS
        )
        app.listen(PORT)
        return app

    @gen_test
    def test_game_socket(self, mocked_auth, MockStarSpace):
        """Test that we connect to socket by default"""
        headers = {"Connection": "Upgrade", "Upgrade": "websocket"}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/game/socket",
                method="GET",
                headers=headers,
            )
        # Need to upgrade in response
        self.assertEqual(cm.exception.code, 426)

    @mock.patch(
        "deploy.web.server.registry.RegistryApplication.run_new_game",
        return_value=async_return("test"),
    )
    @gen_test
    def test_new_game(self, mocked_auth, MockStarSpace, mocked_method):
        """Test that we can post to create a new game"""
        response = yield self.client.fetch(
            f"{URL}/game/new/01",
            method="POST",
            body=b"test",
        )
        self.assertEqual(response.code, 201)


@mock.patch(
    "deploy.web.server.builder_server.BaseHandler.get_current_user", return_value="test"
)
class TestWorldSaving(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, "test_server.db")
        self.db = LIGHTDatabase(self.db_path)
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = BuildApplication(
            get_handlers(self.db), tornado_settings=TEST_TORNADO_SETTINGS
        )
        app.listen(PORT)
        return app

    @gen_test
    def test_list_worlds(self, mocked_auth):
        """Test that the list worlds endpoint can be hit succesfully and returns world
        dimesnions in expected format"""
        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
            world1 = db.create_world("default", player_id, 3, 3, 1)[0]
            world2 = db.create_world("default2", player_id, 4, 2, 2)[0]

        response = yield self.client.fetch(
            f"{URL}/builder/worlds/",
            method="GET",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "auto": None,
                "data": [
                    {
                        "height": 3,
                        "id": world1,
                        "in_use": 1,
                        "name": "default",
                        "num_floors": 1,
                        "owner_id": player_id,
                        "width": 3,
                    },
                    {
                        "height": 4,
                        "id": world2,
                        "in_use": 1,
                        "name": "default2",
                        "num_floors": 2,
                        "owner_id": player_id,
                        "width": 2,
                    },
                ],
            },
        )

    @gen_test
    def test_delete_world(self, mocked_auth):
        """Test the endpoint for deleting worlds works as expected"""
        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
            world1 = db.create_world("default", player_id, 3, 3, 1)[0]
            world2 = db.create_world("default2", player_id, 4, 2, 2)[0]

        response = yield self.client.fetch(
            f"{URL}/builder/world/delete/{world1}",
            method="DELETE",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), str(world1))

    @gen_test
    def test_save_world(self, mocked_auth):
        """Test the endpoint for saving worlds works as expected"""
        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = yield self.client.fetch(
            f"{URL}/builder/world/", method="POST", headers=headers, body=b""
        )
        self.assertEqual(response.code, 201)
        # Get back a world code,
        self.assertEqual(type(json.loads(response.body.decode())), int)

    @gen_test
    def test_autosave_endpoints(self, mocked_auth):
        """Test the endpoint for posting worlds works as expected, and loading back matches"""
        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
            d = {
                "data": {
                    "dimensions": {
                        "name": "default",
                        "height": 4,
                        "width": 1,
                        "floors": 1,
                    },
                    "entities": {
                        "room": {},
                        "character": {},
                        "object": {},
                        "nextID": 1,
                    },
                    "map": {"tiles": [], "edges": []},
                }
            }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = yield self.client.fetch(
            f"{URL}/builder/world/autosave/",
            method="POST",
            headers=headers,
            body=self.get_encoded_url_params(d),
        )
        self.assertEqual(response.code, 201)

        response = yield self.client.fetch(
            f"{URL}/builder/world/autosave/",
            method="GET",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), d["data"])

    @gen_test
    def test_load_world(self, mocked_auth):
        """Test the endpoint for loading worlds works as expected"""
        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
            world1 = db.create_world("default", player_id, 4, 1, 1)[0]
        response = yield self.client.fetch(
            f"{URL}/builder/world/{world1}", method="GET"
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "dimensions": {
                    "id": world1,
                    "name": "default",
                    "height": 4,
                    "width": 1,
                    "floors": 1,
                },
                "entities": {"room": {}, "character": {}, "object": {}, "nextID": 1},
                "map": {"tiles": [], "edges": []},
            },
        )

    @gen_test
    def test_world_saving_integration(self, mocked_auth):
        """Test a flow where a user creates a world, views the saved worlds, loads the world, then
        deletes it"""

        with LIGHTDatabase(self.db_path) as db:
            player_id = db.create_user("test")[0]
            base_room_id = db.create_base_room("room")[0]
            base_char_id = db.create_base_character("character")[0]
            base_obj_id = db.create_base_object("object")[0]
            rcontent_id1 = db.create_room("room1", base_room_id, "dirty", "old")[0]
            ccontent_id1 = db.create_character("troll", base_char_id, "tall", "big")[0]
            ocontent_id1 = db.create_object(
                "small obj", base_obj_id, 0, 0, 0, 0, 0, 0, 0, "dusty"
            )[0]
            d = {
                "dimensions": {
                    "id": None,
                    "name": "Test",
                    "height": 5,
                    "width": 5,
                    "floors": 2,
                },
                "entities": {
                    "room": {
                        "1": {
                            "id": rcontent_id1,
                            "name": "room1",
                            "base_id": base_room_id,
                            "description": "dirty",
                            "backstory": "old",
                        },
                        "2": {
                            "id": rcontent_id1,
                            "name": "room1",
                            "base_id": base_room_id,
                            "description": "dirty",
                            "backstory": "old",
                        },
                    },
                    "character": {
                        "3": {
                            "id": ccontent_id1,
                            "name": "troll",
                            "base_id": base_char_id,
                            "persona": "tall",
                            "physical_description": "big",
                            "name_prefix": "a",
                            "is_plural": 0,
                            "char_type": "unknown",
                        }
                    },
                    "object": {
                        "4": {
                            "id": ocontent_id1,
                            "name": "small obj",
                            "base_id": base_obj_id,
                            "is_container": 0,
                            "is_drink": 0,
                            "is_food": 0,
                            "is_gettable": 0,
                            "is_surface": 0,
                            "is_wearable": 0,
                            "is_weapon": 0,
                            "physical_description": "dusty",
                            "name_prefix": "a",
                            "is_plural": 0,
                            "size": None,
                            "contain_size": None,
                            "shape": None,
                            "value": None,
                        }
                    },
                    "nextID": 5,
                },
                "map": {
                    "tiles": [
                        {
                            "room": 1,
                            "color": "#8A9BA8",
                            "x_coordinate": 1,
                            "y_coordinate": 1,
                            "floor": 0,
                        },
                        {
                            "room": 2,
                            "color": "#8A9BA8",
                            "x_coordinate": 2,
                            "y_coordinate": 1,
                            "floor": 0,
                        },
                    ],
                    "edges": [
                        {"src": 1, "dst": 3, "type": "contains"},
                        {"src": 1, "dst": 4, "type": "contains"},
                        {"src": 1, "dst": 2, "type": "neighbors to the east"},
                        {"src": 2, "dst": 1, "type": "neighbors to the west"},
                    ],
                },
            }
        response = yield self.client.fetch(
            f"{URL}/builder/world/", method="POST", body=self.get_encoded_url_params(d)
        )
        self.assertEqual(response.code, 201)
        self.assertEqual(type(json.loads(response.body.decode())), int)
        w_id = json.loads(response.body.decode())

        # Test listing worlds here
        response = yield self.client.fetch(
            f"{URL}/builder/worlds/",
            method="GET",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "auto": None,
                "data": [
                    {
                        "height": 5,
                        "id": w_id,
                        "in_use": 1,
                        "name": "Test",
                        "num_floors": 2,
                        "owner_id": player_id,
                        "width": 5,
                    },
                ],
            },
        )

        # Test world loading - expect same format! (except differences in local ids, so check dimensions and tiles really)
        d["dimensions"]["id"] = w_id
        response = yield self.client.fetch(f"{URL}/builder/world/{w_id}", method="GET")
        self.assertEqual(response.code, 200)
        actual_dict = json.loads(response.body.decode())
        # Dimensions with updated world id should match exactly
        self.assertEqual(actual_dict["dimensions"], d["dimensions"])
        # Store id will not be the same, but values (and next ID) should be
        self.assertCountEqual(
            actual_dict["entities"]["room"].values(), d["entities"]["room"].values()
        )
        self.assertCountEqual(
            actual_dict["entities"]["character"].values(),
            d["entities"]["character"].values(),
        )
        self.maxDiff = None
        self.assertCountEqual(
            actual_dict["entities"]["object"].values(), d["entities"]["object"].values()
        )

        # Test deletion
        response = yield self.client.fetch(
            f"{URL}/builder/world/delete/{w_id}",
            method="DELETE",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), str(w_id))

        # List should now be empty
        response = yield self.client.fetch(
            f"{URL}/builder/worlds/",
            method="GET",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {"auto": None, "data": []},
        )

    def get_encoded_url_params(self, d):
        formBody = []
        for prop in d.keys():
            encodedKey = urllib.parse.quote(prop)
            encodedValue = urllib.parse.quote(
                json.dumps(d[prop], separators=(",", ":"))
                if (type(d[prop]) is dict or type(d[prop]) is list)
                else d[prop]
            )
            formBody.append(encodedKey + "=" + encodedValue)
        return "&".join(formBody)


@mock.patch(
    "deploy.web.server.tornado_server.BaseHandler.get_current_user", return_value="user"
)
class TestGameApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, "test_server.db")
        self.db = LIGHTDatabase(self.db_path)
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = Application(given_tornado_settings=TEST_TORNADO_SETTINGS)
        app.listen(PORT)
        return app

    @gen_test
    def test_game_page(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that no specific endpoint results in main game served when logged in"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_static_handler(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that index.html will be rendered from static handler correctly"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/index.html",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)


@mock.patch(
    "deploy.web.server.tornado_server.BaseHandler.get_current_user", return_value="user"
)
class TestLandingApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, "test_server.db")
        self.db = LIGHTDatabase(self.db_path)
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = LandingApplication(self.db, given_tornado_settings=TEST_TORNADO_SETTINGS)
        app.listen(PORT)
        return app

    @gen_test
    def test_static_handler(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that index.html will be rendered from static handler correctly"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/index.html",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_static_handler_nonexisting(self, mocked_auth):
        """Test the static handler 404 if resource not found"""
        headers = {
            "Content-Type": "application/json",
        }
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/something.html",
                method="GET",
                headers=headers,
            )
        self.assertEqual(cm.exception.code, 404)

    @gen_test
    def test_landing_page(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that no specific endpoint results in main page served when logged in"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_landing_page_redirect(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that redirect when not logged in"""
        mocked_auth.return_value = None
        headers = {"Content-Type": "application/json"}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/play/",
                method="GET",
                headers=headers,
                follow_redirects=False,
            )
        self.assertEqual(cm.exception.code, 302)
        self.assertEqual(
            cm.exception.response.headers["Location"], "/login?next=%2Fplay"
        )

    @gen_test
    def test_logout(self, mocked_auth):
        """Test that logout clears cookie and redirects"""
        headers = {"Content-Type": "application/json"}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/logout",
                method="GET",
                headers=headers,
                follow_redirects=False,
            )
        # 302 still bc we need to redirect
        self.assertEqual(cm.exception.code, 302)
        self.assertEqual(len(cm.exception.response.headers.get_list("Set-Cookie")), 1)
        # Clearing cookies, so should user should be empty string, then redirect to login
        result = re.search(
            'user="(.*)"(.*)', cm.exception.response.headers["Set-Cookie"]
        )
        self.assertEqual(len(result.group(1)), 0)
        self.assertEqual(cm.exception.response.headers["Location"], "/#/bye")

    @gen_test
    def test_login_succesful(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that login endpoint with correct password gives cookie, 200"""
        headers = {"Content-Type": "multipart/form-data; boundary=SomeRandomBoundary"}
        body = self.build_body()
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/login",
                method="POST",
                headers=headers,
                body=body,
                follow_redirects=False,
            )
            # 302 still bc we need to redirect
            self.assertEqual(cm.exception.code, 302)
        self.assertEqual(len(cm.exception.response.headers.get_list("Set-Cookie")), 1)
        response = yield self.client.fetch(
            f"{URL}/login",
            method="POST",
            headers=headers,
            body=body,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_login_endpoint(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that login endpoint responds with login page"""
        headers = {"Content-Type": "application/json"}
        response = yield self.client.fetch(
            f"{URL}/login",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/html; charset=UTF-8")

    @gen_test
    def test_login_password_protected(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that login does not work with wrong password"""
        headers = {"Content-Type": "multipart/form-data; boundary=SomeRandomBoundary"}
        body = self.build_body(password="dog")
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/login",
                method="POST",
                headers=headers,
                body=body,
                follow_redirects=False,
            )
        self.assertEqual(cm.exception.code, 302)

        # With allowing redirects, we expect to end up back at the login page
        response = yield self.client.fetch(
            f"{URL}/login",
            method="POST",
            headers=headers,
            body=body,
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/html; charset=UTF-8")

    def build_body(name="me", password="LetsPlay"):
        boundary = "SomeRandomBoundary"
        body = "--%s\r\n" % boundary

        # data for field1
        body += 'Content-Disposition: form-data; name="name"\r\n'
        body += "\r\n"  # blank line
        body += "%s\r\n" % name

        # separator boundary
        body += "--%s\r\n" % boundary

        # data for field2
        body += 'Content-Disposition: form-data; name="password"\r\n'
        body += "\r\n"  # blank line
        body += "%s\r\n" % password

        # separator boundary
        body += "--%s--\r\n" % boundary
        return body


@mock.patch(
    "deploy.web.server.builder_server.BaseHandler.get_current_user", return_value="user"
)
class TestBuilderApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, "test_server.db")
        self.db = LIGHTDatabase(self.db_path)
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = BuildApplication(
            get_handlers(self.db), tornado_settings=TEST_TORNADO_SETTINGS
        )
        app.listen(PORT)
        return app

    @gen_test
    def test_builder_page(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that no specific endpoint results in main builder page served when logged in"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/builder/",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_builder_page(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that static data serves landing correctly"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/builder/builderindex.html",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_builder_page(self, mocked_auth):
        self.skipTest("Middle of refactor")
        """Test that static data serves main builder page correctly"""
        headers = {
            "Content-Type": "application/json",
        }
        response = yield self.client.fetch(
            f"{URL}/",
            method="GET",
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_submit_entity_edits(self, mocked_auth):
        """Test that entity edits can be submitted successfully"""
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room("room")[0]
        headers = {"Content-Type": "application/json"}
        body = {
            "id": base_room,
            "field": "name",
            "edited_value": "name_edit_test",
            "player": player,
        }
        response = yield self.client.fetch(
            f"{URL}/builder/edits",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 201)
        response = yield self.client.fetch(
            f"{URL}/builder/edits/1",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "edit_id": 1,
                "id": base_room,
                "field": "name",
                "unedited_value": "room",
                "edited_value": "name_edit_test",
                "player_id": player,
                "status": DB_STATUS_REVIEW,
                "type": DB_TYPE_BASE_ROOM,
            },
        )

    @gen_test
    def test_submit_utterance_edits(self, mocked_auth):
        """Test that utterance edits can be submitted successfully"""
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room("room")[0]
            room = db.create_room("small room", base_room, "tiny", "old")[0]
            base_char = db.create_base_character("troll")[0]
            char = db.create_character(None, base_char, "tall", "big")[0]
            utterance1 = db.create_utterance("Hi")[0]
            utterance2 = db.create_utterance("Hello")[0]
            interaction = db.create_interaction(room)[0]
            participant = db.create_participant(interaction, char, player)[0]
            turn = db.create_turn(
                interaction, 0, 0, "speech", utterance1, None, participant, None
            )[0]
        headers = {"Content-Type": "application/json"}
        body = {
            "id": turn,
            "field": "utterance_id",
            "edited_value": "Hello",
            "player": player,
        }
        response = yield self.client.fetch(
            f"{URL}/builder/edits",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 201)
        self.assertEqual(json.loads(response.body.decode()), {"edit_id": 1})
        response = yield self.client.fetch(f"{URL}/builder/edits/1")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "edit_id": 1,
                "id": turn,
                "field": "utterance_id",
                "edited_value": "Hello",
                "characters": ["troll"],
                "player_id": player,
                "status": DB_STATUS_REVIEW,
                "type": "utterance",
                "turn_number": 0,
                "room": "small room",
                "utterances": ["Hi"],
            },
        )

    @gen_test
    def test_submit_edits_error(self, mocked_auth):
        """Test that missing arguments are detected"""
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
        headers = {"Content-Type": "application/json"}
        body = {"field": "name", "edited_value": "name_edit_test", "player": player}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/builder/edits",
                method="POST",
                headers=headers,
                body=urllib.parse.urlencode(body),
            )
        self.assertEqual(400, cm.exception.code)
        self.assertEqual(cm.exception.message, "Bad Request")

    @gen_test
    def test_reject_edits(self, mocked_auth):
        """Test that edits can be rejected successfully"""
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room("room")[0]
            # insert edit directly into the database and check if it's correct
            edit_id = db.submit_edit(base_room, "name", "name_edit_test", player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id)],
                [
                    (
                        1,
                        base_room,
                        "name",
                        "room",
                        "name_edit_test",
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
        response = yield self.client.fetch(
            f"{URL}/builder/edits/{edit_id}/reject", method="POST", body=b""
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), {"id": base_room})
        response = yield self.client.fetch(f"{URL}/builder/edits/1")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "edit_id": 1,
                "id": base_room,
                "field": "name",
                "unedited_value": "room",
                "edited_value": "name_edit_test",
                "player_id": player,
                "status": DB_STATUS_REJECTED,
                "type": DB_TYPE_BASE_ROOM,
            },
        )

    @gen_test
    def test_accept_edits(self, mocked_auth):
        """Test that edits can be accepted and enacted"""
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room("room")[0]
            # insert edit directly into the database and check if it's correct
            edit_id = db.submit_edit(base_room, "name", "name_edit_test", player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id)],
                [
                    (
                        1,
                        base_room,
                        "name",
                        "room",
                        "name_edit_test",
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
        accept_type = "accepted"
        response = yield self.client.fetch(
            f"{URL}/builder/edits/{edit_id}/accept/{accept_type}",
            method="POST",
            body=b"",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), {"id": base_room})
        # check that the entry in the edits table is updated
        response = yield self.client.fetch(f"{URL}/builder/edits/1")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "edit_id": 1,
                "id": base_room,
                "field": "name",
                "unedited_value": "room",
                "edited_value": "name_edit_test",
                "player_id": player,
                "status": DB_STATUS_ACCEPTED,
                "type": DB_TYPE_BASE_ROOM,
            },
        )
        # test that the accepted edit is enacted
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(db.get_query(base_room)[:], (base_room, "name_edit_test"))

    @gen_test
    def test_view_multiple_edits(self, mocked_auth):
        """
        Tests that edits can be queried based on player, status and entity ID
        """
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room("room")[0]
        with LIGHTDatabase(self.db_path) as db:
            # insert edits directly into the database and check if they're correct
            edit_id1 = db.submit_edit(base_room, "name", "name_edit_test1", player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id1)],
                [
                    (
                        edit_id1,
                        base_room,
                        "name",
                        "room",
                        "name_edit_test1",
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
            edit_id2 = db.submit_edit(base_room, "name", "name_edit_test2", player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id2)],
                [
                    (
                        edit_id2,
                        base_room,
                        "name",
                        "room",
                        "name_edit_test2",
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
            # mark one of the edits as rejected
            db.reject_edit(edit_id1)
        # check that querying for edits with DB_STATUS_REVIEW status only returns
        # the second edit
        response = yield self.client.fetch(
            f"{URL}/builder/edits?status={escape.url_escape(DB_STATUS_REVIEW)}&expand=True",
        )
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {
                    "edit_id": edit_id2,
                    "id": base_room,
                    "field": "name",
                    "unedited_value": "room",
                    "edited_value": "name_edit_test2",
                    "player_id": player,
                    "status": DB_STATUS_REVIEW,
                    "type": DB_TYPE_BASE_ROOM,
                }
            ],
        )
        # check that querying for edits submitted by "player" returns both edits
        response = yield self.client.fetch(
            f"{URL}/builder/edits?player={player}&expand=True"
        )
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {
                    "edit_id": edit_id1,
                    "id": base_room,
                    "field": "name",
                    "unedited_value": "room",
                    "edited_value": "name_edit_test1",
                    "player_id": player,
                    "status": DB_STATUS_REJECTED,
                    "type": DB_TYPE_BASE_ROOM,
                },
                {
                    "edit_id": edit_id2,
                    "id": base_room,
                    "field": "name",
                    "unedited_value": "room",
                    "edited_value": "name_edit_test2",
                    "player_id": player,
                    "status": DB_STATUS_REVIEW,
                    "type": DB_TYPE_BASE_ROOM,
                },
            ],
        )
        # check that expand=False behaves as expected
        response = yield self.client.fetch(
            f"{URL}/builder/edits?player={player}",
        )
        self.assertEqual(json.loads(response.body.decode()), [1, 2])

    @gen_test
    def test_view_entities(self, mocked_auth):
        """
        Tests the ViewEntityWithIDHandler. Checks whether the correct content
        and format is returned when calling entities/<ID>
        """
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room("room")[0]
            base_room2 = db.create_base_room("small room")[0]
            room1 = db.create_room("small room", base_room1, "tiny", "old")[0]
        # Test that base entity can be viewed
        response = yield self.client.fetch(
            f"{URL}/builder/entities/{base_room1}",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {"entity": {"id": base_room1, "name": "room"}, "type": "base room"},
        )
        # Test that entity can be viewed
        response = yield self.client.fetch(
            f"{URL}/builder/entities/{room1}",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "entity": {
                    "id": room1,
                    "name": "small room",
                    "base_id": base_room1,
                    "description": "tiny",
                    "backstory": "old",
                },
                "type": "room",
            },
        )

    @gen_test
    def test_search_entities(self, mocked_auth):
        """
        Tests entries in the database can be searched through the endpoint
        using FTS. More extensive tests on the search function are in test_db.py
        """
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room("room")[0]
            base_room2 = db.create_base_room("small room")[0]
            base_room3 = db.create_base_room("rooming")[0]
            room1 = db.create_room("small room", base_room1, "tiny", "decaying")[0]
            room2 = db.create_room("roomsmall", base_room1, "decayed", "tiny")[0]
            room3 = db.create_room("small room", base_room1, "tiny", "good")[0]
        # check that seraching for base room works properly
        response = yield self.client.fetch(
            f"{URL}/builder/entities/base_room?search=room",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {"id": base_room1, "name": "room"},
                {"id": base_room2, "name": "small room"},
                {"id": base_room3, "name": "rooming"},
            ],
        )
        # check that seraching for room works properly
        response = yield self.client.fetch(
            f"{URL}/builder/entities/room?search=decay",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {
                    "id": room1,
                    "name": "small room",
                    "base_id": base_room1,
                    "description": "tiny",
                    "backstory": "decaying",
                },
                {
                    "id": room2,
                    "name": "roomsmall",
                    "base_id": base_room1,
                    "description": "decayed",
                    "backstory": "tiny",
                },
            ],
        )

    @gen_test
    def test_search_entities_special_character(self, mocked_auth):
        """
        Tests special characters in search string can be processed using urllib
        """
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room("room")[0]
            base_room2 = db.create_base_room("small room")[0]
        search_string = parse.quote_plus("small room")
        response = yield self.client.fetch(
            f"{URL}/builder/entities/base_room?search={search_string}",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [{"id": base_room2, "name": "small room"}],
        )

    @gen_test
    def test_search_entities_incorrect_type(self, mocked_auth):
        """Tests that passing the incorrect type raises 400 bad request"""
        with LIGHTDatabase(self.db_path) as db:
            base_room = db.create_base_room("room")[0]
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f"{URL}/builder/entities/base_?search=room"
            )
        self.assertEqual(400, cm.exception.code)
        self.assertEqual(cm.exception.message, "Type is not valid. ")

    @gen_test
    def test_search_entities_no_search(self, mocked_auth):
        """Tests that not passing search returns all entries"""
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room("room")[0]
            base_room2 = db.create_base_room("small room")[0]
        response = yield self.client.fetch(f"{URL}/builder/entities/base_room?")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {"id": base_room1, "name": "room"},
                {"id": base_room2, "name": "small room"},
            ],
        )

    @gen_test
    def test_get_types(self, mocked_auth):
        """Tests all table names are returned correctly"""
        response = yield self.client.fetch(f"{URL}/builder/tables/types")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                DB_TYPE_BASE_CHAR,
                DB_TYPE_CHAR,
                DB_TYPE_BASE_OBJ,
                DB_TYPE_OBJ,
                DB_TYPE_BASE_ROOM,
                DB_TYPE_ROOM,
                DB_TYPE_TEXT_EDGE,
                DB_TYPE_EDGE,
                DB_TYPE_GRAPH_EDGE,
                DB_TYPE_GRAPH_NODE,
                DB_TYPE_TILE,
                DB_TYPE_INTERACTION,
                DB_TYPE_UTTERANCE,
                DB_TYPE_PARTICIPANT,
                DB_TYPE_TURN,
                DB_TYPE_PLAYER,
                DB_TYPE_WORLD,
            ],
        )

    @gen_test
    def test_get_column_names(self, mocked_auth):
        """Tests all column names are returned correctly"""
        # test base entity
        response = yield self.client.fetch(f"{URL}/builder/entities/base_object/fields")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()), {"id": "integer", "name": "text"}
        )
        # test entity
        response = yield self.client.fetch(f"{URL}/builder/entities/room/fields")
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "id": "integer",
                "name": "text",
                "base_id": "integer",
                "description": "text",
                "backstory": "text",
            },
        )

    @gen_test
    def test_get_column_names_invalid(self, mocked_auth):
        """Tests that when type is invalid, error is raised"""
        with self.assertRaises(Exception):
            response = yield self.client.fetch(
                f"{URL}/builder/entities/base_/fields",
            )
            self.assertEqual(response.code, 400)

    @gen_test
    def test_create_base_entity(self, mocked_auth):
        """Tests that a base entity can be created through the endpoint"""
        body = {"name": "base room lala"}
        response = yield self.client.fetch(
            f"{URL}/builder/entities/base_room",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        # check that the entry in the edits table is updated
        self.assertEqual(response.code, 200)
        id, _ = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(db.get_query(id)[:], (id, "base room lala"))

    @gen_test
    def test_create_entity(self, mocked_auth):
        """Tests that an entity can be created through the endpoint"""
        with LIGHTDatabase(self.db_path) as db:
            base_char = db.create_base_character("animal")[0]
        body = {
            "name": "snake",
            "base_id": base_char,
            "persona": "aggressive",
            "physical_description": "big",
        }
        response = yield self.client.fetch(
            f"{URL}/builder/entities/character",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        # check that the entry in the edits table is updated
        self.assertEqual(response.code, 200)
        id, _ = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(
                db.get_query(id)[:5], (id, "snake", base_char, "aggressive", "big")
            )

    @gen_test
    def test_create_interaction(self, mocked_auth):
        """Tests that an interaction can be created through the endpoint"""
        with LIGHTDatabase(self.db_path) as test:
            base_room = test.create_base_room("room")[0]
            room = test.create_room("room1", base_room, "dirty", "old")[0]
            base_char = test.create_base_character("troll")[0]
            char = test.create_character(None, base_char, "tall", "big")[0]
            player0 = test.create_player()[0]
            player1 = test.create_player()[0]
            player2 = test.create_player()[0]
            participants = [
                (str(char), str(player0)),
                (str(char), str(player1)),
                (str(char), str(player2)),
            ]
            turns = [
                {
                    "speaker": 0,
                    "listener": None,
                    "interaction": {"type": "speech", "content": "utterance1"},
                    "turn_time": 5,
                },
                {
                    "speaker": 2,
                    "listener": 1,
                    "interaction": {"type": "emote", "content": "emote1"},
                    "turn_time": 4,
                },
                {
                    "speaker": 2,
                    "listener": None,
                    "interaction": {"type": "action", "content": "action1"},
                    "turn_time": 3,
                },
            ]
        # check that the add_single_conversation() method is called sucessfully
        # the correctness of the method is checked in test_db.py
        body = {
            "room": room,
            "participants": json.dumps(participants),
            "turns": json.dumps(turns),
        }
        response = yield self.client.fetch(
            f"{URL}/builder/interactions",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 200)
        interaction_id = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(db.get_query(interaction_id)[:], (interaction_id, room))
        # check that duplicates return -1 as interaction_id
        response = yield self.client.fetch(
            f"{URL}/builder/interactions",
            method="POST",
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 200)
        interaction_id = json.loads(response.body.decode())
        self.assertEqual(interaction_id, -1)

    @gen_test
    def test_view_interaction(self, mocked_auth):
        """Tests that an interaction can be viewed through the endpoint"""
        with LIGHTDatabase(self.db_path) as test:
            rbase_id = test.create_base_room("room")[0]
            rcontent_id1 = test.create_room("room1", rbase_id, "dirty", "old")[0]
            cbase_id = test.create_base_character("troll")[0]
            ccontent_id1 = test.create_character(None, cbase_id, "tall", "big")[0]
            player1 = test.create_player()[0]
            player2 = test.create_player()[0]
            utterance1 = test.create_utterance("Hi")[0]
            utterance2 = test.create_utterance("Hello")[0]
            interaction1 = test.create_interaction(rcontent_id1)[0]
            participant1 = test.create_participant(interaction1, ccontent_id1, player1)[
                0
            ]
            participant2 = test.create_participant(interaction1, ccontent_id1, player2)[
                0
            ]
            turn1_1 = test.create_turn(
                interaction1, 0, 1, "speech", utterance1, "", participant1, None
            )[0]
            turn1_2 = test.create_turn(
                interaction1, 1, 1, "speech", utterance2, "", participant1, participant2
            )[0]
        response = yield self.client.fetch(
            f"{URL}/builder/interactions?interaction_id={interaction1}",
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "room": rcontent_id1,
                "participants": [
                    {
                        "ID": participant1,
                        "interaction_id": interaction1,
                        "character_id": ccontent_id1,
                        "player_id": player1,
                    },
                    {
                        "ID": participant2,
                        "interaction_id": interaction1,
                        "character_id": ccontent_id1,
                        "player_id": player2,
                    },
                ],
                "turns": [
                    {
                        "ID": turn1_1,
                        "interaction_id": interaction1,
                        "turn_number": 0,
                        "turn_time": 1,
                        "interaction_type": "speech",
                        "utterance_id": utterance1,
                        "action": "",
                        "speaker_id": participant1,
                        "listener_id": None,
                    },
                    {
                        "ID": turn1_2,
                        "interaction_id": interaction1,
                        "turn_number": 1,
                        "turn_time": 1,
                        "interaction_type": "speech",
                        "utterance_id": utterance2,
                        "action": "",
                        "speaker_id": participant1,
                        "listener_id": participant2,
                    },
                ],
            },
        )


def all():
    suiteList = []
    # TODO: Break out into seperate files, arrange suite elsewhere when automated testing done
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestRegistryApp))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestGameApp))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestWorldSaving))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestBuilderApp))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestLandingApp))
    return unittest.TestSuite(suiteList)


if __name__ == "__main__":
    testing.main()
