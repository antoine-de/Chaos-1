# Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

from flask_restful import fields, url_for
from flask import current_app, request
from utils import make_fake_pager, get_coverage, get_token, get_current_time
from chaos.navitia import Navitia
from copy import deepcopy


class FieldDateTime(fields.Raw):
    def format(self, value):
        if value:
            return value.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return None


class FieldTime(fields.Raw):
    def format(self, value):
        try:
            return value.strftime('%H:%M')
        except:
            return None


class FieldDate(fields.Raw):
    def format(self, value):
        if value:
            return value.strftime('%Y-%m-%d')
        else:
            return None


class FieldPaginateImpacts(fields.Raw):
    '''
    Pagination of impacts list for one disruption
    '''
    def output(self, key, disruption):
        return make_fake_pager(disruption.impacts.count(), 20,
                          'impact',
                          disruption_id=disruption.id)


class FieldUrlDisruption(fields.Raw):
    def output(self, key, obj):
        return {'href': url_for('disruption',
                                id=obj.disruption_id,
                                _external=True)}


class FieldObjectName(fields.Raw):
    def output(self, key, obj):
        if not obj:
            return None
        if obj.type == 'line_section':
            return None
        navitia = Navitia(
            current_app.config['NAVITIA_URL'],
            get_coverage(request),
            get_token(request))
        response = navitia.get_pt_object(obj.uri, obj.type)
        if response and 'name' in response:
            return response['name']
        return 'Unable to find object'


class FieldLocalization(fields.Raw):
    def output(self, key, obj):
        to_return = []
        navitia = Navitia(current_app.config['NAVITIA_URL'],
                          get_coverage(request),
                          get_token(request))
        for localization in obj.localizations:
            response = navitia.get_pt_object(
                localization.uri,
                localization.type)

            if response and 'name' in response:
                response["type"] = localization.type
                to_return.append(response)
            else:
                to_return.append(
                    {
                        "id": localization.uri,
                        "name": "Unable to find object",
                        "type": localization.type
                    }
                )
        return to_return


class FieldContributor(fields.Raw):
    def output(self, key, obj):
        if hasattr(obj, 'contributor'):
            return obj.contributor.contributor_code
        return None


class FieldChannelTypes(fields.Raw):
    def output(self, key, obj):
        if hasattr(obj, 'channel_types'):
            return [ch.name for ch in obj.channel_types]
        return None


class FieldLinks(fields.Raw):
    def output(self, key, obj):
        if obj and "impacts" in obj:
            return [{"internal": True,
                     "type": "disruption",
                     "id": impact.id,
                     "rel": "disruptions",
                     "template": False} for impact in obj["impacts"]]
        return None


class ComputeDisruptionStatus(fields.Raw):
    def output(self, key, obj):
        current_datetime = get_current_time()
        is_future = False
        for application_period in obj.application_periods:
            if current_datetime >= application_period.start_date and current_datetime <= application_period.end_date:
                return 'active'
            if current_datetime <= application_period.start_date:
                is_future = True
        if is_future:
            return 'future'
        return 'past'


class FieldCause(fields.Raw):
    def output(self, key, obj):
        if hasattr(obj.disruption, 'cause') and hasattr(obj.disruption.cause, 'wording'):
            return obj.disruption.cause.wording
        return None


class FieldAssociatedProperties(fields.Raw):
    def output(self, key, obj):
        properties = {}
        if obj.properties:
            for property in obj.properties:
                prop = property.property
                properties.setdefault(prop.type, []).append(
                    {
                        'value': property.value,
                        'property': {
                            'id': prop.id,
                            'created_at': FieldDateTime().format(
                                prop.created_at
                            ),
                            'updated_at': FieldDateTime().format(
                                prop.updated_at
                            ),
                            'self': {
                                'href': url_for(
                                    'property',
                                    id=prop.id,
                                    _external=True
                                )
                            },
                            'key': prop.key,
                            'type': prop.type
                        }
                    }
                )
        return properties

href_field = {
    "href": fields.String
}

wording_fields = {
    "key": fields.Raw,
    "value": fields.Raw
}

category_fields = {
    'id': fields.Raw,
    'name': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'self': {'href': fields.Url('category', absolute=True)}
}

cause_fields = {
    'id': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'self': {'href': fields.Url('cause', absolute=True)},
    'wordings': fields.List(fields.Nested(wording_fields)),
    'category': fields.Nested(category_fields, allow_null=True),
}

causes_fields = {
    'causes': fields.List(fields.Nested(cause_fields)),
    'meta': {}
}

one_cause_fields = {
    'cause': fields.Nested(cause_fields, display_null=False)
}

tag_fields = {
    'id': fields.Raw,
    'name': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'self': {'href': fields.Url('tag', absolute=True)}
}

tags_fields = {
    'tags': fields.List(fields.Nested(tag_fields)),
    'meta': {}
}

one_tag_fields = {
    'tag': fields.Nested(tag_fields)
}

property_fields = {
    'id': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'self': {'href': fields.Url('property', absolute=True)},
    'key': fields.Raw,
    'type': fields.Raw
}

one_property_fields = {
    'property': fields.Nested(property_fields, display_null=False)
}

properties_fields = {
    'properties': fields.List(fields.Nested(property_fields))
}

one_category_fields = {
    'category': fields.Nested(category_fields)
}

categories_fields = {
    'categories': fields.List(fields.Nested(category_fields)),
    'meta': {}
}

disruption_fields = {
    'id': fields.Raw,
    'self': {'href': fields.Url('disruption', absolute=True)},
    'reference': fields.Raw,
    'note': fields.Raw,
    'status': fields.Raw,
    'version': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'publication_period': {
        'begin': FieldDateTime(attribute='start_publication_date'),
        'end': FieldDateTime(attribute='end_publication_date')
    },
    'publication_status': fields.Raw,
    'contributor': FieldContributor,
    'impacts': FieldPaginateImpacts(attribute='impacts'),
    'localization': FieldLocalization(attribute='localizations'),
    'cause': fields.Nested(cause_fields, allow_null=True),
    'tags': fields.List(fields.Nested(tag_fields)),
    'properties': FieldAssociatedProperties(attribute='properties')
}

paginate_fields = {
    "start_page": fields.String,
    "items_on_page": fields.String,
    "items_per_page": fields.String,
    "total_result": fields.String,
    "prev": fields.Nested(href_field),
    "next": fields.Nested(href_field),
    "first": fields.Nested(href_field),
    "last": fields.Nested(href_field)
}

meta_fields = {
    "pagination": fields.Nested(paginate_fields)
}

disruptions_fields = {
    "meta": fields.Nested(meta_fields),
    "disruptions": fields.List(fields.Nested(disruption_fields))
}

one_disruption_fields = {
    'disruption': fields.Nested(disruption_fields)
}

error_fields = {
    'error': fields.Nested({'message': fields.String})
}

base_severity_fields = {
    'id': fields.Raw,
    'color': fields.Raw,
    'priority': fields.Integer(default=None),
    'effect': fields.Raw()
}

severity_fields = deepcopy(base_severity_fields)
severity_fields['wording'] = fields.Raw
severity_fields['created_at'] = FieldDateTime
severity_fields['updated_at'] = FieldDateTime
severity_fields['self'] = {'href': fields.Url('severity', absolute=True)}
severity_fields['wordings'] = fields.List(fields.Nested(wording_fields))

base_severity_fields['name'] = fields.Raw(attribute='wording')


severities_fields = {
    'severities': fields.List(fields.Nested(severity_fields)),
    'meta': {},
}

one_severity_fields = {
    'severity': fields.Nested(severity_fields)
}

one_objectTC_generic_fields = {
    'id': fields.Raw(attribute='uri'),
    'type': fields.Raw
}

one_objectTC_fields = deepcopy(one_objectTC_generic_fields)
one_objectTC_fields['name'] = FieldObjectName()

line_section_fields = {
    'line': fields.Nested(one_objectTC_fields, display_null=False),
    'start_point': fields.Nested(one_objectTC_fields, display_null=False),
    'end_point': fields.Nested(one_objectTC_fields, display_null=False),
    'sens': fields.Integer(default=None),
    'routes': fields.List(
        fields.Nested(one_objectTC_fields, display_null=False),
        display_empty=False),
    'via': fields.List(
        fields.Nested(
            one_objectTC_fields,
            display_null=False),
        display_empty=False),
    'metas': fields.List(fields.Nested(wording_fields),
                         attribute='wordings',
                         display_empty=False),
}

objectTC_fields = {
    'id': fields.Raw(attribute='uri'),
    'type': fields.Raw,
    'name': FieldObjectName(),
    'line_section': fields.Nested(
        line_section_fields,
        display_null=False,
        allow_null=True)
}

channel_type_fields = {
    'name': fields.Raw
}

base_channel_fields = {
    'id': fields.Raw,
    'name': fields.Raw,
    'max_size': fields.Integer(default=None),
    'content_type': fields.Raw,
    'types': FieldChannelTypes()
}

channel_fields = deepcopy(base_channel_fields)
channel_fields['created_at'] = FieldDateTime
channel_fields['updated_at'] = FieldDateTime
channel_fields['self'] = {'href': fields.Url('channel', absolute=True)}

channels_fields = {
    'channels': fields.List(fields.Nested(channel_fields)),
    'meta': {}
}

one_channel_fields = {
    'channel': fields.Nested(channel_fields)
}

base_message_fields = {
    'text': fields.Raw,
    'channel': fields.Nested(base_channel_fields)
}

message_fields = deepcopy(base_message_fields)

message_fields["created_at"] = FieldDateTime
message_fields["updated_at"] = FieldDateTime
message_fields["channel"] = fields.Nested(channel_fields)

application_period_fields = {
    'begin': FieldDateTime(attribute='start_date'),
    'end': FieldDateTime(attribute='end_date')
}

time_slot_fields = {
    'begin': FieldTime,
    'end': FieldTime
}

application_period_pattern_fields = {
    'start_date': FieldDate,
    'end_date': FieldDate,
    'weekly_pattern': fields.Raw,
    'time_slots': fields.List(fields.Nested(time_slot_fields, display_null=False), attribute='time_slots')
}

impact_fields = {
    'id': fields.Raw,
    'created_at': FieldDateTime,
    'updated_at': FieldDateTime,
    'objects': fields.List(fields.Nested(objectTC_fields, display_null=False)),
    'application_periods':
        fields.List(fields.Nested(application_period_fields)),
    'severity': fields.Nested(severity_fields),
    'self': {'href': fields.Url('impact', absolute=True)},
    'disruption': FieldUrlDisruption(),
    'messages': fields.List(fields.Nested(message_fields)),
    'application_period_patterns':
        fields.List(fields.Nested(application_period_pattern_fields), attribute='patterns'),
    'send_notifications': fields.Raw,
    'notification_date': FieldDateTime
}

one_impact_fields = {
    'impact': fields.Nested(impact_fields)
}

impacts_fields = {
    'meta': fields.Nested(meta_fields),
    'impacts': fields.List(fields.Nested(impact_fields))
}

impact_by_object_fields = {
    'id': fields.Raw,
    'type': fields.Raw,
    'name': fields.Raw,
    'impacts': fields.List(fields.Nested(impact_fields))
}

impacts_by_object_fields = {
    'objects': fields.List(fields.Nested(impact_by_object_fields))
}

generic_type = {
    "name": fields.String(),
    "id": fields.String(),
    "type": fields.String(),
    "links": FieldLinks(),
}

line_fields = deepcopy(generic_type)
line_fields['code'] = fields.String()

line_section_for_traffic_report_fields = {
    "line": fields.Nested(line_fields, display_null=False),
    "start_point": fields.Nested(generic_type, display_null=False),
    "end_point": fields.Nested(generic_type, display_null=False),
    'routes': fields.List(
        fields.Nested(one_objectTC_generic_fields, display_null=False),
        display_empty=False),
    'via': fields.List(
        fields.Nested(
            one_objectTC_generic_fields,
            display_null=False),
        display_empty=False),
    'metas': fields.List(fields.Nested(wording_fields)),
}

line_sections_fields = {
    "id": fields.String(),
    "type": fields.String(),
    "line_section": fields.Nested(line_section_for_traffic_report_fields, display_null=False),
    "links":FieldLinks()
}

traffic_report_fields = {
    "network": fields.Nested(generic_type, display_null=False),
    "lines": fields.List(fields.Nested(line_fields, display_null=False)),
    "stop_areas": fields.List(fields.Nested(generic_type, display_null=False)),
    "stop_points": fields.List(fields.Nested(generic_type, display_null=False)),
    "line_sections": fields.List(fields.Nested(line_sections_fields, display_null=False))
}

traffic_report_impact_field = {
    "disruption_id": fields.String(),
    "id": fields.String(attribute="id"),
    "severity": fields.Nested(base_severity_fields, display_null=False),
    "application_periods": fields.List(fields.Nested(application_period_fields)),
    "messages": fields.List(fields.Nested(base_message_fields)),
    "cause": FieldCause(),
    "status": ComputeDisruptionStatus()
}

traffic_reports_marshaler = {
    'traffic_reports': fields.List(fields.Nested(traffic_report_fields, display_null=False)),
    'disruptions': fields.List(fields.Nested(traffic_report_impact_field, display_null=False))
}
