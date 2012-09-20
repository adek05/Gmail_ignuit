# -*- coding: utf-8 -*-
import gmail_ignuit

import imaplib
import sys
import threading

from gi.repository import Gtk, GObject, Gdk

UI_FILE = 'ui.glade'

Gdk.threads_init()
GObject.threads_init()

builder = Gtk.Builder()

def fetch_task(user, password):
    try:
        spinner = builder.get_object('spinner')
        GObject.idle_add(spinner.start)
        cards = gmail_ignuit.get_words_from_mailbox(user, password)
        GObject.idle_add(spinner.stop)
        spinner.stop()
        store = builder.get_object('liststore')
        store.clear()
        for card, i in zip(cards, range(0, len(cards))):
            # TODO: if called this way populates with huge amount of data..., no idea why
            # GObject.idle_add(store.append, [False, card.find('front').text, card.find('back').text])
            store.append([False, card['front'], card['back'], i])
    except imaplib.IMAP4_SSL.error, e:
        sys.stderr.write("[ERROR] Can't login to Gmail account: %s\n" % e)
        GObject.idle_add(spinner.stop)


class Handlers:

    def onToggled(self, cell, path, *args):
        store = builder.get_object('liststore')
        it =  store.get_iter_from_string(path)
        store.set(it, 0, not store.get(it, 0)[0]) # Toggle value

    def onDeleteEvent(self, *args):
        Gtk.main_quit()

    def onAddClicked(self, *args):
        store = builder.get_object('liststore')
        cards_to_be_added = []
        for row in store:
            if row[0] == True:
                cards_to_be_added.append(gmail_ignuit.create_xml_from_card({'front': row[1], 'back': row[2]}))
        gmail_ignuit.add_new_cards(cards_to_be_added)

    def onDownloadClicked(self, *args):
        d = builder.get_object('dialog1')
        d.run()
        t = threading.Thread(target = fetch_task, args=(builder.get_object('dialog_username').get_text(),
            builder.get_object('dialog_password').get_text()))
        d.hide()
        t.start()
        return

builder.add_from_file(UI_FILE)
builder.connect_signals(Handlers())
cell = builder.get_object('cellrenderertoggle1')
cell.set_property('activatable', True)

window = builder.get_object('window1')
window.show_all()
Gtk.main()
