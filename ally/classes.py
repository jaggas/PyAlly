import enum
import os
import json
from typing import Union, Dict

from .exception import ApiKeyException

class RequestType(enum.Enum):
    Order = 1
    Quote = 2
    Info = 3

class ApiKeys:
    ALL_PARAMS = (
        "ALLY_OAUTH_SECRET",
        "ALLY_OAUTH_TOKEN",
        "ALLY_CONSUMER_SECRET",
        "ALLY_CONSUMER_KEY",
        "ALLY_ACCOUNT_NBR",
    )

    def __init__(self, input: Union[str, dict, None] = None):
        self.params: Dict[str, str] = {}
        if type(input) is dict:
            self.params = input
        elif type(input) is str:
            self.params = self._param_load_file(input)
        elif input is None:
            self.params = self._param_load_environ()
        self._validate()
            
    def _param_load_environ(self):
        """Try to use environment params."""
        params = {}
        for t in ApiKeys.ALL_PARAMS:
            params[t] = os.environ.get(t, None)
        return params

    def _param_load_file(self, fname):
        """Try to load params from a json file."""
        with open(fname, "r") as f:
            return json.load(f)
    
    def _validate(self):
        for p in ApiKeys.ALL_PARAMS:
            if self.params.get(p, None) is None:
                raise ApiKeyException("{0} parameter not provided".format(p))
    
    def __getattr__(self, item: str) -> str:
        return self.params[item]
    
    def __getitem__(self, item: str) -> str:
        return self.__getattr__(item)