
📘 README — Ambiente Mainframe TK4- (MVS 3.8j) no macOS

Este projeto instala e executa um mainframe IBM MVS 3.8j (TK4-) totalmente funcional no macOS (Intel ou ARM), utilizando:
	•	Hercules 4.x
	•	TK4- completo
	•	TSO
	•	ISPF-like (CBT)
	•	JES2
	•	VTAM (terminais 3270)

Ideal para treinamento, estudos de COBOL/JCL, prática de TSO, JES2, datasets, REXX, CLIST e ambiente mainframe real.

⸻

🧩 1. Pré-requisitos

Instale no macOS:

brew install hercules x3270

E tenha o Docker Desktop instalado (usado apenas para extrair o TK4- completo).

⸻

🔽 2. Instalação Automática

Toda a instalação é feita por um único script:

./setup_mainframe_tk4.sh

Esse script:
	•	Libera a porta 3270
	•	Baixa TK4-Hercules
	•	Extrai o TK4 completo
	•	Cria ~/tk4-mainframe
	•	Gera o script start_mvs.sh
	•	Prepara tudo para o primeiro boot

⸻

🖥️ 3. Iniciar o Mainframe

cd ~/tk4-mainframe
./start_mvs.sh

Quando aparecer:

herc =====>

Faça o boot:

ipl 148

Isso carrega:
	•	MVS nucleus
	•	JES2
	•	VTAM
	•	Terminais 3270
	•	Dispositivos I/O

⸻

🖥️ 4. Conectar no terminal TN3270

Abra um novo terminal:

Modo texto:

c3270 127.0.0.1:3270

Modo interface gráfica:

x3270 127.0.0.1:3270

Pressione ENTER para aparecer a tela TSO.

Login:

USERID: HERC01
PASSWORD: CUL8TR


⸻

🗂️ 5. Estrutura da pasta ~/tk4-mainframe

tk4-mainframe/
├── conf/          → arquivos de configuração
├── dasd/          → discos (datasets)
├── jcl/           → jobs de exemplo
├── scripts/       → utilitários extras
├── prt/           → saída de JES2
├── rdr/           → entrada de jobs
├── tapes/         → fitas magnéticas
├── hercules       → binário incluso
└── start_mvs.sh   → script de boot


⸻

💼 6. Comandos úteis no Hercules

Iniciar boot:

ipl 148

Finalizar Hercules:

quit


⸻

🧑‍💻 7. Comandos úteis no TSO

Listar datasets:

LISTCAT

Editar membro:

EDIT 'HERC01.CNTL(JOB1)'

Enviar JCL:

SUBMIT 'HERC01.CNTL(JOB1)'

Status dos jobs:

STATUS

Sair:

LOGOFF


⸻

📄 8. Rodar JCL de exemplo

SUBMIT 'SYS1.JCLLIB(LIST001)'


⸻

🚑 9. Solução de problemas

❗ Terminal desconecta imediatamente

A porta 3270 está em uso (normalmente pelo Docker Desktop).

Verifique:

lsof -i :3270

Se aparecer algo como:

com.docker   PID

Mate:

kill -9 PID

Reinicie o Hercules e execute novamente ipl 148.

⸻

❗ Tela 3270 preta

Pressione ENTER.

⸻

❗ VTAM não sobe

Execute novamente:

ipl 148

Espere as linhas:

IST093I T3278xxxx ACTIVE


⸻

🏆 10. Credenciais padrões

Serviço	User	Senha
TSO	HERC01	CUL8TR
Operador	(sem login)	—


⸻

🎯 11. Objetivo

Este ambiente permite:
	•	Estudo de COBOL, JCL, REXX, CLIST
	•	Entendimento de JES2, VTAM, TSO
	•	Simulação real de workflows de mainframe
	•	Ambiente educativo completo

⸻

🧡 12. Suporte

Para instalar:
	•	ISPF moderno
	•	Pacotes CBT adicionais
	•	Usuários customizados
	•	IPL automático
	•	Scripts de automação
	•	Integração com VS Code (COBOL, JCL etc.)

Basta pedir.

⸻

✔️ Resumo final

./setup_mainframe_tk4.sh
cd ~/tk4-mainframe
./start_mvs.sh
ipl 148
c3270 127.0.0.1:3270

🎉 Parabéns! Você agora tem um mainframe completo no seu macOS.