#pylint: disable=C0111

from lettuce import step
from lettuce import world
from lettuce import before
from pymongo import MongoClient
from nose.tools import assert_equals
from nose.tools import assert_in


@before.all
def connect_to_mongodb():
    world.mongo_client = MongoClient()
    world.event_collection = world.mongo_client['track']['events']


@before.each_scenario
def reset_captured_events(_scenario):
    world.event_collection.drop()


@before.outline
def reset_between_outline_scenarios(_scenario, order, outline, reasons_to_fail):
    world.event_collection.drop()


@step('[aA]n? "(.*)" (server|browser) event is emitted')
def event_is_emitted(_step, event_type, event_source):

    # Ensure all events are written out to mongo before querying.
    world.mongo_client.fsync()

    # Note that splinter makes 2 requests when you call browser.visit('/foo')
    # the first just checks to see if the server responds with a status
    # code of 200, the next actually uses the browser to submit the request.
    # We filter out events associated with the status code checks by ignoring
    # events that come directly from splinter.
    criteria = {
        'event_type': event_type,
        'event_source': event_source,
        'agent': {
            '$ne': 'python/splinter'
        }
    }
    cursor = world.event_collection.find(criteria)
    assert_equals(cursor.count(), 1)

    event = cursor.next()

    expected_field_values = {
        "username": world.scenario_dict['USER'].username,
        "event_type": event_type,
    }
    for key, value in expected_field_values.iteritems():
        assert_equals(event[key], value)
