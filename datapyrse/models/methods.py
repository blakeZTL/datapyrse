""" A module for creating HTTP methods in Dataverse """

from enum import StrEnum


class Method(StrEnum):
    """
    Represents an HTTP method in Dataverse or similar systems.

    This class encapsulates the core structure and behavior of an HTTP method
    object in Dataverse, including the available HTTP methods.

    Attributes:
        GET (str): The GET method.
        POST (str): The POST method.
        DELETE (str): The DELETE method.
    """

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
