
Proyecto: Inversor Virtual Pro (Kran Investor)
Un simulador de inversión "Learn-to-Earn" gamificado y basado en Web3.

Tabla de Contenidos
1. Concepto General

2. Pilares Fundamentales

3. Arquitectura del Sistema

4. El Ecosistema del Token: Kran ($KRN)

5. Pila Tecnológica (Tech Stack)

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

3. Arquitectura del Sistema
El sistema se compone de una arquitectura de aplicación descentralizada (DApp) moderna:

  [ 👤 Usuario (Navegador) ]
           |
           V  (Interactúa con la UI, conecta MetaMask)
  [ 💻 Frontend (React, Ethers.js) ] --- (Peticiones API REST) ---> [ 🧠 Backend (Python) ]
           |                                                               |           |
 (Firma y envía transacciones)                               (Envía transacciones, ej. recompensas) | (Consultas)
           |                                                               |           V
           '---------------------> [ 🔗 Blockchain (Polygon) ] <---------'   [ 🗃️ Base de Datos (PostgreSQL) ]
                                     - Smart Contract $KRN (ERC20)             (Datos off-chain: perfiles,
                                     - Smart Contract Mercado (ERC721)          transacciones simuladas, etc.)
                                     - Smart Contract Staking
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

Frontend: Vercel

Backend/DB: Render o Heroku.

6. Hoja de Ruta del Desarrollo (Roadmap)
Este proyecto se desarrollará en fases iterativas para asegurar una base sólida antes de añadir complejidad.

Fase 1: El Simulador Core (MVP Web2)
(Objetivo: Tener un simulador funcional sin blockchain)

Setup Inicial: Crear repositorio en GitHub, configurar entorno de desarrollo.

Diseño de la Base de Datos: Definir los esquemas para Usuarios, Carteras y Transacciones.

Backend (API REST):

  - **Autenticación:** Endpoints para registro (`/auth/register`), login (`/auth/login`) y gestión de perfil de usuario con JWT (JSON Web Tokens).
  - **Cartera (Portfolio):**
    - `GET /portfolio`: Obtener la cartera actual del usuario (activos, cantidad, valor actual).
    - `POST /portfolio/buy`: Simular la compra de un activo (validando saldo virtual).
    - `POST /portfolio/sell`: Simular la venta de un activo (validando tenencia).
  - **Mercado:**
    - `GET /market/quote/{ticker}`: Endpoint para obtener la cotización de un activo específico desde la API externa.
    - `GET /market/search/{query}`: Endpoint para buscar activos.
  - **Trabajo Programado (Cron Job):** Implementar un script para actualizar periódicamente el valor de las carteras de todos los usuarios.

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

Bash

# Clonar el repositorio
git clone https://github.com/jimbomilk/kran-investor.git

# Navegar al directorio del frontend
cd kran-investor/frontend
npm install

# Navegar al directorio del backend
cd ../backend
pip install -r requirements.txt

# Crear un archivo .env en el backend y frontend para las variables de entorno
# (API Keys, conexión a la base de datos, etc.)

# (Instrucciones adicionales para ejecutar la aplicación aquí)
