#!/usr/bin/env python3
"""Offline regression test for the source-to-source UI patch. No Enigma2 runtime needed."""
import importlib.util
import os
import tempfile
import shutil
import xml.etree.ElementTree as ET

this_dir=os.path.dirname(__file__)
spec=importlib.util.spec_from_file_location('patch',os.path.join(this_dir,'upgrade_neoradio_3_1_0.py'))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# Minimal syntactically valid source with anchors copied from 3.0.0.
fhd='''\
def get_skin():
    return """
        <screen name="NeoRadioMain" position="center,center" size="1680,940">
            <eLabel position="22,20" size="500,840" backgroundColor="#00101a2d" zPosition="0" />
            <widget name="key_yellow" position="542,882" size="240,30" font="Regular;24" foregroundColor="#00000000" backgroundColor="#00b99211" halign="center" valign="center" zPosition="2" />
            <widget name="key_info" position="1362,882" size="296,30" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />
        </screen>
    """
    return """
        <screen name="NeoRadioMain" position="center,center" size="1180,660">
        <eLabel position="20,20" size="420,560" backgroundColor="#00101a2d" zPosition="0" />
        <widget name="key_yellow" position="320,614" size="140,24" font="Regular;18" foregroundColor="#00000000" backgroundColor="#00b99211" halign="center" valign="center" zPosition="2" />
        <widget name="key_info" position="850,614" size="220,24" font="Regular;18" foregroundColor="#00ffffff" backgroundColor="#00434b5b" halign="center" valign="center" zPosition="2" />
        </screen>
    """

def get_about_skin():
    return """<screen name="NeoRadioAbout" position="center,center" size="1120,650"></screen>"""
    return """<screen name="NeoRadioAbout" position="center,center" size="820,470"></screen>"""

class NeoRadioMain(object):
    def __init__(self):
        self["footer_brand"] = Label(text_type(""))
'''
source='PLUGIN_VERSION = "3.0.0"\n'+fhd
s=mod.new_plugin(source)
assert s.count('name="credits_footer"')==2
assert s.count('self["credits_footer"] = Label')==1
assert 'PLUGIN_VERSION = "3.1.0"' in s
assert s==mod.new_plugin(s)
assert 'name="credits_footer"' not in source
print('PASS: XML in both skins, version, initialization, strict anchors, idempotence')
