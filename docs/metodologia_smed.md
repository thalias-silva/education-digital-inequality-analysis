# Metodologia - Score Multidimensional de Exclusão Digital (SMED)

## Fórmula Matemática
O cálculo do SMED será realizado através da soma ponderada das variáveis normalizadas:

$$SMED_i = \sum_{k=1}^{n} (w_k \times Z_k)$$

Onde:
- **w_k**: Pesos derivados da Análise de Componentes Principais (PCA).
- **Z_k**: Variáveis padronizadas via Z-score.

## Justificativa da Escolha do PCA
A escolha da Análise de Componentes Principais (PCA) fundamenta-se na necessidade de atribuir pesos às variáveis de forma objetiva, baseando-se na variância dos dados brutos do INEP e CETIC. Diferente de métodos subjetivos (como o AHP), o PCA identifica quais pilares (Acesso, Dispositivos, Infraestrutura ou Socioeconômico) mais contribuem para a variação da exclusão digital no Brasil, garantindo maior rigor estatístico e permitindo que a própria estrutura dos dados direcione a ponderação do indicador.

## Critérios de Seleção e Qualidade
1. **Filtro de Atividade:** Serão consideradas apenas escolas com `TP_SITUACAO_FUNCIONAMENTO = 1` (Em atividade), conforme orientação para evitar distorções por instituições extintas ou paralisadas.
2. **Normalização:** Aplicação de Z-score para garantir que variáveis em escalas diferentes (ex: Sim/Não vs. Quantidades) sejam comparáveis.
3. **Validação:** O score final será validado através da correlação de Spearman com taxas de evasão escolar e o Ideb.
