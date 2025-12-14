# 📡 API Documentation para Frontend
## Backend Amazon Ads Campaigns

---

## 🔗 Base URL
```
http://localhost:8000/api
```

## 📄 Documentación Interactiva
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

---

## 📋 Tabla de Contenido
1. [Endpoints Disponibles](#endpoints-disponibles)
2. [Crear Campaña](#1-crear-campaña)
3. [Listar Campañas](#2-listar-campañas)
4. [Obtener Detalle de Campaña](#3-obtener-detalle-de-campaña)
5. [Eliminar Campaña](#4-eliminar-campaña)
6. [Obtener Estadísticas](#5-obtener-estadísticas)
7. [Reintentar Campaña Fallida](#6-reintentar-campaña-fallida)
8. [Tipos de Datos](#tipos-de-datos)
9. [Estados de Campaña](#estados-de-campaña)
10. [Códigos de Error](#códigos-de-error)
11. [Ejemplos Frontend (JavaScript)](#ejemplos-frontend)

---

## Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/campaigns/` | Crear nueva campaña |
| `GET` | `/campaigns/` | Listar todas las campañas |
| `GET` | `/campaigns/{id}/` | Obtener detalles de campaña |
| `DELETE` | `/campaigns/{id}/` | Eliminar campaña |
| `GET` | `/campaigns/stats/` | Estadísticas agregadas |
| `POST` | `/campaigns/{id}/retry/` | Reintentar sincronización |

---

## 1. Crear Campaña

### `POST /api/campaigns/`

Crea una nueva campaña publicitaria. La campaña se crea en estado `PENDING` y automáticamente se dispara una tarea asíncrona para sincronizarla con Amazon Ads.

### Request Body

```json
{
  "name": "string (requerido, max 255 caracteres)",
  "budget": "number (requerido, mínimo 0.01, 2 decimales)",
  "keywords": ["array de strings"] o "string separado por comas"
}
```

### Validaciones
- ✅ `name`: No puede estar vacío, se eliminan espacios al inicio/final
- ✅ `budget`: Debe ser mayor a 0.01, máximo 10 dígitos, 2 decimales
- ✅ `keywords`: Mínimo 1 keyword, se eliminan duplicados automáticamente

### Ejemplo Request

**Opción 1: Array de keywords**
```json
{
  "name": "Summer Sale Campaign",
  "budget": "250.50",
  "keywords": ["running shoes", "sports", "nike", "adidas"]
}
```

**Opción 2: String separado por comas**
```json
{
  "name": "Winter Sale Campaign",
  "budget": "150.00",
  "keywords": "jackets, coats, winter clothing, warm clothes"
}
```

### Response (201 Created)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Summer Sale Campaign",
  "budget": "250.50",
  "keywords": ["running shoes", "sports", "nike", "adidas"],
  "status": "PENDING",
  "status_display": "Pending",
  "external_id": null,
  "has_external_id": false,
  "is_synced": false,
  "error_message": null,
  "retry_count": 0,
  "synced_at": null,
  "created_at": "2025-12-14T21:00:00Z",
  "updated_at": "2025-12-14T21:00:00Z"
}
```

### Errores Posibles

**400 Bad Request - Validación fallida**
```json
{
  "name": ["This field is required."],
  "budget": ["Ensure this value is greater than or equal to 0.01."],
  "keywords": ["This field is required."]
}
```

**400 Bad Request - Nombre vacío**
```json
{
  "name": ["Campaign name cannot be empty."]
}
```

---

## 2. Listar Campañas

### `GET /api/campaigns/`

Obtiene una lista paginada de todas las campañas con soporte para filtrado, búsqueda y ordenamiento.

### Query Parameters

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `page` | integer | Número de página | `?page=2` |
| `page_size` | integer | Resultados por página (default: 20) | `?page_size=50` |
| `status` | string | Filtrar por estado | `?status=ACTIVE` |
| `name` | string | Buscar por nombre (contiene) | `?name=summer` |
| `has_external_id` | boolean | Campañas sincronizadas | `?has_external_id=true` |
| `ordering` | string | Ordenar resultados | `?ordering=-created_at` |

### Valores válidos para `status`
- `PENDING` - Pendiente de sincronización
- `PROCESSING` - En proceso de sincronización
- `ACTIVE` - Activa en Amazon
- `FAILED` - Sincronización fallida

### Valores válidos para `ordering`
- `created_at` / `-created_at` (ascendente/descendente)
- `name` / `-name`
- `budget` / `-budget`
- `status` / `-status`

### Ejemplo Request

```bash
GET /api/campaigns/?status=ACTIVE&ordering=-created_at&page=1&page_size=10
```

### Response (200 OK)

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/campaigns/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Summer Sale Campaign",
      "budget": "250.50",
      "keywords": ["running shoes", "sports"],
      "status": "ACTIVE",
      "status_display": "Active",
      "external_id": "AMZ-12345",
      "has_external_id": true,
      "created_at": "2025-12-14T21:00:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440111",
      "name": "Winter Sale Campaign",
      "budget": "150.00",
      "keywords": ["jackets", "coats"],
      "status": "PROCESSING",
      "status_display": "Processing",
      "external_id": "AMZ-67890",
      "has_external_id": true,
      "created_at": "2025-12-14T20:55:00Z"
    }
  ]
}
```

### Ejemplos de uso

**Filtrar campañas fallidas**
```bash
GET /api/campaigns/?status=FAILED
```

**Buscar campañas por nombre**
```bash
GET /api/campaigns/?name=sale
```

**Obtener solo campañas sincronizadas**
```bash
GET /api/campaigns/?has_external_id=true
```

---

## 3. Obtener Detalle de Campaña

### `GET /api/campaigns/{id}/`

Obtiene información completa de una campaña específica.

### Path Parameters
- `id` (UUID): ID de la campaña

### Ejemplo Request

```bash
GET /api/campaigns/550e8400-e29b-41d4-a716-446655440000/
```

### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Summer Sale Campaign",
  "budget": "250.50",
  "keywords": ["running shoes", "sports", "nike", "adidas"],
  "status": "ACTIVE",
  "status_display": "Active",
  "external_id": "AMZ-12345",
  "has_external_id": true,
  "is_synced": true,
  "error_message": null,
  "retry_count": 0,
  "synced_at": "2025-12-14T21:01:30Z",
  "created_at": "2025-12-14T21:00:00Z",
  "updated_at": "2025-12-14T21:01:30Z"
}
```

### Errores Posibles

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

---

## 4. Eliminar Campaña

### `DELETE /api/campaigns/{id}/`

Elimina una campaña. **Solo permite eliminar campañas que NO estén sincronizadas con Amazon** (que no tengan `external_id`).

### Path Parameters
- `id` (UUID): ID de la campaña

### Ejemplo Request

```bash
DELETE /api/campaigns/550e8400-e29b-41d4-a716-446655440000/
```

### Response (204 No Content)

Sin cuerpo de respuesta.

### Errores Posibles

**400 Bad Request - Campaña sincronizada**
```json
{
  "error": {
    "code": "cannot_delete_synced",
    "message": "Cannot delete a campaign that is synced with Amazon."
  }
}
```

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

---

## 5. Obtener Estadísticas

### `GET /api/campaigns/stats/`

Obtiene estadísticas agregadas de todas las campañas.

### Ejemplo Request

```bash
GET /api/campaigns/stats/
```

### Response (200 OK)

```json
{
  "total": 125,
  "by_status": {
    "PENDING": 5,
    "PROCESSING": 12,
    "ACTIVE": 98,
    "FAILED": 10
  }
}
```

---

## 6. Reintentar Campaña Fallida

### `POST /api/campaigns/{id}/retry/`

Reintenta la sincronización de una campaña fallida. Solo funciona si:
- El estado es `FAILED`
- El contador de reintentos es menor a 3

### Path Parameters
- `id` (UUID): ID de la campaña

### Ejemplo Request

```bash
POST /api/campaigns/550e8400-e29b-41d4-a716-446655440000/retry/
```

### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Failed Campaign",
  "budget": "100.00",
  "keywords": ["test"],
  "status": "FAILED",
  "status_display": "Failed",
  "external_id": null,
  "has_external_id": false,
  "is_synced": false,
  "error_message": "Rate limit exceeded. Retry after 60 seconds.",
  "retry_count": 2,
  "synced_at": null,
  "created_at": "2025-12-14T20:00:00Z",
  "updated_at": "2025-12-14T20:05:00Z"
}
```

### Errores Posibles

**400 Bad Request - No se puede reintentar**
```json
{
  "error": {
    "code": "cannot_retry",
    "message": "Campaign cannot be retried. Status: ACTIVE, Retries: 0/3"
  }
}
```

---

## Tipos de Datos

### Campaign (Objeto Completo)

```typescript
interface Campaign {
  id: string;                      // UUID
  name: string;                    // max 255 caracteres
  budget: string;                  // Decimal como string "250.50"
  keywords: string[];              // Array de strings
  status: CampaignStatus;          // Ver enumeración abajo
  status_display: string;          // Versión legible del estado
  external_id: string | null;      // ID de Amazon Ads
  has_external_id: boolean;        // true si está sincronizada
  is_synced: boolean;              // true si está ACTIVE y sincronizada
  error_message: string | null;    // Mensaje de error si falló
  retry_count: number;             // Número de reintentos (0-3)
  synced_at: string | null;        // ISO 8601 timestamp
  created_at: string;              // ISO 8601 timestamp
  updated_at: string;              // ISO 8601 timestamp
}
```

### Campaign (Listado)

```typescript
interface CampaignListItem {
  id: string;
  name: string;
  budget: string;
  keywords: string[];
  status: CampaignStatus;
  status_display: string;
  external_id: string | null;
  has_external_id: boolean;
  created_at: string;
}
```

### Campaign Stats

```typescript
interface CampaignStats {
  total: number;
  by_status: {
    PENDING?: number;
    PROCESSING?: number;
    ACTIVE?: number;
    FAILED?: number;
  };
}
```

### Paginated Response

```typescript
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

### Create Campaign Input

```typescript
interface CampaignCreateInput {
  name: string;
  budget: string | number;
  keywords: string[] | string;
}
```

---

## Estados de Campaña

```typescript
enum CampaignStatus {
  PENDING = "PENDING",           // Creada, esperando sincronización
  PROCESSING = "PROCESSING",     // Sincronizando con Amazon
  ACTIVE = "ACTIVE",             // Activa en Amazon
  FAILED = "FAILED"              // Sincronización fallida
}
```

### Flujo de Estados

```
┌─────────┐
│ PENDING │ → Creada localmente
└────┬────┘
     │ (Tarea asíncrona inicia)
     ▼
┌────────────┐
│ PROCESSING │ → Enviada a Amazon, esperando confirmación
└─────┬──────┘
      │
      ├─────► ┌────────┐
      │       │ ACTIVE │ → Confirmada por Amazon (éxito)
      │       └────────┘
      │
      └─────► ┌────────┐
              │ FAILED │ → Error en sincronización (reintentable)
              └────────┘
```

---

## Códigos de Error

### Errores HTTP

| Código | Significado | Cuándo Ocurre |
|--------|-------------|---------------|
| `400` | Bad Request | Datos de entrada inválidos |
| `404` | Not Found | Campaña no existe |
| `429` | Too Many Requests | Rate limit excedido |
| `500` | Internal Server Error | Error del servidor |

### Códigos de Error Personalizados

```typescript
interface ApiError {
  error?: {
    code: string;
    message: string;
  };
  // O errores de validación:
  [field: string]: string[];
}
```

**Códigos posibles:**
- `cannot_delete_synced`: No se puede eliminar campaña sincronizada
- `cannot_retry`: No se puede reintentar la campaña

---

## Ejemplos Frontend

### JavaScript/Fetch

#### 1. Crear Campaña

```javascript
async function createCampaign(campaignData) {
  try {
    const response = await fetch('http://localhost:8000/api/campaigns/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: campaignData.name,
        budget: campaignData.budget,
        keywords: campaignData.keywords
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }

    const campaign = await response.json();
    console.log('Campaña creada:', campaign);
    return campaign;
  } catch (error) {
    console.error('Error creando campaña:', error);
    throw error;
  }
}

// Uso
const newCampaign = await createCampaign({
  name: "Black Friday 2025",
  budget: "500.00",
  keywords: ["electronics", "deals", "discount"]
});
```

#### 2. Listar Campañas con Filtros

```javascript
async function getCampaigns(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.status) params.append('status', filters.status);
  if (filters.name) params.append('name', filters.name);
  if (filters.page) params.append('page', filters.page);
  if (filters.pageSize) params.append('page_size', filters.pageSize);
  if (filters.ordering) params.append('ordering', filters.ordering);

  const url = `http://localhost:8000/api/campaigns/?${params.toString()}`;

  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error obteniendo campañas:', error);
    throw error;
  }
}

// Uso
const activeCampaigns = await getCampaigns({ 
  status: 'ACTIVE', 
  ordering: '-created_at',
  pageSize: 20
});
```

#### 3. Obtener Detalle de Campaña

```javascript
async function getCampaignDetail(campaignId) {
  try {
    const response = await fetch(`http://localhost:8000/api/campaigns/${campaignId}/`);
    
    if (response.status === 404) {
      throw new Error('Campaña no encontrada');
    }

    const campaign = await response.json();
    return campaign;
  } catch (error) {
    console.error('Error obteniendo campaña:', error);
    throw error;
  }
}

// Uso
const campaign = await getCampaignDetail('550e8400-e29b-41d4-a716-446655440000');
```

#### 4. Eliminar Campaña

```javascript
async function deleteCampaign(campaignId) {
  try {
    const response = await fetch(`http://localhost:8000/api/campaigns/${campaignId}/`, {
      method: 'DELETE'
    });

    if (response.status === 400) {
      const error = await response.json();
      if (error.error?.code === 'cannot_delete_synced') {
        alert('No puedes eliminar una campaña sincronizada con Amazon');
        return false;
      }
    }

    if (!response.ok) {
      throw new Error('Error eliminando campaña');
    }

    return true;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

#### 5. Reintentar Campaña Fallida

```javascript
async function retryCampaign(campaignId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/campaigns/${campaignId}/retry/`,
      { method: 'POST' }
    );

    if (response.status === 400) {
      const error = await response.json();
      alert(error.error.message);
      return null;
    }

    const campaign = await response.json();
    console.log('Reintento iniciado:', campaign);
    return campaign;
  } catch (error) {
    console.error('Error reintentando campaña:', error);
    throw error;
  }
}
```

#### 6. Obtener Estadísticas

```javascript
async function getCampaignStats() {
  try {
    const response = await fetch('http://localhost:8000/api/campaigns/stats/');
    const stats = await response.json();
    return stats;
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
    throw error;
  }
}

// Uso
const stats = await getCampaignStats();
console.log(`Total: ${stats.total}`);
console.log(`Activas: ${stats.by_status.ACTIVE || 0}`);
console.log(`Fallidas: ${stats.by_status.FAILED || 0}`);
```

---

### React Example (Hooks)

```jsx
import { useState, useEffect } from 'react';

function CampaignList() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', page: 1 });

  useEffect(() => {
    async function loadCampaigns() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        params.append('page', filters.page);

        const response = await fetch(
          `http://localhost:8000/api/campaigns/?${params}`
        );
        const data = await response.json();
        setCampaigns(data.results);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    }

    loadCampaigns();
  }, [filters]);

  return (
    <div>
      <select onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
        <option value="">Todos</option>
        <option value="PENDING">Pendientes</option>
        <option value="PROCESSING">Procesando</option>
        <option value="ACTIVE">Activas</option>
        <option value="FAILED">Fallidas</option>
      </select>

      {loading ? (
        <p>Cargando...</p>
      ) : (
        <ul>
          {campaigns.map(campaign => (
            <li key={campaign.id}>
              {campaign.name} - ${campaign.budget} - {campaign.status_display}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### Axios Example

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Crear campaña
export const createCampaign = async (data) => {
  const response = await api.post('/campaigns/', data);
  return response.data;
};

// Listar campañas
export const getCampaigns = async (params = {}) => {
  const response = await api.get('/campaigns/', { params });
  return response.data;
};

// Detalle de campaña
export const getCampaign = async (id) => {
  const response = await api.get(`/campaigns/${id}/`);
  return response.data;
};

// Eliminar campaña
export const deleteCampaign = async (id) => {
  await api.delete(`/campaigns/${id}/`);
};

// Reintentar campaña
export const retryCampaign = async (id) => {
  const response = await api.post(`/campaigns/${id}/retry/`);
  return response.data;
};

// Estadísticas
export const getStats = async () => {
  const response = await api.get('/campaigns/stats/');
  return response.data;
};
```

---

## Casos de Uso Comunes

### 1. Dashboard de Campañas

```javascript
// Cargar estadísticas y lista de campañas
const [stats, campaigns] = await Promise.all([
  getStats(),
  getCampaigns({ ordering: '-created_at', page_size: 10 })
]);
```

### 2. Crear y Monitorear Campaña

```javascript
// 1. Crear campaña
const campaign = await createCampaign({
  name: "Spring Sale",
  budget: "200.00",
  keywords: ["spring", "sale", "discount"]
});

// 2. Polling para actualizar estado
const pollInterval = setInterval(async () => {
  const updated = await getCampaign(campaign.id);
  
  if (updated.status === 'ACTIVE') {
    console.log('Campaña activada!');
    clearInterval(pollInterval);
  } else if (updated.status === 'FAILED') {
    console.log('Campaña falló:', updated.error_message);
    clearInterval(pollInterval);
  }
}, 5000); // Cada 5 segundos
```

### 3. Filtrar Campañas Fallidas y Reintentar

```javascript
// Obtener campañas fallidas
const failedCampaigns = await getCampaigns({ status: 'FAILED' });

// Reintentar cada una
for (const campaign of failedCampaigns.results) {
  if (campaign.retry_count < 3) {
    await retryCampaign(campaign.id);
  }
}
```

---

## TypeScript Interfaces Completas

```typescript
// types.ts
export enum CampaignStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  ACTIVE = "ACTIVE",
  FAILED = "FAILED"
}

export interface Campaign {
  id: string;
  name: string;
  budget: string;
  keywords: string[];
  status: CampaignStatus;
  status_display: string;
  external_id: string | null;
  has_external_id: boolean;
  is_synced: boolean;
  error_message: string | null;
  retry_count: number;
  synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreateInput {
  name: string;
  budget: string | number;
  keywords: string[] | string;
}

export interface CampaignListItem {
  id: string;
  name: string;
  budget: string;
  keywords: string[];
  status: CampaignStatus;
  status_display: string;
  external_id: string | null;
  has_external_id: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CampaignStats {
  total: number;
  by_status: Partial<Record<CampaignStatus, number>>;
}

export interface ApiError {
  error?: {
    code: string;
    message: string;
  };
  [key: string]: any;
}

export interface CampaignFilters {
  status?: CampaignStatus;
  name?: string;
  has_external_id?: boolean;
  page?: number;
  page_size?: number;
  ordering?: string;
}
```

---

## Notas Importantes para Frontend

### 1. Procesamiento Asíncrono
Cuando creas una campaña, se devuelve inmediatamente en estado `PENDING`. La sincronización con Amazon se realiza en segundo plano. Debes implementar una de estas estrategias para actualizar el estado:

**Opción A: Polling** (recomendado para comenzar)
```javascript
const pollCampaignStatus = async (campaignId) => {
  const interval = setInterval(async () => {
    const campaign = await getCampaignDetail(campaignId);
    if (campaign.status !== 'PENDING' && campaign.status !== 'PROCESSING') {
      clearInterval(interval);
      // Actualizar UI
    }
  }, 3000); // Cada 3 segundos
};
```

**Opción B: WebSockets** (para actualizaciones en tiempo real, requiere configuración adicional en backend)

### 2. Paginación
- Por defecto son 20 resultados por página
- Usa los campos `next` y `previous` para navegar
- Personaliza con `page_size` (máximo recomendado: 100)

### 3. Formato de Datos

| Campo | Envío | Recepción |
|-------|-------|-----------|
| `budget` | String o Number | String con 2 decimales |
| `keywords` | Array o String CSV | Array de strings |
| `id` | - | UUID v4 string |
| `timestamps` | - | ISO 8601 UTC |

### 4. Rate Limiting
- **Anónimos**: 100 requests/hora
- **Autenticados**: 1000 requests/hora (cuando se implemente auth)
- Header `X-RateLimit-Remaining` indica requests restantes

### 5. CORS
Para desarrollo local, asegúrate de que el backend tenga CORS configurado:
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 6. Manejo de Errores
Siempre valida el código de respuesta HTTP:
```javascript
if (!response.ok) {
  const error = await response.json();
  // Manejar según el código de error
  if (error.error?.code === 'cannot_delete_synced') {
    // Mostrar mensaje específico
  }
}
```

### 7. UUIDs
- Los IDs son UUID v4, no uses números enteros
- Ejemplo: `550e8400-e29b-41d4-a716-446655440000`
- Valida formato UUID en el frontend antes de hacer requests

---

## Testing de la API

### Con cURL

```bash
# Crear campaña
curl -X POST http://localhost:8000/api/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "budget": "100.00",
    "keywords": ["test", "demo"]
  }'

# Listar campañas
curl http://localhost:8000/api/campaigns/

# Obtener detalle
curl http://localhost:8000/api/campaigns/{id}/

# Estadísticas
curl http://localhost:8000/api/campaigns/stats/
```

### Con Postman
Importa la colección desde Swagger:
1. Abre http://localhost:8000/api/docs/
2. Click en "Download OpenAPI specification"
3. Importa en Postman

---

## Soporte

Para dudas o problemas con la API:
- **Documentación interactiva**: http://localhost:8000/api/docs/
- **Logs del backend**: Revisa los logs de Django/Celery para detalles de errores
- **Equipo Backend**: [contacto del equipo]

---

**Última actualización**: 2025-12-14
**Versión API**: 1.0.0
