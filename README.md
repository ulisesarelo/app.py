# ARLINOST - Interfaz Cliente y Prestador

Aplicación que proporciona interfaces para gestionar las interacciones entre clientes y prestadores de servicios.

## Características

### Interfaz de Cliente
- **Autenticación**: Acceso seguro al sistema
- **Crear Solicitudes**: Solicitar servicios específicos
- **Gestionar Solicitudes**: Listar, ver detalles, cancelar solicitudes
- **Calificar Prestadores**: Evaluar el servicio recibido
- **Historial**: Ver todas las solicitudes completadas

### Interfaz de Prestador
- **Autenticación**: Acceso seguro al sistema
- **Registrar Servicios**: Publicar servicios disponibles
- **Gestionar Solicitudes**: Aceptar, rechazar, actualizar progreso
- **Completar Trabajo**: Marcar solicitudes como finalizadas
- **Calificaciones**: Ver evaluaciones de clientes
- **Estadísticas**: Seguimiento de desempeño

## Estructura del Proyecto

```
.
├── cliente.py          # Interfaz y implementación de Cliente
├── prestador.py        # Interfaz y implementación de Prestador
├── README.md           # Este archivo
└── requirements.txt    # Dependencias del proyecto
```

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/ulisesarelo/app.py.git
cd app.py

# Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Cliente

```python
from cliente import Cliente

# Crear una instancia de cliente
cliente = Cliente("CLI001", "Juan Pérez", "juan@email.com")

# Autenticar
cliente.autenticar("usuario", "contraseña")

# Crear una solicitud
solicitud = cliente.crear_solicitud("Necesito reparación de plomería", prioridad=4)
print(f"Solicitud creada: {solicitud.id}")

# Listar solicitudes
solicitudes = cliente.listar_solicitudes()
for sol in solicitudes:
    print(f"Solicitud {sol.id}: {sol.descripcion} - Estado: {sol.estado}")
```

### Prestador

```python
from prestador import Prestador, Servicio

# Crear una instancia de prestador
prestador = Prestador("PRES001", "Carlos López", "carlos@email.com")

# Autenticar
prestador.autenticar("usuario", "contraseña")

# Registrar servicios
servicios = [
    Servicio("SRV001", "Plomería", "Reparación de tuberías", 50.0, True),
    Servicio("SRV002", "Electricidad", "Instalación eléctrica", 75.0, True)
]
prestador.registrar_servicios(servicios)

# Ver estadísticas
stats = prestador.obtener_estadisticas()
print(f"Tasa de completación: {stats['tasa_completacion']:.1f}%")
```

## Próximos Pasos

- [ ] Integración con base de datos
- [ ] Sistema de autenticación segura
- [ ] API REST
- [ ] Interfaz web (Frontend)
- [ ] Sistema de notificaciones
- [ ] Integración de pagos
- [ ] Tests unitarios

## Contribuir

Las contribuciones son bienvenidas. Por favor, abra un issue o un pull request.

## Licencia

Este proyecto está bajo la licencia MIT.
