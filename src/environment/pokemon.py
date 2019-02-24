import json


class Pokemon:
    def __init__(self, *, ident:str=None, ) -> None:
        self.ability = None
        self.active = None
        self.current_hp = None
        self.item = None
        self.level = None
        self.max_hp = None
        self.moves = None
        self.sex = None
        self.species = None
        self.stats = None

        self.ident = ident

    def update_from_request(self, request) -> None:
        if self.ident is None:
            self.ident = request.pop('ident')
        else:
            assert self.ident == request.pop('ident')
        
        details = request.pop('details').split(',')
        if len(details) == 3:
            self.species, self.level, self.sex = details
        elif len(details) == 2:
            self.species, self.level = details
            self.sex = None
        else:
            self.species = details[0]
            self.sex = None
            self.level = 100

        condition = request.pop('condition')
        if condition == '0 fnt':
            # TODO : switch to enum ?
            self.status = 'fnt'
            self.current_hp = self.max_hp = 0
        else:
            if condition[-1] not in '1234567890':
                self.status = condition[-3:]
                condition = condition[:-4]
            self.current_hp, self.max_hp = [int(el) for el in condition.split('/')]
        
        self.ability = request.pop('baseAbility')
        self.active = request.pop('active')
        self.item = request.pop('item')
        self.moves = request.pop('moves')
        self.stats = request.pop('stats')

        request.pop('pokeball')
        request.pop('ability')

        if request:
            print(request)
