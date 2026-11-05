# -*- coding: utf-8 -*-
"""NeoRadio 3.2.1 independent HD/FHD themes.

The screens contain real Enigma2 widgets. All dynamic text, lists, picons and
artwork are provided by the existing plugin code, NOT baked into the PNG.
"""
from __future__ import print_function
import os
from xml.sax.saxutils import quoteattr

_BASE_SIZE = (1680, 940)


def _q(value):
    return quoteattr(str(value))


def _widget(name, pos, size, font=18, fg='#00ffffff', bg='#00000000', halign=None,
            transparent=True, z=4, extra=None, scale=1.0):
    x, y = pos
    w, h = size
    p = '%d,%d' % (int(round(x*scale)), int(round(y*scale)))
    s = '%d,%d' % (max(1,int(round(w*scale))), max(1,int(round(h*scale))))
    attrs = {'name':name, 'position':p, 'size':s, 'font':'Regular;%d' % max(12,int(round(font*scale))),
             'foregroundColor':fg,'backgroundColor':bg,'transparent':'1' if transparent else '0',
             'zPosition':str(z)}
    if halign:
        attrs['halign'] = halign
    if extra:
        attrs.update(extra)
    return '    <widget %s />' % ' '.join('%s=%s' % (k,_q(v)) for k,v in attrs.items())


def _pixmap_widget(name,pos,size,scale=1.0,z=3):
    x,y=pos;w,h=size
    return '    <widget name="%s" position="%d,%d" size="%d,%d" alphatest="blend" zPosition="%d" />' % (
        name,round(x*scale),round(y*scale),round(w*scale),round(h*scale),z)


def _layout(theme):
    # x, y, width, height; all coordinates are on the 1680x940 canvas.
    # Both themes use distinct geometry derived from the reference concepts.
    white='#00f7ffff' if theme=='future' else '#00fff1d3'
    muted='#00b5e4f7' if theme=='future' else '#00f0d4a3'
    gold='#00ffd76a' if theme=='future' else '#00e9ad53'
    brown='#003b1e0c'
    green='#0030e483' if theme=='future' else '#00d3ff9e'
    if theme=='future':
        fields={
            'list_title':((109,112,280,37),28,white,None),
            'filter_label':((77,701,389,24),17,muted,None),
            'search_label':((77,726,389,22),17,gold,None),
            'help_label':((77,747,389,35),15,white,None),
            'clock_label':((1393,28,254,44),20,white,'right'),
            'status_label':((522,127,579,31),24,green,None),
            'station_name':((521,160,594,51),35,white,None),
            'station_meta':((523,213,594,32),23,muted,None),
            'station_url':((524,249,586,25),17,muted,None),
            'station_desc_title':((523,282,220,23),18,gold,None),
            'station_desc':((526,308,580,35),17,white,None),
            'station_extra':((522,343,574,22),15,muted,None),
            'visualizer_label':((0,0,1,1),12,white,None),
            'hero_clock':((0,0,1,1),12,white,None),
            'hero_date':((0,0,1,1),12,white,None),
            'spectrum_title':((0,0,1,1),12,white,None),
            'spectrum_label':((835,430,209,39),30,'#0049e9ea','center'),
            'np_header':((745,570,370,33),24,gold,None),
            'np_title':((744,604,531,34),25,white,None),
            'np_artist':((745,641,529,27),19,muted,None),
            'np_album':((745,667,528,27),18,muted,None),
            'np_status':((746,697,523,27),17,green,None),
            'footer_brand':((746,725,148,21),15,gold,None),
            'footer_label':((897,725,391,20),14,muted,None),
            'picon_large_title':((0,0,1,1),12,white,None),
            'audio_title':((0,0,1,1),12,white,None),
            'audio_balance_title':((524,495,184,23),20,white,None),
            'audio_treble_title':((879,495,184,23),20,white,None),
            'audio_bass_title':((1236,495,184,23),20,white,None),
            'audio_balance':((529,521,111,25),20,gold,None),
            'audio_treble':((884,521,111,25),20,gold,None),
            'audio_bass':((1241,521,111,25),20,gold,None),
            'audio_balance_help':((530,548,315,20),13,muted,None),
            'audio_treble_help':((885,548,310,20),13,muted,None),
            'audio_bass_help':((1238,548,315,20),13,muted,None),
            'key_red':((35,789,256,32),19,white,'center'),
            'key_green':((319,789,235,32),19,white,'center'),
            'key_yellow':((586,789,232,32),19,'#001f170b','center'),
            'key_blue':((842,789,231,32),19,white,'center'),
            'key_menu':((1104,789,267,32),18,white,'center'),
            'key_info':((1396,789,252,32),18,white,'center'),
            'detail_bitrate':((1464,153,162,32),23,white,'center'),
            'detail_country':((1462,250,166,32),22,white,'center'),
            'detail_favorite':((1460,351,164,32),19,white,'center'),
            'credits_footer':((53,861,1203,35),17,muted,None),
        }
        listarea=(77,166,387,531,22,33)
        picon=(1148,176,222,234)
        cover=(519,584,197,152)
        picon_large=(0,0,1,1)
        cards=[(497,488,332,60),(849,488,333,60),(1209,488,403,60)]
        listbg='#00051526'; sel_bg='#0000ceec'; sel_fg='#00031b2b'
        bgcolor='#00061321'
    else:
        fields={
            'list_title':((161,115,220,43),27,'#00371d0a',None),
            'filter_label':((69,706,344,24),16,muted,None),
            'search_label':((69,729,344,22),16,gold,None),
            'help_label':((69,751,345,34),15,white,None),
            'clock_label':((1289,44,256,35),19,gold,'right'),
            'status_label':((1171,253,161,31),19,green,None),
            'station_name':((650,246,483,50),28,white,None),
            'station_meta':((650,298,476,31),22,muted,None),
            'station_url':((650,333,480,25),17,muted,None),
            'station_desc_title':((651,359,281,25),20,gold,None),
            'station_desc':((650,387,478,44),17,white,None),
            'station_extra':((650,428,476,21),15,gold,None),
            'hero_clock':((0,0,1,1),12,white,None),
            'hero_date':((0,0,1,1),12,white,None),
            'visualizer_label':((0,0,1,1),12,white,None),
            'spectrum_title':((1235,450,195,26),17,gold,'center'),
            'spectrum_label':((1230,496,192,35),27,'#00ffdd6e','center'),
            'np_header':((510,459,140,28),21,'#007c380c',None),
            'np_title':((657,453,490,32),25,brown,None),
            'np_artist':((665,489,474,28),20,brown,None),
            'np_album':((665,516,474,23),18,brown,None),
            'np_status':((288,780,712,25),16,green,None),
            'footer_brand':((1008,781,161,22),14,gold,None),
            'footer_label':((1170,781,409,20),14,muted,None),
            'picon_large_title':((0,0,1,1),12,white,None),
            'audio_title':((0,0,1,1),12,white,None),
            'audio_balance_title':((569,610,117,23),17,'#00381e0c',None),
            'audio_treble_title':((919,610,117,23),17,'#00381e0c',None),
            'audio_bass_title':((1261,610,117,23),17,'#00381e0c',None),
            'audio_balance':((745,610,46,24),19,brown,None),
            'audio_treble':((1086,610,50,24),19,brown,None),
            'audio_bass':((1433,610,46,24),19,brown,None),
            'audio_balance_help':((545,644,270,19),12,muted,None),
            'audio_treble_help':((893,644,270,19),12,muted,None),
            'audio_bass_help':((1235,644,270,19),12,muted,None),
            'key_red':((115,827,221,28),18,white,'center'),
            'key_green':((366,827,194,28),18,white,'center'),
            'key_yellow':((591,827,180,28),18,'#00291305','center'),
            'key_blue':((803,827,185,28),18,white,'center'),
            'key_menu':((1016,827,248,28),17,white,'center'),
            'key_info':((1294,827,237,28),18,white,'center'),
            'detail_bitrate':((0,0,1,1),12,white,None),
            'detail_country':((0,0,1,1),12,white,None),
            'detail_favorite':((0,0,1,1),12,white,None),
            'credits_footer':((500,878,591,38),15,gold,'center'),
        }
        listarea=(67,187,333,516,21,32)
        picon=(486,266,146,154)
        cover=(0,0,1,1)
        picon_large=(0,0,1,1)
        cards=[(524,557,281,85),(869,557,279,85),(1210,557,285,85)]
        listbg='#001f120a';sel_bg='#00e8bb5a';sel_fg='#00321905'
        bgcolor='#00321a0c'
    return fields,listarea,picon,cover,picon_large,cards,bgcolor,listbg,sel_bg,sel_fg


def create_theme_skin(theme, fhd, assets_path):
    if theme not in ('retro','future'):
        raise ValueError('Unknown NeoRadio theme')
    scale=1.0 if fhd else 1180.0/1680.0
    W,H=(1680,940) if fhd else (1180,660)
    fields,listarea,picon,cover,picon_large,cards,bgcolor,listbg,sel_bg,sel_fg=_layout(theme)
    img_name='skin_%s_%s.png' % (theme, 'fhd' if fhd else 'hd')
    image_path=os.path.join(assets_path,img_name)
    lines=['<screen name="NeoRadioMain" position="center,center" size="%d,%d" title="NeoRadio Online" backgroundColor="%s">' % (W,H,bgcolor)]
    lines.append('    <ePixmap position="0,0" size="%d,%d" pixmap=%s zPosition="0" alphatest="blend" />' % (W,H,_q(image_path)))
    # Actual list widget must be opaque and match the prepared blank panel.
    x,y,w,h,ft,it=listarea
    lines.append(_widget('station_list',(x,y),(w,h),font=ft,fg='#00ffffff' if theme=='future' else '#00fff0d7',bg=listbg,
       transparent=False,z=2,scale=scale,extra={'scrollbarMode':'showOnDemand','itemHeight':str(int(it*scale)),
          'foregroundColorSelected':sel_fg,'backgroundColorSelected':sel_bg}))
    pixmaps={'picon':picon,'cover':cover,'picon_large':picon_large}
    for name,pos in pixmaps.items():
        lines.append(_pixmap_widget(name,(pos[0],pos[1]),(pos[2],pos[3]),scale=scale,z=3))
    for i,name in enumerate(('audio_balance_card','audio_treble_card','audio_bass_card')):
        pos=cards[i]
        lines.append(_pixmap_widget(name,(pos[0],pos[1]),(pos[2],pos[3]),scale=scale,z=4))
    # All dynamic labels are independent of the illustration (the previous bug was
    # drawing them on black opaque widgets above the pixmap).
    for name,data in fields.items():
        rect,font,color,align=data
        lines.append(_widget(name,rect[:2],rect[2:],font=font,fg=color,halign=align,
                             transparent=True,z=6 if name.startswith('audio_') else 5,scale=scale))
    for name in ('header_title','audio_help'):
        lines.append(_widget(name,(0,0),(1,1),font=12,fg='#00000000',scale=scale))
    # Both themes preserve the existing overlay-based screensaver behavior.
    saver=[('saver_bg',(0,0,1680,940)),
       ('saver_picon',(1252,690,260,120)),
       ('saver_station',(155,762,1080,53)),
       ('saver_hint',(155,821,1050,33)),
       ('saver_clock',(605,243,480,87)),
       ('saver_date',(604,345,482,38))]
    for name,(x,y,w,h) in saver:
        if name=='saver_picon':
            lines.append(_pixmap_widget(name,(x,y),(w,h),scale=scale,z=22))
        else:
            lines.append(_widget(name,(x,y),(w,h),font=70 if name=='saver_clock' else 28,
                fg='#00ffffff' if name!='saver_bg' else '#00000000',bg='#00040a13',
                transparent=False if name=='saver_bg' else True,z=20 if name=='saver_bg' else 22,scale=scale))
    lines.append('</screen>')
    return '\n'.join(lines)

if __name__=='__main__':
    import xml.etree.ElementTree as ET
    for theme in ('future','retro'):
        for fhd in (True,False):
            s=create_theme_skin(theme,fhd,'/tmp/mock')
            x=ET.fromstring(s)
            names=[v.get('name') for v in x.findall('widget')]
            assert len(names)==len(set(names)), 'duplicates'
            print(theme, fhd,len(names))
