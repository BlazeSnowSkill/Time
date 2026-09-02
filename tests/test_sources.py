# -*- coding: utf-8 -*-
"""timelib.sources 测试：NTP 报文解析与校验、HTTP Date 解析、回退顺序。全部离线 mock，不访问真实网络。"""

import struct
from unittest.mock import patch

import pytest

from timelib import sources
from timelib.sources import (
    HTTP_URLS,
    NTP_EPOCH_DELTA,
    NTP_SERVERS,
    get_network_time,
    http_offset,
    ntp_offset,
)


class _FakeSocket:
    """socket.socket 替身：返回预置 NTP 报文并记录发送内容。"""

    def __init__(self, response):
        self.response = response
        self.sent = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def settimeout(self, value):
        pass

    def sendto(self, data, addr):
        self.sent = data

    def recvfrom(self, size):
        return self.response, ("203.0.113.1", 123)


class _FakeHttpResponse:
    """urlopen 返回值替身：仅提供响应头。"""

    def __init__(self, headers):
        self.headers = headers

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _ntp_response(stratum, t1, t2):
    packet = bytearray(48)
    packet[0] = 0x24
    packet[1] = stratum
    struct.pack_into("!II", packet, 32, int(t1 + NTP_EPOCH_DELTA), 0)  # 服务器接收时刻
    struct.pack_into("!II", packet, 40, int(t2 + NTP_EPOCH_DELTA), 0)  # 服务器发送时刻
    return bytes(packet)


def test_ntp_to_unix_epoch():
    assert sources._ntp_to_unix(struct.pack("!II", NTP_EPOCH_DELTA, 0)) == 0.0


def test_ntp_to_unix_fraction():
    assert (
        sources._ntp_to_unix(struct.pack("!II", NTP_EPOCH_DELTA + 100, 0x80000000))
        == 100.5
    )


def test_ntp_offset_parses_server_timestamps():
    fake = _FakeSocket(_ntp_response(2, 100.0, 101.0))
    with (
        patch.object(sources.socket, "socket", return_value=fake),
        patch.object(sources.time, "time", side_effect=[100.0, 100.5]),
    ):
        assert ntp_offset("ntp.example.com", 1) == pytest.approx(0.25)
    assert len(fake.sent) == 48
    assert fake.sent[0] == 0x23  # LI=0, VN=4, Mode=3（客户端）


def test_ntp_offset_rejects_stratum_zero():
    fake = _FakeSocket(bytes(48))
    with (
        patch.object(sources.socket, "socket", return_value=fake),
        patch.object(sources.time, "time", side_effect=[100.0, 100.5]),
    ):
        with pytest.raises(ValueError):
            ntp_offset("ntp.example.com", 1)


def test_ntp_offset_rejects_short_response():
    fake = _FakeSocket(bytes(20))
    with (
        patch.object(sources.socket, "socket", return_value=fake),
        patch.object(sources.time, "time", side_effect=[100.0, 100.5]),
    ):
        with pytest.raises(ValueError):
            ntp_offset("ntp.example.com", 1)


def test_http_offset_parses_date_header_with_rtt_compensation():
    response = _FakeHttpResponse({"Date": "Wed, 02 Sep 2026 09:00:00 GMT"})
    with (
        patch.object(
            sources.urllib.request, "urlopen", return_value=response
        ) as urlopen,
        patch.object(sources.time, "time", side_effect=[1000.0, 1000.2]),
    ):
        offset = http_offset("https://www.example.com", 1)
    assert offset == pytest.approx(1788339600 + 0.1 - 1000.0)
    assert urlopen.call_args.args[0].method == "HEAD"
    assert urlopen.call_args.kwargs["timeout"] == 1


def test_http_offset_requires_date_header():
    response = _FakeHttpResponse({})
    with (
        patch.object(sources.urllib.request, "urlopen", return_value=response),
        patch.object(sources.time, "time", side_effect=[1000.0, 1000.0]),
    ):
        with pytest.raises(ValueError):
            http_offset("https://www.example.com", 1)


def test_get_network_time_prefers_ntp():
    with (
        patch.object(sources, "ntp_offset", return_value=0.5) as ntp,
        patch.object(sources, "http_offset") as http,
    ):
        assert get_network_time(2) == (0.5, "ntp", NTP_SERVERS[0])
    ntp.assert_called_once()
    http.assert_not_called()


def test_get_network_time_falls_back_to_http():
    with (
        patch.object(sources, "ntp_offset", side_effect=OSError("udp blocked")),
        patch.object(sources, "http_offset", return_value=1.0) as http,
    ):
        assert get_network_time(2) == (1.0, "http", HTTP_URLS[0])
    assert http.call_count == 1


def test_get_network_time_returns_none_when_all_fail():
    with (
        patch.object(sources, "ntp_offset", side_effect=OSError("down")),
        patch.object(sources, "http_offset", side_effect=OSError("down")),
    ):
        assert get_network_time(2) is None


def test_get_network_time_debug_prints_failures(capsys):
    with (
        patch.object(sources, "ntp_offset", side_effect=OSError("down")),
        patch.object(sources, "http_offset", side_effect=OSError("down")),
    ):
        get_network_time(2, debug=True)
    err = capsys.readouterr().err
    assert "[debug] NTP" in err
    assert "[debug] HTTP" in err
