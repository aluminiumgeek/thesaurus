# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# thesaurus.py (c) Mikhail Mezyakov <mihail265@gmail.com>
#
# Pretty and really fast asynchronous client for Thesaurus service written with Twisted
#
# pip install twisted
# pip install colorama

import optparse
import sys

from urllib import urlencode

from colorama import Fore, Style
from colorama import init
init(autoreset=True)

from word import Word, NoResponseException


parameters = {
    'output': 'json',
    'key': 'fNPX4FgUWBPd4yQwOwK5'
}

languages = {
    'en': 'US',
    'ru': 'RU',
    'it': 'IT',
    'fr': 'FR',
    'de': 'DE',
    'el': 'GR',
    'es': 'ES',
    'no': 'NO',
    'pt': 'PT',
    'ro': 'RO',
    'sk': 'SK'
}


def parse_args():
    usage = """Usage: %prog [-l <lang>|--lang=<lang>] <word1> [word2] [word3] ...

    Thesaurus multilingual client.
    Example:

      python %prog sun morning show word ...

    Available 'lang' options:
    \t{0}
    Default lang: en
    """.format(', '.join(languages))

    parser = optparse.OptionParser(usage, version='%prog 1.0')
    
    parser.add_option(
        '--lang', '-l',
        action='store',
        dest='lang',
        default='en',
        help='Input language'
    )
    
    options, words = parser.parse_args()
    
    if not options.lang in languages:
        parser.error("Incorrect language value.\nAvailable languages: {0}".format(
            ', '.join(languages)
        ))
        
    if not words:
        parser.error('No words to process')
    
    return options, words


def generate_lang(lang):
    """
    Generate standart language string.
    
    @param lang: lanuage code
    @type lang: 2-letter string
    
    @return: language string (en_US)
    @rtype: string
    """
    
    return '{0}_{1}'.format(lang, languages[lang])
      
def print_err(msg):
    """Print colored error message to stderr"""
    
    print >>sys.stderr, Fore.RED + Style.BRIGHT + msg

def get_answer(word, lang=None):
    """
    Create and return Deferred for data retrieving.
    
    @param word: word for processing
    @type word: string
    
    @param lang: language code
    @type lang: 2-letter string
    
    @return: deferred for page retrieving
    @rtype: Twisted Deferred
    """
    
    from twisted.web.client import getPage
    
    parameters.update(word=word)
    
    if lang is not None:
        parameters.update(language=generate_lang(lang))
    
    url = 'http://thesaurus.altervista.org/service.php?%s'%urlencode(parameters)
    
    return getPage(url)

def thesaurus():
    """Retrieve and print word's info from Thesaurus service"""
    
    options, words = parse_args()
    
    from twisted.internet import reactor
    
    completed = []

    def answer_received(answer, word):
        """Callback for successful call."""
        
        completed.append(answer)
        
        word = Word(word, answer)
        synonyms = word.get_synonyms()
        
        print u'{green}{word}{normal} {cyan}has {num} synonyms:{normal}\n{synonyms}'.format(
            word = unicode(str(word), 'utf-8'),
            num = len(synonyms),
            synonyms = u', '.join(synonyms),
            green = Fore.GREEN+Style.BRIGHT,
            cyan = Fore.CYAN,
            normal = Style.RESET_ALL
        )
        
    def answer_lost(err):
        """Errback for unsuccessful data"""
        
        completed.append(err)
        
        print_err('No answer')
        
    def processing_finished(_):
        if len(completed) == len(words):
            reactor.stop() # stop reactor when all words were processed
            
    def processing_error(err):
        """Errback for unsuccessfull word processing"""
        
        print_err('There was an error while processing answer')
    
    for word in words:
        d = get_answer(word, options.lang)
        
        args = (word,)
        
        d.addCallbacks(answer_received, answer_lost, args)
        d.addCallbacks(processing_finished, processing_error)

    reactor.run()

if __name__ == '__main__':
    thesaurus()
