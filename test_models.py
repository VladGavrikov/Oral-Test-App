import os
import unittest

from app import app,db




#basedir = os.path.abspath(os.path.dirname(__file__))

TEST_DB = 'test.db'
class BasicTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        self.assertEqual(app.debug, False)
    def tearDown(self):
        pass    

    def test_main_page(self):
        response = self.app.get('/',follow_redirects = True)
        self.assertEqual(response.status_code,200)
class ModelTest(unittest.TestCase):
    def test_create_user(self):
        signup_data = {'id':'2220000','email': 'admin@gmail.com', 'Firstname': 'A','Lastname':'B',
                       'password': 'admin', 'isTeacher':'True'}

        result = requests.post(self.hostname + '/register', data=signup_data).text

        assert 'Thanks for registering please login' in result

    def test_login(self):

         #Login data
         data = {'email': 'admin@gmail.com', 'password': 'admin'}
        result = self.session.post(self.hostname + '/login', data=data).text

        assert 'Create a poll' in result        


if __name__ == "__main__":
    unittest.main()

