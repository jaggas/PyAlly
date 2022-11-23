# MIT License
#
# Copyright (c) 2020 Brett Graves
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The ally.Ally module/file.

Controls the Ally() account class, the bread and butter of the library.
"""

from .Api import setTimeout
from .Auth import Auth
from .Watchlist import Watchlist
from .classes import ApiKeys


class Ally:
    """The ally.Ally.Ally class.

    This is the main class for this library.
    """

    from .Account import get_accounts, balances, history, holdings
    from .Info import clock, status
    from .News import lookupNews, searchNews
    from .Option import expirations, optionSearchQuery, search, strikes
    from .Order import orders, submit
    from .Quote import quote, stream, timesales, toplists

    auth = None
    account_nbr = None

    def __init__(self, keys = ApiKeys(), timeout: float = 1.0):
        """Manages all facets of your Ally Invest account.

        Manage your account
            Track the current and past state of your account. Visit the Account_ page for full details.

            * Balances (gets all current cash and margin balances)
            * History (gets full history of all trades, dividends, and cash transfers of the account)
            * Holdings (gets list of all currently-held non-cash positions, and profitability information)

        Get quotes
            Specified in-detail in Quotes_. Supports 3 types of quote-gathering:

            * Real-time quotes
            * Timesales (historical intraday prices over rolling 5 day window)
            * Quote Streaming (get quotes for up to 256 symbols in real-time, as prices update)

        Place trades
            Trades can be placed, modified (after being created locally, and even after submitting), or cancelled. Order objects described in Trading_ in detail.

        Arguments:
            timeout (float): number of seconds to wait before failing unresponsive api call
            params: provide keys in the form of:

                #. A dictionary: { ALLY_OAUTH_SECRET: ...}
                #. A string: (filename to json file containing api keys)
                #. None (default): Grab the api keys from environment variables

                For any of the mediums above, be sure to provide all of the keys:

                .. code-block:: python

                    params = {
                        'ALLY_OAUTH_SECRET': ...,
                        'ALLY_OAUTH_TOKEN': ...,
                        'ALLY_CONSUMER_SECRET': ...,
                        'ALLY_CONSUMER_KEY': ...,
                        'ALLY_ACCOUNT_NBR': ...
                    }

        .. _Trading: trading.html
        .. _Quotes: quotes.html
        .. _Account: account.html
        """
        # Store keys
        self.keys: ApiKeys = keys

        # Create the auth that we want
        #  This is the only tidbit that actually
        #   needs these parameters anyways
        self.auth = Auth(keys)

        # But keep account number
        self.account_nbr = keys["ALLY_ACCOUNT_NBR"]

        # Watchlist gets copy of our object
        #  this is so that it can manage its own api calls
        self.watchlists = Watchlist(self)
