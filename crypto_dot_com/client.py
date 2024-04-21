import hashlib
import urllib
import urllib.parse
from typing import Any

import requests

from crypto_dot_com.data_models import CryptDotComResponseType
from crypto_dot_com.settings import API_VERSION
from crypto_dot_com.settings import ROOT_API_ENDPOINT
from crypto_dot_com.utils import get_current_time_ms_as_string


class CryptoAPI:
    def __init__(
        self, api_key: str, api_secret: str, timeout: int = 1000
    ) -> None:
        self._timeout = timeout
        self._base_url = ROOT_API_ENDPOINT + "/" + API_VERSION
        self.api_key = api_key
        self.api_secret = api_secret

    def _get_headers(self, method: str) -> dict[str, str]:
        if method in ["POST", "DELETE"]:
            return {"Content-Type": "application/x-www-form-urlencoded"}
        else:
            return {}

    def _get(
        self, url: str, params: dict[str, Any], sign: bool = False
    ) -> CryptDotComResponseType:
        if sign is True:
            params = self._create_signed_params(params)
        data = urllib.parse.urlencode(params or {})
        try:
            response = requests.get(
                url,
                data,
                headers=self._get_headers(method="GET"),
                timeout=self._timeout,
            )
            if response.ok:
                response_data: CryptDotComResponseType = response.json()
                return response_data
            else:
                return {
                    "code": "-1",
                    "msg": f"response status: {response.status_code}",
                    "data": None,
                }
        except Exception as e:
            print("httpGet failed, detail is:%s" % e)
            return {"code": "-1", "msg": str(e), "data": None}

    def _post(
        self, url: str, params: dict[str, Any], sign: bool = False
    ) -> CryptDotComResponseType:
        if sign is True:
            params = self._create_signed_params(params)
        data = urllib.parse.urlencode(params or {})
        try:
            response = requests.post(
                url,
                data,
                headers=self._get_headers(method="POST"),
                timeout=self._timeout,
            )
            if response.ok:
                response_data: CryptDotComResponseType = response.json()
                return response_data
            else:
                return {
                    "code": "-1",
                    "msg": f"response status: {response.status_code}",
                    "data": None,
                }
        except Exception as e:
            print("httpPost failed, detail is:%s" % e)
            return {"code": "-1", "msg": str(e), "data": None}

    def _create_signed_params(self, params: dict[str, Any]) -> dict[str, Any]:
        if not params:
            signed_params = {}
        else:
            signed_params = params.copy()
        signed_params["api_key"] = self.api_key
        signed_params["time"] = get_current_time_ms_as_string()
        sorted_params = sorted(
            signed_params.items(), key=lambda d: d[0], reverse=False
        )
        messageNotEncoded = (
            "".join(map(lambda x: str(x[0]) + str(x[1] or ""), sorted_params))
            + self.api_secret
        )
        sign = hashlib.sha256(messageNotEncoded.encode("utf-8")).hexdigest()
        signed_params["sign"] = sign
        return signed_params

    def depth(self, symbol: str) -> CryptDotComResponseType:
        url = self._base_url + "/depth"
        params = {"symbol": symbol, "type": "step0"}
        return self._get(url, params)

    def balance(self) -> CryptDotComResponseType:
        url = self._base_url + "/account"
        return self._post(url, {}, sign=True)

    def get_all_orders(self, symbol: str) -> CryptDotComResponseType:
        url = self._base_url + "/allOrders"
        params = {}
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def get_order(self, symbol: str, order_id: str) -> CryptDotComResponseType:
        url = self._base_url + "/showOrder"
        params = {}
        params["order_id"] = order_id
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def get_ordst(self, symbol: str, order_id: str) -> int:
        url = self._base_url + "/showOrder"
        params = {}
        params["order_id"] = order_id
        params["symbol"] = symbol
        res = self._post(url, params, sign=True)
        if res is not None and type(res["data"]) is dict:

            if (
                ("code" in res)
                and (res["code"] == "0")
                and ("order_info" in res["data"])
            ):
                status: int = res["data"]["order_info"]["status"]
                return status
        return -1

    def get_open_orders(self, symbol: str) -> CryptDotComResponseType:
        url = self._base_url + "/openOrders"
        params = {}
        params["pageSize"] = "200"
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def get_trades(self, symbol: str) -> CryptDotComResponseType:
        url = self._base_url + "/myTrades"
        params = {}
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def cancel_order(
        self, symbol: str, order_id: str
    ) -> CryptDotComResponseType:
        url = self._base_url + "/orders/cancel"
        params = {}
        params["order_id"] = order_id
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def cancel_order_all(self, symbol: str) -> CryptDotComResponseType:
        url = self._base_url + "/cancelAllOrders"
        params = {}
        params["symbol"] = symbol
        return self._post(url, params, sign=True)

    def create_order(
        self, symbol: str, side: str, price: float, size: float
    ) -> CryptDotComResponseType:
        """
        s:return:
        """
        url = self._base_url + "/order"
        params: dict[str, Any] = {}
        params["price"] = price
        params["side"] = side
        params["symbol"] = symbol
        params["type"] = 1
        params["volume"] = size
        return self._post(url, params, sign=True)
