# data-pipeline-telegram

O [telegram](https://pt.wikipedia.org/wiki/Telegram) é uma famosa rede social de mensagens que está ativa no mercado desde 2013 e desde então se tornou uma fonte rica de diversos tipos de dados

-----

### Contexto
O projeto a seguir consiste na criação de um pipeline que coleta esses dados através de um chatbot alocado em um grupo e torna-os em dados visíveis que podem, futuramente, se tornar insights valiosos. 

Chatbot é um robô conversacional que oferece respostas aos usuários e é com ele que faremos as coletas de todas as mensagens.

As mensagens enviadas no grupo e coletadas pelo chatbot são dados transacionais, ou seja, são dados brutos, sem nenhum tipo de tratamento e que muitas vezes cotém informações irrelevantes para determinada análise.

Os dados transacionais passarão pelo processo de ETL para então se tornarem dados analíticos. Dados analíticos por sua vez, são dados tratados de uma forma que podem ser utilizados em análises.

-----

### Fluxograma do pipeline dos dados
![fluxograma](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/fluxograma_data_pipeline.png)


O chat bot faz a leitura dos dados transacionais, ou melhor dizendo, as mensagens enviadas pelos usuários no grupo do telegram,  e através do API Gateway e do AWS Lambda elas são salvas em um bucket no AWS S3 no formato json

----

### Bot Telegram


Após criar o bot no telegram atravé do BotFather ele mostrará o *token* de acesso, caso não tenha anotado, segue passo a passo para buscar esse toke

*Lembre-se, esse token é confidencial, portanto,  não o compartilhe*

Para acessar o *token* basta mandar a menssagem */mybots* para o BotFather, selecionar o bot criado e então acessar a aba *API Token*, como demonstrado abaixo:

![screen_shot_1](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print1.png)



O *token* de acesso é um código que aparece logo abaixo do nome do bot na cor laranja

![screen_shoot_2](https://github.com/LucasGuimaDev/data-pipeline-telegram/blob/main/imagens/print2.png)

