#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib
import os
import sys
import time
import sensormonman
import threading

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
HOME=os.environ.get('HOME')
DEFAULT_SAVE_PATH=HOME+"/.local/share/applications/"

class App(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id="com.gabmus.gSensorMon", flags=Gio.ApplicationFlags.FLAGS_NONE)


		builder.get_object("aboutdialog").connect("delete-event", lambda *_: builder.get_object("aboutdialog").hide() or True)
		self.connect("activate", self.activateCb)

	def do_startup(self):
	# start the application
		Gtk.Application.do_startup(self)

	def activateCb(self, app):
		window = builder.get_object("window1")
		window.set_wmclass("gSensorMon", "gSensorMon")
		app.add_window(window)
		appMenu=Gio.Menu()
		appMenu.append("About", "app.about")
		appMenu.append("Quit", "app.quit")
		about_action = Gio.SimpleAction.new("about", None)
		about_action.connect("activate", self.on_about_activate)
		app.add_action(about_action)
		quit_action = Gio.SimpleAction.new("quit", None)
		quit_action.connect("activate", self.on_quit_activate)
		app.add_action(quit_action)
		app.set_app_menu(appMenu)
		window.show_all()

	def on_about_activate(self, *agrs):
		builder.get_object("aboutdialog").show()

	def on_quit_activate(self, *args):
		global stopThread
		manager.stop() #cleanup the sensor lib before quitting?
		stopThread=True
		self.quit()


settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", True)


def wait(time_lapse):
	time_start = time.time()
	time_end = (time_start + time_lapse)

	while time_end > time.time():
		while Gtk.events_pending():
			Gtk.main_iteration()

manager= sensormonman.SmManager()
manager.start()


level = builder.get_object("levelbar1")
label = builder.get_object("label1")

listbox = builder.get_object("listbox1")

listboxRows=0
valLabels=[]
valLevels=[]
def populateListbox():
	global listboxRows
	for i in manager.chips:
		box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		box.set_spacing(6)

		labelSensorName=Gtk.Label()
		labelSensorName.set_text(i.label)

		hbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		hbox.set_spacing(6)

		labelVal=Gtk.Label()
		labelVal.set_text(str(manager.chipsVal[listboxRows]))
		valLabels.append(labelVal) #added to list

		levelVal=Gtk.LevelBar()
		levelVal.set_max_value(130) #for temperatures, TODO: make it dynamic
		levelVal.set_min_value(0) #should be ok? No levelBar should look empty
		levelVal.set_value(manager.chipsVal[listboxRows])
		levelVal.set_size_request(-1,20)
		valLevels.append(levelVal) #added to list

		hbox.pack_end(labelVal, False, True, 6)
		hbox.pack_end(levelVal, True, True, 6)

		box.pack_end(hbox, True, True, 6)
		box.pack_end(labelSensorName, True, True, 6)
		row = Gtk.ListBoxRow()
		row.add(box)
		listbox.add(row)
		listboxRows+=1
	listbox.show_all()

def updateListbox():
	j=0
	while j<listboxRows:
		valLabels[j].set_text(str(manager.chipsVal[j]))
		valLevels[j].set_value(manager.chipsVal[j])
		j+=1


populateListbox()
stopThread=False

class Handler:

	selectedRow=0

	def onDeleteWindow(self, *args):
		app.on_quit_activate()

	def on_listbox1_row_activated(self, lbox, row):
		self.selectedRow=row.get_index()


builder.connect_signals(Handler())

#async shit, Apparently works, dont know how or why
#BEGIN
def refreshAsync():
	manager.restart()
	updateListbox()
	wait(1)

def soos():
	while not stopThread:
		GLib.idle_add(refreshAsync)
		time.sleep(1)

thread = threading.Thread(target=soos)
thread.daemon = False
thread.start()

#END

if __name__ == "__main__":
	app= App()
	app.run(sys.argv)
#Gtk.main()
