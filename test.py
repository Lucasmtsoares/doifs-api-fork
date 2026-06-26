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