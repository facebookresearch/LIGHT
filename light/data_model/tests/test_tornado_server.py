#!/usr/bin/env python3
# import unittest.mock as mock
import json
import re
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
    DB_TYPE_EDGE,
    DB_TYPE_TEXT_EDGE,
    DB_TYPE_INTERACTION,
    DB_TYPE_UTTERANCE,
    DB_TYPE_PARTICIPANT,
    DB_TYPE_TURN,
    DB_TYPE_PLAYER,
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
from deploy.web.server.builder_server import (
    BuildApplication,
    get_handlers,
    EntityEditHandler,
    ViewEditWithIDHandler,
)
from deploy.web.server.tornado_server import (
    LandingApplication, 
    Application,
)

PORT = 35494
URL = f'http://localhost:{PORT}'
COOK_HEADER = {'Cookie': 
    'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"'}

class TestGameApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, 'test_server.db')
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = Application()
        app.listen(PORT)
        return app


    @gen_test
    def test_game_page(self):
        '''Test that no specific endpoint results in main game served when logged in'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_static_handler(self):
        '''Test that index.html will be rendered from static handler correctly'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/index.html',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

class TestLandingApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, 'test_server.db')
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = LandingApplication()
        app.listen(PORT)
        return app
        
    @gen_test
    def test_static_handler(self):
        '''Test that index.html will be rendered from static handler correctly'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/index.html',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_static_handler_nonexisting(self):
        '''Test the static handler 404 if resource not found'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/something.html',
                method='GET',
                headers=headers,
            )
        self.assertEqual(cm.exception.code, 404)

    @gen_test
    def test_landing_page(self):
        '''Test that no specific endpoint results in main page served when logged in'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_landing_page(self):
        '''Test that redirect when not logged in'''
        headers = {'Content-Type': 'application/json'}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/',
                method='GET',
                headers=headers,
                follow_redirects=False,
            )
        self.assertEqual(cm.exception.code, 302)
        self.assertEqual(cm.exception.response.headers['Location'], '/login?next=%2F')

    @gen_test
    def test_logout(self):
        '''Test that logout clears cookie and redirects'''
        headers = {'Content-Type': 'application/json'}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/logout',
                method='GET',
                headers=headers,
                follow_redirects=False,
            )
        # 302 still bc we need to redirect
        self.assertEqual(cm.exception.code, 302)
        self.assertEqual(len(cm.exception.response.headers.get_list('Set-Cookie')), 1)
        # Clearing cookies, so should user should be empty string, then redirect to login
        result = re.search('user="(.*)"(.*)', cm.exception.response.headers['Set-Cookie'])
        self.assertEqual(len(result.group(1)), 0)
        self.assertEqual(cm.exception.response.headers['Location'], '/login')

    @gen_test
    def test_login_succesful(self):
        '''Test that login endpoint with correct password gives cookie, 200'''
        headers = {'Content-Type': 'multipart/form-data; boundary=SomeRandomBoundary'}
        body = self.build_body()
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/login',
                method='POST',
                headers=headers,
                body=body,
                follow_redirects=False,
            )
        # 302 still bc we need to redirect
            self.assertEqual(cm.exception.code, 302)
        self.assertEqual(len(cm.exception.response.headers.get_list('Set-Cookie')), 1)
        response = yield self.client.fetch(
            f'{URL}/login',
            method='POST',
            headers=headers,
            body=body,
        )
        self.assertEqual(response.code, 200)


    @gen_test
    def test_login_endpoint(self):
        '''Test that login endpoint responds with login page'''
        headers = {'Content-Type': 'application/json'}
        response = yield self.client.fetch(
            f'{URL}/login',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=UTF-8')
        # This part is liable to change, can just remove in future
        self.assertEqual(response.body, b'<html><body><form action="/login?next=/" method="post">Name:<input type="text" name="name"> Password: <input type="text" name="password"><input type="submit" value="Sign in"></form></body></html>')

    @gen_test
    def test_login_password_protected(self):
        '''Test that login does not work with wrong password'''
        headers = {'Content-Type': 'multipart/form-data; boundary=SomeRandomBoundary'}
        body = self.build_body(password="dog")
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/login',
                method='POST',
                headers=headers,
                body=body,
                follow_redirects=False,
            )
        self.assertEqual(cm.exception.code, 302)

        # With allowing redirects, we expect to end up back at the login page
        response = yield self.client.fetch(
            f'{URL}/login',
            method='POST',
            headers=headers,
            body=body,
        )        
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=UTF-8')
        # This part is liable to change, can just remove in future
        self.assertEqual(response.body, b'<html><body><form action="/login?next=/" method="post">Name:<input type="text" name="name"> Password: <input type="text" name="password"><input type="submit" value="Sign in"></form></body></html>')

    def build_body(name='me', password='LetsPlay'):
        boundary = 'SomeRandomBoundary'
        body = '--%s\r\n' % boundary 

        # data for field1
        body += 'Content-Disposition: form-data; name="name"\r\n'
        body += '\r\n' # blank line
        body += '%s\r\n' % name

        # separator boundary
        body += '--%s\r\n' % boundary 

        # data for field2
        body += 'Content-Disposition: form-data; name="password"\r\n'
        body += '\r\n' # blank line
        body += '%s\r\n' % password

        # separator boundary
        body += '--%s--\r\n' % boundary 
        return body

class TestBuilderApp(AsyncHTTPTestCase):
    def setUp(self):
        self.data_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.data_dir, 'test_server.db')
        self.client = httpclient.AsyncHTTPClient()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def get_app(self):
        app = BuildApplication(get_handlers(self.db_path))
        app.listen(PORT)
        return app


    @gen_test
    def test_builder_page(self):
        '''Test that no specific endpoint results in main builder page served when logged in'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/builder/',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_builder_page(self):
        '''Test that static data serves landing correctly'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/builder/builderindex.html',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_builder_page(self):
        '''Test that static data serves main builder page correctly'''
        headers = {'Content-Type': 'application/json',
                'Cookie': 'user="2|1:0|10:1591809198|4:user|16:InRoYXRfZ3V5Ig==|02e1a9835b94ea0c0d5e95d6bb13094b120b9a5cb7dd0c8b149e264f037e755a"',
        }
        response = yield self.client.fetch(
            f'{URL}/',
            method='GET',
            headers=headers,
        )
        self.assertEqual(response.code, 200)

    @gen_test
    def test_submit_entity_edits(self):
        '''Test that entity edits can be submitted successfully'''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room('room')[0]
        headers = {'Content-Type': 'application/json'}
        body = {
            'id': base_room,
            'field': 'name',
            'edited_value': 'name_edit_test',
            'player': player,
        }
        response = yield self.client.fetch(
            f'{URL}/builder/edits',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 201)
        #with mock.patch.object(ViewEditWithIDHandler, 'get_secure_cookie') as mget:
           # mget.return_value = 'user'
        response = yield self.client.fetch(f'{URL}/builder/edits/1', headers=COOK_HEADER)
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
    def test_submit_utterance_edits(self):
        '''Test that utterance edits can be submitted successfully'''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room('room')[0]
            room = db.create_room('small room', base_room, 'tiny', 'old')[0]
            base_char = db.create_base_character("troll")[0]
            char = db.create_character(None, base_char, "tall", "big")[0]
            utterance1 = db.create_utterance("Hi")[0]
            utterance2 = db.create_utterance("Hello")[0]
            interaction = db.create_interaction(room)[0]
            participant = db.create_participant(interaction, char, player)[0]
            turn = db.create_turn(
                interaction, 0, 0, 'speech', utterance1, None, participant, None
            )[0]
        headers = {'Content-Type': 'application/json'}
        body = {
            'id': turn,
            'field': 'utterance_id',
            'edited_value': 'Hello',
            'player': player,
        }
        response = yield self.client.fetch(
            f'{URL}/builder/edits',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 201)
        self.assertEqual(json.loads(response.body.decode()), {'edit_id': 1})
        response = yield self.client.fetch(f'{URL}/builder/edits/1', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                "edit_id": 1,
                "id": turn,
                "field": "utterance_id",
                "edited_value": 'Hello',
                'characters': ['troll'],
                "player_id": player,
                "status": DB_STATUS_REVIEW,
                "type": "utterance",
                "turn_number": 0,
                'room': 'small room',
                "utterances": ['Hi'],
            },
        )

    @gen_test
    def test_submit_edits_error(self):
        '''Test that missing arguments are detected'''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
        headers = {'Content-Type': 'application/json'}
        body = {'field': 'name', 'edited_value': 'name_edit_test', 'player': player}
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(
                f'{URL}/builder/edits',
                method='POST',
                headers=COOK_HEADER,
                body=urllib.parse.urlencode(body),
            )
        self.assertEqual(400, cm.exception.code)
        self.assertEqual(cm.exception.message, 'Bad Request')

    @gen_test
    def test_reject_edits(self):
        '''Test that edits can be rejected successfully'''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room('room')[0]
        with LIGHTDatabase(self.db_path) as db:
            # insert edit directly into the database and check if it's correct
            edit_id = db.submit_edit(base_room, 'name', 'name_edit_test', player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id)],
                [
                    (
                        1,
                        base_room,
                        'name',
                        'room',
                        'name_edit_test',
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
        response = yield self.client.fetch(
            f'{URL}/builder/edits/{edit_id}/reject', method='POST', headers=COOK_HEADER, body=b''
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), {'id': base_room})
        response = yield self.client.fetch(f'{URL}/builder/edits/1', headers=COOK_HEADER)
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
    def test_accept_edits(self):
        '''Test that edits can be accepted and enacted'''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room('room')[0]
            # insert edit directly into the database and check if it's correct
            edit_id = db.submit_edit(base_room, 'name', 'name_edit_test', player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id)],
                [
                    (
                        1,
                        base_room,
                        'name',
                        'room',
                        'name_edit_test',
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
        accept_type = 'accepted'
        response = yield self.client.fetch(
            f'{URL}/builder/edits/{edit_id}/accept/{accept_type}',
            method='POST',
            headers=COOK_HEADER,
            body=b'',
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body.decode()), {'id': base_room})
        # check that the entry in the edits table is updated
        response = yield self.client.fetch(f'{URL}/builder/edits/1', headers=COOK_HEADER)
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
            self.assertEqual(db.get_query(base_room)[:], (base_room, 'name_edit_test'))

    @gen_test
    def test_view_multiple_edits(self):
        '''
        Tests that edits can be queried based on player, status and entity ID
        '''
        with LIGHTDatabase(self.db_path) as db:
            player = db.create_player()[0]
            base_room = db.create_base_room('room')[0]
        with LIGHTDatabase(self.db_path) as db:
            # insert edits directly into the database and check if they're correct
            edit_id1 = db.submit_edit(base_room, 'name', 'name_edit_test1', player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id1)],
                [
                    (
                        edit_id1,
                        base_room,
                        'name',
                        'room',
                        'name_edit_test1',
                        player,
                        DB_STATUS_REVIEW,
                    )
                ],
            )
            edit_id2 = db.submit_edit(base_room, 'name', 'name_edit_test2', player)
            self.assertEqual(
                [i[:] for i in db.get_edit(edit_id=edit_id2)],
                [
                    (
                        edit_id2,
                        base_room,
                        'name',
                        'room',
                        'name_edit_test2',
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
            f'{URL}/builder/edits?status={escape.url_escape(DB_STATUS_REVIEW)}&expand=True',
            headers=COOK_HEADER,
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
        response = yield self.client.fetch(f'{URL}/builder/edits?player={player}&expand=True', headers=COOK_HEADER)
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
        response = yield self.client.fetch(f'{URL}/builder/edits?player={player}', headers=COOK_HEADER)
        self.assertEqual(json.loads(response.body.decode()), [1, 2])

    @gen_test
    def test_view_entities(self):
        '''
        Tests the ViewEntityWithIDHandler. Checks whether the correct content
        and format is returned when calling entities/<ID>
        '''
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room('room')[0]
            base_room2 = db.create_base_room('small room')[0]
            room1 = db.create_room('small room', base_room1, 'tiny', 'old')[0]
        # Test that base entity can be viewed
        response = yield self.client.fetch(f'{URL}/builder/entities/{base_room1}', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()), {'entity': {'id': base_room1, 'name': 'room'}, 'type': 'base room'}
        )
        # Test that entity can be viewed
        response = yield self.client.fetch(f'{URL}/builder/entities/{room1}', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                'entity': {
                    'id': room1,
                    'name': 'small room',
                    'base_id': base_room1,
                    'description': 'tiny',
                    'backstory': 'old',
                },
                'type': 'room'
            },
        )

    @gen_test
    def test_search_entities(self):
        '''
        Tests entries in the database can be searched through the endpoint
        using FTS. More extensive tests on the search function are in test_db.py
        '''
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room('room')[0]
            base_room2 = db.create_base_room('small room')[0]
            base_room3 = db.create_base_room('rooming')[0]
            room1 = db.create_room('small room', base_room1, 'tiny', 'decaying')[0]
            room2 = db.create_room('roomsmall', base_room1, 'decayed', 'tiny')[0]
            room3 = db.create_room('small room', base_room1, 'tiny', 'good')[0]
        # check that seraching for base room works properly
        response = yield self.client.fetch(f'{URL}/builder/entities/base_room?search=room', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {'id': base_room1, 'name': 'room'},
                {'id': base_room2, 'name': 'small room'},
                {'id': base_room3, 'name': 'rooming'},
            ],
        )
        # check that seraching for room works properly
        response = yield self.client.fetch(f'{URL}/builder/entities/room?search=decay', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {
                    'id': room1,
                    'name': 'small room',
                    'base_id': base_room1,
                    'description': 'tiny',
                    'backstory': 'decaying',
                },
                {
                    'id': room2,
                    'name': 'roomsmall',
                    'base_id': base_room1,
                    'description': 'decayed',
                    'backstory': 'tiny',
                },
            ],
        )

    @gen_test
    def test_search_entities_special_character(self):
        '''
        Tests special characters in search string can be processed using urllib
        '''
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room('room')[0]
            base_room2 = db.create_base_room('small room')[0]
        search_string = parse.quote_plus('small room')
        response = yield self.client.fetch(
            f'{URL}/builder/entities/base_room?search={search_string}',
            headers=COOK_HEADER,
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [{'id': base_room2, 'name': 'small room'}],
        )

    @gen_test
    def test_search_entities_incorrect_type(self):
        '''Tests that passing the incorrect type raises 400 bad request'''
        with LIGHTDatabase(self.db_path) as db:
            base_room = db.create_base_room('room')[0]
        with self.assertRaises(httpclient.HTTPClientError) as cm:
            response = yield self.client.fetch(f'{URL}/builder/entities/base_?search=room', headers=COOK_HEADER)
        self.assertEqual(400, cm.exception.code)
        self.assertEqual(cm.exception.message, 'Type is not valid. ')

    @gen_test
    def test_get_in_contained_from_database(self):
        '''
        When given a room, test that the endpoint can successfullly retrieve
        all objects/characters in the database whose name is contained in the
        room description.
        '''
        with LIGHTDatabase(self.db_path) as test:
            base_room = test.create_base_room('room')[0]
            classroom = test.create_room(
                'classroom',
                base_room,
                'The classroom contains several students and teachers. There is a giant podium near the entrance.',
                'old',
            )[0]
            base_char = test.create_base_character("people")[0]
            teacher1 = test.create_character(
                "teacher", base_char, "I teach 1", "older"
            )[0]
            student = test.create_character(
                "student", base_char, "I go to school", "younger"
            )[0]
            priest = test.create_character(
                "priest", base_char, "I preach", "religious"
            )[0]
            base_obj1 = test.create_base_object("podium")[0]
            podium = test.create_object(
                None, base_obj1, 0.4, 0.2, 0, 0, 0, 0, 0, "big"
            )[0]
            base_obj2 = test.create_base_object("tree")[0]
            tree = test.create_object(None, base_obj2, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[
                0
            ]
        response = yield self.client.fetch(f'{URL}/builder/edges?room={classroom}', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()), [teacher1, student, podium]
        )

    @gen_test
    def test_create_edges(self):
        '''Tests creating edges'''
        with LIGHTDatabase(self.db_path) as test:
            base_room = test.create_base_room('room')[0]
            room1 = test.create_room('small room', base_room, 'tiny', 'old')[0]
            room2 = test.create_room('roomsmall', base_room, 'tiny', 'old')[0]
            baes_char = test.create_base_character("troll")[0]
            char1 = test.create_character(None, baes_char, "tall", "big")[0]
            char2 = test.create_character("troll2", baes_char, "short", "big")[0]
            base_obj = test.create_base_object("knife")[0]
            obj1 = test.create_object(None, base_obj, 0.4, 0.2, 0, 0, 0, 0, 0, "big")[0]
        body = {
            'room': room1,
            'objs': [obj1],
            'chars': [char1, char2],
            'neighbors': [room2],
            'dry_run': True,
        }
        response = yield self.client.fetch(
            f'{URL}/builder/edges',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                [2, 5, 'ex_contained', 0],
                [2, 6, 'ex_contained', 0],
                [2, 8, 'ex_contained', 0],
                [2, 3, 'neighbor', 1],
            ],
        )
        # check that when dry_run = True nothing is changed in the database
        with LIGHTDatabase(self.db_path) as test:
            self.assertEqual(test.get_id(type=DB_TYPE_EDGE), [])
        body = {
            'room': room1,
            'objs': [obj1],
            'chars': [char1],
            'neighbors': [room2],
            'dry_run': False,
        }
        response = yield self.client.fetch(
            f'{URL}/builder/edges',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        # check that when dry_run = False the database is altered
        with LIGHTDatabase(self.db_path) as test:
            # the actual content of the database is checked in the database
            # unit tests
            self.assertNotEqual(test.get_id(type=DB_TYPE_EDGE), [])

    @gen_test
    def test_search_entities_no_search(self):
        '''Tests that not passing search returns all entries'''
        with LIGHTDatabase(self.db_path) as db:
            base_room1 = db.create_base_room('room')[0]
            base_room2 = db.create_base_room('small room')[0]
        response = yield self.client.fetch(f'{URL}/builder/entities/base_room?', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            [
                {'id': base_room1, 'name': 'room'},
                {'id': base_room2, 'name': 'small room'},
            ],
        )

    @gen_test
    def test_get_types(self):
        '''Tests all table names are returned correctly'''
        response = yield self.client.fetch(f'{URL}/builder/tables/types', headers=COOK_HEADER)
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
                DB_TYPE_EDGE,
                DB_TYPE_INTERACTION,
                DB_TYPE_UTTERANCE,
                DB_TYPE_PARTICIPANT,
                DB_TYPE_TURN,
                DB_TYPE_PLAYER,
            ],
        )

    @gen_test
    def test_get_column_names(self):
        '''Tests all column names are returned correctly'''
        # test base entity
        response = yield self.client.fetch(f'{URL}/builder/entities/base_object/fields', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()), {'id': 'integer', 'name': 'text'}
        )
        # test entity
        response = yield self.client.fetch(f'{URL}/builder/entities/room/fields', headers=COOK_HEADER)
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                'id': 'integer',
                'name': 'text',
                'base_id': 'integer',
                'description': 'text',
                'backstory': 'text',
            },
        )

    @gen_test
    def test_get_column_names_invalid(self):
        '''Tests that when type is invalid, error is raised'''
        with self.assertRaises(Exception):
            response = yield self.client.fetch(f'{URL}/builder/entities/base_/fields', headers=COOK_HEADER)
            self.assertEqual(response.code, 400)

    @gen_test
    def test_create_base_entity(self):
        '''Tests that a base entity can be created through the endpoint'''
        body = {'name': 'base room lala'}
        response = yield self.client.fetch(
            f'{URL}/builder/entities/base_room',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        # check that the entry in the edits table is updated
        self.assertEqual(response.code, 200)
        id, _ = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(db.get_query(id)[:], (id, 'base room lala'))

    @gen_test
    def test_create_entity(self):
        '''Tests that an entity can be created through the endpoint'''
        with LIGHTDatabase(self.db_path) as db:
            base_char = db.create_base_character('animal')[0]
        body = {
            'name': 'snake',
            'base_id': base_char,
            'persona': 'aggressive',
            'physical_description': 'big',
        }
        response = yield self.client.fetch(
            f'{URL}/builder/entities/character',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        # check that the entry in the edits table is updated
        self.assertEqual(response.code, 200)
        id, _ = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(
                db.get_query(id)[:5], (id, 'snake', base_char, 'aggressive', 'big')
            )

    @gen_test
    def test_create_interaction(self):
        '''Tests that an interaction can be created through the endpoint'''
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
                    'speaker': 0,
                    'listener': None,
                    'interaction': {'type': 'speech', 'content': 'utterance1'},
                    'turn_time': 5,
                },
                {
                    'speaker': 2,
                    'listener': 1,
                    'interaction': {'type': 'emote', 'content': 'emote1'},
                    'turn_time': 4,
                },
                {
                    'speaker': 2,
                    'listener': None,
                    'interaction': {'type': 'action', 'content': 'action1'},
                    'turn_time': 3,
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
            f'{URL}/builder/interactions',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 200)
        interaction_id = json.loads(response.body.decode())
        with LIGHTDatabase(self.db_path) as db:
            self.assertEqual(db.get_query(interaction_id)[:], (interaction_id, room))
        # check that duplicates return -1 as interaction_id
        response = yield self.client.fetch(
            f'{URL}/builder/interactions',
            method='POST',
            headers=COOK_HEADER,
            body=urllib.parse.urlencode(body),
        )
        self.assertEqual(response.code, 200)
        interaction_id = json.loads(response.body.decode())
        self.assertEqual(interaction_id, -1)

    @gen_test
    def test_view_interaction(self):
        '''Tests that an interaction can be viewed through the endpoint'''
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
            f'{URL}/builder/interactions?interaction_id={interaction1}',
            headers=COOK_HEADER
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            json.loads(response.body.decode()),
            {
                'room': rcontent_id1,
                'participants': [
                    {
                        'ID': participant1,
                        'interaction_id': interaction1,
                        'character_id': ccontent_id1,
                        'player_id': player1,
                    },
                    {
                        'ID': participant2,
                        'interaction_id': interaction1,
                        'character_id': ccontent_id1,
                        'player_id': player2,
                    },
                ],
                'turns': [
                    {
                        'ID': turn1_1,
                        'interaction_id': interaction1,
                        'turn_number': 0,
                        'turn_time': 1,
                        'interaction_type': 'speech',
                        'utterance_id': utterance1,
                        'action': '',
                        'speaker_id': participant1,
                        'listener_id': None,
                    },
                    {
                        'ID': turn1_2,
                        'interaction_id': interaction1,
                        'turn_number': 1,
                        'turn_time': 1,
                        'interaction_type': 'speech',
                        'utterance_id': utterance2,
                        'action': '',
                        'speaker_id': participant1,
                        'listener_id': participant2,
                    },
                ],
            },
        )


def all():
    suiteList = []
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestGameApp))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestBuilderApp))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(TestLandingApp))
    return unittest.TestSuite(suiteList)

if __name__ == '__main__':
    testing.main()
