
Proyecto: Inversor Virtual Pro (Kran Investor)
Un simulador de inversión "Learn-to-Earn" gamificado y basado en Web3.

Tabla de Contenidos
1. Concepto General

2. Pilares Fundamentales

3. Arquitectura del Sistema

4. El Ecosistema del Token: Kran ($KRN)

5. Pila Tecnológica (Tech Stack)

6. Estado Actual del Proyecto

6. Hoja de Ruta del Desarrollo (Roadmap)

7. Cómo Empezar (Getting Started)

_______________________________________________________________________________

1. Concepto General
Kran Investor Pro (KINV) es una plataforma que gamifica el aprendizaje del mercado de valores. Permite a los usuarios operar en mercados reales (NYSE, NASDAQ, etc.) con dinero 100% virtual, eliminando cualquier riesgo financiero. A diferencia de otros simuladores, IVP integra una economía Web3 a través de su token nativo, el Kran ($KRN), recompensando a los usuarios por su habilidad, consistencia y aprendizaje bajo un modelo "Learn-to-Earn".

El objetivo es crear un entorno adictivo y competitivo donde los usuarios no solo aprenden estrategias de inversión reales, sino que también obtienen activos digitales (tokens y NFTs) con utilidad dentro del ecosistema del juego.

2. Pilares Fundamentales
📈 Realismo sin Riesgo: Se utilizan datos de mercado en tiempo real (o con un retraso de 15 min) de proveedores de API fiables. Se simulan eventos corporativos (dividendos, splits) y comisiones para una experiencia auténtica, pero con un capital inicial virtual.

🎮 Gamificación Adictiva: Un sistema de ligas, misiones diarias/semanales, niveles de experiencia (XP) y logros mantiene a los usuarios enganchados y motivados para mejorar sus estrategias y competir contra otros.

🎓 Componente Educativo: La plataforma integra herramientas como un potente "Explorador de Mercado" (Screener) que permite a los usuarios aplicar estrategias conocidas (Value, Growth, Dividend Investing), además de un feed de noticias contextualizado.

🔗 Economía Web3 con Kran ($KRN): El corazón del proyecto. Los usuarios ganan $KRN por su desempeño, no con dinero real. Estos tokens les otorgan propiedad real sobre sus recompensas y pueden ser utilizados en un mercado interno para adquirir NFTs (skins, badges) y acceder a funcionalidades premium.

3. Arquitectura del Sistema y Mapa de Contexto
El sistema se compone de una arquitectura de aplicación descentralizada (DApp) moderna. El siguiente diagrama y descripción detallan los componentes principales y cómo se interrelacionan para crear la experiencia "Learn-to-Earn".

```
+---------------------------------+      +---------------------------------+
|      👤 Usuario (Navegador)      |      |      📈 API Externa (FMP)       |
| - Conecta Wallet (MetaMask)     |      | - Datos de mercado en tiempo real|
| - Realiza trades virtuales      |      | - Búsqueda de activos           |
+----------------|----------------+      +----------------^----------------+
                 |                                         | (Petición de datos)
      (Interactúa con la UI)                               |
                 |                                         |
                 v                                         |
+----------------+----------------+      +-----------------+-----------------+
|   💻 Frontend (React/Ethers.js) |----->|     🧠 Backend (Python/Flask)     |
| - Interfaz de Usuario (UI)      |      | - API REST para el cliente        |
| - Gestión de estado (JWT)       |      | - Lógica de negocio (trades)      |
| - Llama a la API del Backend    |      | - Autenticación y perfiles        |
| - Firma transacciones Web3      |      | - Conexión con BD y API externa   |
+----------------|----------------+      +-----------------+-----------------+
                 |                                         |                 |
(Transacciones firmadas:          (Consultas y            (Transacciones:
 comprar NFT, Staking)             mutaciones de datos)      distribuir recompensas)
                 |                                         |                 |
                 v                                         v                 v
+----------------+----------------+      +-----------------+-----------------+
|     🔗 Blockchain (Polygon)     |      |   🗃️ Base de Datos (PostgreSQL)   |
| - Contrato $KRN (ERC20)         |<---->| - Perfiles de usuario             |
| - Contrato Mercado (ERC721)     |      | - Carteras virtuales (dinero/activos)|
| - Contrato Staking              |      | - Historial de transacciones      |
+---------------------------------+      +-----------------------------------+
```

**Descripción de Componentes y Flujos:**

*   **Usuario (User):** Es el actor principal. Interactúa exclusivamente con el Frontend a través de su navegador, donde conecta su billetera digital (ej. MetaMask) para gestionar sus activos Web3.

*   **Frontend (React & Ethers.js):** Es la puerta de entrada a la aplicación.
    *   **Relación con el Usuario:** Provee la interfaz gráfica para todas las operaciones: visualizar el dashboard, buscar activos, y ejecutar órdenes de compra/venta.
    *   **Relación con el Backend:** Se comunica vía una API REST para registrar/autenticar usuarios, obtener el estado de la cartera, y enviar operaciones de trading simuladas.
    *   **Relación con la Blockchain:** Utiliza `Ethers.js` para que el usuario pueda firmar y enviar transacciones directamente a los smart contracts (ej. comprar un NFT en el mercado o hacer staking de $KRN).

*   **Backend (Python, Flask, SQLAlchemy, Web3.py):** Es el cerebro de la lógica de negocio y el orquestador de datos.
    *   **Relación con el Frontend:** Expone una API REST segura (usando JWT) que el frontend consume.
    *   **Relación con la Base de Datos:** Utiliza `SQLAlchemy` para persistir y consultar toda la información *off-chain*, como los perfiles de usuario, el contenido de sus carteras virtuales, y el historial de todas las operaciones simuladas.
    *   **Relación con la API Externa:** Se conecta al servicio de *Financial Modeling Prep (FMP)* para obtener cotizaciones de activos en tiempo real, asegurando que las operaciones simuladas se basen en datos de mercado reales.
    *   **Relación con la Blockchain:** Utiliza `Web3.py` para interactuar con los smart contracts desde el lado del servidor. Su principal función es la de actuar como un "distribuidor" o "faucet", enviando recompensas en tokens $KRN a los usuarios cuando cumplen objetivos (ej. ganar una liga).

*   **Base de Datos (PostgreSQL):** Es el almacén de datos centralizado y *off-chain*. Guarda toda la información que no necesita estar en la blockchain por razones de coste y velocidad, como los datos de perfil, el estado del juego (misiones, XP) y el registro detallado de las operaciones de trading virtuales.

*   **Blockchain (Polygon):** Es la capa descentralizada que aporta la propiedad real de los activos digitales.
    *   **Relación con Frontend y Backend:** Ambos pueden interactuar con los contratos. El frontend se enfoca en operaciones iniciadas por el usuario (gastar tokens), mientras que el backend se enfoca en la distribución de recompensas (ganar tokens).
    *   **Componentes:** Contiene la lógica inmutable para el token $KRN (ERC-20), los NFTs del mercado (ERC-721) y las reglas de staking.

*   **API Externa (Financial Modeling Prep):** Es el proveedor de datos de mercado. El Backend depende de este servicio para dar realismo al simulador.

4. El Ecosistema del Token: Kran ($KRN)
Kran es el token de utilidad estándar ERC-20 del ecosistema IVP.

Obtención (Learn-to-Earn):

Completar misiones y desafíos (ej. "Consigue un 5% de rentabilidad").

Ganar o quedar en el top de las ligas semanales/mensuales.

Desbloquear logros importantes.

Hacer "staking" de $KRN para obtener recompensas pasivas.

Utilidad (Gasto):

Mercado de NFTs: Comprar y vender activos cosméticos como skins para el dashboard, avatares especiales o badges de perfil únicos.

Acceso Premium: Desbloquear temporalmente herramientas de análisis avanzadas.

Torneos: Pagar la cuota de inscripción para torneos de alto riesgo con grandes premios en $KRN.

5. Pila Tecnológica (Tech Stack)
Frontend:

Framework: React.js o Vue.js

Librería Gráficos: TradingView Lightweight Charts

Conexión Web3: Ethers.js

Backend:

Lenguaje/Framework: Python con Django o Flask.

Conexión Web3: Web3.py

Base de Datos:

Sistema: PostgreSQL

Blockchain:

Red: Polygon (PoS Mainnet) y Mumbai (Testnet).

Lenguaje Smart Contracts: Solidity.

Entorno de Desarrollo: Hardhat.

Estándares: ERC-20 (para $KRN), ERC-721 (para NFTs).

APIs Externas:

  Datos de Mercado: Financial Modeling Prep (FMP) o Alpha Vantage.

Despliegue:

  Repositorio: [kran-investor en GitHub](https://github.com/jimbomilk/kran-investor)
  Plataforma: Render.com
  Servicios en Render:
    - **Web Service (API):** `kran-investor-api`
    - **PostgreSQL (Base de Datos):** `kran-investor-db`
  Frontend: Vercel

6. Estado Actual del Proyecto
El backend del proyecto está parcialmente implementado. Se ha construido una base sólida con Flask, SQLAlchemy para la base de datos y JWT para la autenticación.

**Funcionalidades Implementadas:**

*   **Autenticación de Usuarios:**
    *   `POST /api/auth/register`: Creación de nuevos usuarios.
    *   `POST /api/auth/login`: Inicio de sesión y obtención de token JWT.
*   **Gestión de Cartera (Portfolio):**
    *   `GET /api/portfolio`: Un usuario autenticado puede ver su cartera (dinero virtual y activos).
    *   `POST /api/portfolio/buy`: Endpoint para simular la compra de un activo.
    *   `POST /api/portfolio/sell`: Endpoint para simular la venta de un activo.
*   **Servicio de Mercado:**
    *   Existe un servicio (`app/services/market_service.py`) que se conecta a la API de Financial Modeling Prep para obtener precios reales.

**Punto Crítico Actual:**
Las rutas `/buy` y `/sell` **aún no están conectadas al servicio de precios reales**. Actualmente, utilizan una función simulada con precios fijos. El siguiente paso de desarrollo es integrar el `market_service` en estas rutas para que las operaciones se realicen con datos de mercado en tiempo real.

6. Hoja de Ruta del Desarrollo (Roadmap)
Este proyecto se desarrollará en fases iterativas para asegurar una base sólida antes de añadir complejidad.

Fase 1: El Simulador Core (MVP Web2)
(Objetivo: Tener un simulador funcional sin blockchain)

Setup Inicial: Crear repositorio en GitHub, configurar entorno de desarrollo.

Diseño de la Base de Datos: Definir los esquemas para Usuarios, Carteras y Transacciones.

Backend (API REST):

  - **[✓] Autenticación:** Endpoints para registro (`/auth/register`), login (`/auth/login`) y gestión de perfil de usuario con JWT (JSON Web Tokens).
  - **Cartera (Portfolio):**
    - **[✓] `GET /portfolio`**: Obtener la cartera actual del usuario (activos, cantidad, valor actual).
    - **[✓] `POST /portfolio/buy`**: Simular la compra de un activo (validando saldo virtual). *(Nota: Usa precios simulados)*.
    - **[✓] `POST /portfolio/sell`**: Simular la venta de un activo (validando tenencia). *(Nota: Usa precios simulados)*.
  - **Mercado:**
    - **[✓] `GET /api/market/quote/{ticker}`**: Endpoint para obtener la cotización de un activo específico desde la API externa.
    - **[✓] `GET /api/market/search/{query}`**: Endpoint para buscar activos.
  - **[ ] Trabajo Programado (Cron Job):** Implementar un script para actualizar periódicamente el valor de las carteras de todos los usuarios.

Frontend:

  - **Componentes de Autenticación:** Formularios de Login y Registro. Lógica para manejar el estado de autenticación (ej. con Context API o Redux).
  - **Vistas Principales:**
    - **Dashboard:** Vista principal que muestra el valor total del portfolio, un gráfico de rendimiento y la lista de activos en posesión.
    - **Página de Activo (`/asset/{ticker}`):** Muestra información detallada de un activo, su gráfico histórico y los botones de compra/venta.
    - **Explorador/Buscador:** Interfaz para buscar nuevos activos para invertir.
  - **Lógica de Interacción:**
    - Conectar los componentes con la API REST del backend para realizar operaciones.
    - Integrar la librería de gráficos (TradingView) para mostrar datos de mercado.

Fase 2: Creación e Integración del Kran ($KRN)
(Objetivo: Transformar el simulador en una DApp básica)

Creación del Token:

Escribir el Smart Contract ERC-20 para Kran ($KRN) usando OpenZeppelin y Hardhat.

Desplegar en la red de pruebas Mumbai.

Integración Web3 en el Frontend:

Implementar la conexión con billeteras (MetaMask) usando Ethers.js.

Reemplazar el login tradicional por un sistema "Connect Wallet".

Integración Web3 en el Backend:

Crear un servicio "distribuidor" que envíe recompensas en $KRN (de prueba) desde una billetera de tesorería a los usuarios al cumplir un objetivo simple.

Fase 3: Gamificación Avanzada y Mercado NFT
(Objetivo: Construir la economía y la adicción del juego)

Sistema de Gamificación:

Implementar la lógica de misiones, logros y ligas en el Backend.

Conectar estos eventos a la distribución de recompensas en $KRN.

Mercado de NFTs:

Escribir y desplegar los Smart Contracts para los NFTs (ERC-721) y el mercado.

Crear la interfaz del mercado en el Frontend donde los usuarios puedan comprar NFTs con sus $KRN ganados.

Fase 4: Lanzamiento y Futuro
(Objetivo: Preparar para el público y escalar)

Auditoría de Seguridad: Realizar una auditoría externa de todos los Smart Contracts.

Despliegue en Mainnet: Desplegar los contratos finales en la red principal de Polygon.

Lanzamiento Beta: Abrir la plataforma a un grupo cerrado de usuarios para feedback.

Lanzamiento Público: Apertura a todo el mundo y comienzo de las competiciones oficiales.

7. Cómo Empezar (Getting Started)
Esta sección se completará a medida que el proyecto avance.
Esta sección contiene las instrucciones para configurar y ejecutar el proyecto en un entorno de desarrollo local.

### 1. Prerrequisitos
- Python 3.8 o superior.
- Node.js 18 o superior y npm.
- `pip` y `venv` (generalmente incluidos con Python).

### 2. Configuración del Frontend

1.  **Navegar a la carpeta del frontend:**
    ```bash
    cd kran-investor/frontend
    ```

2.  **Instalar las dependencias de Node.js:**
    ```bash
    npm install
    ```

3.  **(Opcional) Configurar variables de entorno:**
    Si tu backend se ejecuta en un puerto o dirección diferente, puedes crear un fichero `.env` en la raíz de `frontend/` para apuntar a él.
    ```
    VITE_API_URL=http://127.0.0.1:5000/api
    ```

4.  **Ejecutar el servidor de desarrollo de Vite:**
    ```bash
    npm run dev
    ```

El frontend estará disponible en `http://127.0.0.1:5173` (o el puerto que indique Vite).

### 3. Configuración del Backend
### 1. Prerrequisitos
- Python 3.8 o superior.
- `pip` y `venv` (generalmente incluidos con Python).

### 2. Configuración del Backend

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/jimbomilk/kran-investor.git
    cd kran-investor/backend
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate

    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar las variables de entorno:**
    Crea un fichero llamado `.env` dentro de la carpeta `backend/` y añade el siguiente contenido. **Necesitarás obtener tu propia clave de API de Financial Modeling Prep.**

    ```
    # Clave secreta para firmar los tokens JWT. Puedes generar una con: python -c 'import secrets; print(secrets.token_hex())'
    SECRET_KEY="tu_clave_secreta_aqui"

    # URL de conexión a la base de datos. Para empezar, SQLite es lo más sencillo.
    DATABASE_URL="sqlite:///site.db"

    # Clave de API de Financial Modeling Prep (https://site.financialmodelingprep.com/developer/docs)
    FMP_API_KEY="tu_clave_de_api_de_fmp_aqui"
    ```

5.  **Crear y actualizar la base de datos:**
    (Asumiendo que se usa Flask-Migrate)
    ```bash
    # Si es la primera vez, para crear el repositorio de migraciones:
    # flask db init

    # Para generar una migración inicial y aplicar los modelos:
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6.  **Ejecutar el servidor de desarrollo:**
    ```bash
    flask run
    ```

El servidor estará disponible en `http://127.0.0.1:5000`. Ya puedes usar una herramienta como Postman o Insomnia para probar los endpoints de la API.
