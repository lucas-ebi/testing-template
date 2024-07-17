import unittest
import logging
from logging.handlers import RotatingFileHandler
import json

def setup_logger(name, log_file, level=logging.DEBUG):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=3)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger('http_logger', 'http_detailed_log_file.log')


class HttpRequest:
    def __init__(self, method, path, headers=None, body=None):
        self.method = method
        self.path = path
        self.headers = headers if headers else {}
        self.body = body

class HttpResponse:
    def __init__(self, status_code, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers if headers else {}
        self.body = body

class Repository:
    pass

class Service:
    def __init__(self, repository):
        self.repository = repository

def process_post_buggy(data):
    # Buggy: raises KeyError if "name" is missing and does not handle it
    return {"message": f"Hello, {data['name']}!"}

def process_post_fixed(data):
    # Fixed: handle the case where "name" is missing
    if "name" in data:
        return {"message": f"Hello, {data['name']}!"}
    else:
        return {"error": "Name not provided"}

def handle_request_no_exception(request, process_post):
    logger.debug(f"Received {request.method} request: Path={request.path}, Headers={request.headers}, Body={request.body}")
    
    if request.method == 'GET':
        response_body = {"message": "Hello, World!"}
        response = HttpResponse(status_code=200, headers={"Content-Type": "application/json"}, body=response_body)
        logger.debug(f"Generated response: Status=200, Headers={response.headers}, Body={response_body}")
        return response
    elif request.method == 'POST':
        data = json.loads(request.body)
        logger.debug(f"Parsed POST data: {data}")
        response_body = process_post(data)
        response = HttpResponse(status_code=200, headers={"Content-Type": "application/json"}, body=response_body)
        logger.debug(f"Generated response: Status=200, Headers={response.headers}, Body={response_body}")
        return response

def handle_request_with_exception(request, process_post):
    logger.debug(f"Received {request.method} request: Path={request.path}, Headers={request.headers}, Body={request.body}")
    
    if request.method == 'GET':
        response_body = {"message": "Hello, World!"}
        response = HttpResponse(status_code=200, headers={"Content-Type": "application/json"}, body=response_body)
        logger.debug(f"Generated response: Status=200, Headers={response.headers}, Body={response_body}")
        return response
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Parsed POST data: {data}")
            response_body = process_post(data)
            response = HttpResponse(status_code=200, headers={"Content-Type": "application/json"}, body=response_body)
            logger.debug(f"Generated response: Status=200, Headers={response.headers}, Body={response_body}")
            return response
        except KeyError as e:
            error_message = {"error": "Invalid JSON"}
            response = HttpResponse(status_code=400, headers={"Content-Type": "application/json"}, body=error_message)
            logger.error(f"Failed to process POST data: {request.body}. Error: {e}")
            return response
        except json.JSONDecodeError:
            error_message = {"error": "Invalid JSON"}
            response = HttpResponse(status_code=400, headers={"Content-Type": "application/json"}, body=error_message)
            logger.error(f"Failed to parse POST data: {request.body}")
            return response


# Unit test class
class TestRequestHandler(unittest.TestCase):
    def setUp(self):
        self.repository = Repository()
        self.service = Service(self.repository)

    def assertDoesNotRaise(self, func, *args, **kwargs):
        """
        Ensures a function does not raise an exception.
        """
        try:
            func(*args, **kwargs)
        except Exception as e:
            self.fail(f"{func.__name__} raised {type(e).__name__} unexpectedly: {e}")

    def test_get_request(self):
        request = HttpRequest(method="GET", path="/hello", headers={"Accept": "application/json"})
        response = handle_request_with_exception(request, process_post_fixed)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, {"message": "Hello, World!"})

    def test_post_request_with_name(self):
        request_body = json.dumps({"name": "Alice"})
        request = HttpRequest(method="POST", path="/hello", headers={"Content-Type": "application/json"}, body=request_body)
        
        # Buggy implementation with name without exception handling should NOT raise KeyError
        # try:
        #     handle_request_no_exception(request, process_post_buggy)
        # except KeyError:
        #     self.fail("handle_request_no_exception raised KeyError unexpectedly")
        self.assertDoesNotRaise(handle_request_no_exception, request, process_post_buggy)

        # Buggy implementation with exception handling should not raise KeyError
        response_buggy_with_exception = handle_request_with_exception(request, process_post_buggy)
        self.assertEqual(response_buggy_with_exception.status_code, 200)
        self.assertEqual(response_buggy_with_exception.body, {"message": "Hello, Alice!"})

        # Fixed implementation without exception handling
        response_fixed_no_exception = handle_request_no_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_no_exception.status_code, 200)
        self.assertEqual(response_fixed_no_exception.body, {"message": "Hello, Alice!"})

        # Fixed implementation with exception handling
        response_fixed_with_exception = handle_request_with_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_with_exception.status_code, 200)
        self.assertEqual(response_fixed_with_exception.body, {"message": "Hello, Alice!"})

    def test_post_request_without_name_buggy(self):
        request_body = json.dumps({"age": 30})
        request = HttpRequest(method="POST", path="/hello", headers={"Content-Type": "application/json"}, body=request_body)
        
        # Buggy implementation without exception handling should raise KeyError
        with self.assertRaises(KeyError):
            handle_request_no_exception(request, process_post_buggy)

        # Buggy implementation with exception handling should handle KeyError
        response_buggy_with_exception = handle_request_with_exception(request, process_post_buggy)
        self.assertEqual(response_buggy_with_exception.status_code, 400)
        self.assertEqual(response_buggy_with_exception.body, {"error": "Invalid JSON"})
        
    def test_post_request_without_name_fixed(self):
        request_body = json.dumps({"age": 30})
        request = HttpRequest(method="POST", path="/hello", headers={"Content-Type": "application/json"}, body=request_body)
        
        # Fixed implementation without exception handling
        response_fixed_no_exception = handle_request_no_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_no_exception.status_code, 200)  # Correct response status
        self.assertEqual(response_fixed_no_exception.body, {"error": "Name not provided"})  # Correct response message

        # Fixed implementation with exception handling
        response_fixed_with_exception = handle_request_with_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_with_exception.status_code, 200)
        self.assertEqual(response_fixed_with_exception.body, {"error": "Name not provided"})

    def test_buggy_vs_fixed_output(self):
        request_body = json.dumps({"age": 30})
        request = HttpRequest(method="POST", path="/hello", headers={"Content-Type": "application/json"}, body=request_body)
        
        # Buggy implementation without exception handling should raise KeyError
        with self.assertRaises(KeyError):
            handle_request_no_exception(request, process_post_buggy)
        
        # Buggy implementation with exception handling should handle KeyError
        response_buggy_with_exception = handle_request_with_exception(request, process_post_buggy)
        self.assertEqual(response_buggy_with_exception.status_code, 400)
        self.assertEqual(response_buggy_with_exception.body, {"error": "Invalid JSON"})
        
        # Fixed implementation without exception handling
        response_fixed_no_exception = handle_request_no_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_no_exception.status_code, 200)
        self.assertEqual(response_fixed_no_exception.body, {"error": "Name not provided"})
        
        # Fixed implementation with exception handling
        response_fixed_with_exception = handle_request_with_exception(request, process_post_fixed)
        self.assertEqual(response_fixed_with_exception.status_code, 200)
        self.assertEqual(response_fixed_with_exception.body, {"error": "Name not provided"})
        
        # Additional assertions
        # Buggy implementation doesn't match the correct output
        with self.assertRaises(KeyError):
            handle_request_no_exception(request, process_post_buggy)
        # Fixed implementation doesn't match the wrong output
        response_fixed_with_exception = handle_request_with_exception(request, process_post_fixed)
        self.assertNotEqual(response_fixed_with_exception.body, {"error": "Invalid JSON"})
        # Fixed implementation matches the correct output
        self.assertEqual(response_fixed_with_exception.body, {"error": "Name not provided"})

if __name__ == "__main__":
    unittest.main()