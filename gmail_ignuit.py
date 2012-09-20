# -*- coding: utf-8 -*-
import re
import imaplib
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ET

GMAIL_IMAP_SERVER = 'imap.gmail.com'
XML_FILE = ''
LABEL='"Word of the day"'

def fetch_unread(user, password):
    gmail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
    gmail.login(user, password)
    gmail.select(LABEL)
    msgs = gmail.fetch(re.sub(' ', ',', gmail.search('', 'UNSEEN')[1][0]), '(BODY[text])')
    msgs = [x for x in msgs[1] if len(x) > 1]
    gmail.close()
    gmail.logout()
    return msgs

def parse_msg(msg):
    res_word = dict()
    res_idiom = dict()
    # Extract HTML from message
    msg = msg[msg.find('<html>'):]
    msg = msg[:msg.find('</html>') + len('</html>')]
    msg = re.sub(r'&nbsp;', '', msg) # Strip useless &nbsp;
    soup = BeautifulSoup(msg)
    word, idiom = soup.findAll('td', attrs={'class': 'f13'})
    res_word['word'] = word.text
    res_idiom['idiom'] = idiom.text
    word_def, word_example, word_tr, idiom_example, idiom_tr = soup.findAll('td', attrs={'class': 'f7'})
    res_word['word_def'] = word_def.findNextSibling().text
    res_word['word_example'] = word_example.findNextSibling().text
    res_word['word_tr'] = word_tr.findNextSibling().text
    res_idiom['idiom_example'] = idiom_example.findNextSibling().text
    res_idiom['idiom_tr'] = idiom_tr.findNextSibling().text
    return res_word, res_idiom

def create_xml_from_card(c):
    card = ET.Element('card', {'grp': '0', 'crt': '700000'})
    front = ET.Element('front')
    front.text = c['front'].decode('utf-8')
    back = ET.Element('back')
    back.text = c['back'].decode('utf-8')
    card.append(front)
    card.append(back)
    return card

def parse_xml():
    doc = ET.parse(XML_FILE)
    return doc

def add_new_cards(cards):
    tree = parse_xml()
    category = tree.find('category')
    for card in cards:
        category.insert(0, card)
    tree.write(XML_FILE, encoding="utf-8", xml_declaration=True, method='xml')
    return tree

def get_words_from_mailbox(user, password):
    messages = fetch_unread(user, password)
    cards = []
    for msg in messages:
        word, idiom = parse_msg(msg[1])
        cards.append({'front': word['word_tr'], 'back': "%s\nDefinition: %s\nExample: %s"\
            % (word['word'], word['word_def'], word['word_example'])})
        cards.append({'front': idiom['idiom_tr'], 
                      'back': "%s\nExample: %s" % (idiom['idiom'], idiom['idiom_example'])})
    return cards
