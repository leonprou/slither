import logging

from slither.core.declarations.contract import Contract
from slither.vyper_parsing.declarations.function import FunctionVyper
from slither.vyper_parsing.declarations.event import EventVyper
from vyper.signatures.event_signature import EventSignature
from vyper.signatures.function_signature import FunctionSignature

from slither.vyper_parsing.variables.state_variable import StateVariableVyper


logger = logging.getLogger("ContractVyperParsing")

class ContractVyper(Contract):
    def __init__(self, slitherVyper, data):
        super(ContractVyper, self).__init__()

        self.set_slither(slitherVyper)
        self._data = data

        self._functionsNotParsed = []
        # self._modifiersNotParsed = []
        self._functions_no_params = []
        # self._modifiers_no_params = []
        self._eventsNotParsed = []
        self._variablesNotParsed = []
        # self._enumsNotParsed = []
        self._structuresNotParsed = []
        # self._usingForNotParsed = []

        self._is_analyzed = False

        # use to remap inheritance id
        # self._remapping = {}

        self._name = self._data['name']
        #
        # self._id = self._data['id']
        #
        # self._inheritance = []

        # self._parse_contract_info()
        self._parse_contract_items()

    def get_key(self):
        return self.slither.get_key()

    def _parse_contract_items(self):
        if not 'body' in self._data: # empty contract
            return
        for item in self._data['body']:
            # print(item[self.get_key()])
            if item[self.get_key()] == 'FunctionDef':
                self._functionsNotParsed.append(item)
            elif item[self.get_key()] == 'EventDef':
                self._eventsNotParsed.append(item)
            elif item[self.get_key()] == 'VariableDeclaration':
                self._variablesNotParsed.append(item)
            else:
                logger.error('Unknown contract item: '+ item[self.get_key()])
                # exit(-1)

    def _parse_function(self, function):
        func = FunctionVyper(function, self)
        self.slither.add_function(func)
        self._functions_no_params.append(func)

    def parse_functions(self):

        for function in self._functionsNotParsed:
            self._parse_function(function)


        self._functionsNotParsed = None

        return

    def parse_state_variables(self):
        for key, var_rec in self.slither._global_ctx._globals.items():
            var = StateVariableVyper(var_rec)
            var.set_contract(self)
            self._variables[var.name] = var

    def analyze_events(self):
        for code in self.slither._global_ctx._events:
            event_sig = EventSignature.from_declaration(code, self.slither._global_ctx)
            event = EventVyper(event_sig, self)
            event.analyze()
            self._events[event._name] = event

    def analyze_state_variables(self):
        for var in self.variables:
            var.analyze()

    @property
    def is_analyzed(self):
        return self._is_analyzed

    def set_is_analyzed(self, is_analyzed):
        self._is_analyzed = is_analyzed
