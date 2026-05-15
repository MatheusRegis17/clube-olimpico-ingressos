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
