# -*- coding: utf-8 -*-
#
# word.py (c) Mikhail Mezyakov <mihail265@gmail.com>
#
# Object that represents content received from Thesaurus

import json


class NoResponseException(Exception):
    """Raises when json has no 'response' block"""
    
    def __str__(self):
        return 'No response block!'


class Word:
    """Class represents Thesaurus word content"""
    
    def __init__(self, word, structure):
        self.word = word
        self.structure_json = structure
        self.structure = self.load_json(structure)
        
    @property
    def structure(self):
        """Getter for structure variable"""
        
        return self.structure
      
    @property
    def raw_structure(self):
        """Getter for json string"""
        
        return self.structure_json
      
    def load_json(self, to_load):
        """
        Return var with loaded json. Raise NoResponseException
        if there's no response block in json.
        
        @param to_load: json string
        @type to_load: string or unicode
        
        @return: new dictionary from json
        @rtype: dictionary
        """
        
        loads = json.loads(to_load, encoding='utf-8')
        
        if 'response' in loads:
            return loads['response']
        else:
            raise NoResponseException
      
    def get_synonyms(self):
        """
        Generate and return list of synonyms.
        
        @return: list of synonyms
        @rtype: list
        """
        
        lists = map(lambda x: x['list'], self.structure)
        categories = map(lambda x: x['synonyms'], lists)
        
        synonyms = reduce(
            lambda x, y: x + y,
            map(lambda x: x.split('|'), categories)
        )
        
        return synonyms
      
    def __str__(self):
        return self.word
