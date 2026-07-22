import re

def clean_and_convert_number(number) -> str:
    content = str(number)
    result = re.sub(r'[^\d]', '', content)
    
    return result

# --- Exemplos de Uso ---
testes = [
    "4.131",          # String com ponto
    "123.456.789-00", # Formato de CPF com pontos e traço
    "Nº 13/2018",     # String com símbolos, letras e barras
    45600,            # Um número inteiro puro
    12.34             # Um número float
    
]

print("--- Resultados da Limpeza ---")
for t in testes:
    resultado = clean_and_convert_number(t)
    print(f"Entrada: {repr(t)} (Tipo: {type(t).__name__}) -> Saída: '{resultado}' (Tipo: {type(resultado).__name__})")   
    
    
    
    
    
    
    
    
    
{
  "_id": {
    "$oid": "694e842cbb644cb8bed90fba"
  },
  "url": "https://www.in.gov.br/web/dou/-/portaria-n-1-262-de-4-de-setembro-de-2018-39943233",
  "date": "2018-09-06",
  "last_updated": {
    "$date": "2025-12-28T03:57:07.101Z"
  },
  "month": "Set",
  "ordinance": "PORTARIA Nº 1.262, DE 4 DE SETEMBRO DE 2018",
  "organ": "Ministério da Educação/Instituto Federal de Educação, Ciência e Tecnologia do Acre",
  "responsible": "ROSANA CAVALCANTE DOS SANTOS",
  "year": 2018,
  "acronym": "IFAC",
  "institute": "Instituto Federal do Acre",
  "tags": [
    "Nomeação",
    "Afastamento"
  ],
  "type": "Nomeação",
  "content": "a reitora do instituto federal de educacao, ciencia e tecnologia do acre - ifac, no uso de suas atribuicoes legais, que lhe confere o artigo 12 da lei no 11.892, de 29/12/2008, nomeada pelo decreto presidencial de 13 de abril de 2016, publicado no dou, no 71, secao 2, pagina 1, de 14/04/2016, resolve: art. 1o - nomear o servidor andre alfonso peixoto, tae, matricula siape no 3008727, para exercer o cargo de segundo substituto eventual nos casos de afastamento e impedimento legal ou regulamentar do titular do cargo da assessoria de relacoes internacionais - arint, codigo cd-3, no ambito do instituto federal de educacao, ciencia e tecnologia do acre, a partir da publicacao. rosana cavalcante dos santos",
  "number": "1262"
}



{
  "_id": {
    "$oid": "694e843bbb644cb8bed90fe6"
  },
  "url": "https://www.in.gov.br/web/dou/-/portaria-n-1-031-de-12-de-julho-de-2018-29900450",
  "date": "2018-07-13",
  "last_updated": {
    "$date": "2025-12-28T03:57:20.894Z"
  },
  "month": "Jul",
  "ordinance": "PORTARIA Nº 1.031, DE 12 DE JULHO DE 2018",
  "organ": "Ministério da Educação/Instituto Federal de Educação, Ciência e Tecnologia do Acre",
  "responsible": "UBIRACY DA SILVA DANTAS",
  "year": 2018,
  "acronym": "IFAC",
  "institute": "Instituto Federal do Acre",
  "tags": [
    "Nomeação",
    "Afastamento"
  ],
  "type": "Nomeação",
  "content": "o reitor substituto do instituto federal de educacao, ciencia e tecnologia do acre - ifac, no uso de suas atribuicoes legais, que lhe confere o artigo 12 da lei no 11.892, de 29/12/2008, nomeado pela portaria no 635 de 07 de maio de 2018, publicada no diario oficial da uniao no 87 de 08 de maio de 2018, secao 2, resolve: art. 1o - nomear a servidora janara alexandre da silva vasconcelos, matricula siape: 1937548-4, ao cargo de 3a substituta eventual, nos casos de afastamento e impedimento legal ou regulamentar do titular do cargo de pro-reitor de administracao - cd 02, da pro-reitoria de administracao do instituto federal de educacao, ciencia e tecnologia do acre. art. 2o - esta portaria entra em vigor na data de sua publicacao. ubiracy da silva dantas",
  "number": "1031"
}