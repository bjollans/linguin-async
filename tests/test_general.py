

from lambda_function import lambda_handler

def test_happy_path():
    event = {'queryStringParameters':{'type':'test'}}
    context = {}
    lambda_handler(event, context)