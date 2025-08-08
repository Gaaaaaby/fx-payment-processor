 FX Payment Processor (Versión en Español)

**FX Payment Processor** es un prototipo de procesador de pagos multi-moneda. Permite la gestión de wallets en distintas divisas, realiza conversiones entre ellas y ofrece funciones básicas como depósito, retiro de fondos y consulta de balances.


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


