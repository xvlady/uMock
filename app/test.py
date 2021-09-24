import unittest

from app import app
from swagger import SWAGGER_URL, API_URL


class MainTestCase(unittest.TestCase):

    def setUp(self):
        # self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        # flaskr.init_db()

    URL = '/aaaa/xxxx/kjskdfjlfs/124/kjlg'

    # def tearDown(self):
    #     os.close(self.db_fd)
    #     os.unlink(flaskr.app.config['DATABASE'])

    def test_ping(self):
        res = self.app.get('/ping')
        assert res.json == {'ping': 'pong'}

    # def test_list(self):
    #     res = self.app.get('/ustmock')
    #     assert res.json == {'ping': 'pong'}

    def test_ustmock_test_negative(self):
        res = self.app.post('/ustmock', data={'ping': 'pong'})
        assert res.content_length != 0
        assert res.status_code == 400, res.get_data()
        assert res.is_json, res.get_data()
        assert res.json == {'error': {'ping': ['Unknown field.'],
                                      'url': ['Missing data for required field.']}}

    def test_ustmock_test(self):
        res = self.app.post('/ustmock', data={'url': self.URL})
        assert res.content_length != 0
        assert res.status_code == 200, res.get_data()
        assert res.is_json, res.get_data()
        assert res.json == {
            'url': self.URL,
            'content_type': 'application/json',
            'trace_id': '',
            'result_list': [],
        }

    # def test_swagger(self):
    #     res = self.app.get(API_URL)
    #     assert res.json == {'ping': 'pong'}

    def test_swagger_html(self):
        res = self.app.get(SWAGGER_URL)
        assert res.content_length != 0
        assert res.status_code == 308, res.get_data()


if __name__ == '__main__':
    unittest.main()
