#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-     <AUTHOR>                                   <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.5 and
#  upwards.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import datetime
import time
import os
import json

from lib.item import Items
from lib.model.smartplugin import SmartPluginWebIf


# ------------------------------------------
#    Webinterface of the plugin
# ------------------------------------------

import cherrypy
import csv
from jinja2 import Environment, FileSystemLoader


class WebInterface(SmartPluginWebIf):

    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.items = Items.get_instance()

        self.tplenv = self.init_template_environment()

    def _get_speaker_list(self):
        """get list of speakers and return it"""

        speaker_list = []

        for zone in self.plugin.zones:
            # self.logger.debug(f"vars(zone): {vars(zone)}")
            speaker = dict()
            try:
                speaker['name'] = zone.player_name
            except Exception:
                speaker['name'] = 'unknown'

            try:
                speaker['ip'] = zone.ip_address
            except Exception:
                speaker['ip'] = 'unknown'

            try:
                speaker['uid'] = zone.uid
            except Exception:
                speaker['uid'] = 'unknown'

            speaker_list.append(speaker)

        self.logger.debug(f"_get_speaker_list: {speaker_list=}")
        return speaker_list

    def _get_item_list(self):
        """get list of items for that plugin and return it"""

        item_list = []

        for item in self.items.return_items():
            for entry in item.conf:
                if entry.startswith('sonos'):
                    item_list.append(item)

        self.logger.debug(f"_get_item_list: {item_list=}")
        return item_list

    @cherrypy.expose
    def index(self, reload=None):
        """
        Build index.html for cherrypy

        Render the template and return the html file to be delivered to the browser

        :return: contents of the template after being rendered
        """

        tmpl = self.tplenv.get_template('index.html')

        # get speaker_list
        speaker_list_sorted = sorted(self._get_speaker_list(), key=lambda k: k['name'])

        # get item_list
        item_list = self._get_item_list()

        # try to get the webif pagelength from the module.yaml configuration
        global_pagelength = cherrypy.config.get("webif_pagelength")
        if global_pagelength:
            pagelength = global_pagelength
            self.logger.debug("Global pagelength {}".format(pagelength))
        # try to get the webif pagelength from the plugin specific plugin.yaml configuration
        try:
            pagelength = self.plugin.webif_pagelength
            self.logger.debug("Plugin pagelength {}".format(pagelength))
        except Exception:
            pagelength = 100

        # add values to be passed to the Jinja2 template eg: tmpl.render(p=self.plugin, interface=interface, ...)
        return tmpl.render(p=self.plugin,
                           webif_pagelength=pagelength,
                           item_list=item_list,
                           item_count=len(item_list),
                           speaker_list=self._get_speaker_list(),
                           plugin_shortname=self.plugin.get_shortname(),
                           plugin_version=self.plugin.get_version(),
                           plugin_info=self.plugin.get_info(),
                           )

    @cherrypy.expose
    def get_data_html(self, dataSet=None):
        """
        Return data to update the webpage

        For the standard update mechanism of the web interface, the dataSet to return the data for is None

        :param dataSet: Dataset for which the data should be returned (standard: None)
        :return: dict with the data needed to update the web page.
        """
        # if dataSets are used, define them here
        if dataSet == 'overview':
            # get the new data from the plugin variable called _webdata
            data = self.plugin._webdata
            try:
                data = json.dumps(data)
                return data
            except Exception as e:
                self.logger.error(f"get_data_html exception: {e}")
        if dataSet is None:
            # get the new data
            data = {}

            # data['item'] = {}
            # for i in self.plugin.items:
            #     data['item'][i]['value'] = self.plugin.getitemvalue(i)
            #
            # return it as json the web page
            # try:
            #     return json.dumps(data)
            # except Exception as e:
            #     self.logger.error("get_data_html exception: {}".format(e))
        return {}
