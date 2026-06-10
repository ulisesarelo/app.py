"""
Sistema Principal de ARLINOST
Orquesta la interacción entre clientes y prestadores
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from cliente import Cliente, Solicitud
from prestador import Prestador, Servicio


class SistemaARLINOST:
    """Sistema central que gestiona clientes, prestadores y solicitudes"""
    
    def __init__(self):
        self.clientes: Dict[str, Cliente] = {}
        self.prestadores: Dict[str, Prestador] = {}
        self.solicitudes: Dict[str, Solicitud] = {}
        self.asignaciones: Dict[str, str] = {}  # solicitud_id -> prestador_id
        self.contador_solicitudes = 0
    
    # ==================== GESTIÓN DE CLIENTES ====================
    
    def registrar_cliente(self, cliente_id: str, nombre: str, email: str) -> Cliente:
        """Registra un nuevo cliente en el sistema"""
        if cliente_id in self.clientes:
            raise ValueError(f"Cliente {cliente_id} ya existe")
        
        cliente = Cliente(cliente_id, nombre, email)
        self.clientes[cliente_id] = cliente
        print(f"✓ Cliente registrado: {nombre} ({cliente_id})")
        return cliente
    
    def obtener_cliente(self, cliente_id: str) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        return self.clientes.get(cliente_id)
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes registrados"""
        return list(self.clientes.values())
    
    # ==================== GESTIÓN DE PRESTADORES ====================
    
    def registrar_prestador(self, prestador_id: str, nombre: str, email: str) -> Prestador:
        """Registra un nuevo prestador en el sistema"""
        if prestador_id in self.prestadores:
            raise ValueError(f"Prestador {prestador_id} ya existe")
        
        prestador = Prestador(prestador_id, nombre, email)
        self.prestadores[prestador_id] = prestador
        print(f"✓ Prestador registrado: {nombre} ({prestador_id})")
        return prestador
    
    def obtener_prestador(self, prestador_id: str) -> Optional[Prestador]:
        """Obtiene un prestador por su ID"""
        return self.prestadores.get(prestador_id)
    
    def listar_prestadores(self) -> List[Prestador]:
        """Lista todos los prestadores registrados"""
        return list(self.prestadores.values())
    
    # ==================== GESTIÓN DE SOLICITUDES ====================
    
    def crear_solicitud(self, cliente_id: str, descripcion: str, prioridad: int = 3) -> Solicitud:
        """Crea una nueva solicitud desde un cliente"""
        cliente = self.obtener_cliente(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")
        
        if not cliente.autenticado:
            cliente.autenticar("usuario", "contraseña")
        
        solicitud = cliente.crear_solicitud(descripcion, prioridad)
        self.solicitudes[solicitud.id] = solicitud
        self.contador_solicitudes += 1
        
        print(f"✓ Solicitud creada: {solicitud.id}")
        print(f"  Cliente: {cliente.nombre}")
        print(f"  Descripción: {descripcion}")
        print(f"  Prioridad: {prioridad}/5")
        
        return solicitud
    
    def listar_solicitudes_pendientes(self) -> List[Solicitud]:
        """Lista todas las solicitudes pendientes"""
        return [s for s in self.solicitudes.values() if s.estado == "pendiente"]
    
    def obtener_solicitud(self, solicitud_id: str) -> Optional[Solicitud]:
        """Obtiene una solicitud por su ID"""
        return self.solicitudes.get(solicitud_id)
    
    # ==================== ASIGNACIÓN DE SOLICITUDES ====================
    
    def asignar_solicitud(self, solicitud_id: str, prestador_id: str) -> bool:
        """Asigna una solicitud a un prestador"""
        solicitud = self.obtener_solicitud(solicitud_id)
        prestador = self.obtener_prestador(prestador_id)
        
        if not solicitud:
            raise ValueError(f"Solicitud {solicitud_id} no existe")
        if not prestador:
            raise ValueError(f"Prestador {prestador_id} no existe")
        
        if solicitud.estado != "pendiente":
            raise ValueError(f"Solo se pueden asignar solicitudes pendientes")
        
        if not prestador.autenticado:
            prestador.autenticar("usuario", "contraseña")
        
        # Aceptar la solicitud en el prestador
        prestador.aceptar_solicitud(solicitud_id)
        
        # Actualizar estado de la solicitud
        solicitud.estado = "asignada"
        self.asignaciones[solicitud_id] = prestador_id
        
        print(f"✓ Solicitud asignada:")
        print(f"  Solicitud: {solicitud_id}")
        print(f"  Prestador: {prestador.nombre}")
        
        return True
    
    def obtener_prestador_asignado(self, solicitud_id: str) -> Optional[Prestador]:
        """Obtiene el prestador asignado a una solicitud"""
        prestador_id = self.asignaciones.get(solicitud_id)
        if prestador_id:
            return self.obtener_prestador(prestador_id)
        return None
    
    # ==================== PROGRESO Y ACTUALIZACIÓN ====================
    
    def actualizar_progreso_solicitud(self, solicitud_id: str, progreso: int, comentario: str = "") -> bool:
        """Actualiza el progreso de una solicitud en curso"""
        solicitud = self.obtener_solicitud(solicitud_id)
        prestador = self.obtener_prestador_asignado(solicitud_id)
        
        if not solicitud or not prestador:
            return False
        
        prestador.actualizar_progreso(solicitud_id, progreso, comentario)
        solicitud.estado = "en_progreso"
        
        print(f"✓ Progreso actualizado: {solicitud_id} - {progreso}%")
        if comentario:
            print(f"  Comentario: {comentario}")
        
        return True
    
    def completar_solicitud(self, solicitud_id: str, resultado: str) -> bool:
        """Completa una solicitud"""
        solicitud = self.obtener_solicitud(solicitud_id)
        prestador = self.obtener_prestador_asignado(solicitud_id)
        
        if not solicitud or not prestador:
            return False
        
        prestador.completar_solicitud(solicitud_id, resultado)
        solicitud.estado = "completada"
        
        print(f"✓ Solicitud completada: {solicitud_id}")
        print(f"  Resultado: {resultado}")
        
        return True
    
    # ==================== CALIFICACIONES ====================
    
    def calificar_prestador(self, cliente_id: str, prestador_id: str, 
                           calificacion: int, comentario: str = "") -> bool:
        """Cliente califica a un prestador"""
        cliente = self.obtener_cliente(cliente_id)
        prestador = self.obtener_prestador(prestador_id)
        
        if not cliente or not prestador:
            return False
        
        if calificacion < 1 or calificacion > 5:
            raise ValueError("Calificación debe estar entre 1 y 5")
        
        cliente.calificar_prestador(prestador_id, calificacion, comentario)
        
        # Guardar en el prestador
        calificacion_data = {
            "cliente_id": cliente_id,
            "calificacion": calificacion,
            "comentario": comentario,
            "fecha": datetime.now().isoformat()
        }
        prestador.calificaciones.append(calificacion_data)
        
        # Actualizar promedio
        if prestador.calificaciones:
            promedio = sum(c["calificacion"] for c in prestador.calificaciones) / len(prestador.calificaciones)
            prestador.calificacion_promedio = round(promedio, 2)
        
        print(f"✓ Calificación registrada:")
        print(f"  Cliente: {cliente.nombre}")
        print(f"  Prestador: {prestador.nombre}")
        print(f"  Calificación: {'⭐' * calificacion} ({calificacion}/5)")
        if comentario:
            print(f"  Comentario: {comentario}")
        
        return True
    
    # ==================== REPORTES Y ESTADÍSTICAS ====================
    
    def obtener_estadisticas_sistema(self) -> Dict:
        """Obtiene estadísticas generales del sistema"""
        total_clientes = len(self.clientes)
        total_prestadores = len(self.prestadores)
        total_solicitudes = len(self.solicitudes)
        
        solicitudes_pendientes = len(self.listar_solicitudes_pendientes())
        solicitudes_completadas = len([s for s in self.solicitudes.values() if s.estado == "completada"])
        
        return {
            "total_clientes": total_clientes,
            "total_prestadores": total_prestadores,
            "total_solicitudes": total_solicitudes,
            "solicitudes_pendientes": solicitudes_pendientes,
            "solicitudes_completadas": solicitudes_completadas,
            "tasa_completacion": (solicitudes_completadas / total_solicitudes * 100) if total_solicitudes > 0 else 0
        }
    
    def obtener_estadisticas_prestador(self, prestador_id: str) -> Optional[Dict]:
        """Obtiene estadísticas de un prestador específico"""
        prestador = self.obtener_prestador(prestador_id)
        if not prestador:
            return None
        
        return prestador.obtener_estadisticas()
    
    def generar_reporte(self):
        """Genera un reporte completo del sistema"""
        stats = self.obtener_estadisticas_sistema()
        
        print("\n" + "="*60)
        print("REPORTE DE SISTEMA - ARLINOST")
        print("="*60)
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"  • Clientes registrados: {stats['total_clientes']}")
        print(f"  • Prestadores registrados: {stats['total_prestadores']}")
        print(f"  • Total de solicitudes: {stats['total_solicitudes']}")
        print(f"  • Solicitudes pendientes: {stats['solicitudes_pendientes']}")
        print(f"  • Solicitudes completadas: {stats['solicitudes_completadas']}")
        print(f"  • Tasa de completación: {stats['tasa_completacion']:.1f}%")
        
        print(f"\n👥 CLIENTES:")
        for cliente in self.listar_clientes():
            print(f"  • {cliente.nombre} ({cliente.cliente_id}) - {cliente.email}")
        
        print(f"\n🔧 PRESTADORES:")
        for prestador in self.listar_prestadores():
            stats_pres = prestador.obtener_estadisticas()
            print(f"  • {prestador.nombre} ({prestador.prestador_id})")
            print(f"    - Calificación: {'⭐' * int(prestador.calificacion_promedio) if prestador.calificacion_promedio > 0 else 'Sin calificación'} ({prestador.calificacion_promedio})")
            print(f"    - Servicios: {stats_pres['servicios_ofrecidos']}")
            print(f"    - Solicitudes completadas: {stats_pres['solicitudes_completadas']}")
        
        print(f"\n📋 SOLICITUDES:")
        for solicitud in self.solicitudes.values():
            prestador = self.obtener_prestador_asignado(solicitud.id)
            prestador_nombre = prestador.nombre if prestador else "Sin asignar"
            prioridad_str = "🔴" * solicitud.prioridad if solicitud.prioridad else ""
            print(f"  • {solicitud.id} - {solicitud.estado.upper()}")
            print(f"    - Cliente: {self.clientes[solicitud.cliente_id].nombre}")
            print(f"    - Prestador: {prestador_nombre}")
            print(f"    - Prioridad: {prioridad_str} ({solicitud.prioridad}/5)")
            print(f"    - Descripción: {solicitud.descripcion}")
        
        print("\n" + "="*60 + "\n")


# ==================== DEMOSTRACIÓN ====================

if __name__ == "__main__":
    # Crear instancia del sistema
    sistema = SistemaARLINOST()
    
    print("\n🚀 INICIANDO DEMOSTRACIÓN DE ARLINOST\n")
    
    # Registrar clientes
    cliente1 = sistema.registrar_cliente("CLI001", "Juan Pérez", "juan@email.com")
    cliente2 = sistema.registrar_cliente("CLI002", "María García", "maria@email.com")
    
    # Registrar prestadores
    prestador1 = sistema.registrar_prestador("PRES001", "Carlos López", "carlos@email.com")
    prestador2 = sistema.registrar_prestador("PRES002", "Ana Martínez", "ana@email.com")
    
    # Registrar servicios
    servicios_carlos = [
        Servicio("SRV001", "Plomería", "Reparación de tuberías", 50.0, True),
        Servicio("SRV002", "Fontanería general", "Mantenimiento general", 40.0, True)
    ]
    prestador1.registrar_servicios(servicios_carlos)
    
    servicios_ana = [
        Servicio("SRV003", "Electricidad", "Instalación eléctrica", 75.0, True),
        Servicio("SRV004", "Reparación de equipos", "Reparación eléctrica", 60.0, True)
    ]
    prestador2.registrar_servicios(servicios_ana)
    
    # Crear solicitudes
    print("\n📝 CREANDO SOLICITUDES:\n")
    sol1 = sistema.crear_solicitud("CLI001", "Necesito reparación de plomería urgente", prioridad=5)
    sol2 = sistema.crear_solicitud("CLI002", "Revisar instalación eléctrica de mi casa", prioridad=4)
    sol3 = sistema.crear_solicitud("CLI001", "Mantenimiento general de fontanería", prioridad=2)
    
    # Asignar solicitudes
    print("\n🔗 ASIGNANDO SOLICITUDES:\n")
    sistema.asignar_solicitud(sol1.id, "PRES001")
    sistema.asignar_solicitud(sol2.id, "PRES002")
    sistema.asignar_solicitud(sol3.id, "PRES001")
    
    # Actualizar progreso
    print("\n⏳ ACTUALIZANDO PROGRESO:\n")
    sistema.actualizar_progreso_solicitud(sol1.id, 50, "Encontré la fuga, trabajando en la reparación")
    sistema.actualizar_progreso_solicitud(sol2.id, 75, "Casi terminado, ajustando circuitos")
    
    # Completar solicitudes
    print("\n✅ COMPLETANDO SOLICITUDES:\n")
    sistema.completar_solicitud(sol1.id, "Tubería reparada correctamente, probada y funcionando")
    sistema.completar_solicitud(sol2.id, "Instalación completada, todo funcionando correctamente")
    
    # Calificar prestadores
    print("\n⭐ CALIFICANDO PRESTADORES:\n")
    sistema.calificar_prestador("CLI001", "PRES001", 5, "Excelente trabajo, muy profesional")
    sistema.calificar_prestador("CLI002", "PRES002", 4, "Buen trabajo, pero podría mejorar la comunicación")
    
    # Generar reporte
    sistema.generar_reporte()
