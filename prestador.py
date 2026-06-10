"""
Interfaz de Prestador para ARLINOST
Módulo que define la interfaz y funcionalidades del prestador
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Servicio:
    """Representa un servicio que puede ofrecer un prestador"""
    id: str
    nombre: str
    descripcion: str
    tarifa: float
    disponible: bool


@dataclass
class AsignacionSolicitud:
    """Representa la asignación de una solicitud a un prestador"""
    solicitud_id: str
    prestador_id: str
    fecha_asignacion: datetime
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    estado: str = "asignada"  # asignada, en_progreso, completada, rechazada


class PrestadorInterfaz(ABC):
    """Interfaz abstracta para prestadores en ARLINOST"""
    
    @abstractmethod
    def autenticar(self, usuario: str, contrasena: str) -> bool:
        """Autentica al prestador en el sistema"""
        pass
    
    @abstractmethod
    def registrar_servicios(self, servicios: List[Servicio]) -> bool:
        """Registra los servicios que ofrece el prestador"""
        pass
    
    @abstractmethod
    def listar_solicitudes_disponibles(self) -> List[Dict[str, Any]]:
        """Lista las solicitudes disponibles para el prestador"""
        pass
    
    @abstractmethod
    def aceptar_solicitud(self, solicitud_id: str) -> bool:
        """Acepta una solicitud para trabajar en ella"""
        pass
    
    @abstractmethod
    def rechazar_solicitud(self, solicitud_id: str, razon: str = "") -> bool:
        """Rechaza una solicitud asignada"""
        pass
    
    @abstractmethod
    def actualizar_progreso(self, solicitud_id: str, progreso: int, comentario: str = "") -> bool:
        """Actualiza el progreso de una solicitud en curso"""
        pass
    
    @abstractmethod
    def completar_solicitud(self, solicitud_id: str, resultado: str) -> bool:
        """Marca una solicitud como completada"""
        pass
    
    @abstractmethod
    def obtener_calificaciones(self) -> List[Dict[str, Any]]:
        """Obtiene todas las calificaciones recibidas"""
        pass
    
    @abstractmethod
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del prestador"""
        pass


class Prestador(PrestadorInterfaz):
    """Implementación concreta de Prestador para ARLINOST"""
    
    def __init__(self, prestador_id: str, nombre: str, email: str):
        self.prestador_id = prestador_id
        self.nombre = nombre
        self.email = email
        self.autenticado = False
        self.servicios: Dict[str, Servicio] = {}
        self.asignaciones: Dict[str, AsignacionSolicitud] = {}
        self.calificaciones: List[Dict[str, Any]] = []
        self.calificacion_promedio = 0.0
    
    def autenticar(self, usuario: str, contrasena: str) -> bool:
        """Autentica al prestador"""
        # TODO: Implementar autenticación real con base de datos
        self.autenticado = True
        return True
    
    def registrar_servicios(self, servicios: List[Servicio]) -> bool:
        """Registra los servicios"""
        if not self.autenticado:
            raise Exception("Prestador no autenticado")
        
        for servicio in servicios:
            self.servicios[servicio.id] = servicio
        return True
    
    def listar_solicitudes_disponibles(self) -> List[Dict[str, Any]]:
        """Lista solicitudes disponibles"""
        # TODO: Conectar con base de datos para obtener solicitudes
        return []
    
    def aceptar_solicitud(self, solicitud_id: str) -> bool:
        """Acepta una solicitud"""
        if not self.autenticado:
            raise Exception("Prestador no autenticado")
        
        asignacion = AsignacionSolicitud(
            solicitud_id=solicitud_id,
            prestador_id=self.prestador_id,
            fecha_asignacion=datetime.now(),
            estado="asignada"
        )
        self.asignaciones[solicitud_id] = asignacion
        return True
    
    def rechazar_solicitud(self, solicitud_id: str, razon: str = "") -> bool:
        """Rechaza una solicitud"""
        asignacion = self.asignaciones.get(solicitud_id)
        if asignacion:
            asignacion.estado = "rechazada"
            return True
        return False
    
    def actualizar_progreso(self, solicitud_id: str, progreso: int, comentario: str = "") -> bool:
        """Actualiza el progreso"""
        asignacion = self.asignaciones.get(solicitud_id)
        if asignacion:
            if asignacion.estado == "asignada":
                asignacion.estado = "en_progreso"
                asignacion.fecha_inicio = datetime.now()
            # TODO: Guardar progreso en base de datos
            return True
        return False
    
    def completar_solicitud(self, solicitud_id: str, resultado: str) -> bool:
        """Completa una solicitud"""
        asignacion = self.asignaciones.get(solicitud_id)
        if asignacion:
            asignacion.estado = "completada"
            asignacion.fecha_finalizacion = datetime.now()
            return True
        return False
    
    def obtener_calificaciones(self) -> List[Dict[str, Any]]:
        """Obtiene las calificaciones"""
        return self.calificaciones
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del prestador"""
        total_solicitudes = len(self.asignaciones)
        completadas = len([a for a in self.asignaciones.values() if a.estado == "completada"])
        
        return {
            "prestador_id": self.prestador_id,
            "nombre": self.nombre,
            "total_solicitudes": total_solicitudes,
            "solicitudes_completadas": completadas,
            "tasa_completacion": (completadas / total_solicitudes * 100) if total_solicitudes > 0 else 0,
            "calificacion_promedio": self.calificacion_promedio,
            "servicios_ofrecidos": len(self.servicios)
        }
