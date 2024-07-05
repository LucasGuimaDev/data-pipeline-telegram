# data-pipeline-telegram

O [telegram](https://pt.wikipedia.org/wiki/Telegram) é uma famosa rede social de mensagens que está ativa no mercado desde 2013 e desde então se tornou uma fonte rica de diversos tipos de dados

-----

### Contexto
O projeto a seguir consiste na criação de um pipeline que coleta esses dados através de um chatbot alocado em um grupo e torna-os em dados visíveis que podem, futuramente, se tornar insights valiosos. 

Chatbot é um robô conversacional que oferece respostas aos usuários e é com ele que faremos as coletas de todas as mensagens.

As mensagens enviadas no grupo e coletadas pelo chatbot são dados transacionais, ou seja, são dados brutos, sem nenhum tipo de tratamento e que muitas vezes cotém informações irrelevantes para determinada análise.

Os dados transacionais passarão pelo processo de ETL para então se tornarem dados analíticos. Dados analíticos por sua vez, são dados tratados de uma forma que podem ser utilizados em análises.

