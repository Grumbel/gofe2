#!/usr/bin/env python

import vte
import signal
import os
import fcntl
import pygtk
pygtk.require('2.0')
import gtk, gobject, pango
import subprocess

# http://oldblog.earobinson.org/2007/09/10/python-vteterminal-example/

#while gtk.events_pending():
#    gtk.main_iteration()

def on_data_stdout(source, condition):
    print ">>>out<<< ", source, " -- ", condition, gobject.IO_IN
    print "-- try read"
    text = source.read(10)
    print "-- done: try read"
    print len(text)
    print text
    
    iter = text_buffer.get_end_iter()
    text_buffer.insert(iter,text)

    return True

def on_data_stderr(source, condition):
    print ">>>err<<< ", source, " -- ", condition, gobject.IO_IN
    text = source.read(1030)
    print len(text)
    text_buffer.set_text(text)
    return True

def make_nonblock(fd):
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

proc = None

def start_subprocess(widget):
    global proc
    print widget
    proc = subprocess.Popen(["./subprocess.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print proc
    print proc.stdin
    print proc.stdout
    print proc.stderr
    
    make_nonblock(proc.stdout)
    make_nonblock(proc.stderr)

    gobject.io_add_watch(proc.stdout, gobject.IO_IN, on_data_stdout)
    gobject.io_add_watch(proc.stderr, gobject.IO_IN, on_data_stderr)

def check_subprocess():
    global proc
    if proc and proc.poll():
        print "Process exited:", proc.returncode
        proc = None

        iter = text_buffer.get_end_iter()
        text_buffer.insert(iter, "\nProcess Exited\n")

    return True

def stop_subprocess(widget):
    global proc
    proc.terminate()
    
def kill_subprocess(widget):
    global proc
    proc.kill()

window = gtk.Window()
window.set_title("Gofe2")
window.connect("delete_event", gtk.mainquit)

text_buffer = gtk.TextBuffer()
text_view = gtk.TextView(text_buffer)

font = pango.FontDescription('Inconsolata 12')
text_view.modify_font(font)

scrolled_window = gtk.ScrolledWindow()
scrolled_window.add(text_view)
vbox = gtk.VBox()
hbox = gtk.HBox()

play_button = gtk.Button(stock=gtk.STOCK_MEDIA_PLAY)
play_button.connect("clicked", start_subprocess)

stop_button = gtk.Button(stock=gtk.STOCK_MEDIA_STOP)
stop_button.connect("clicked", stop_subprocess)

kill_button = gtk.Button(stock=gtk.STOCK_CLOSE)
kill_button.connect("clicked", kill_subprocess)

hbox.pack_start(play_button, expand=False, fill=False)
hbox.pack_start(stop_button, expand=False, fill=False)
hbox.pack_end(kill_button, expand=False, fill=False)

vbox.pack_start(hbox, expand=False, fill=False)
vbox.add(scrolled_window)

terminal = vte.Terminal()
terminal.fork_command("./subprocess.sh")
vbox.add(terminal)

window.add(vbox)

window.set_default_size(640, 480)

gobject.timeout_add(100, check_subprocess)

window.show_all()


gtk.main()

# EOF #
