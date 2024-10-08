from backend import semanas, Planejamento, Turmas, DOCENTE
from backend import disciplinas as new_disciplinas
from unidecode import unidecode
import re, os, sys
import pickle as pk
import easygui as eg
import pandas as pd
from datetime import datetime as dt
import signal

def deseja_salvar():
    if input("Deseja salvar alterações antes de sair [s/N]? ").upper().startswith("S"):
        with open(planFile, "wb") as f:
            pk.dump(disciplinas, f)
            print("Alterações salvas!")

def handle_sigint(signum, frame):
    print("Se quiser sair, use a opção apropriada do menu.")
    
signal.signal(signal.SIGINT, handle_sigint)

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

def mostraDF(subdf, dsubdf):
    old = ""
    for ind in subdf.index:
        docente = dsubdf.loc[dsubdf["COD_TURMA"] == subdf["COD_TURMA"][ind], "NOME_DOCENTE"].values
        if subdf["COD_TURMA"][ind] != old:
            print('>> ', subdf["COD_DISCIPLINA"][ind], end=" ")
            print("   ", subdf["NOME_DISCIPLINA"][ind], end=" ")
            print(" - Turma", subdf["COD_TURMA"][ind])
            print("   ", "Docentes", docente)
        print("    -", subdf["TIPO_AULA"][ind], "(", subdf["NUM_SALA"][ind], ")", subdf["DIA_SEMANA"][ind], end=" ")
        print(dt.time(subdf["HR_INICIO"][ind]), end=" ")
        print(dt.time(subdf["HR_FIM"][ind]))
        old = subdf["COD_TURMA"][ind]
    print("")

def entraSigla(msg="Informe sigla: ", force=False):
    global SIGLA
    if SIGLA and not force:
        return SIGLA
    sigla = input(msg).upper()
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
        if opc and int(opc) in options:
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
        if opc and opc.isnumeric() and int(opc) < len(aux):
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
    planejamento.printDisciplina(disciplinas, sigla)
    print(f"\n({sigla}) {disciplina['codigo']} > {disciplina['nome']}")
    print(f"- {disciplina['periodo']}º período" if disciplina['periodo'] != 99 else "- Optativa", end=" | ")
    print(f"Carga Horária: {disciplina['cht']} (T) + {disciplina['chp']} (P) = {disciplina['ch']} horas")
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
    if "obs" in disciplinas.curriculum[sigla]:
        print("*** OBS.:", disciplinas.curriculum[sigla]["obs"])
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
        observa = input("Informe observação sobre modificação [ENTER p/ não informar]:\n")
        if observa:
            disciplinas.curriculum[sigla]['obs'] = observa
        print("Alteração realizada!")
    if prop == 'slt' or prop == 'slp':
        while True:
            novo = input("Informe o novo número de slots: ")
            if novo.isnumeric():
                novo = int(novo)
                break
        if input(f"Deseja continuar [s/N]? ").upper() in ["", "N"]:
            return
        disciplinas.curriculum[sigla][prop] = novo
        observa = input("Informe observação sobre modificação [ENTER p/ não informar]:\n")
        if observa:
            disciplinas.curriculum[sigla]['obs'] = observa
        print("Alteração realizada!")
    if prop == 'nome':
        novo = input("Informe o novo nome: ")
        if input(f"Deseja continuar [s/N]? ").upper() in ["", "N"]:
            return
        disciplinas.curriculum[sigla][prop] = novo
        observa = input("Informe observação sobre modificação [ENTER p/ não informar]:\n")
        if observa:
            disciplinas.curriculum[sigla]['obs'] = observa
        print("Alteração realizada!")
    

planejamento = Planejamento()
while True:
    try:
        print("\n\n============")
        print("    MENU")
        print("============\n")
        if SIGLA:
            print(f"FOCO: ({SIGLA}) {disciplinas.curriculum[SIGLA]['codigo']} {disciplinas.curriculum[SIGLA]['nome']}")
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
        print(" PD - imPrimir um Docente")
        print(" PO - imPrimir tOdos os Docentes")
        print(" CH - Conflito Horário")
        print(" CD - Conflito Docente")
        print(" MP - Modifica Propriedades")
        print(" S  - Salva planejamento")
        print(" OB - OBservações")
        print(" RC - Relatório engenharia de Computação")
        print(" CO - Comparar com ofertas")
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
                foco = disciplinas.curriculum[m[0]]
                print(f"> {m[0]:>7s} {foco['codigo']} {foco['nome']}",*m[1:])
            print("")
            sigla = entraSigla("Informe sigla, se desejar assumir [ENTER p/ cancelar]: ", force=True)
            if not sigla:
                continue
            SIGLA = sigla
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
            while True:
                lookup = unidecode(input("Informe codigo, nome ou padrão de busca: ")).upper()
                if not lookup in disciplinas.curriculum:
                    for k, v in disciplinas.curriculum.items():
                        if lookup in v["codigo"] or lookup in unidecode(v["nome"]).upper():
                            print(v["codigo"], v["nome"]," > ", k)
                    sigla = input("Qual sigla deseja trabalhar [ENTER para cancelar]: ").upper()
                    if sigla and sigla in disciplinas.curriculum:
                        SIGLA = sigla
                        break
                    elif sigla == "":
                        break
                    else:
                        print("Não encontrado!")
                else:
                    sigla = lookup
                    v = disciplinas.curriculum[sigla]
                    print("Assumindo:", v["codigo"], v["nome"]," > ", sigla)
                    SIGLA = sigla
                    break
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
        elif opc == "PD":
            while True:
                doc = input("Informe o docente [ENTER para cancelar]: ").title()
                if doc == "" or doc in DOCENTE:
                    break
            if doc:
                planejamento.printDocentes(disciplinas, DOCENTE[doc])
        elif opc == "RC":
            ecpdocs = [
                "Cardoso",
                "Lamounier",
                "Louza",
                "Peretta",
                "Keiji",
                "Kil",
                "Barros",
                "Rodrigues",
                "Cunha",
            ]
            for doc in ecpdocs:
                planejamento.printDocentes(disciplinas, DOCENTE[doc])
            planejamento.conflitoHorarios(disciplinas)
            planejamento.conflitoProfessores(disciplinas, docs=ecpdocs)   
            planejamento.printHoraAulaDocentes(disciplinas, ecpdocs)
        elif opc == "PO":
            planejamento.printDocentes(disciplinas)
        elif opc == "C":
            print("\n>> Informação completa em:")
            for m in disciplinas.complete():
                print(*m)
            print("")
        elif opc == "CH":
            planejamento.conflitoHorarios(disciplinas)
        elif opc == "CD":
            planejamento.conflitoProfessores(disciplinas)
        elif opc == "MP":
            sigla = entraSigla()
            if not sigla:
                continue
            modificaPropriedades(sigla)
        elif opc == "OB":
            print("OBSERVAÇÕES:")
            fno = "observações.txt"
            with open(fno, "r") as f:
                for line in list(l.strip() for l in f.readlines() if l.strip()):
                    print(line)
            while True:
                obs = input("INCLUIR [ENTER p/ cancelar]: ")
                if obs == "":
                    break
                with open(fno, "a") as f:
                    f.write("- " + obs + "\n")
        elif opc == "CO":
            dxlsfn = eg.fileopenbox(title='Selecione arquivo com docentes em ofertas (SG 11.02.03.99.10)', default="../*.xlsx",
                                filetypes=[["*", "All files"], ["*.xls","*.xlsx","*.ods", "Excel Files"]])
            if dxlsfn:
                xlsfn = eg.fileopenbox(title='Selecione arquivo com ofertas (SG 11.02.03.99.02)', default="../*.xlsx",
                                    filetypes=[["*", "All files"], ["*.xls","*.xlsx","*.ods", "Excel Files"]])
                if xlsfn:
                    df = pd.read_excel(xlsfn)
                    ddf = pd.read_excel(dxlsfn)
                    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
                    ddf = ddf.map(lambda x: x.strip() if isinstance(x, str) else x)
                    for k, v in disciplinas.curriculum.items():
                        mostraDisciplina(k)
                        subdf = df[df["COD_DISCIPLINA"] == v['codigo']]
                        dsubdf = ddf[ddf["COD_DISCIPLINA"] == v['codigo']]
                        mostraDF(subdf, dsubdf[["COD_TURMA","NOME_DOCENTE"]])
                        input("Tecle ENTER pra continuar... ")
        elif opc == "Q":
            # if input("Deseja salvar alterações antes de sair [s/N]? ").upper().startswith("S"):
            #     with open(planFile, "wb") as f:
            #         pk.dump(disciplinas, f)
            #         print("Alterações salvas!")
            deseja_salvar()
            break
    except KeyboardInterrupt:
        print("COTRL+C detectado!")
    pause()
        