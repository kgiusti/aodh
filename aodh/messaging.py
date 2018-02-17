# -*- coding: utf-8 -*-
# Copyright 2013-2015 eNovance <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import oslo_messaging
from oslo_messaging import serializer as oslo_serializer
from oslo_log import log
import traceback

DEFAULT_URL = "__default__"
TRANSPORTS = {}
_SERIALIZER = oslo_serializer.JsonPayloadSerializer()

LOG = log.getLogger(__name__)

def setup():
    oslo_messaging.set_transport_defaults('aodh')


def get_transport(conf, url=None, optional=False, cache=True):
    """Initialise the oslo_messaging layer."""
    global TRANSPORTS, DEFAULT_URL
    LOG.warning("KAG: aodh getting notification transport url=%s", str(url))

    cache_key = url or DEFAULT_URL
    LOG.warning("KAG: aodh cache_key=%s", str(cache_key))
    transport = TRANSPORTS.get(cache_key)
    LOG.warning("KAG: aodh got transport=%s", str(transport))
    if not transport or not cache:
        try:
            LOG.warning("KAG: getting new notification transport url=%s", str(url))
            transport = oslo_messaging.get_notification_transport(conf, url)
            LOG.warning("KAG: notification driver=%s", str(transport))
            if hasattr(transport, "_driver") and hasattr(transport._driver,
                                                         "_url"):
                LOG.warning("KAG: transport URL=%s", str(transport._driver._url))
            #LOG.warning("KAG traceback: %s", str(traceback.format_stack()))
        except (oslo_messaging.InvalidTransportURL,
                oslo_messaging.DriverLoadFailure):
            if not optional or url:
                # NOTE(sileht): oslo_messaging is configured but unloadable
                # so reraise the exception
                LOG.warning("KAG: 1 WTF??? %s", str(url))
                raise
            LOG.warning("KAG: 2 WTF??? %s", str(url))
            return None
        else:
            if cache:
                TRANSPORTS[cache_key] = transport
                LOG.warning("KAG: transports now: %s", str(TRANSPORTS))
    return transport


def get_batch_notification_listener(transport, targets, endpoints,
                                    allow_requeue=False,
                                    batch_size=1, batch_timeout=None):
    """Return a configured oslo_messaging notification listener."""
    return oslo_messaging.get_batch_notification_listener(
        transport, targets, endpoints, executor='threading',
        allow_requeue=allow_requeue,
        batch_size=batch_size, batch_timeout=batch_timeout)


def get_notifier(transport, publisher_id):
    """Return a configured oslo_messaging notifier."""
    notifier = oslo_messaging.Notifier(transport, serializer=_SERIALIZER)
    return notifier.prepare(publisher_id=publisher_id)
