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
            'label': remove_formatting(name),
            'path': url,
            'thumbnail':xbmcaddon.Addon(id).getAddonInfo('icon') or get_icon_path('tv'),
            'is_playable':True,
        })
        '''
        if plugin.get_setting('test') == 'true':
            if url.startswith("ftp://"):
                continue
            xbmc.executebuiltin("PlayMedia(%s)" % url)
            countdown = 10
            while countdown:
                time.sleep(1)
                countdown = countdown -1
                if xbmc.Player().isPlaying():
                    time.sleep(5)
                    break
            path = xbmc.translatePath("special://temp/%s.png" % re.sub("[^\w ]","",name, flags=re.UNICODE))
            xbmc.executebuiltin("TakeScreenshot(%s)" % path)
            xbmc.executebuiltin("PlayerControl(Stop)")
        '''

    return items

@plugin.route('/add_channel')
def add_channel():
    channels = plugin.get_storage('channels')
    d = xbmcgui.Dialog()
    channel = d.input("Add Channel")
    if channel:
        channels[channel] = ""
    xbmc.executebuiltin('Container.Refresh')


@plugin.route('/remove_channel')
def remove_channel():
    channels = plugin.get_storage('channels')
    channel_list = sorted(channels)
    d = xbmcgui.Dialog()
    which = d.select("Remove Channel",channel_list)
    if which == -1:
        return
    channel = channel_list[which]
    del channels[channel]
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/remove_this_channel/<channel>')
def remove_this_channel(channel):
    channels = plugin.get_storage('channels')
    del channels[channel]
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/clear_channels')
def clear_channels():
    channels = plugin.get_storage('channels')
    channels.clear()
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/import_channels')
def import_channels():
    channels = plugin.get_storage('channels')
    d = xbmcgui.Dialog()
    filename = d.browse(1, 'Import Channels (name=url .ini file)', 'files', '', False, False, 'special://home/')
    if not filename:
        return
    if filename.endswith('.ini'):
        lines = xbmcvfs.File(filename,'rb').read().splitlines()
        for line in lines:
            if not line.startswith('[') and not line.startswith('#') and "=" in line:
                channel_url = line.split('=',1)
                if len(channel_url) == 2:
                    name = channel_url[0]
                    channels[name] = ""
    xbmc.executebuiltin('Container.Refresh')

@plugin.route('/stream_search_dialog/<channel>')
def stream_search_dialog(channel):
    #folders = plugin.get_storage('folders')
    streams = {}

    folder = plugin.get_setting("addons.folder")
    file = plugin.get_setting("addons.file")
    filename = os.path.join(folder,file)
    f = xbmcvfs.File(filename,"rb")
    lines = f.read().splitlines()
    for line in lines:
        if line.startswith('['):
            addon = line.strip('[]')
            if addon not in streams:
                streams[addon] = {}
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                streams[addon][url] = name

    channel_search = channel.lower().replace(' ','')
    stream_list = []
    for id in sorted(streams):
        files = streams[id]
        for f in sorted(files, key=lambda k: files[k]):
            label = files[f]
            label_search = label.lower().replace(' ','')
            if label_search in channel_search or channel_search in label_search:
                stream_list.append((id,f,label))
    labels = ["[%s] %s" % (x[0],x[2]) for x in stream_list]
    d = xbmcgui.Dialog()
    which = d.select(channel, labels)
    if which == -1:
        return
    stream_name = stream_list[which][2]
    stream_link = stream_list[which][1]
    plugin.set_resolved_url(stream_link)

@plugin.route('/stream_search/<channel>')
def stream_search(channel):
    #folders = plugin.get_storage('folders')
    streams = {}

    folder = plugin.get_setting("addons.folder")
    file = plugin.get_setting("addons.file")
    filename = os.path.join(folder,file)
    f = xbmcvfs.File(filename,"rb")
    lines = f.read().splitlines()
    for line in lines:
        if line.startswith('['):
            addon = line.strip('[]')
            if addon not in streams:
                streams[addon] = {}
        elif "=" in line:
            (name,url) = line.split('=',1)
            if url and addon is not None:
                streams[addon][url] = remove_formatting(name)

    channel_search = channel.lower().replace(' ','')
    stream_list = []
    for id in sorted(streams):
        files = streams[id]
        for f in sorted(files, key=lambda k: files[k]):
            label = files[f]
            label_search = label.lower().replace(' ','')
            if label_search in channel_search or channel_search in label_search:
                stream_list.append((id,f,label))
    #labels = ["[%s] %s" % (x[0],x[2]) for x in stream_list]
    items = []
    for s in stream_list:
        label = "%s - %s" % (s[2], xbmcaddon.Addon(s[0]).getAddonInfo('name'))
        path = s[1]
        items.append({
        "label":label,
        "path":path,
        "thumbnail":xbmcaddon.Addon(s[0]).getAddonInfo('icon') or get_icon_path('tv'),
        'is_playable': True,
        })
    return items


@plugin.route('/export_channels')
def export_channels():
    channels = plugin.get_storage('channels')

    f = xbmcvfs.File('special://profile/addon_data/plugin.video.addons.ini.player/export.ini','wb')
    for channel in sorted(channels):
        url = plugin.url_for('stream_search',channel=channel)
        s = "%s=%s\n" % (channel,url)
        f.write(s)
    f.close()

@plugin.route('/channel_player')
def channel_player():
    channels = plugin.get_storage("channels")

    items = []
    for channel in sorted(channels):
        context_items = []
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Add Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(add_channel))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Remove Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(remove_this_channel, channel=channel))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Import Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(import_channels))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Export Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(export_channels))))
        context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Clear Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(clear_channels))))
        items.append(
        {
            'label': channel,
            'path': plugin.url_for('stream_search',channel=channel),
            'thumbnail':get_icon_path('tv'),
            #'is_playable': True,
            'context_menu': context_items,
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
                addon[name] = url.strip('@ ')

    items = []
    context_items = []
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Add Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(add_channel))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Remove Channel', 'XBMC.RunPlugin(%s)' % (plugin.url_for(remove_channel))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Import Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(import_channels))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Export Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(export_channels))))
    context_items.append(("[COLOR yellow][B]%s[/B][/COLOR] " % 'Clear Channels', 'XBMC.RunPlugin(%s)' % (plugin.url_for(clear_channels))))
    items.append(
    {
        'label': "Channels",
        'path': plugin.url_for('channel_player'),
        'thumbnail':get_icon_path('tv'),
        'context_menu': context_items,
    })

    for id in sorted(addons):
        items.append(
        {
            'label': xbmcaddon.Addon(id).getAddonInfo('name'),
            'path': plugin.url_for('addon',id=id),
            'thumbnail':xbmcaddon.Addon(id).getAddonInfo('icon'),
        })


    return items


if __name__ == '__main__':
    plugin.run()
    if big_list_view == True:
        view_mode = int(plugin.get_setting('view_mode'))
        plugin.set_view_mode(view_mode)