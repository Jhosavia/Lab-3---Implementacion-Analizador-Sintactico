class ParserBase:
    def __init__(self, tokens):
        self.tokens = list(tokens) + [("EOF", "EOF")]
        self.i = 0
        self.token, self.lexema = self.tokens[0]

    def leer(self):
        if self.i < len(self.tokens) - 1:
            self.i += 1
        self.token, self.lexema = self.tokens[self.i]

    def error(self, esperado):
        raise SyntaxError(
            f"Error sintáctico: se esperaba {esperado} "
            f"y se encontró {self.token} ('{self.lexema}')"
        )

    def consumir(self, esperado):
        if self.token == esperado:
            lex = self.lexema
            self.leer()
            return lex
        self.error(esperado)

    def fin(self):
        if self.token != "EOF":
            self.error("EOF")


class ParserFor(ParserBase):
    def for_stmt(self):
        self.consumir("for")
        destino = self.consumir("target_list")
        self.consumir("in")
        origen = self.consumir("expression_list")
        self.consumir(":")
        cuerpo = []
        sino = None
        if self.token == "simple_stmt":
            cuerpo.append(self.consumir("simple_stmt"))
        else:
            while self.token == "suite":
                cuerpo.append(self.consumir("suite"))
            if self.token == "else":
                sino = self.else_part()
        return ("ForStmt", destino, origen, cuerpo, sino)

    def else_part(self):
        self.consumir("else")
        self.consumir(":")
        if self.token == "Newline":
            return self.consumir("Newline")
        return self.consumir("suite_else")

    def analizar(self):
        arbol = self.for_stmt()
        self.fin()
        return arbol


class ParserLogica(ParserBase):
    def expresion_logica(self):
        nodo = self.termino()
        while self.token == "or":
            self.leer()
            nodo = ("or", nodo, self.termino())
        return nodo

    def termino(self):
        nodo = self.factor()
        while self.token == "and":
            self.leer()
            nodo = ("and", nodo, self.factor())
        return nodo

    def factor(self):
        negado = False
        if self.token == "not":
            self.leer()
            negado = True
        if self.token == "(":
            self.leer()
            nodo = self.expresion_logica()
            self.consumir(")")
        elif self.token in ("True", "False"):
            nodo = self.consumir(self.token)
        else:
            self.error("'(', True o False")
        return ("not", nodo) if negado else nodo

    def analizar(self):
        arbol = self.expresion_logica()
        self.fin()
        return arbol


class ParserDef(ParserBase):
    def def_stmt(self):
        self.consumir("def")
        nombre = self.consumir("function_name")
        params = []
        if self.token == "(":
            self.leer()
            if self.token == "parameter":
                params = self.parametros()
            self.consumir(")")
        self.consumir(":")
        if self.token == "simple_stmt":
            cuerpo = [self.consumir("simple_stmt")]
        else:
            cuerpo = [self.consumir("statement")]
            while self.token == "statement":
                cuerpo.append(self.consumir("statement"))
        return ("DefStmt", nombre, params, cuerpo)

    def parametros(self):
        lista = [self.consumir("parameter")]
        while self.token == ",":
            self.leer()
            lista.append(self.consumir("parameter"))
        return lista

    def analizar(self):
        arbol = self.def_stmt()
        self.fin()
        return arbol
