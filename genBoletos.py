from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
import sqlite3, sys, datetime, os

def getForn():
        """Função responsável por retornar lista de Fornecedores """
        cursor = conn.cursor()
        action = ("""SELECT nome_forn FROM fornecedores
                    ORDER BY nome_forn;""")
        cursor.execute(action)
        rows = cursor.fetchall()
        forn = [row[0] for row in rows]
        return forn

tfont = ('Tahoma',15)
dfont = ('Tahoma',12)
bolfont = ('Tahoma',11)


#Conectando ao DB
try:
    conn = sqlite3.connect('boletos.db')
except:
    sys.exit()

class aplicativo(Tk):
        
    def __init__(self):
        Tk.__init__(self)
        global container

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.frames['principal'] = principal(parent=container)
        self.frames['principal'].grid(row=0, column=0, sticky="nsew")
        self.frames['fornecedores'] = fornecedores(parent=container)
        self.frames['fornecedores'].grid(row=0, column=0, sticky="nsew")
        self.frames['boletos'] = boletos(parent=container)
        self.frames['boletos'].grid(row=0, column=0, sticky="nsew")

        self.show_frame('principal')

    def show_frame(self, page_name):
        """ Chama o frame """
        frame = self.frames[page_name]
        frame.tkraise()

#JANELA PRINCIPAL
class principal(Frame):
    """Janela Principal do Gerenciador """
    
    def __init__(self, parent):
        Frame.__init__(self,parent)
        #Título
        self.lbNome = Label(self, text='Gerenciador de Boletos')
        self.lbNome.place(x=370, y=20)
        self.lbNome.config(font=('Tahoma',20))

        #Data de Hoje
        self.Hoje = datetime.date.today()
        self.Hoje = self.Hoje.strftime("%d/%m/%Y")
        self.lbHoje = Label(self, text=self.Hoje)
        self.lbHoje.place(x=830, y=20)
        self.lbHoje.config(font=('Tahoma',18))

        #Inserir Boleto
        self.lbInBoleto = Label(self,text='Inserir Boleto:')
        self.lbInBoleto.place(x=100, y=110)
        self.lbInBoleto.config(font=tfont)

        self.lbInData = Label(self,text='Data:')
        self.lbInData.place(x=100, y=150)
        self.lbInData.config(font=dfont)

        self.tData = StringVar()
        self.tData.set('dd-mm-aaaa')
        self.tInBoleto = Entry(self,textvariable=self.tData,width=11)
        self.tInBoleto.place(x=100, y=170)
        self.tInBoleto.config(font=dfont)

        self.lbInValor = Label(self,text='Valor:')
        self.lbInValor.place(x=230, y=150)
        self.lbInValor.config(font=dfont)

        self.tValor = StringVar()
        self.tValor.set('xxxx,xx')
        self.tValor = Entry(self,textvariable=self.tValor,width=8)
        self.tValor.place(x=230, y=170)
        self.tValor.config(font=dfont)

        self.lbForn = Label(self,text='Fornecedor:')
        self.lbForn.place(x=340, y=150)
        self.lbForn.config(font=dfont)

        self.listaForn = getForn()
        self.ltForn= Combobox(self,values= self.listaForn)
        self.ltForn.place(x=340, y=170)

        self.btnBoleto = Button(self,text='Adicionar Boleto',command= self.addBole)
        self.btnBoleto.place(x=555, y=161)

        #Texto Último Boleto
        self.lbUltBoleto = Label(self,text='')
        self.lbUltBoleto.place(x=100, y=215)

        #Janela Lateral Direita
        self.btnBole = Button(self,text='Boletos', command = self.callBoletos)
        self.btnBole.place(x=800,y=130)
        self.btnBole.config(font=tfont)

        self.btnForn = Button(self,text='Fornecedores', command = self.callForn)
        self.btnForn.place(x=800,y=200)
        self.btnForn.config(font=tfont)

        #Próximos boletos
        self.lbNext = Label(self,text='Lista dos Próximos Boletos')
        self.lbNext.place(x=330, y=300)
        self.lbNext.config(font=('Tahoma',20))

        #Número de boletos
        actionCount = """SELECT COUNT(*) FROM boletos
                        WHERE st_bole = 0;"""
        cursor2 = conn.cursor()
        cursor2.execute(actionCount)
        qtdBole = cursor2.fetchall()[0][0]
        if qtdBole >= 7:
                qtdBole = 7

        actionBole = ("""SELECT va_bole, dt_bole, nome_forn, id_bole FROM boletos
                        INNER JOIN  fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE st_bole = 0
                        ORDER BY dt_bole, va_bole DESC
                        LIMIT ?;""")
        cursor2.execute(actionBole,(qtdBole,))
        self.lastBole = cursor2.fetchall()
        self.bolePagos = [IntVar() for x in range(qtdBole)]
        for i in range(len(self.lastBole)):
                tmpTxt = "Valor: R$ " + str(self.lastBole[i][0]) + ' - Fornecedor: ' + self.lastBole[i][2] + " - Vencimento: " + self.lastBole[i][1][-2:] + '-' + self.lastBole[i][1][-5:-3] + '-' + self.lastBole[i][1][:4]
                self.cBtn = Checkbutton(self,text=tmpTxt, variable = self.bolePagos[i], font= bolfont)
                self.cBtn.place(x=50,y=360 + i*40)

        #Pagar Boletos Listados
        self.btnPagBole = Button(self,text='Pagamento de Boletos',font=tfont,command= self.pagBole)
        self.btnPagBole.place(x=730,y=490)

        #Boletos da Semana
        self.lbSemana1= Label(self, text='Valor total dos boletos devidos\nnesta semana',font=tfont)
        self.lbSemana1.place(x=680,y=580)

        self.bValue = StringVar()
        self.bValue.set(f'R$ {self.bolSemana():.2f}')
        self.lbSemana2 = Label(self, textvariable= self.bValue, font= tfont)
        self.lbSemana2.place(x=780,y=660)
        
    def addBole(self):
        """Função de adição de um boleto na tela principal """
        cursor = conn.cursor()
        data = self.tData.get()
        try:
                datetime.datetime.strptime(data,"%d-%m-%Y")
        except:
                self.lbUltBoleto.config(text='Boleto Não Adicionado\nData inválida')
                return None
        
        data2 = data[-4:] + '-' + data[3:5] + '-' + data[0:2]
        valor = self.tValor.get().replace(',','.')
        valor = float(valor)
        forn = self.ltForn.get()
        act1 = ("""SELECT id_forn FROM fornecedores
                        WHERE nome_forn = ? """)
        cursor.execute(act1,(forn,))
        idForn = cursor.fetchall()[0][0]
        act2 = ("""INSERT INTO boletos(va_bole, st_bole, id_forn, dt_bole)
                VALUES (?,?,?,?);""")
        try:
                cursor.execute(act2,(valor,0,idForn,data2))
                conn.commit()
                cursor.close()
                tempTxt = 'Último Boleto Criado:'+'\n'+forn+'\nValor: R$'+str(valor)+'\nVencimento: '+ data
                self.lbUltBoleto.config(text=tempTxt)
                self.tData.set("")
        
        except:
                cursor.close()
                self.lbUltBoleto.config(text='Boleto Não Adicionado')
                return None
            
    def pagBole(self):
        """ Função de Pagar Boletos no menu principal """
        cursor3 = conn.cursor()
        tmpId_bole = [(self.lastBole[i][3],) for i in range(len(self.bolePagos)) if self.bolePagos[i].get() == 1]
        actionId = """UPDATE boletos
                        SET st_bole = 1
                        WHERE id_bole = (?);"""
        
        status = messagebox.askokcancel("Pagamento Boletos","Estes boletos foram pagos?")
        if status == True:
            cursor3.executemany(actionId,tmpId_bole)
            conn.commit()
            global app
            #Refresh da página
            app.frames['principal'].destroy()
            app.frames['principal'] = principal(container)
            app.frames['principal'].grid(row=0, column=0, sticky="nsew")
            app.show_frame('principal')
            
        else:
            return None

    def callForn(self):
        """ Inicializa Frame de Fornecedores """
        global app
        app.frames['principal'].destroy()
        app.frames['fornecedores'] = fornecedores(container)
        app.frames['fornecedores'].grid(row=0, column=0, sticky="nsew")
        app.show_frame('fornecedores')
        return None

    def callBoletos(self):
        """ Inicializa Frame de Boletos """
        global app
        app.frames['principal'].destroy()
        app.frames['boletos'] = boletos(container)
        app.frames['boletos'].grid(row=0, column=0, sticky="nsew")
        app.show_frame('boletos')
        return None

    def bolSemana(self):
        """ Somatório dos Boletos da Semana atual """
        #Limite das datas dos boletos em Python
        hojeDt = datetime.date.today()
        diasAteSab = (hojeDt.weekday()+2) % 7
        ultSab = hojeDt - datetime.timedelta(diasAteSab)
        ultSabStr = ultSab.strftime("%Y-%m-%d")
        prxSex = hojeDt + datetime.timedelta(6 - diasAteSab)
        prxSexStr = prxSex.strftime("%Y-%m-%d")

        #Select Datas SQL
        cursor4 = conn.cursor()
        actionTmp = """SELECT ROUND(SUM(va_bole),2) FROM boletos
                        WHERE (st_bole = 0) AND (dt_bole BETWEEN (?) AND (?))"""
        cursor4.execute(actionTmp,[ultSabStr, prxSexStr])
        sumBoletos = cursor4.fetchall()
        cursor4.close()

        if sumBoletos[0][0] == None:
                return 0
        return sumBoletos[0][0]


#JANELA DOS FORNECEDORES
class fornecedores(Frame):
    """Janela Informações dos fornecedores"""

    def __init__(self, parent):
        Frame.__init__(self,parent)
        #Título
        self.lbNome = Label(self, text='Fornecedores')
        self.lbNome.place(x=410, y=20)
        self.lbNome.config(font=('Tahoma',20))

        #Retorno à tela principal
        self.btnPrinc = Button(self, text='Página Inicial', command = self.callPrinc)
        self.btnPrinc.place(x=815, y=70)
        self.btnPrinc.config(font=('Tahoma',16))

        #Data de Hoje
        self.Hoje = datetime.date.today()
        self.Hoje = self.Hoje.strftime("%d/%m/%Y")
        self.lbHoje = Label(self, text=self.Hoje)
        self.lbHoje.place(x=830, y=20)
        self.lbHoje.config(font=('Tahoma',18))

        #Inserir Fornecedor
        self.lbInForn = Label(self,text='Novo Fornecedor:')
        self.lbInForn.place(x=800, y=190)
        self.lbInForn.config(font=tfont)
        
        self.tNewForn = Entry(self,width=24)
        self.tNewForn.place(x=800, y=235)
        self.tNewForn.config(font=dfont)

        self.btnNewForn = Button(self,text='Adicionar', command = self.newForn)
        self.btnNewForn.place(x=845, y=270)

        self.newFornStr = StringVar()
        self.lbNewForn = Label(self, textvariable = self.newFornStr)
        self.lbNewForn.place(x=830, y=315)


        #Informações dos Fornecedores
        self.lbForn = Label(self,text='Fornecedor:')
        self.lbForn.place(x=60, y=120)
        self.lbForn.config(font=tfont)

        self.listaForn = getForn()
        self.ltForn= Combobox(self,values= self.listaForn)
        self.ltForn.place(x=60, y=150)

        self.btnFornInf = Button(self, text='Informações', command= self.infoForn)
        self.btnFornInf.place(x= 250, y= 143)

        self.lbStrFornNome = StringVar()
        self.lbFornNome = Label(self, textvariable = self.lbStrFornNome, font=tfont)
        self.lbFornNome.place(x=60, y=230)
        
        self.strQtdBol = StringVar()
        self.lbQtdBol = Label(self, textvariable = self.strQtdBol, font=dfont)
        self.lbQtdBol.place(x=60, y=280)

        self.strSumBol = StringVar()
        self.lbSumBol = Label(self, textvariable = self.strSumBol, font=dfont)
        self.lbSumBol.place(x=60, y=320)

        self.strUltBol = StringVar()
        self.lbUltBol = Label(self, textvariable = self.strUltBol, font=dfont)
        self.lbUltBol.place(x=60, y=360)

        self.strMaxBol = StringVar()
        self.lbMaxBol = Label(self, textvariable = self.strMaxBol, font=dfont)
        self.lbMaxBol.place(x=60, y=400)

    def callPrinc(self):
        """ Inicializa Frame Inicial """
        global app
        app.frames['fornecedores'].destroy()
        app.frames['principal'] = principal(container)
        app.frames['principal'].grid(row=0, column=0, sticky="nsew")
        app.show_frame('principal')
        return None

    def newForn(self):
        """ Registra um novo fornecedor no DB"""
        tmpTxt = (self.tNewForn.get())
        cursor4 = conn.cursor()
        tmpAction = """INSERT INTO fornecedores(nome_forn)
                        VALUES((?));"""
        status = messagebox.askokcancel("Novo Fornecedor","Deseja adicionar " + tmpTxt + " a lista de Fornecedores?")        

        if status == True:
            try:
                cursor4.execute(tmpAction,[tmpTxt])
                conn.commit()
            except:
                return None
        else:
            return None

        self.newFornStr.set(tmpTxt + " cadastrado\ncom sucesso.")
        return None

    def infoForn(self):
        ''' Retorna Informações referentes ao Fornecedor Selecionado '''
        #Fornecedor
        self.lbStrFornNome.set(self.ltForn.get())

        #Quantidade de Boletos
        actQtdBol = """SELECT COUNT() FROM boletos
                        INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE (nome_forn = (?)) AND (st_bole = 0); """
        cursor4 = conn.cursor()
        cursor4.execute(actQtdBol, [self.ltForn.get()])
        tmpQtdBol = cursor4.fetchall()[0][0]
        self.strQtdBol.set('Número de boletos pendentes: ' + str(tmpQtdBol))

        #Somatório dos Boletos Devidos
        actSumBol = """SELECT SUM(va_bole) FROM boletos
                        INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE (nome_forn = (?)) AND (st_bole = 0); """
        cursor4.execute(actSumBol, [self.ltForn.get()])
        tmpSumBol = cursor4.fetchall()[0][0]
        if tmpSumBol == None:
            tmpSumBol = 0.00
        self.strSumBol.set(f'Somatório dos boletos devidos: R$ {tmpSumBol:.2f}')

        #Data do Último Boleto Devido e Data e Valor do boleto de maior valor
        if tmpQtdBol != 0:
            actUltBol = """SELECT dt_bole FROM boletos
                        INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE (nome_forn = (?)) AND (st_bole = 0)
                        ORDER BY dt_bole DESC LIMIT 1;"""
            cursor4.execute(actUltBol, [self.ltForn.get()])
            tmpDtBol = cursor4.fetchall()[0][0]
            tmpDtBol = tmpDtBol[-2:] + '-' + tmpDtBol[5:7] + '-' + tmpDtBol[0:4]
            self.strUltBol.set('Data do último boleto: ' + tmpDtBol)
            
            actMaxBol = """SELECT va_bole, dt_bole FROM boletos
                        INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE (nome_forn = (?)) AND (st_bole = 0)
                        ORDER BY va_bole DESC LIMIT 1;"""
            cursor4.execute(actMaxBol, [self.ltForn.get()])
            resultados = cursor4.fetchall()[0]
            maxBol = resultados[0]
            maxDtBol = resultados[1]
            maxDtBol = maxDtBol[-2:] + '-' + maxDtBol[5:7] + '-' + maxDtBol[0:4]
            self.strMaxBol.set(f'Há um boleto de R$ {maxBol:.2f} com vencimento em {maxDtBol}.')
            
        else:
            self.strUltBol.set(' ')
            self.strMaxBol.set(' ')


#JANELA DOS BOLETOS
class boletos(Frame):
    """Janela Informações dos Boletos"""

    def __init__(self, parent):
        Frame.__init__(self,parent)
        #Título
        self.lbNome = Label(self, text='Boletos')
        self.lbNome.place(x=450, y=20)
        self.lbNome.config(font=('Tahoma',20))

        #Retorno à tela principal
        self.btnPrinc = Button(self, text='Página Inicial', command = self.callPrinc)
        self.btnPrinc.place(x=815, y=70)
        self.btnPrinc.config(font=('Tahoma',16))

        #Data de Hoje
        self.Hoje = datetime.date.today()
        self.Hoje = self.Hoje.strftime("%d/%m/%Y")
        self.lbHoje = Label(self, text=self.Hoje)
        self.lbHoje.place(x=830, y=20)
        self.lbHoje.config(font=('Tahoma',18))

        #Datas dos Boletos
        self.lbDataIni = Label(self,text='Data Inicial')
        self.lbDataIni.place(x=830, y=200)
        self.lbDataIni.config(font=('Tahoma',18))

        self.strDataIni = StringVar()
        self.strDataIni.set('dd-mm-aaaa')
        self.tDataIni = Entry(self,textvariable=self.strDataIni,width=11)
        self.tDataIni.place(x=850, y=250)
        self.tDataIni.config(font=dfont)

        self.lbDataFin = Label(self,text='Data Final')
        self.lbDataFin.place(x=830, y=300)
        self.lbDataFin.config(font=('Tahoma',18))

        self.strDataFin = StringVar()
        self.strDataFin.set('01-01-2025')
        self.tDataFin = Entry(self,textvariable=self.strDataFin,width=11)
        self.tDataFin.place(x=850, y=350)
        self.tDataFin.config(font=dfont)

        #Status (Pago ou Não Pago)
        self.lbDataStat = Label(self,text='Status')
        self.lbDataStat.place(x=855, y=400)
        self.lbDataStat.config(font=('Tahoma',18))

        self.ltStat = Combobox(self,values= ['Pago', 'Não Pago'], width=11)
        self.ltStat.place(x=844, y=460)

        #Filtrar
        self.btnFiltro = Button(self, text='Filtrar', command = self.filtrar)
        self.btnFiltro.place(x=850, y=510)
        self.btnFiltro.config(font=('Tahoma',16))

        #Pagar
        self.btnPag = Button(self, text='Pagar', command= self.pagBoleto)
        self.btnPag.place(x=100, y=510)
        self.btnPag.config(font=('Tahoma',16))

        #Deletar
        self.btnDel = Button(self, text='Deletar', command= self.delBoleto)
        self.btnDel.place(x=300, y=510)
        self.btnDel.config(font=('Tahoma',16))

        #Somatório
        self.strResult = StringVar()
        self.strResult.set('Somatório: ')
        self.lbSemana2 = Label(self, textvariable= self.strResult, font= tfont)
        self.lbSemana2.place(x=100,y=580)

        #Lista de Boletos
        self.listBoletos = []
        self.ltForn= Combobox(self,values= self.listBoletos, width=30, font=bolfont)
        self.ltForn.place(x=100, y=210)


    def callPrinc(self):
        """ Inicializa Frame Inicial """
        global app
        app.frames['boletos'].destroy()
        app.frames['principal'] = principal(container)
        app.frames['principal'].grid(row=0, column=0, sticky="nsew")
        app.show_frame('principal')
        return None

    def filtrar(self):
        """ Filtra boletos com parâmetros fornecidos """
        #Somatório dos boletos filtrados
        dataIni = self.tDataIni.get()
        dataFin = self.tDataFin.get()
        try:
            datetime.datetime.strptime(dataIni,"%d-%m-%Y")
            datetime.datetime.strptime(dataFin,"%d-%m-%Y")
        except:
            self.strResult.set('Somatório:')
            return None
        
        if self.ltStat.get() == 'Pago':
            tmpStatus = 1
        else:
            tmpStatus = 0

        dataIni = dataIni[-4:] + '-' + dataIni[3:5] + '-' + dataIni[0:2]
        dataFin = dataFin[-4:] + '-' + dataFin[3:5] + '-' + dataFin[0:2]

        actSum = """SELECT sum(va_bole) FROM boletos
                        INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                        WHERE (st_bole = (?)) AND (dt_bole BETWEEN (?) AND (?));"""
        cursor4 = conn.cursor()
        cursor4.execute(actSum,[tmpStatus, dataIni, dataFin])
        somatorio = cursor4.fetchall()[0][0]
        if somatorio == None:
            self.strResult.set('Somatório: R$')
            self.ltForn['values'] = []
            self.ltForn.set('')
            return None
        
        self.strResult.set(f'Somatório: R$ {somatorio:.2f}')

        #Lista de boletos
        self.listBoletos.clear()
        actBol = """SELECT dt_bole, va_bole, nome_forn, id_bole FROM boletos
                INNER JOIN fornecedores ON boletos.id_forn = fornecedores.id_forn
                WHERE (st_bole = (?)) AND (dt_bole BETWEEN (?) AND (?))
                ORDER BY dt_bole, va_bole DESC;"""
        cursor4.execute(actBol,[tmpStatus, dataIni, dataFin])
        resultados = cursor4.fetchall()
        vencRes = [f'R${x[1]:.2f} | {x[2]} | {x[0][-2:]}-{x[0][5:7]} | ID:{x[3]}' for x in resultados]
        self.updtBolsLst(vencRes)

    def updtBolsLst(self, vencRes):
        """ Atualiza lista de boletos da página de Boletos """
        self.ltForn['values'] = vencRes

    def pagBoleto(self):
        """ Pagamento de 1 boleto da tela de Boletos """
        tmpTxt= self.ltForn.get()
        try:
            id_bole = tmpTxt.split(':')
            id_bole = int(id_bole[1])
        except:
            return None
        actPag = """UPDATE boletos
                 SET st_bole = 1
                 WHERE id_bole = (?) """
        
        status = messagebox.askokcancel('Pagamento de Boleto',tmpTxt + ' foi pago?')
        cursor4 = conn.cursor()

        if status == True:
            try:
                cursor4.execute(actPag, [id_bole])
                conn.commit()
            except:
                return None
        else:
            return None
        self.callBoletos()
        

    def delBoleto(self):
        """ Deletando um boleto da base de Dados """
        tmpTxt= self.ltForn.get()
        try:
            id_bole = tmpTxt.split(':')
            id_bole = int(id_bole[1])
        except:
            return None
        
        actDel = """DELETE FROM boletos
                 WHERE id_bole = (?) """
        status = messagebox.askokcancel('Deletar Boleto ',tmpTxt + ' da base de dados?')
        cursor4 = conn.cursor()

        if status == True:
            try:
                cursor4.execute(actDel, [id_bole])
                conn.commit()
            except:
                return None
        else:
            return None
        self.callBoletos()

    def callBoletos(self):
        """ Reinicia Frame de Boletos """
        global app
        app.frames['boletos'].destroy()
        app.frames['boletos'] = boletos(container)
        app.frames['boletos'].grid(row=0, column=0, sticky="nsew")
        app.show_frame('boletos')
        return None
        
        
# INICIALIZAÇÃO DO PROGRAMA            
if __name__ == "__main__":
    app = aplicativo()
    app.geometry("1024x768")
    app.title('Gerenciador de Boletos')
    app.mainloop()
