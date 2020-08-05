# -*- coding: UTF-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2017-2020 NV Access Limited, Thomas Stivers
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
import os
import tempfile
import typing

import gui
import ui
import wx
from logHandler import log


def writeRedirect(helpId: str, helpFilePath: str, contextHelpPath: str):
	redirect = rf"""
<html><head>
<meta http-equiv="refresh" content="0;url=file:///{helpFilePath}#{helpId}" />
</head></html>
	"""
	with open(contextHelpPath, 'w') as f:
		f.write(redirect)


def showHelp(helpId: str):
	"""Display the corresponding section of the user guide when either the Help
	button in an NVDA dialog is pressed or the F1 key is pressed on a
	recognized control.
	"""
	if not helpId:
		# Translators: Message indicating no context sensitive help is available.
		noHelpMessage = _("No context sensitive help is available here at this time.")
		ui.message(noHelpMessage)
	helpFile = gui.getDocFilePath("userGuide.html")
	if not os.path.exists(helpFile):
		# Translators: Message shown when trying to display context sensitive help,
		# indicating that	the user guide could not be found.
		noHelpMessage = _("No user guide found.")
		log.debugWarning("No user guide found: possible cause - running from source without building user docs")
		ui.message(noHelpMessage)
	log.debug(f"Opening help: helpId = {helpId}, userGuidePath: {helpFile}")

	nvdaTempDir = os.path.join(tempfile.gettempdir(), "nvda")
	if not os.path.exists(nvdaTempDir):
		os.mkdir(nvdaTempDir)

	contextHelpRedirect = os.path.join(nvdaTempDir, "contextHelp.html")
	try:
		writeRedirect(helpId, helpFile, contextHelpRedirect)
	except Exception:
		log.error("Unable to write context help redirect file.", exc_info=True)
		return

	try:
		os.startfile(f"file://{contextHelpRedirect}")
	except Exception:
		log.error("Unable to launch context help.", exc_info=True)


def bindHelpEvent(helpId: str, window: wx.Window):
	window.Unbind(wx.EVT_HELP)
	window.Bind(
		wx.EVT_HELP,
		lambda evt: _onEvtHelp(helpId, evt),
	)
	log.debug(f"Did context help binding for {window.__class__.__qualname__}")


def _onEvtHelp(helpId: str, evt: wx.HelpEvent):
	# Don't call evt.skip. Events bubble upwards through parent controls.
	# Context help for more specific controls should override the less specific parent controls.
	showHelp(helpId)


class ContextHelpMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		helpId = getattr(self, "helpId", None)
		if not helpId or not isinstance(helpId, str):
			log.warning(f"No helpId (or incorrect type) for: {self.__class__.__qualname__}")
			return
		window = typing.cast(wx.Window, self)
		bindHelpEvent(helpId, window)
		log.debug(f"ContextHelpMixin for {self.__class__.__qualname__}")

	def bindHelpEvent(self, helpId: str, window: wx.Window):
		bindHelpEvent(helpId, window)
