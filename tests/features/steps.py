from lettuce import *
from nose.tools import *
import re
from chaos import db
from chaos.formats import id_format
from chaos.models import Disruption, Severity, Cause, Impact, PTobject,\
    Channel, Message, ApplicationPeriods, Tag, associate_impact_pt_object,\
    associate_disruption_tag, LineSection,\
    associate_line_section_route_object, associate_line_section_via_object,\
    Client, Contributor, associate_disruption_pt_object, Category, Wording, \
    associate_wording_severity, Pattern, TimeSlot, ChannelType,\
    associate_wording_line_section, Property, AssociateDisruptionProperty
import chaos

model_classes = {
    'disruption': Disruption,
    'severity': Severity,
    'cause': Cause,
    'disruptions': Disruption,
    'severities': Severity,
    'causes': Cause,
    'impact': Impact,
    'impacts': Impact,
    'ptobject': PTobject,
    'channel': Channel,
    'channels': Channel,
    'messages': Message,
    'applicationperiods': ApplicationPeriods,
    'tag': Tag,
    'tags': Tag,
    'line_section': LineSection,
    'clients': Client,
    'client': Client,
    'contributors': Contributor,
    'contributor': Contributor,
    'categories': Category,
    'wording': Wording,
    'pattern': Pattern,
    'timeslot': TimeSlot,
    'channel_type': ChannelType,
    'properties': Property,
    'associate_disruption_properties': AssociateDisruptionProperty
}

associations = {
    'associate_impact_pt_object': associate_impact_pt_object,
    'associate_disruption_tag': associate_disruption_tag,
    'associate_line_section_route_object': associate_line_section_route_object,
    'associate_line_section_via_object': associate_line_section_via_object,
    'associate_disruption_pt_object': associate_disruption_pt_object,
    'associate_wording_severity': associate_wording_severity,
    'associate_wording_line_section': associate_wording_line_section
}


def pythonify(value):
    if value.isdigit():
        return int(value)
    if value == 'False':
        return False
    if value == 'True':
        return True
    return value


def find_field(json, fields):
    separated_fields = map(pythonify, fields.split('.'))
    current_node = json

    field_found = True
    for field in separated_fields:
        try:
            current_node = current_node[field]
        except KeyError:
            field_found = False
            pass

    if not field_found:
        return False

    return current_node


@step(u'I (\w+) (?:to\s)?"([^"]+)"(?:\swith:)?')
def when_i_post_to(step, method, url):
    if step.multiline:
        data = step.multiline
    else:
        data = None
    if hasattr(world, 'headers'):
        headers = world.headers
    else:
        headers = {'content-type': 'application/json'}
    world.response = world.client.open(path=url, method=method, data=data, headers=headers)


@step('I fill in header "(.*?)" with "(.*?)"')
def i_fill_in_header(step, field_name, value):
    world.headers[field_name] = value


@step('I clean header')
def i_clean_header(step):
    if hasattr(world, 'headers'):
        world.headers = {'content-type': 'application/json'}


@step(u'Then the status code should be "(\d+)"')
def then_the_status_code_should_be(step, status_code):
    eq_(world.response.status_code, int(status_code))


@step(u'And the header "([^"]*)" should be "([^"]*)"')
def and_the_header_is_set_to(step, header, value):
    eq_(world.response.headers[header], value)


@step(u'And the field "([^"]*)" should be "([^"]*)"')
def and_in_the_json_the_field_is_set_to(step, fields, value):
    value = pythonify(value)
    eq_(find_field(world.response_json, fields), value)


@step(u'And the field "([^"]*)" should be null')
def and_in_the_json_the_field_is_null(step, fields):
    eq_(find_field(world.response_json, fields), None)


@step(u'And the field "([^"]*)" should be not null')
def and_in_the_json_the_field_is_not_null(step, fields):
    assert_not_equal(find_field(world.response_json, fields), None)


@step(u'and "([^"]*)" should be empty')
def and_field_should_be_empty(step, fields):
    assert_equals(len(find_field(world.response_json, fields)), 0)


@step(u'And the field "([^"]*)" should have a size of (\d+)')
def and_the_field_should_have_a_size_of_n(step, fields, size):
    eq_(len(find_field(world.response_json, fields)), int(size))


@step(u'And the field "([^"]*)" should exist')
def and_the_field_should_exist(step, fields):
    assert_not_equals(len(find_field(world.response_json, fields)), 0)


@step(u'And the field "([^"]*)" should not exist')
def and_the_field_should_not_exist(step, fields):
    assert_equals(find_field(world.response_json, fields), False)


@step(u'And the field "([^"]*)" should be (\d+)')
def and_in_the_json_the_field_is_int(step, fields, value):
    eq_(int(find_field(world.response_json, fields)), int(value))


@step(u'And the field "([^"]*)" should contain "([^"]*)"')
def and_in_the_json_the_field_contain(step, fields, value):
    assert(value in find_field(world.response_json, fields))


@step(u'And the field "([^"]*)" should be an id')
def and_in_the_json_the_field_is_an_id(step, fields):
    assert(re.match(id_format, find_field(world.response_json, fields)))


@step(u'And in the database for the (\w+) "([^"]+)" the field "([^"]*)" should be "([^"]*)"')
def and_in_the_database_the_severity_group1_the_field_group2_should_be_group3(step, cls, id, field, value):
    #this way flask manage the sqlalchemy session
    with chaos.app.app_context():
        row = model_classes[cls].query.filter_by(id=id).first()
        eq_(getattr(row, field), pythonify(value))


@step(u'Given I have the following (\w+) in my database:')
def given_i_have_the_following_causes_in_my_database(step, cls):
    for values_dict in step.hashes:
        row = model_classes[cls]()
        for key, value in values_dict.iteritems():
            if value == 'None':
                value = None
            setattr(row, key, value)
        db.session.add(row)
    db.session.commit()


@step(u'Given I have the relation (\w+) in my database:')
def given_i_have_the_relation_in_my_database(step, cls):
    for values_dict in step.hashes:
        keys = []
        values = []
        for key, value in values_dict.iteritems():
            keys.append(key)
            values.append("'{}'".format(value))
        db.session.execute("INSERT INTO {} ({}) VALUES ({})".format(associations[cls], ','.join(keys), ','.join(values)))
    db.session.commit()


@step(u'And the field "([^"]*)" should contain all of "(.*)"')
def and_the_field_group1_should_contain_all_of_group2(step, group1, group2):
    import json
    group2_json = json.loads(group2)
    group2_keys = set(group2_json.keys())
    for obj in find_field(world.response_json, group1):
        obj_keys = set(obj.keys())
        if group2_keys.issubset(obj_keys):
            exists = True
            for k in group2_keys:
                exists = exists and (obj[k] == group2_json[k])
            if exists:
                assert True
        else:
            assert False
