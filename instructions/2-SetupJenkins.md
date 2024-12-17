# Configurando o Jenkins

## Objetivos

- Aprender sobre [Jenkins](https://jenkins.io/).
- Configurar uma [Pipeline de Implantação](https://martinfowler.com/bliki/DeploymentPipeline.html) para construir e implantar sua aplicação em produção.
- Implantar o modelo no servidor de produção.

---

## Passo a Passo

### 1. Acessar o Jenkins
- Abra o Jenkins em: [http://localhost:10000/blue](http://localhost:10000/blue) (verifique a porta no seu ambiente).
- Após o login, você será apresentado à interface Blue Ocean do Jenkins.

---

### 2. Criar uma Pipeline
1. Clique em **"Create a Pipeline"**.
2. Escolha **"GitHub"** como a origem do código.
3. Insira o **GitHub Personal Access Token**:
   - Este token é criado na sua conta do GitHub e permite que o Jenkins acesse seus repositórios.
4. Selecione seu repositório do GitHub (ex.: `cd4ml-scenarios`) e clique em **"Create Pipeline"**.

---

### 3. Pipeline no Jenkins
- A pipeline realizará as seguintes etapas:
  1. **Indexar branches:** Identifica os branches disponíveis no repositório.
  2. **Checkout do código:** Faz o download do código do repositório.
  3. **Executar a pipeline:** Cada etapa será executada automaticamente.

> Observação: Algumas etapas podem demorar (como indexação de branches e checkout). Se necessário, você pode acionar a execução manualmente.

---

### 4. Verificar a Pipeline
- Após a execução, uma pipeline "verde" indica que todas as etapas foram bem-sucedidas.
- Em caso de falhas, revise os logs e ajuste conforme necessário.

---

### 5. Verificar o Modelo em Produção
- Após a pipeline ser concluída, o modelo estará disponível no servidor em: [http://localhost:11000](http://localhost:11000).
- **Testar o modelo:**
  1. Clique em **"Use latest valid model"** no cenário de Previsão de Preço de Casas.
  2. Insira os dados de entrada (veja exemplo abaixo).
  3. Clique em **"Submit"** para obter a previsão.

---

### 6. Executar um Novo Cenário
- Volte para o Jenkins.
- Acesse a aba **Branches** e clique no botão "play" ao lado do branch `master`.
- Na janela exibida, selecione o problema/cenário desejado.
- Clique em **"Run"** para iniciar a execução.

---

## Próximos Passos
- Explore o [Zillow rendimento Scenario](./rendimento/3-MachineLearning.md) para previsões de preços de casas (recomendado).
- Alternativamente, inicie o [Shopping Scenario](./insumo/3-MachineLearning.md).

---

## Imagens de Referência
- Tela inicial do **Blue Ocean** do Jenkins.
- Pipeline com status "verde" indicando sucesso.
- Página de boas-vindas do modelo em produção.
- Exemplo de previsão de preço de casas.

> Certifique-se de comparar sua configuração com as imagens do tutorial para garantir que está no caminho certo.