#!/usr/bin/python
#
# Copyright 2025 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2025-12-03.
#
# Create BDS (baramundi deploy script) files.
# Output needs work.
# 20251203 Nick Heim: Initial release.

"""
BDS Generator

This is a processor for AutoPkg.

Important! You *must* install the lxml library to AutoPkg's Python framework.
You can do this by running:

pip install lxml

Due to limitiation in YAML, 'PropertyEntry' tags must be provided in XML notation.
YAML can not work with more than one tag with the same name.
See example recipes for usage.
"""
import os
import sys
import uuid
from datetime import datetime
from lxml import etree as ET

from autopkglib import Processor, ProcessorError

def _is_simple_value(v):
    return v is None or isinstance(v, (str, int, float, bool, bytes))

def _dict_is_all_simple(d):
    # True wenn alle Werte einfache Typen sind -> Attribute sinnvoll
    return all(_is_simple_value(v) for v in d.values())

__all__ = ["BDSGenerator"]

class BDSGenerator(Processor):
    description = "Create deploy script file for baramundi (BDS)."
    input_variables = {
        "BDS_file": {
            "required": True,
            "description": "Path to the BDS file file to write, required",
        },
        "new_actions": {
            "required": True,
            "description": "Array of dicts with action(s) to add, required",
        },
        "input_file": {
            "required": False,
            "default": "default_content",
            "description": "Script to start with. If not provided, a minimal default fragment will be used.",
        },
        "new_author": {
            "required": False,
            "description": 'Set a different "Author" for the script. Defaults to "AutoPkg"',
        },
        "ignore_errors": {
            "required": False,
            "description": "Ignore any errors during the run.",
        },
    }
    output_variables = {
    }

    __doc__ = description

    ATTR_KEYS = {"type", "level", "breakpoint", "ignore_error", "comment", "is_included", "logging_enabled", "op1", "op", "op2", "options"}
    
    DEFAULT_ACTION_ATTRS = {
        "type": "Comment",
        "level": "0",
        "breakpoint": "0",
        "ignore_error": "0",
        "comment": "0",
        "is_included": "0",
        "logging_enabled": "1"
    }

    def convert_dict_to_xml_recursively(self, parent_el, dict_item):
        assert isinstance(dict_item, dict), "Must provide a dictionary"
        
        for (k, v) in dict_item.items():
            # self.output( "Recursive value: %s" % v)
            if isinstance(v, dict):
                # The <CONDITION> element needs special handling,
                # because its sub elements are actually attributes.
                if k == "CONDITION":
                    sub_elem = ET.SubElement(parent_el, "CONDITION", **v)
                    # self.output( "CONDITION-Attr: %s" % v)
                # elif k == "ACTION":
                    # #self.output( "ACTION-Elem: %s" % k)
                else:
                    self.output( "DICT: %s" % v)
                    sub_elem = ET.SubElement(parent_el, k)
                self.convert_dict_to_xml_recursively(sub_elem, v)
            else:
                if not k in self.ATTR_KEYS:
                # continue
                    sub_elem = ET.SubElement(parent_el, k)
                    sub_elem.text = str(v)
                
    def create_action_element(self, parent, action_dict, default_attrs=DEFAULT_ACTION_ATTRS):
        """
        The creation of the <ACTION> element needs special handling,
        because the attribute have default values, but can be changed as needed.
        The sub elements are then being created recursively.
        """
        # self.output( "ACTION-Elem: %s" % action_dict)
        # self.output( "ACTION-Element-Value: %s" % (action_dict["ACTION"]).split('|||'))
        
        # Get the attributes from the <ACTION> element.
        attrib_list = (action_dict["ACTION"]).split('|||')
        # self.output( "ACTION-Value-Type: %s" % type(attrib_list))

        attrib_dict ={}
        for i in attrib_list:
        #Get Key Value pairs separately to store in dictionary
            keyvalue = i.split(":")
            attrib_dict[keyvalue[0].strip()] = keyvalue[1].strip()
            
        # self.output( "ACTION-attrib_dict: %s" % attrib_dict)
      
        # Get the default attributes. Copies DEFAULT_ACTION_ATTRS to let it stay unchanged.
        attrs = default_attrs.copy()
        
        # Writing the explicitly set attributes over the defaults.
        for k in default_attrs:
            if k in attrib_dict:
                # This could have some extra work/thinking, but works for now
                attrs[k] = str(attrib_dict[k]) if attrib_dict[k] is not None else ""
                
        # Finally create the <ACTION> element with its attributes.
        try:
            action_el = ET.SubElement(parent, "ACTION", **attrs)
        except TypeError as e:
            self.output( "SubElement error, parent type: %s" % type(parent))
            for k, v in attrs.items():
                print(" attr", k, "->", type(v), repr(v))
            raise
        
        # Remove the <ACTION> element from the dictionary.
        del action_dict['ACTION']
        
        # Call the subroutine to recursively create the underlying elements.
        self.convert_dict_to_xml_recursively(action_el, action_dict)
        
        return action_el
            
    def main(self):
        BDS_file = self.env.get('BDS_file')
        new_actions = self.env.get('new_actions')
        ignore_errors = self.env.get('ignore_errors', True)
        verbosity = self.env.get('verbose', 1)

        # self.output( "new_actions: %s" % new_actions)
        if "input_file" in self.env:
            input_file = self.env.get('input_file')

            # We provide a minimal default fragment to start with, if there is no input file.
            if input_file == "default_content":
                default_content = '''\
<baramundiDeployScript Version="2420" LastChange="29.11.2025 09:08:32">
<META>
<INFO Vendor="" Name="" Version="" Author="Autopkg" Comment=""/>
<STATICVARS LoadInstallIni="1">
<BMSVars>""</BMSVars>
</STATICVARS>
</META>
<ACTIONS>
</ACTIONS>
</baramundiDeployScript>
'''


                BDSData = ET.fromstring(default_content)
            else:
                BDSData = ET.parse(input_file).getroot()

        # Set the author, if provided
        if "new_author" in self.env:
            new_author = self.env.get('new_author')            
            BDS_INFO = BDSData.find(".//INFO")
            BDS_INFO.set("Author", new_author)
        
        # Set the element under which we put the new ones in.
        BDS_ACTIONS = BDSData.find("ACTIONS")
        # Walk through the dictionary with the actions.
        for pi,ACTIONS_new in enumerate(new_actions):
            # self.output( "ACTION: %s" % ACTIONS_new)
            self.create_action_element(BDS_ACTIONS, ACTIONS_new)

        # Create new time stamp
        new_ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        # Set "LastChange"
        BDSData.set("LastChange", new_ts)

        # Set the indent for pretty printing
        ET.indent(BDSData, space="  ")

        xml_bytes = ET.tostring(BDSData, pretty_print=False, xml_declaration=True, encoding="ISO-8859-1")

        # Write the BDS file
        with open(BDS_file, "wb") as f:
            f.write(xml_bytes)

        # Read in the BDS file again
        with open(BDS_file, "r") as editfile:
            filedata = editfile.read()
        # Replace the escape for "<>"
        newdata = filedata.replace("&lt;","<")
        newdata = newdata.replace("&gt;",">")
        newdata = newdata.replace("&amp;","&")
        newdata = newdata.replace("&#38;","&")
        
        # And create the final file (overwrite).
        with open(BDS_file, "w") as wfile:
            wfile.write(newdata)

if __name__ == '__main__':
    processor = BDSGenerator()
    processor.execute_shell()
