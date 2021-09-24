import json
import pickle
from base64 import b64encode, b64decode
from dataclasses import field, dataclass
from http.client import BAD_REQUEST
from io import BytesIO
from typing import List

import marshmallow_dataclass
from flask import Flask, jsonify, request, Response, abort
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import Length, Range
from redis import Redis

from api_spec import get_apispec
from swagger import swagger_ui_blueprint, SWAGGER_URL, API_URL

app = Flask(__name__)
ma = Marshmallow(app)


class UstmockLinkSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("path", "host", "body", "trace_id")


ustmock_link_schema = UstmockLinkSchema()
ustmock_links_schema = UstmockLinkSchema(many=True)


@app.route('/ping')
def ping():
    """
    простая проверка живо ли приложение
    :rtype: str pong
    """
    return jsonify(ping='pong')


@app.get('/ustmock')
def ustmock_list():
    return jsonify(ok='Hello World!')


app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route(API_URL)
def create_swagger_spec():
    r = get_apispec(app)
    return jsonify(r.to_dict())


#
#
# @app.get('/ustmock/<str:id>')
# def ustmock_get(id: str):
#     ustmock_link = User.get(id)
#     return ustmock_link_schema.dump(ustmock_link)
#
# @app.delete('/ustmock/<str:id>')
# def ustmock_del():
#     return 'Hello World!'
#
# @app.patch('/ustmock/<str:id>')
# @app.put('/ustmock/<str:id>')
# def hello_world():
#     return 'Hello World!'
#
# def hello_world():
#     return 'Hello World!'


@dataclass
class UrlFromMockResult:
    body: str = field(default='')
    status: int = field(default=200, metadata={"validate": Range(min=1)})


@dataclass
class UrlFromMock:
    url: str = field(metadata={"validate": Length(max=60)})
    content_type: str = field(default='application/json')
    trace_id: str = field(default='')
    # result_main: UrlFromMockResult = field(default=UrlFromMockResult())
    result_list: List[UrlFromMockResult] = field(default_factory=list)
    # trace_id: List[TraceId] = field(default_factory=list)
    # time_created = fields.DateTime(required=True)
    #
    # @validates('time_created')
    # def is_not_in_future(value):
    #     """'value' is the datetime parsed from time_created by marshmallow"""
    #     now = datetime.now()
    #     if value > now:
    #         raise ValidationError("Can't create notes in the future!")

    @property
    def key(self) -> str:
        return f'{self.url}:{self.content_type}:{self.trace_id}'

    @property
    def result_as_str(self) -> str:
        bytes_output = BytesIO()
        pickle.dump(self.result_list, bytes_output)
        bytes_output_base64 = b64encode(bytes_output.getvalue()).decode()  # convert the bytes to base64 string
        bytes_output.close()
        return bytes_output_base64

    @staticmethod
    def load_result(result: str) -> List[UrlFromMockResult]:
        pickle_bytes = BytesIO(b64decode(result))
        pickle_obj = pickle.loads(pickle_bytes.read())
        pickle_bytes.close()
        return pickle_obj



ustmock_schema = marshmallow_dataclass.class_schema(UrlFromMock)()


class ErrorSchema(Schema):
    error = fields.Str()


@app.post('/ustmock')
def hello_world():
    try:
        u = ustmock_schema.load(request.form)
    except ValidationError as error:
        r = jsonify(error=error.messages)
        r.status = BAD_REQUEST
        return r
    redis.set(u.key, u.result_as_str)
    # actually_create_note(request.form)
    return jsonify(ustmock_schema.dump(u))


# @app.errorhandler(404)
# def page_not_found(e):
#     # your processing here
#     return 'xxx'

redis = Redis()

if __name__ == '__main__':
    app.run()
