 FX Payment Processor (Versión en Español)

**FX Payment Processor** es un prototipo de procesador de pagos multi-moneda. Permite la gestión de wallets en distintas divisas, realiza conversiones entre ellas y ofrece funciones básicas como depósito, retiro de fondos y consulta de balances.

# Branches
-main: with the tests and functional endpoints 
-gaby_test: for testing only 

## Tecnologías utilizadas

- **FastAPI** – Framework para construir APIs con Python.
- **Uvicorn** – Servidor ASGI para aplicaciones FastAPI.
- **Pydantic** – Validación de datos basada en modelos.
- **SQLAlchemy** – ORM para la gestión de bases de datos relacionales.


## Instalación

```bash
git clone https://github.com/Gaaaaaby/fx-payment-processor.git
cd fx-payment-processor
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn main:app --reload
```
PS C:\Users\richa\Downloads\fx-payment-processor\app> uvicorn main:app --reload

# Para los tests pytest
PS C:\Users\richa\Downloads\fx-payment-processor\app> pytest tests/test_wallet.py

## Modelos 

### `User`  
Representa al usuario del sistema.  
El modelo:  
- Tiene un `id` único (`str`) como identificador.  
- Puede tener múltiples wallets asociadas.  
- Si se elimina el usuario, sus wallets también se eliminan automáticamente.

---

### `Wallet`  
Representa una wallet individual del usuario.  
El modelo:  
- Tiene un `id` autoincremental (`int`).  
- Está asociada a un `user_id`.  
- Contiene una moneda (`currency`) y su balance (`balance`).  
- Cada usuario puede tener **una sola wallet por moneda** (restricción única).

---

### `ExchangeRate`  
Define la tasa de cambio entre dos monedas.  
El modelo:  
- Contiene `currency_from`, `currency_to` y el `rate` de conversión.  
- Cada par de monedas es único en la base de datos.

---

## Payloads y resultados

### `ConvertPayload`  
Usado para solicitar una conversión de fondos.  
Incluye:  
- `from_currency`: moneda de origen.  
- `to_currency`: moneda de destino.  
- `amount`: monto a convertir.

---

### `ConvertResult`  
Respuesta al convertir fondos entre monedas.  
Incluye:  
- `user_id`: ID del usuario.  
- `wallet_id`: ID de la wallet.  
- `from_currency`: moneda de origen.  
- `to_currency`: moneda de destino.

---

### `WithdrawPayload`  
Usado para retirar fondos de una wallet.  
Incluye:  
- `wallet_id`: ID de la wallet.  
- `currency`: moneda a retirar.  
- `amount`: monto a retirar.

---

### `WithdrawResult`  
Respuesta al retirar fondos.  
Incluye:  
- `wallet_id`: ID de la wallet.  
- `amount`: monto retirado.  
- `balance`: balance restante.

---

### `FundPayload`  
Payload vacío (por ahora), usado para depositar fondos.  
Puede extenderse en el futuro si se requiere más información.

---

### `FundResult`  
Respuesta al depositar fondos.  
Incluye:  
- `currency`: moneda depositada.  
- `amount_funded`: monto depositado.

---

### `BalanceResult`  
Respuesta al consultar balances.  
Incluye:  
- `user_id`: ID del usuario.  
- `balance`: balance total.

## Endpoints disponibles

### 1. `/fund`
Permite **depositar dinero** en la cuenta, proporcionando el `user_id` y el modelo `FundPayload`.  
El sistema:
- Verifica que el usuario exista.
- Comprueba que la moneda en la cual se desea depositar esté disponible.
- Valida que el monto sea correcto (no negativo).
- Si la wallet existe, agrega el monto al balance.
- Si no existe, crea la wallet y asigna el monto inicial.


### 2. `/withdraw`
Permite **retirar dinero** de la cuenta, proporcionando el `user_id` y el modelo `WithdrawPayload`.  
El sistema:
- Verifica que el usuario exista.
- Comprueba que la moneda esté disponible en sus wallets.
- Valida que el monto sea correcto (no negativo).
- Si la wallet existe y tiene fondos suficientes, descuenta el monto del balance.
- Si no existe la wallet o el saldo es insuficiente, devuelve un error.

---

### 3. `/balances`
Permite **consultar los balances** actuales del usuario en todas las monedas disponibles.  
El sistema:
- Verifica que el usuario exista.
- Devuelve un diccionario con cada moneda y su balance correspondiente.
- Si el usuario no tiene wallets registradas, devuelve una respuesta vacía o con balances en cero.

---

### 4. `/convert`  
Permite **convertir fondos** de una moneda a otra dentro de una wallet específica del usuario.  
El sistema:  
- Verifica que el usuario y la wallet existan.  
- Comprueba que haya fondos suficientes en la moneda de origen (`from_currency`).  
- Valida que la moneda de destino (`to_currency`) y la moneda inicial (`from_currency`)esten soportadas en la wallet.  
- Consulta la tasa de cambio correspondiente en la base de datos.  
- Calcula el monto convertido y actualiza los balances de ambas monedas.  
- Devuelve los datos de la conversión realizada.



