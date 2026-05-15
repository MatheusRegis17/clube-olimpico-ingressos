# Clube Olímpico Ingressos

## Como trocar as imagens manualmente

A pasta `assets` agora controla as imagens do sistema.

### Arquivos:
- `assets/logo_clube.png` = logo do clube
- `assets/logo_arraia.png` = logo da festa junina
- `assets/mapa_mesas_base.png` = imagem base do mapa da quadra
- `assets/mesa_coords.json` = posições das mesas em cima do mapa

## Como trocar no futuro

### 1) Logo do clube
Substitua o arquivo `assets/logo_clube.png` pelo novo arquivo, mantendo o mesmo nome.

### 2) Logo da festa junina
Substitua o arquivo `assets/logo_arraia.png` pelo novo arquivo, mantendo o mesmo nome.

### 3) Imagem do mapa da quadra
Substitua o arquivo `assets/mapa_mesas_base.png` pela nova imagem, mantendo o mesmo nome.

### 4) Ajustar posição das mesas
Abra o arquivo `assets/mesa_coords.json` no bloco de notas.
Cada linha tem este formato:

```json
{ "mesa": 1, "x": 388, "y": 146 }
```

- `mesa` = número da mesa
- `x` = posição horizontal
- `y` = posição vertical

Se trocar a imagem do mapa, talvez seja preciso ajustar os valores `x` e `y`.

## Login direto
Se já existir um último acesso salvo, a tela inicial abre direto com o campo de senha.
Use o botão **Trocar usuário** se quiser entrar com outro cadastro.

## Streamlit
Main file path: `app.py`


## Redesign da entrada
- tela de login refeita
- logo central maior
- visual mais limpo
- entrada direta com senha do último usuário


## Ajuste adicional da entrada
- card mais centralizado
- elementos internos centralizados
- logo maior
- visual mais estilizado


## Estilo Facebook na entrada
- card branco central
- botão azul
- visual inspirado em login limpo do Facebook


## Login estilo Facebook limpo
- fundo claro
- duas colunas
- card branco
- botão azul
- logo em formato escudo


## Design livre
- nova tela de login com layout profissional
- painel informativo à esquerda
- card de acesso à direita
- identidade mais limpa e equilibrada


## Dark Premium
- fundo escuro premium
- card de login em vidro escuro
- visual sem fundo branco


## Atualização solicitada

- Tela inicial agora sempre exige seleção de usuário.
- Se o usuário já tiver senha, aparece campo de senha e botão Entrar.
- Se o usuário ainda não tiver senha, ele precisa cadastrar senha para entrar.
- Removida a opção de entrar sem senha.
- Mapa das mesas trocado para `assets/mapa_mesas_base.png`.


## Fundo e mapa atualizados
- fundo principal com arte de festa junina
- mapa base trocado pela nova planta da quadra
- 100 mesas distribuídas automaticamente no mapa
- renderização das mesas com caixas numeradas mais legíveis
- preview do mapa em assets/preview_mapa_100_mesas.png


## Painel Master

Entrando com o usuário `Adm`, aparece o menu `Painel Master`.

Funções:
- alterar fundo do sistema
- alterar logo do clube
- alterar logo do Arraiá
- alterar imagem do mapa
- ajustar posição das mesas
- alterar opacidade, desfoque e posição do fundo
- recriar o layout padrão de 100 mesas

Observação: alterações feitas pelo Painel Master ficam salvas nos arquivos do app enquanto o ambiente Streamlit estiver ativo. Para persistência 100% profissional, o próximo passo é migrar esses arquivos/configurações para Google Drive/Sheets.


## Ajuste solicitado
- a prévia do Painel Master agora mostra a coordenada/identificação de cada mesa em cima da mesa numerada
- adicionado ajuste visual do tamanho da marcação das mesas no mapa


## Correção final aplicada

Principais correções:
- o mapa agora usa a planta limpa enviada pelo usuário
- as 100 mesas são desenhadas dinamicamente em cima da quadra
- a página Mesas não mostra mais etiquetas verdes desalinhadas
- o Painel Master mostra etiquetas verdes apenas no modo de edição
- o fundo de Festa Junina foi mantido em `assets/background_festa_junina.png`
- usuário `Adm` já vem com senha padrão `Cata1010#` para evitar travamento após redeploy
- não existe entrada sem identificação

Para testar senha:
- Usuário: Adm
- Senha: Cata1010#



## Atualização: Zoom no mapa

- A página `Mesas` agora tem controle de `Zoom do mapa (%)`.
- O `Painel Master > Aparência` agora tem `Zoom padrão do mapa (%)`.
- As prévias do Painel Master também têm controle de zoom.
- Na tela de posicionamento com clique, existe `Tamanho da imagem clicável` para equilibrar visão e velocidade.


## Atualização: camadas de leitura e segurança Adm

- Foram adicionadas camadas escuras/translúcidas nas páginas, cards, métricas e sidebar para melhorar leitura sobre a imagem de fundo.
- O Painel Master continua aparecendo apenas para o usuário `Adm`.
- Também foi adicionada uma trava interna: mesmo que alguém tente acessar a função do Painel Master, o sistema bloqueia se o usuário atual não for `Adm`.


## Editor visual das mesas

No Painel Master, foi adicionada a aba `Editor visual`.

Recursos:
- arrastar mesas diretamente no mapa
- selecionar várias mesas
- mover grupos de mesas com botões de direção
- salvar todas as posições alteradas de uma vez
- ajuste individual separado na aba `Posição individual`

Observação: o editor usa `streamlit-drawable-canvas`.


## Editor de bloco / grade

Foi adicionada uma janela de edição de bloco no Painel Master.

Ela permite:
- selecionar um intervalo de mesas, como 1 a 40
- selecionar mesas manualmente
- organizar as mesas em grade com X inicial, Y inicial, colunas e espaçamento
- mover um bloco inteiro mantendo o desenho atual
- reorganizar fileiras e setores muito mais rápido do que mexer mesa por mesa
