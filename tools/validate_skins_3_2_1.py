#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline structural verification for NeoRadio 3.2.1 (HD/FHD, Py2-compatible UI)."""
from __future__ import print_function
import ast
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR=ROOT/'pkgroot/usr/lib/enigma2/python/Plugins/Extensions/NeoRadio'
PLUGIN=PLUGIN_DIR/'plugin.py'
CONTROL=ROOT/'release/CONTROL/control'
sys.path.insert(0,str(PLUGIN_DIR))
from skin_layouts import create_theme_skin


def fail(msg):
    raise SystemExit('BŁĄD: '+msg)

def png_size(p):
    with open(p,'rb') as h:
        head=h.read(24)
    if len(head)!=24 or head[:8]!=b'\x89PNG\r\n\x1a\n':
        fail('Nieprawidłowy PNG: '+str(p))
    return struct.unpack('>II',head[16:24])


def main():
    source=PLUGIN.read_text(encoding='utf-8')
    tree=ast.parse(source)
    if 'PLUGIN_VERSION = "3.2.1"' not in source:fail('Wersja w plugin.py jest nieprawidłowa')
    if 'Version: 3.2.1' not in CONTROL.read_text(encoding='utf-8'):fail('Wersja CONTROL/control jest nieprawidłowa')
    if 'self.skin = get_skin()' not in source:fail('Brakuje wyboru skina dla instancji')
    if 'self["detail_bitrate"]' not in source:fail('Brakuje dynamicznych danych Future')
    f=next((node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='get_default_skin'),None)
    if f is None:fail('Nie znaleziono get_default_skin')
    defaults=[]
    for node in ast.walk(f):
        if isinstance(node,ast.Return) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str) and '<screen ' in node.value.value:
            defaults.append(ET.fromstring(node.value.value))
    if len(defaults)!=2:fail('Oczekiwano dwóch oryginalnych skinów HD/FHD')
    required=set(widget.get('name') for widget in defaults[0].findall('widget'))
    if len(required)<50:fail('Za mało widgetów domyślnego skina')
    for theme in ('future','retro'):
        for fhd in (True,False):
            mode='fhd' if fhd else 'hd'
            screen=ET.fromstring(create_theme_skin(theme,fhd,str(PLUGIN_DIR/'skins')))
            width,height=map(int,screen.get('size').split(','))
            expect=(1680,940) if fhd else (1180,660)
            if (width,height)!=expect:fail('Rozmiar XML: %s %s'%(theme,mode))
            pixmaps=screen.findall('ePixmap')
            if len(pixmaps)!=1 or pixmaps[0].get('zPosition')!='0':fail('Brak prawidłowej warstwy PNG: '+theme)
            img=PLUGIN_DIR/'skins'/('skin_%s_%s.png'%(theme,mode))
            if png_size(img)!=expect:fail('Złe wymiary PNG: '+str(img))
            widgets=screen.findall('widget')
            names=[item.get('name') for item in widgets]
            if set(names)!=set(names):fail('Niespójne nazwy')
            if len(names)!=len(set(names)):fail('Powtarzające się widgety: '+theme)
            if required-set(names):fail('Brak widgetów: '+str(sorted(required-set(names))))
            for item in widgets:
                name=item.get('name')
                x,y=map(int,item.get('position').split(','))
                w,h=map(int,item.get('size').split(','))
                if w<1 or h<1 or x<0 or y<0 or x+w>width+1 or y+h>height+1:
                    fail('Widget poza ekranem: %s %s %s'%(theme,mode,name))
                if name not in ('station_list','audio_balance_card','audio_treble_card','audio_bass_card','picon','cover','picon_large','saver_bg','saver_picon'):
                    if item.get('transparent')!='1' and not name.startswith('saver_'):
                        fail('Nieprzezroczysty tekst: '+name)
            for control in ('balance','treble','bass'):
                for value in range(-10,11):
                    card=PLUGIN_DIR/'skins/audio'/('eq_%s_%s_%s_%+03d.png'%(theme,mode,control,value))
                    if not card.exists():fail('Brak animowanego wskaźnika: '+str(card))
                    png_size(card)
            print('PASS %s %s - %s widgetów'%(theme,mode,len(widgets)))
    print('PASS: NeoRadio 3.2.1 - wersje, XML HD/FHD, pełne grafiki i wszystkie wskaźniki')

if __name__=='__main__':main()
