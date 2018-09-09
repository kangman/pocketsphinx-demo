#!/usr/bin/env python

# Note this has been modified since its original source.

# SOURCE:
# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system. See LICENSE for more information.

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import Gtk

GObject.threads_init()
Gst.init(None)

gst = Gst

print("Using pygtkcompat and Gst from gi")


class DemoApp(object):
    """GStreamer/PocketSphinx Demo Application"""

    def __init__(self):
        """Initialize a DemoApp object"""
        self.init_gui()
        self.init_gst()

    def init_gui(self):
        """Initialize the GUI components."""
        self.window = Gtk.Window()
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.set_default_size(400, 200)
        self.window.set_border_width(10)
        vbox = Gtk.VBox()
        self.textbuf = Gtk.TextBuffer()
        self.text = Gtk.TextView(buffer=self.textbuf)
        self.text.set_wrap_mode(Gtk.WrapMode.WORD)
        vbox.pack_start(self.text, True, True, 0)
        self.button = Gtk.ToggleButton("Speak")
        self.button.connect("clicked", self.button_clicked)
        vbox.pack_start(self.button, False, False, 5)
        self.window.add(vbox)
        # Recursively shows a widget, and any child widgets (if the widget is a container).
        self.window.show_all()

    def init_gst(self):
        """Initialize the speech components"""
        self.pipeline = Gst.parse_launch(
            "autoaudiosrc ! audioconvert ! audioresample " + "! pocketsphinx ! fakesink"
        )
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::element", self.element_message)

        # bus.connect(
        #     "message::eos", self._on_message
        # )
        # bus.connect(
        #     "message::error", self._on_message
        # )
        # bus.connect(
        #     "message::state-changed", self._on_state_changed
        # )

        # # ************************************************************
        # # get gst pipeline element pocketsphinx and set properties - BEGIN
        # # ************************************************************
        # pocketsphinx = pipeline.get_by_name("asr")
        # # from scarlett_os.internal.debugger import dump
        # # print("debug-2018-pocketsphinx - BEGIN")
        # # dump(pocketsphinx.get_property('decoder'))
        # # print("debug-2018-pocketsphinx - END")
        # # print(pocketsphinx.list_properties())
        # if self._hmm:
        #     pocketsphinx.set_property("hmm", self._hmm)
        # if self._lm:
        #     pocketsphinx.set_property("lm", self._lm)
        # if self._dic:
        #     pocketsphinx.set_property("dict", self._dic)

        # if self._fwdflat:
        #     pocketsphinx.set_property("fwdflat", self._fwdflat)

        # if self._bestpath:
        #     pocketsphinx.set_property("bestpath", self._bestpath)

        # if self._dsratio:
        #     pocketsphinx.set_property("dsratio", self._dsratio)

        # if self._maxhmmpf:
        #     pocketsphinx.set_property("maxhmmpf", self._maxhmmpf)

        # if self._bestpath:
        #     pocketsphinx.set_property("bestpath", self._bestpath)

        self.pipeline.set_state(Gst.State.PAUSED)

    def element_message(self, bus, msg):
        """Receive element messages from the bus."""
        msgtype = msg.get_structure().get_name()
        if msgtype != "pocketsphinx":
            return

        if msg.get_structure().get_value("final"):
            self.final_result(
                msg.get_structure().get_value("hypothesis"),
                msg.get_structure().get_value("confidence"),
            )
            self.pipeline.set_state(Gst.State.PAUSED)
            self.button.set_active(False)
        elif msg.get_structure().get_value("hypothesis"):
            self.partial_result(msg.get_structure().get_value("hypothesis"))

    def partial_result(self, hyp):
        """Delete any previous selection, insert text and select it."""
        # All this stuff appears as one single action
        self.textbuf.begin_user_action()
        self.textbuf.delete_selection(True, self.text.get_editable())
        self.textbuf.insert_at_cursor(hyp)
        ins = self.textbuf.get_insert()
        iter = self.textbuf.get_iter_at_mark(ins)
        iter.backward_chars(len(hyp))
        self.textbuf.move_mark(ins, iter)
        self.textbuf.end_user_action()

    def final_result(self, hyp, confidence):
        """Insert the final result."""
        # All this stuff appears as one single action
        self.textbuf.begin_user_action()
        self.textbuf.delete_selection(True, self.text.get_editable())
        self.textbuf.insert_at_cursor(hyp)
        self.textbuf.end_user_action()

    def button_clicked(self, button):
        """Handle button presses."""
        if button.get_active():
            button.set_label("Stop")
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            button.set_label("Speak")
            self.pipeline.set_state(Gst.State.PAUSED)


app = DemoApp()
Gtk.main()
