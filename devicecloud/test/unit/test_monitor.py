# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2015 Digi International, Inc.
from devicecloud.test.unit.test_utilities import HttpTestBase
import six

CREATE_MONITOR_GOOD_REQUEST = """\
<Monitor>
    <monTopic>topA,topB</monTopic>
    <monBatchSize>10</monBatchSize>
    <monFormatType>json</monFormatType>
    <monTransportType>tcp</monTransportType>
    <monCompression>gzip</monCompression>
</Monitor>
"""

CREATE_MONITOR_GOOD_RESPONSE = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<result>
  <location>Monitor/178008</location>
</result>
"""

GET_MONITOR_SINGLE_FOUND = """\
{
    "resultTotalRows": "1",
    "requestedStartRow": "0",
    "resultSize": "1",
    "requestedSize": "1000",
    "remainingSize": "0",
    "items": [
        {
            "monId": "178007",
            "cstId": "7603",
            "monTopic": "DeviceCore,FileDataCore,FileData,DataPoint",
            "monTransportType": "tcp",
            "monFormatType": "json",
            "monBatchSize": "1",
            "monCompression": "zlib",
            "monStatus": "INACTIVE",
            "monBatchDuration": "10"
        }
   ]
}
"""

GET_MONITOR_METADTATA = """\
{
    "resultTotalRows": "1",
    "requestedStartRow": "0",
    "resultSize": "1",
    "requestedSize": "1000",
    "remainingSize": "0",
    "items": [
        {
            "monId": "178007",
            "cstId": "7603",
            "monTopic": "DeviceCore,FileDataCore,FileData,DataPoint",
            "monTransportType": "tcp",
            "monFormatType": "json",
            "monBatchSize": "1",
            "monCompression": "zlib",
            "monStatus": "INACTIVE",
            "monBatchDuration": "10"
        }
    ]
}
"""

GET_MONITOR_MULTIPLE_FOUND = """\
{
    "resultTotalRows": "2",
    "requestedStartRow": "0",
    "resultSize": "2",
    "requestedSize": "1000",
    "remainingSize": "0",
    "items": [
        {
            "monId": "178007",
            "cstId": "7603",
            "monTopic": "DeviceCore,FileDataCore,FileData,DataPoint",
            "monTransportType": "tcp",
            "monFormatType": "json",
            "monBatchSize": "1",
            "monCompression": "zlib",
            "monStatus": "INACTIVE",
            "monBatchDuration": "10"
        },
        {
            "monId": "198765",
            "cstId": "7603",
            "monTopic": "DeviceCore,FileDataCore,FileData,DataPoint",
            "monTransportType": "tcp",
            "monFormatType": "json",
            "monBatchSize": "1",
            "monCompression": "",
            "monStatus": "INACTIVE",
            "monBatchDuration": "10"
        }
   ]
}
"""

GET_MONITOR_NONE_FOUND = """\
{
    "resultTotalRows": "0",
    "requestedStartRow": "0",
    "resultSize": "0",
    "requestedSize": "1000",
    "remainingSize": "0",
    "items": []
}
"""



class TestMonitorAPI(HttpTestBase):

    def test_create_monitor(self):
        self.prepare_response("POST", "/ws/Monitor", data=CREATE_MONITOR_GOOD_RESPONSE)
        mon = self.dc.monitor.create_monitor(['topA', 'topB'], batch_size=10, batch_duration=0,
                                       transport_type='tcp', compression='gzip', format_type='json')
        self.assertEqual(self._get_last_request().body, six.b(CREATE_MONITOR_GOOD_REQUEST))
        self.assertEqual(mon.get_id(), 178008)

    def test_get_monitor_present(self):
        self.prepare_response("GET", "/ws/Monitor", data=GET_MONITOR_SINGLE_FOUND)
        mon = self.dc.monitor.get_monitor(['DeviceCore', 'FileDataCore', 'FileData', 'DataPoint'])
        self.assertEqual(mon.get_id(), 178007)
        self.assertEqual(self._get_last_request_params(), {
            'condition': "monTopic='DeviceCore,FileDataCore,FileData,DataPoint'",
            'start': '0',
            'size': '1000'
        })

    def test_get_monitor_multiple(self):
        # Should just pick the first result (currently), so results are the same as ever
        self.prepare_response("GET", "/ws/Monitor", data=GET_MONITOR_MULTIPLE_FOUND)
        mon = self.dc.monitor.get_monitor(['DeviceCore', 'FileDataCore', 'FileData', 'DataPoint'])
        self.assertEqual(mon.get_id(), 178007)
        self.assertEqual(self._get_last_request_params(), {
            'condition': "monTopic='DeviceCore,FileDataCore,FileData,DataPoint'",
            'start': '0',
            'size': '1000'
        })

    def test_get_monitor_does_not_exist(self):
        # Should just pick the first result (currently), so results are the same as ever
        self.prepare_response("GET", "/ws/Monitor", data=GET_MONITOR_NONE_FOUND)
        mon = self.dc.monitor.get_monitor(['DeviceCore', 'FileDataCore', 'FileData', 'DataPoint'])
        self.assertEqual(mon, None)


class TestDeviceCloudMonitor(HttpTestBase):

    def setUp(self):
        HttpTestBase.setUp(self)
        self.prepare_response("GET", "/ws/Monitor", data=GET_MONITOR_SINGLE_FOUND)
        mon = self.dc.monitor.get_monitor(['DeviceCore', 'FileDataCore', 'FileData', 'DataPoint'])
        self.mon = mon

    def test_get_metadata(self):
        self.prepare_response("GET", "/ws/Monitor/178007", data=GET_MONITOR_METADTATA)
        self.assertEqual(self.mon.get_metadata(), {
            "monId": "178007",
            "cstId": "7603",
            "monTopic": "DeviceCore,FileDataCore,FileData,DataPoint",
            "monTransportType": "tcp",
            "monFormatType": "json",
            "monBatchSize": "1",
            "monCompression": "zlib",
            "monStatus": "INACTIVE",
            "monBatchDuration": "10"
        })

    def test_delete(self):
        self.prepare_response("DELETE", "/ws/Monitor/178007")
        self.mon.delete()
        req = self._get_last_request()
        self.assertEqual(req.method, "DELETE")
        self.assertEqual(req.path, "/ws/Monitor/178007")

    def test_get_id(self):
        self.assertEqual(self.mon.get_id(), 178007)
