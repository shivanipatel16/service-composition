import copy
from flask import request
import json
import logging
from datetime import datetime

logger = logging.getLogger()


class RESTContext:

    _default_limit = 20

    @classmethod
    def _de_array_args(cls, args):
        result = {}

        if args is not None:
            for k, v in args.items():
                if type(v) == list:
                    result[k] = ",".join(v)
                else:
                    result[k] = v

        return result

    def __init__(self, request_context, path_parameters=None):

        log_message = ""

        self.url = request_context.url

        self.path = request_context.path
        args = dict(request_context.args)

        args = self._de_array_args(args)
        self.path = request.path

        self.data = None
        self.headers = dict(request.headers)
        self.method = request.method
        self.host_url = request.host_url

        self.path_parameters = path_parameters

        try:
            self.data = request_context.get_json()
        except Exception as e:
            pass

        args, limit = self._get_and_remove_arg(args, "limit")
        if not limit:
            self.limit = RESTContext._default_limit
        else:
            self.limit = int(limit)

        args, offset = self._get_and_remove_arg(args, "offset")
        if not offset:
            self.offset = 0
        else:
            self.offset = int(offset)

        args, order_by = self._get_and_remove_arg(args, "order_by")
        self.order_by = order_by

        args, fields = self._get_and_remove_arg(args, "fields")
        self.fields = fields

        self.args = args

        try:
            if request.data is not None:
                data = request.json
            else:
                data = None
        except Exception as e:
            # This would fail the request in a more real solution.
            data = "You sent something but I could not get JSON out of it."

            log_message = str(datetime.now()) + ": Method " + self.method

        log_message += " received: \n" + json.dumps(str(self), indent=2)
        logger.debug(log_message)

    def to_json(self):

        result = {
            'path': self.path,
            "path_parameters": self.path_parameters,
            'args': self.args,
            'headers': self.headers,
            'limit': self.limit,
            'offset': self.offset,
            'method': self.method,
            'host_url': self.host_url,
            'order_by': self.order_by,
            'fields': self.fields,
            'data': self.data}

        return result

    def __str__(self):
        result = self.to_json()
        result = json.dumps(result, indent=2)
        return result

    @staticmethod
    def _add_query(url, query_name, old_query_parameter, query_parameter):
        if query_name + "=" in url:
            url = url.replace(query_name + "=" + str(old_query_parameter), "offset=" + str(query_parameter))
        elif "?" in url:
            url += "&{}=".format(query_name) + str(query_parameter)
        else:
            url += "?{}=".format(query_name) + str(query_parameter)
        return url

    # TODO: should this be here?
    def get_link(self, direction=None):
        url = self.url.replace(self.host_url, "")

        if direction == "next":
            new_offset = self.offset + self.limit
            url = self._add_query(url, "offset", self.offset, new_offset)

        elif direction == "prev":
            new_offset = self.offset - self.limit
            if new_offset < 0:
                url = self._add_query(url, "offset", self.offset, 0)
            else:
                url = self._add_query(url, "offset", self.offset, new_offset)

        return url

    def get_links(self):
        self_link = {"rel": "self", "href": self.get_link()}
        next_link = {"rel": "next", "href": self.get_link("next")}
        prev_link = {"rel": "prev", "href": self.get_link("prev")}

        return [self_link, prev_link, next_link]

    def get_location(self, key):
        url = self.url.replace(self.host_url, "") + "/" + key
        return url

    @classmethod
    def _get_and_remove_arg(cls, args, arg_name):
        val = copy.copy(args.get(arg_name, None))
        if val is not None:
            del args[arg_name]

        return args, val


# TODO
def log_response(method, status, data, txt):
    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2, default=str))


# TODO
def log_request(method_name, request_context):

    info = {
        "method_name": method_name,
        "request": request_context
    }
    msg = json.dumps(info, indent=2, default=str)

    logger.debug(str(datetime.now()) + ": \n" + msg)


# TODO move?
def split_key_string(s):

    result = s.split("_")
    return result
