# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from datetime import datetime
import StringIO

import stix.bindings.stix_core as stix_core_binding
import stix.bindings.stix_common as stix_common_binding
import stix.bindings.incident as stix_incident_binding
import cybox.bindings.cybox_common as cybox_common_binding
import cybox.bindings.cybox_core as cybox_core_binding


class StixTransformer(object):

    def transform(self, event):

        cybox_ipaddress = cybox_core_binding.AddressObjectType()
        cybox_ipaddress.is_source = True
        cybox_ipaddress_value = cybox_common_binding.StringObjectPropertyType()
        cybox_ipaddress_value.set_valueOf_(event['remote'][0])
        cybox_ipaddress.set_Address_Value(cybox_ipaddress_value)

        cybox_port = cybox_core_binding.PortObjectType()
        cybox_port_value = cybox_common_binding.StringObjectPropertyType()
        cybox_port_value.set_valueOf_(event['remote'][1])
        cybox_port.set_Port_Value(cybox_port_value)

        cybox_socketAddress = cybox_core_binding.SocketAddressObjectType()
        cybox_socketAddress.set_IP_Address(cybox_ipaddress)
        cybox_socketAddress.set_Port(cybox_port)

        cybox_networkConnection = cybox_core_binding.NetworkConnectionObjectType()
        cybox_networkConnection.set_Source_Socket_Address(cybox_socketAddress)

        cybox_l7_protocol = cybox_common_binding.StringObjectPropertyType()
        cybox_l7_protocol.set_valueOf_(event['data_type'])
        cybox_networkConnection.set_Layer7_Protocol(cybox_l7_protocol)

        stix_related_observable = stix_common_binding.RelatedObservableType()
        stix_related_observable.set_Observable(cybox_networkConnection)

        stix_related_observables = stix_incident_binding.RelatedObservablesType()
        stix_related_observables.add_Related_Observable(stix_related_observable)

        stix_incident = stix_incident_binding.IncidentType()
        stix_incident.set_Related_Observables(stix_related_observables)
        stix_incident_description = stix_common_binding.StructuredTextType()
        stix_incident_description.set_valueOf_('Traffic to ConPot honeypot')
        stix_incident.set_Description(stix_incident_description)
        stix_incident.set_id(event['session_id'])

        stix_incident_category = stix_common_binding.ControlledVocabularyStringType()
        stix_incident_category.set_valueOf_('Scans/Probes/Attempted Access')
        stix_incident_categories = stix_incident_binding.CategoriesType()
        stix_incident_categories.add_Category(stix_incident_category)
        stix_incident.set_Categories(stix_incident_categories)

        # how do we set timezone?
        stix_incident_time = stix_incident_binding.TimeType()
        stix_incident_time.set_First_Malicious_Action(datetime.now())
        stix_incident.set_Time(stix_incident_time)

        stix_package = stix_core_binding.STIXType()
        stix_header = stix_core_binding.STIXHeaderType()

        stix_header_description = stix_common_binding.StructuredTextType()
        stix_header_description.set_valueOf_('Describes one or more honeypot incidents')

        stix_header_title = stix_common_binding.StructuredTextType()
        stix_header_title.set_valueOf_('Observed traffic to honeypot')

        stix_header_time = cybox_common_binding.TimeType()
        stix_header_time.set_Produced_Time(datetime.now())
        stix_header_info_source = stix_common_binding.InformationSourceType()
        stix_header_info_source.set_Time(stix_header_time)
        stix_header.set_Description(stix_header_description)
        stix_header.set_Information_Source(stix_header_info_source)
        stix_package.set_Incidents(stix_incident)
        stix_package.set_STIX_Header(stix_header)

        output = StringIO.StringIO()
        stix_package.export(output, 0, stix_core_binding.DEFAULT_XML_NS_MAP)
        return output.getvalue()


if __name__ == '__main__':

        test_event =      {'remote': ('1.2.3.4', 54872), 'data_type': 'modbus',
                           'timestamp': datetime.now(),
                           'session_id': '101d9884-b695-4d8b-bf24-343c7dda1b68',
                           'public_ip': '111.222.222.111'}
        transformer = StixTransformer()
        xml_string = transformer.transform(test_event)
        print xml_string
