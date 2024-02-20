class Semanas:
    def __init__(self):
        def code(x):
            a = int(x.split(":")[0])
            if a < 12:
                return "M"
            elif 12 < a < 18:
                return "T"
            return "N"
        self.dias = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]
        self.horarios = [
            ("7:10", "8:00"),
            ("8:00", "8:50"),
            ("8:50", "9:40"),
            ("9:50", "10:40"),
            ("10:40", "11:30"),
            ("11:30", "12:20"),
            ("13:10", "14:00"),
            ("14:00", "14:50"),
            ("14:50", "15:40"),
            ("16:00", "16:50"),
            ("16:50", "17:40"),
            ("17:40", "18:30"),
            ("19:00", "19:50"),
            ("19:50", "20:40"),
            ("20:50", "21:40"),
            ("21:40", "22:30"),
        ]
        values = list(
            (i, j) for i in range(len(self.dias)) for j in range(len(self.horarios))
        )
        keys = list(
            # f"{i}:{code(self.horarios[j][0])}{j%6 + 1}" for i in range(1, len(self.dias)+1) for j in range(len(self.horarios))
            f"{i}{code(self.horarios[j][0])}{j%6 + 1}" for i in range(1, len(self.dias)+1) for j in range(len(self.horarios))
        )
        self.slots = dict(zip(keys, values))
    def slot(self, key):
        aux = self.slots[key]
        return self.dias[aux[0]], self.horarios[aux[1]]
    
DOCENTE = {
    "Cardoso": "Alexandre Cardoso",
    "Lamounier": "Edgard Afonso Lamounier Júnior",
    "Louza": "Felipe Alves da Louza",
    "Peretta": "Igor Santos Peretta ",
    "Keiji": "Keiji Yamanaka",
    "Kil": "Kil Jin Brandini Park ",
    "Vieira": "Luciano Vieira Lima",
    "Barros": "Marcelo Barros de Almeida",
    "Rodrigues": "Marcelo Rodrigues de Sousa ",
    "Cunha": "Márcio José da Cunha",
    "?": "Outro",
    "Alan": "Alan Petrônio Pinheiro",
    "Eder": "Éder Alves de Moura",
    "Milena": "Milena Bueno Pereira Carneiro",
    "Ederson": "Éderson Rosa da Silva",
}

class Turmas:
    def __init__(self, key, id, tipo, nslots):
        self.parent = key
        self.id = id
        self.tipo = tipo # "T" | "P"
        self.docentes = list()
        self.slots = list()
        self.nslots = nslots
    def __repr__(self):
        return f"Turmas OBJ: {self.parent} {self.id} {self.tipo}"

class Disciplinas:
    def load(self, filename):
        with open(filename, "r") as f:
            lines = list(l.strip() for l in f.readlines() if l.strip())
        info = list()
        for l in lines:
            aux = l.split(",")
            for a in range(len(aux)):
                if aux[a].isnumeric():
                    aux[a] = int(aux[a])
            info.append(aux)
        return info
    def __init__(self, filename):
        info = self.load(filename)
        self.curriculum = dict()
        for i in sorted(info, key=lambda x:(x[3], x[0])):
            key = i[2] # sigla
            if key in self.curriculum:
                raise Exception(f"{key} de {i[1]} já existe; {self.curriculum[key]['nome']}")
            self.curriculum[key] = dict()
            self.curriculum[key]["codigo"] = i[0]
            self.curriculum[key]["nome"] = i[1]
            self.curriculum[key]["periodo"] = i[3]
            self.curriculum[key]["cht"] = i[4]
            self.curriculum[key]["chp"] = i[5]
            self.curriculum[key]["ch"] = i[6]
            self.curriculum[key]["slt"] = i[4]//15
            self.curriculum[key]["slp"] = i[5]//15
            self.curriculum[key]["turmas"] = dict() # "turma:T" | "turma:P"
    def iscomplete(self, sigla):
        analise = list()
        turmas = list()
        for tid, tobj in self.curriculum[sigla]["turmas"].items():
            analise.append((tid, self.curriculum[sigla]["turmas"][tid].docentes and self.curriculum[sigla]["turmas"][tid].slots))
            if analise[-1][1]:
                turmas.append(tobj)
        return all(list(a[1] for a in analise)) if analise else False, analise, turmas
    def getForDocente(self, docente):
        report = list()
        for k, v in self.curriculum.items():
            for kk, vv in v["turmas"].items():
                if docente in vv.docentes:
                    report.append((f"({v['codigo']}) {v['nome']} - Turma: {vv.id}[{kk[-1]}]", v["slt"] if kk[-1] == "T" else v["slp"]))
        total = sum(map(lambda x: x[1], report))
        return report, total
    def getForPeriodo(self, periodo):
        report = list()
        for k, v in self.curriculum.items():
            if periodo == v["periodo"]:
                for kk, vv in v["turmas"].items():
                    report.append((f"({v['codigo']}) {v['nome']} - Turma: {vv.id}[{kk[-1]}]", v["slt"] if kk[-1] == "T" else v["slp"]))
        total = sum(map(lambda x: x[1], report))
        return report, total
    def setTurma(self, key, turma):
        if self.curriculum[key]["slt"] > 0:
            self.curriculum[key]["turmas"][f"{turma}:{'T'}"] = Turmas(
                key, turma, 'T', self.curriculum[key]["slt"] # if tipo == "T" else self.curriculum[key]["slp"]
            )
        if self.curriculum[key]["slp"] > 0:
            self.curriculum[key]["turmas"][f"{turma}:{'P'}"] = Turmas(
                key, turma, 'P', self.curriculum[key]["slp"] # if tipo == "T" else self.curriculum[key]["slp"]
            )
    def missing(self):
        miss = list()
        for k, v in sorted(self.curriculum.items(), key=lambda x:x[0]):
            if v["turmas"]:
                for kk, vv in v["turmas"].items():
                    reason = list()
                    if not vv.docentes:
                        reason.append("sem docente")
                    if not vv.slots:
                        reason.append(f"sem horários ({vv.nslots} slots)")
                    if len(reason) > 0:
                        miss.append((k, kk, reason))
            else:
                miss.append((k, None, ["sem turma"]))
        return miss
    def complete(self):
        compl = list()
        for k, v in sorted(self.curriculum.items(), key=lambda x:x[0]):
            if v["turmas"]:
                for kk, vv in v["turmas"].items():
                    okd = list()
                    if vv.docentes:
                        okd.append(True)
                    else:
                        okd.append(False)
                    if vv.slots:
                        okd.append(True)
                    else:
                        okd.append(False)
                    if all(okd):
                        compl.append((k, kk))
        return compl
    
class ListMatrixByLabels:
    def __init__(self, row_labels:list, col_labels:list):
        self.rows = row_labels
        self.cols = col_labels
        self.data = [[list() for _ in range(len(self.cols))] for _ in range(len(self.rows))]
    def __getitem__(self, key):
        row, col = key
        return self.data[self.rows.index(row)][self.cols.index(col)]
    def __setitem__(self, key, value):
        row, col = key
        self.data[self.rows.index(row)][self.cols.index(col)].append(value)
    def __repr__(self):
        return str(self.data)


class Planejamento:
    def __init__(self):
        semana = Semanas()
        self.rows = semana.horarios
        self.cols = semana.dias[1:] # remove "DOM"
    def prepare(self, disciplinas):
        periodos = dict()
        for k, v in disciplinas.curriculum.items():
            if not v["periodo"] in periodos:
                periodos[v["periodo"]] = ListMatrixByLabels(self.rows, self.cols)
            _, anali, turmas = disciplinas.iscomplete(k)
            for a, t in zip(anali, turmas):
                if a:
                    for s in a[1]:
                        periodos[v["periodo"]][s[1], s[0]].append((k, t.id, t.tipo))
        return periodos
    def prepareDocentes(self, disciplinas):
        docentes = dict(zip(DOCENTE.values(), list(ListMatrixByLabels(self.rows, self.cols) for _ in range(len(DOCENTE)))))
        for k, v in disciplinas.curriculum.items():
            for tid, tinf in v["turmas"].items():
                for d in tinf.docentes:
                    for s in tinf.slots:
                        docentes[d][s[1], s[0]].append((tinf.parent, tinf.id, tinf.tipo))
    def prepareDisciplinas(self, disciplinas):
        all_disciplinas = dict(zip(disciplinas.curriculum.keys(), list(ListMatrixByLabels(self.rows, self.cols) \
                                                                   for _ in range(len(disciplinas.curriculum.keys())))))
        for k, v in disciplinas.curriculum.items():
            for tid, tinf in v["turmas"].items():
                for s in tinf.slots:
                    all_disciplinas[k][s[1], s[0]].append((tinf.parent, tinf.id, tinf.tipo))
        return all_disciplinas
    def conflitoHorarios(self, disciplinas):
        print("\nCONFLITOS DE HORÁRIOS:")
        prep_disc = self.prepare(disciplinas)     
        for periodo, matriz in prep_disc.items():
            for hor in self.rows:
                linesincols = list()
                for dia in self.cols:
                    siglas = set(s[0] for s in matriz[hor, dia])
                    linesincols.append(len(siglas))
                nlines = max(linesincols)
                if nlines > 1:
                    dia = self.cols[linesincols.index(nlines)]
                    print(f"- {str(periodo)}º período" if periodo != 99 else "- Optativas", end=" ==> ")
                    print(f"{dia} ({hor[0]}~{hor[1]}) : ", end= "")
                    listadisc = list()
                    for info in matriz[hor, dia]:
                        listadisc.append(f"{info[0]}/{info[1]}({info[2]})")
                    print("; ".join(listadisc))
        print("")
    def conflitoProfessores(self, disciplinas, docs=[]):
        print("\nCONFLITOS DE PROFESSORES:")
        prep_disc = self.prepareDocentes(disciplinas)
        for k, v in prep_disc.items():
            if (k != DOCENTE["?"] and docs == []) or k in list(DOCENTE[d] for d in docs):
                for hor in self.rows:
                    for dia in self.cols:
                        siglas = set(s[0] for s in v[hor, dia])
                        if len(siglas) > 1:
                            print(f"- {k} ==> {dia} ({hor[0]}~{hor[1]}) : ", end= "")
                            listadisc = list()
                            for info in v[hor, dia]:
                                per = disciplinas.curriculum[info[0]]["periodo"]
                                listadisc.append(f"{info[0]}/{info[1]}({info[2]}).{'OPT' if per == 99 else str(per)+'ºP'}")
                            print("; ".join(listadisc))
        print("")
    def somaHorariosDocente(self, disciplinas):
        prep_disc = self.prepareDocentes(disciplinas)
        docentes = dict(zip(DOCENTE.values(), [0]*len(DOCENTE)))
        for k, v in prep_disc.items():
            for hor in self.rows:
                for dia in self.cols:
                    docentes[k] += 1 if v[hor, dia] else 0
        return docentes        
    def print(self, disciplinas, perinteresse=None):
        NC = 20
        HLINE = (13+(NC+1)*6)
        prep_disc = self.prepare(disciplinas)
        for periodo, matriz in prep_disc.items():
            siglas = set()
            if perinteresse is None or periodo == perinteresse:
                print("")
                print("="*HLINE)
                print(f"{str(periodo):>4s}º período" if periodo != 99 else "   Optativas")
                print("="*HLINE)
                header = list()
                for s in self.cols:
                    x = NC//2 - (2 if NC%2 == 0 else 1)
                    m = " "*x + s + " "*x
                    while len(m) < NC:
                        m += " "
                    header.append(m)
                print(" "*12 + "|" + "|".join(header))
                print("—"*HLINE)
                for hor in self.rows:
                    linesincols = list()
                    for dia in self.cols:
                        linesincols.append(len(matriz[hor, dia]))
                    nlines = max(linesincols)
                    for l in range(nlines):
                        if l == 0:
                            print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        else:
                            print(" "*12 + "|", end="")
                        row = list()
                        for dia in self.cols:
                            if len(matriz[hor, dia]) > l:
                                info = matriz[hor, dia][l]
                                siglas.add(info[0])
                                aux = f"{info[0]}/{info[1]}({info[2]})"
                                eval(f"row.append(f'{aux:^{NC}s}')")
                            else:
                                row.append(" "*NC)
                        print("|".join(row))
                        if l == nlines - 1:
                            if hor[0] in ["11:30", "17:40", "21:40"]:
                                print("—"*HLINE)
                            else:
                                print("-"*HLINE)
                    if nlines == 0:
                        print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        print("|".join([" "*NC]*len(self.cols)))
                        if hor[0] in ["11:30", "17:40", "21:40"]:
                            print("—"*HLINE)
                            # print("—"*(HLINE//2)+("" if HLINE%2 == 0 else "-"))
                        else:
                            print("-"*HLINE)
            for s in sorted(siglas):
                print(f"> {s:>7s}:", disciplinas.curriculum[s]['codigo'], disciplinas.curriculum[s]['nome'])
        print("")
    def printDocentes(self, disciplinas, docinteresse=None):
        NC = 20
        HLINE = (13+(NC+1)*6)
        prep_disc = self.prepareDocentes(disciplinas)
        horas = self.somaHorariosDocente(disciplinas)
        print("")
        for docente, matriz in prep_disc.items():
            siglas = set()
            if docente != DOCENTE["?"] and docinteresse is None or docente == docinteresse:
                print("="*HLINE)
                print(f"    Docente: {docente} : {horas[docente]} HA por semana")
                print("="*HLINE)
                header = list()
                for s in self.cols:
                    x = NC//2 - (2 if NC%2 == 0 else 1)
                    m = " "*x + s + " "*x
                    while len(m) < NC:
                        m += " "
                    header.append(m)
                print(" "*12 + "|" + "|".join(header))
                print("—"*HLINE)
                for hor in self.rows:
                    linesincols = list()
                    for dia in self.cols:
                        linesincols.append(len(matriz[hor, dia]))
                    nlines = max(linesincols)
                    for l in range(nlines):
                        if l == 0:
                            print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        else:
                            print(" "*12 + "|", end="")
                        row = list()
                        for dia in self.cols:
                            if len(matriz[hor, dia]) > l:
                                info = matriz[hor, dia][l]
                                siglas.add(info[0])
                                per = disciplinas.curriculum[info[0]]["periodo"]
                                aux = f"{info[0]}/{info[1]}({info[2]}).{'OPT' if per == 99 else str(per)+'ºP'}"
                                eval(f"row.append(f'{aux:^{NC}s}')")
                            else:
                                row.append(" "*NC)
                        print("|".join(row))
                        if l == nlines - 1:
                            if hor[0] in ["11:30", "17:40", "21:40"]:
                                print("—"*HLINE)
                            else:
                                print("-"*HLINE)
                    if nlines == 0:
                        print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        print("|".join([" "*NC]*len(self.cols)))
                        if hor[0] in ["11:30", "17:40", "21:40"]:
                            print("—"*HLINE)
                            # print("—"*(HLINE//2)+("" if HLINE%2 == 0 else "-"))
                        else:
                            print("-"*HLINE)
            for s in sorted(siglas):
                print(f"{s:>7s}:", disciplinas.curriculum[s]['codigo'], disciplinas.curriculum[s]['nome'])
        print("")
    def printHoraAulaDocentes(self, disciplinas, docsinteresse=[]):
        horas = self.somaHorariosDocente(disciplinas)
        print("Horas-Aula por Docente")
        for doc in docsinteresse:
            docente = DOCENTE[doc]
            print(f"> Docente: {docente} : {horas[docente]} HA por semana")
        print("")
    def printDisciplina(self, disciplinas, discinteresse=None):
        NC = 20
        HLINE = (13+(NC+1)*6)
        prep_disc = self.prepareDisciplinas(disciplinas)
        print("")
        for sigladisc, matriz in prep_disc.items():
            if sigladisc != DOCENTE["?"] and discinteresse is None or sigladisc == discinteresse:
                print("="*HLINE)
                print(f"    Disciplina: ({sigladisc}) {disciplinas.curriculum[sigladisc]['codigo']} {disciplinas.curriculum[sigladisc]['nome']}")
                print("="*HLINE)
                header = list()
                for s in self.cols:
                    x = NC//2 - (2 if NC%2 == 0 else 1)
                    m = " "*x + s + " "*x
                    while len(m) < NC:
                        m += " "
                    header.append(m)
                print(" "*12 + "|" + "|".join(header))
                print("—"*HLINE)
                for hor in self.rows:
                    linesincols = list()
                    for dia in self.cols:
                        linesincols.append(len(matriz[hor, dia]))
                    nlines = max(linesincols)
                    for l in range(nlines):
                        if l == 0:
                            print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        else:
                            print(" "*12 + "|", end="")
                        row = list()
                        for dia in self.cols:
                            if len(matriz[hor, dia]) > l:
                                info = matriz[hor, dia][l]
                                per = disciplinas.curriculum[info[0]]["periodo"]
                                aux = f"{info[0]}/{info[1]}({info[2]}).{'OPT' if per == 99 else str(per)+'ºP'}"
                                eval(f"row.append(f'{aux:^{NC}s}')")
                            else:
                                row.append(" "*NC)
                        print("|".join(row))
                        if l == nlines - 1:
                            if hor[0] in ["11:30", "17:40", "21:40"]:
                                print("—"*HLINE)
                            else:
                                print("-"*HLINE)
                    if nlines == 0:
                        print(f"{hor[0]:>5s}~{hor[1]:>5s}", end=" |")
                        print("|".join([" "*NC]*len(self.cols)))
                        if hor[0] in ["11:30", "17:40", "21:40"]:
                            print("—"*HLINE)
                            # print("—"*(HLINE//2)+("" if HLINE%2 == 0 else "-"))
                        else:
                            print("-"*HLINE)
        print("")
                    




semanas = Semanas()
disciplinas = Disciplinas("disciplinas.txt")
planeja_mentos = Planejamento()


if __name__ == "__main__":
    print(semanas.slot("2M5"))
    print(semanas.slot("2M6"))
    print(semanas.slot("3T3"))
    print(semanas.slot("5N1"))
    disciplinas.setTurma("SDIST", "C")
    disciplinas.setTurma("SEMB1", "A1")
    disciplinas.setTurma("SEMB1", "A2")
    disciplinas.setTurma("SEMB1", "B1")
    disciplinas.setTurma("SEMB1", "B2")
    disciplinas.setTurma("CQU", "X3")
    disciplinas.setTurma("AWC", "R")
    disciplinas.curriculum["SDIST"]["turmas"]["C:T"].slots.append(semanas.slot("2M1"))
    disciplinas.curriculum["SDIST"]["turmas"]["C:T"].slots.append(semanas.slot("2M2"))
    disciplinas.curriculum["SDIST"]["turmas"]["C:P"].slots.append(semanas.slot("2M3"))
    disciplinas.curriculum["SDIST"]["turmas"]["C:T"].docentes.append(DOCENTE["Peretta"])
    disciplinas.curriculum["SDIST"]["turmas"]["C:P"].docentes.append(DOCENTE["Peretta"])
    disciplinas.curriculum["CQU"]["turmas"]["X3:T"].slots.append(semanas.slot("4T1"))
    disciplinas.curriculum["CQU"]["turmas"]["X3:T"].slots.append(semanas.slot("4T2"))
    disciplinas.curriculum["CQU"]["turmas"]["X3:P"].slots.append(semanas.slot("4T3"))
    disciplinas.curriculum["CQU"]["turmas"]["X3:T"].docentes.append(DOCENTE["Peretta"])
    disciplinas.curriculum["CQU"]["turmas"]["X3:P"].docentes.append(DOCENTE["Peretta"])
    disciplinas.curriculum["AWC"]["turmas"]["R:T"].slots.append(semanas.slot("4T3"))
    disciplinas.curriculum["AWC"]["turmas"]["R:T"].slots.append(semanas.slot("4T4"))
    disciplinas.curriculum["AWC"]["turmas"]["R:P"].slots.append(semanas.slot("4T5"))
    disciplinas.curriculum["AWC"]["turmas"]["R:T"].docentes.append(DOCENTE["Cunha"])
    disciplinas.curriculum["AWC"]["turmas"]["R:P"].docentes.append(DOCENTE["Cunha"])
    # for m in disciplinas.missing():
    #     print(m)
    print(disciplinas.curriculum["SDIST"]["turmas"]["C:T"].slots)
    planeja = Planejamento()
    print(planeja.prepare(disciplinas))
    planeja.print(disciplinas)
    planeja.conflitoHorarios(disciplinas)
    # m = Matrix(rheader=semanas.horarios, cheader=semanas.dias)
    # print(m[('7:10', '8:00'), 'SEG'])
    # m[('7:10', '8:00'), 'SEG'] = 99
    # print(m[('7:10', '8:00'), 'SEG'])
    # print(m.content)
    # m = np.zeros(shape=(16, 7))
    # print(m[0, 1])
    # m[0, 1] = 99
    # print(m[0, 1])
    # # print(m.content)
    # print(m)
    print(planeja.prepareDocentes(disciplinas))
    planeja.printDocentes(disciplinas)