#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from toscaparser.elements.capabilitytype import CapabilityTypeDef

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTypeError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.elements.capabilities import CapabilityDefinitions
from toscaparser.elements.statefulentitytype import StatefulEntityType


class GroupType(StatefulEntityType):
    '''TOSCA built-in group type.'''

    SECTIONS = (DERIVED_FROM, VERSION, METADATA, DESCRIPTION, PROPERTIES,
                MEMBERS, INTERFACES, CAPABILITIES, REQUIREMENTS) = \
               ("derived_from", "version", "metadata", "description",
                "properties", "members", "interfaces", 'capabilities', 'requirements')

    def __init__(self, grouptype, custom_def=None):
        super(GroupType, self).__init__(grouptype, self.GROUP_PREFIX,
                                        custom_def)
        self.custom_def = custom_def
        self.grouptype = grouptype
        self._validate_fields()
        self.group_description = None
        if self.DESCRIPTION in self.defs:
            self.group_description = self.defs[self.DESCRIPTION]

        self.group_version = None
        if self.VERSION in self.defs:
            self.group_version = self.defs[self.VERSION]

        self.group_properties = None
        if self.PROPERTIES in self.defs:
            self.group_properties = self.defs[self.PROPERTIES]

        self.group_members = None
        if self.MEMBERS in self.defs:
            self.group_members = self.defs[self.MEMBERS]

        if self.METADATA in self.defs:
            self.meta_data = self.defs[self.METADATA]
            self._validate_metadata(self.meta_data)


    @property
    def capabilities(self):
        return self.get_capabilities_objects()

    def get_capabilities_objects(self):
        '''Return a list of capability objects.'''
        typecapabilities = []
        caps = self.get_value(self.CAPABILITIES, None, True)
        if caps:
            # 'name' is symbolic name of the capability
            # 'value' is a dict { 'type': <capability type name> }
            for name, value in caps.items():
                ctype = value.get('type')
                cap = CapabilityTypeDef(name, ctype, self.type,
                                        self.custom_def)
                typecapabilities.append(cap)
        return typecapabilities

    def get_capabilities(self):
        '''Return a dictionary of capability name-objects pairs.'''
        return {cap.name: cap
                for cap in self.get_capabilities_objects()}

    def get_capability(self, name):
        caps = self.get_capabilities()
        if caps and name in caps.keys():
            return caps[name]

    def get_capability_type(self, name):
        captype = self.get_capability(name)
        if captype:
            return captype.type

    @property
    def requirements(self):
        return self.get_value(self.REQUIREMENTS, None, True)

    def get_all_requirements(self):
        return self.requirements


    @property
    def parent_type(self):
        '''Return a group statefulentity of this entity is derived from.'''
        if not hasattr(self, 'defs'):
            return None
        pgroup_entity = self.derived_from(self.defs)
        if pgroup_entity:
            return GroupType(pgroup_entity, self.custom_def)

    @property
    def description(self):
        return self.group_description

    @property
    def version(self):
        return self.group_version

    @property
    def interfaces(self):
        return self.get_value(self.INTERFACES)

    def _validate_fields(self):
        if self.defs:
            for name in self.defs.keys():
                if name not in self.SECTIONS:
                    ExceptionCollector.appendException(
                        UnknownFieldError(what='Group Type %s'
                                          % self.grouptype, field=name))

    def _validate_metadata(self, meta_data):
        if not meta_data.get('type') in ['map', 'tosca:map']:
            ExceptionCollector.appendException(
                InvalidTypeError(what='"%s" defined in group for '
                                 'metadata' % (meta_data.get('type'))))
        for entry_schema, entry_schema_type in meta_data.items():
            if isinstance(entry_schema_type, dict) and not \
                    entry_schema_type.get('type') == 'string':
                ExceptionCollector.appendException(
                    InvalidTypeError(what='"%s" defined in group for '
                                     'metadata "%s"'
                                     % (entry_schema_type.get('type'),
                                        entry_schema)))
