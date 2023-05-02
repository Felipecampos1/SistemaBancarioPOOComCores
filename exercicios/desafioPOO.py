#Desafio DIO Sistema Bancário com POO

import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
CorBranco = '\033[49;97m'
CorVermelho = '\033[49;91m'
CorVerde = '\033[49;92m'


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print(f"\n{CorVermelho}Operação falhou! Você não tem saldo suficiente.{CorVermelho}")

        elif valor > 0:
            self._saldo -= valor
            print(f"\n{CorVerde}=== Saque realizado com sucesso! ==={CorVerde}")
            return True

        else:
            print(f"\n{CorVermelho}Operação falhou! O valor informado é inválido.{CorVermelho}")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"\n{CorVerde}=== Depósito realizado com sucesso! ==={CorVerde}")
        else:
            print(f"\n{CorVermelho}Operação falhou! O valor informado é inválido.{CorVermelho}")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print(f"\n{CorVermelho}Operação falhou! O valor do saque excede o limite.{CorVermelho}")

        elif excedeu_saques:
            print(f"\n{CorVermelho}Operação falhou! Número máximo de saques excedido.{CorVermelho}")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            {CorBranco}Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:{CorBranco}\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = f"""\n
    {CorBranco}================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [7]\tSair{CorBranco}
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print(f"\n{CorVermelho}Cliente não possui conta!{CorVermelho}")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input(f"{CorBranco}Informe o CPF do cliente: {CorBranco}")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print(f"\n{CorVermelho}Cliente não encontrado!{CorVermelho}")
        return

    valor = float(input(f"{CorBranco}Informe o valor do depósito: {CorBranco}"))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input(f"{CorBranco}Informe o CPF do cliente: {CorBranco}")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print(f"\n{CorVermelho}Cliente não encontrado!{CorVermelho}")
        return

    valor = float(input(f"{CorBranco}Informe o valor do saque: {CorBranco}"))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input(f"{CorBranco}Informe o CPF do cliente: {CorBranco}")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print(f"\n{CorVermelho}Cliente não encontrado!{CorVermelho}")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print(f"\n{CorBranco}================ EXTRATO ================{CorBranco}")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = f"{CorBranco}Não foram realizadas movimentações.{CorBranco}"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\t R$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\n{CorBranco}Saldo:\n\tR$ {conta.saldo:.2f}{CorBranco}")


def criar_cliente(clientes):
    cpf = input(f"{CorBranco}Informe o CPF (somente número): {CorBranco}")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print(f"\n{CorVermelho}Já existe cliente com esse CPF!{CorVermelho}")
        return

    nome = input(f"{CorBranco}Informe o nome completo: {CorBranco}")
    data_nascimento = input(f"{CorBranco}Informe a data de nascimento (dd-mm-aaaa): {CorBranco}")
    endereco = input(f"{CorBranco}Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): {CorBranco}")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print(f"\n{CorVerde}=== Cliente criado com sucesso! ==={CorVerde}")


def criar_conta(numero_conta, clientes, contas):
    cpf = input(f"{CorBranco}Informe o CPF do cliente: {CorBranco}")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print(f"\n{CorVermelho}Cliente não encontrado, fluxo de criação de conta encerrado!{CorVermelho}")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print(f"\n{CorVerde}=== Conta criada com sucesso! ==={CorVerde}")


def listar_contas(contas):
    for conta in contas:
        print(f"{CorBranco}={CorBranco}" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            depositar(clientes)

        elif opcao == "2":
            sacar(clientes)

        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "5":
            listar_contas(contas)

        elif opcao == "6":
            criar_cliente(clientes)

        elif opcao == "7":
            print(f"{CorBranco}Até mais...{CorBranco}")
            break

        else:
            print(f"\n{CorVermelho}Operação inválida, por favor selecione novamente a operação desejada.{CorVermelho}")


main()