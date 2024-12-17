# Configurando seu Ambiente

## Objetivos

- Configurar um ambiente de desenvolvimento para CD4ML, incluindo:
  - Fazer o fork do repositório Git no GitHub.
  - Configurar um runtime de containers.
  - Configurar um ambiente de desenvolvimento em Python.
  - Instalar Docker Desktop ou [uma alternativa](https://www.rockyourcode.com/docker-desktop-alternatives-for-macos/).

---

## Configuração do GitHub

1. Acesse a página de [Tokens de Acesso Pessoal do GitHub](https://github.com/settings/tokens).
2. Clique em **"Generate new token"** no canto superior direito. Talvez seja necessário inserir sua senha novamente.
3. Dê um nome ao token e selecione as permissões **"repo"** e **"user:email"**. Clique em **"Generate Token"**.

> ⚠️ **Importante:** Salve este token com segurança, pois ele não será exibido novamente.

4. Faça o fork do repositório [CD4ML-Scenarios](https://github.com/ThoughtWorksInc/CD4ML-Scenarios) para sua conta no GitHub.
5. Clone o repositório para sua máquina local:
   ```bash
   git clone https://github.com/<SeuUsuario>/CD4ML-Scenarios