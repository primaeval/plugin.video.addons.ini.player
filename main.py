from xbmcswift2 import Plugin
from xbmcswift2 import actions
import xbmc,xbmcaddon,xbmcvfs,xbmcgui
import re

import requests
import random

from datetime import datetime,timedelta
import time
#import urllib
import HTMLParser
import xbmcplugin
#import xml.etree.ElementTree as ET
#import sqlite3
import os
#import shutil
#from rpc import RPC
from types import *

plugin = Plugin()
big_list_view = False

def log2(v):
    xbmc.log(repr(v))

def log(v):
    xbmc.log(re.sub(',',',\n',repr(v)))

def get_icon_path(icon_name):
    addon_path = xbmcaddon.Addon().getAddonInfo("path")
    return os.path.join(addon_path, 'resources', 'img', icon_name+".png")


def remove_formatting(label):
    label = re.sub(r"\[/?[BI]\]",'',label)
    label = re.sub(r"\[/?COLOR.*?\]",'',label)
    return label

@plugin.route('/addon/<id>')
def addon(id):
    addon = plugin.get_storage(id)
    items = []
    for name in sorted(addon):
        url = addon[name]
        items.append(
        {
            'label': name,
            'path': url,
            'thumbnail':get_icon_path('tv'),
            'is_playable':True,
        })
    return items

@plugin.route('/')
def index():
    addons = plugin.get_storage("addons")
    for a in addons.keys():
        add = plugin.get_storage(a)
        add.clear()
    addons.clear()
    if plugin.get_setting('addons.type') == "0":
        name = plugin.get_setting('addons.file')
        f = xbmcvfs.File(name,"rb")
        lines = f.read().splitlines()
    else:
        url = plugin.get_setting('addons.url')
        data = requests.get(url).content
        lines = data.splitlines()
    addon = None
    for line in lines:
        if line.startswith('['):
            a = line.strip('[]')
            addons[a] = a
            addon = plugin.get_storage(a)
            addon.clear()
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                addon[name] = url
                    
    items = []
    for id in sorted(addons):
        items.append(
        {
            'label': id,
            'path': plugin.url_for('addon',id=id),
            'thumbnail':get_icon_path('tv'),
        })

    
    return items


if __name__ == '__main__':
    plugin.run()
    if big_list_view == True:
        view_mode = int(plugin.get_setting('view_mode'))
        plugin.set_view_mode(view_mode)