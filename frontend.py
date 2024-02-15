from backend import semanas, Planejamento, Turmas, DOCENTE
from backend import disciplinas as new_disciplinas
from unidecode import unidecode
import re, os
import pickle as pk

planFile = "planning.pk"

if os.path.exists(planFile):
    with open(planFile, "rb") as f:
        disciplinas = pk.load(f)
    for k, v in new_disciplinas.curriculum.items():
        if not k in disciplinas.curriculum:
            disciplinas.curriculum[k] = v
    todel = list()
    for k, v in disciplinas.curriculum.items():
        if not k in new_disciplinas.curriculum:
            todel.append(k)
    for td in todel:
        del disciplinas.curriculum[td]
else:
    disciplinas = new_disciplinas

SIGLA = ""

pause = lambda : input("Tecle ENTER ...")

def entraSigla():
    global SIGLA
    if SIGLA:
        return SIGLA
    sigla = input("Informe sigla: ").upper()
    if sigla in disciplinas.curriculum:
        SIGLA = sigla
        return sigla
    print("Sigla não encontrada")
    pause()

def insereTurma(sigla):
    turma = input("Informe a turma [',' para sep, ENTER para cancelar]: ").upper()
    if turma:
        for t in turma.split(","):
            t = t.strip()
            disciplinas.setTurma(sigla, t)

def apagaTurma(sigla):
    while True:
        aux = disciplinas.curriculum[sigla]["turmas"]
        aux = sorted(list(set(list(a.split(":")[0] for a in aux))))
        if not aux:
            break
        options = dict()
        for i, t in enumerate(aux):
            print(i, "-", t)
            options[i] = t
        print("Q - Cancelar")
        opc = input("Qual apagar? ").upper()
        if opc == "Q":
            break
        if opc:
            p, q = f"{options[int(opc)]}:T", f"{options[int(opc)]}:P"
            if p in disciplinas.curriculum[sigla]["turmas"]:
                del disciplinas.curriculum[sigla]["turmas"][p]
            if q in disciplinas.curriculum[sigla]["turmas"]:
                del disciplinas.curriculum[sigla]["turmas"][q]

def insereDocente(sigla, docente):
    if not docente in DOCENTE:
        print("Não encontrado!")
        print("Cadastrados: " + "; ".join(DOCENTE.keys()))
        return
    docente = DOCENTE[docente.title()]
    while True:
        aux = disciplinas.curriculum[sigla]["turmas"]
        if not aux:
            print("\n> ERRO: Sem turmas na disciplina\n")
            break
        options = dict()
        for i, t in enumerate(aux):
            print(i, "-", t)
            options[i] = t
        print("Q - Cancelar")
        opc = input(f"Qual atribuir a {docente}? ").upper()
        if opc == "Q":
            break
        if opc and opc.isnumeric() and int(opc) < len(aux):
            disciplinas.curriculum[sigla]["turmas"][options[int(opc)]].docentes.append(docente)

def apagaDocente(sigla):
    print("Os docentes alocados:")
    while True:
        aux = disciplinas.curriculum[sigla]["turmas"]
        if not aux:
            print("\n> ERRO: Sem turmas na disciplina\n")
            break
        options = dict()
        for i, t in enumerate(aux):
            options[i] = t
        for i, t in enumerate(aux):
            print(i, "-", t, ":", *disciplinas.curriculum[sigla]["turmas"][t].docentes)
        print("Q - Cancelar")
        opc = input(f"Apagar docentes de qual turma? ").upper()
        if opc == "Q":
            break
        if opc and opc.isnumeric() and int(opc) < len(aux):
            if input(f"Da turma {options[int(opc)]}; deseja continuar [s/N]? ").upper() in ["", "N"]:
                return
            disciplinas.curriculum[sigla]["turmas"][options[int(opc)]].docentes = list()

def insereSlots(sigla):
    while True:
        aux = disciplinas.curriculum[sigla]["turmas"]
        if not aux:
            print("\n> ERRO: Sem turmas na disciplina\n")
            break
        options = dict()
        for i, t in enumerate(aux):
            print(i, "-", t)
            options[i] = t
        print("Q - Cancelar")
        opc = input(f"Qual atribuir horários? ").upper()
        if opc == "Q":
            break
        if opc:
            turma = options[int(opc)]
            nslots = disciplinas.curriculum[sigla]["slt"] if turma.endswith("T") else disciplinas.curriculum[sigla]["slp"]
            while True:
                print(f"Informe horários para {turma} ({nslots} slots) [',' para sep, ENTER para cancelar]")
                horarios = input("na forma '[2-7(dds)][M|T|N][1-6(*no turno)]': ").upper()
                if horarios == "":
                    return
                # pattern = r"[2-6]:[M|T|N][1-6]"
                pattern = r"[2-7][M|T|N][1-6]"
                if len(re.findall(pattern, horarios)) == nslots:
                    break
                print(f"> {nslots} slots não condiz com '{horarios}' ou mnemônico não reconhecido!\n")
            for horario in list(h.strip() for h in horarios.split(",")):
                disciplinas.curriculum[sigla]["turmas"][turma].slots.append(semanas.slot(horario))

def apagaSlots(sigla):
    print("Os horários alocados:")
    while True:
        aux = disciplinas.curriculum[sigla]["turmas"]
        if not aux:
            print("\n> ERRO: Sem turmas na disciplina\n")
            break
        options = dict()
        for i, t in enumerate(aux):
            options[i] = t
        for i, t in enumerate(aux):
            print(i, "-", t, ":", disciplinas.curriculum[sigla]["turmas"][t].slots)
        print("Q - Cancelar")
        opc = input(f"Apagar horários de qual turma? ").upper()
        if opc == "Q":
            break
        if opc and opc.isnumeric() and int(opc) < len(aux):
            if input(f"Da turma {options[int(opc)]}; deseja continuar [s/N]? ").upper() in ["", "N"]:
                return
            disciplinas.curriculum[sigla]["turmas"][options[int(opc)]].slots = list()

def mostraDisciplina(sigla):
    disciplina = disciplinas.curriculum[sigla]
    print(f"\n({sigla}) {disciplina["codigo"]} > {disciplina["nome"]}")
    print(f"{disciplina["periodo"]}º período | Carga Horária: {disciplina["cht"]} (T) + {disciplina["chp"]} (P) = {disciplina["ch"]}")
    print("Turmas:")
    if disciplinas.curriculum[sigla]["turmas"]:
        for k, v in disciplinas.curriculum[sigla]["turmas"].items():
            docente = "< Sem docente >"
            horario = "< Sem horário >"
            if v.docentes:
                docente = ", ".join(v.docentes)
            if v.slots:
                horario = "; ".join(list(f"{t[0]} {t[1][0]}~{t[1][1]}" for t in v.slots))
            print(f"- {k} - {docente}")
            print(f"--- Horários: {horario}")
    else:
        print("< Sem turmas >")
    print("")

def modificaPropriedades(sigla):
    disciplina = disciplinas.curriculum[sigla]
    print("\nATENÇÃO! Opção **avançada**!")
    for i, k in enumerate(disciplina.keys()):
        if k != "turmas":
            print(f"{i}. {k}")
    opc = input("Escolha a propriedade a modificar [ENTER para cancelar]: ")
    if opc == "" or not opc.isnumeric() or int(opc) >= len(disciplina):
        return
    prop = list(disciplina.keys())[int(opc)]
    print(f"A propriedade escolhida '{prop}' é do tipo "
          f"'{type(disciplinas.curriculum[sigla][prop])}' e contém: {disciplinas.curriculum[sigla][prop]}")
    if prop == 'periodo':
        while True:
            novo = input("Informe o novo período de oferta: ")
            if novo.isnumeric():
                novo = int(novo)
                break
        if input(f"Deseja continuar [s/N]? ").upper() in ["", "N"]:
            return
        disciplinas.curriculum[sigla][prop] = novo
        print("Alteração realizada!")
    

planejamento = Planejamento()
while True:
    print("\n\n============")
    print("    MENU")
    print("============\n")
    if SIGLA:
        print(f"FOCO: ({SIGLA}) {disciplinas.curriculum[SIGLA]["codigo"]} {disciplinas.curriculum[SIGLA]["nome"]}")
        print("Completo:", disciplinas.iscomplete(SIGLA)[0])
    else:
        print(f"Disciplina ativa: Nenhuma")
    print("\n *  - limpa foco")
    print(" M  - Muda foco de disciplina")
    print(" F  - Faltando informação")
    print(" C  - Completas")
    print(" V  - Visualizar disciplina")
    print(" IT - Insere Turma")
    print(" ID - Insere Docentes")
    print(" IH - Insere Horário (slots)")
    print(" AT - Apaga Turma")
    print(" AD - Apaga Docentes")
    print(" AH - Apaga Horários (slots)")
    print(" PP - imPrimir um Período")
    print(" PT - imPrimir Todos os períodos")
    print(" CH - Conflito Horário")
    print(" CD - Conflito Docente")
    print(" MP - Modifica Propriedades")
    print(" S  - Salva planejamento")
    print(" Q  - sair (Quit)")
    opc = input("Opção: ").upper()
    if 0 < opc.count("*") < len(opc):
        SIGLA = ""
        opc = opc.replace("*", "")
    if opc in ["IT", "AT"]:
        extra = entraSigla()
        if not extra:
            continue
        if opc == "IT":
            insereTurma(extra)
        elif opc == "AT":
            apagaTurma(extra)
    elif opc == "F":
        print("\n>> Falta informação em:")
        for m in disciplinas.missing():
            print(*m)
        print("")
    elif opc == "*":
        SIGLA = ""
    elif opc == "ID":
        sigla = entraSigla()
        if not sigla:
            continue
        docente = input("Informe docente: ").title()
        insereDocente(sigla, docente)
    elif opc == "IH":
        sigla = entraSigla()
        if not sigla:
            continue
        insereSlots(sigla)
    elif opc == "V":
        sigla = entraSigla()
        if not sigla:
            continue
        mostraDisciplina(sigla)
    elif opc == "M":
        lookup = unidecode(input("Informe codigo, nome ou padrão de busca: ")).upper()
        for k, v in disciplinas.curriculum.items():
            if lookup in v["codigo"] or lookup in unidecode(v["nome"]).upper():
                print(v["codigo"], v["nome"]," > ", k)
        sigla = input("Qual sigla deseja trabalhar [ENTER para cancelar]: ").upper()
        if sigla and sigla in disciplinas.curriculum:
            SIGLA = sigla
    elif opc == "AD": # apaga docente
        sigla = entraSigla()
        if not sigla:
            continue
        apagaDocente(sigla)
    elif opc == "AH": # apaga horarios
        sigla = entraSigla()
        if not sigla:
            continue
        apagaSlots(sigla)
    elif opc == "S":
        with open(planFile, "wb") as f:
            pk.dump(disciplinas, f)
            print("Alterações salvas!")
    elif opc == "PP":
        per = input("Informe o período [99 p/ optativas, ENTER para cancelar]: ")
        if per.isnumeric():
            planejamento.print(disciplinas, int(per))
    elif opc == "PT":
        planejamento.print(disciplinas)
    elif opc == "C":
        print("\n>> Informação completa em:")
        for m in disciplinas.complete():
            print(*m)
        print("")
    elif opc == "CH":
        planejamento.conflitoHorarios(disciplinas)
    elif opc == "CD":
        print("NÃO IMPLEMENTADO AINDA!")
        pass
    elif opc == "MP":
        sigla = entraSigla()
        if not sigla:
            continue
        modificaPropriedades(sigla)
    elif opc == "Q":
        if input("Deseja salvar alterações antes de sair [s/N]? ").upper().startswith("S"):
            with open(planFile, "wb") as f:
                pk.dump(disciplinas, f)
                print("Alterações salvas!")
        break
    pause()
        