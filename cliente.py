"""
Interfaz de Cliente para ARLINOST
Módulo que define la interfaz y funcionalidades del cliente
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Solicitud:
    """Representa una solicitud del cliente al prestador"""
    id: str
    cliente_id: str
    descripcion: str
    fecha_creacion: datetime
    estado: str  # pendiente, en_progreso, completada, cancelada
    prioridad: int  # 1-5, siendo 5 la mayor prioridad
    metadata: Dict[str, Any] = None


class ClienteInterfaz(ABC):
    """Interfaz abstracta para clientes en ARLINOST"""
    
    @abstractmethod
    def autenticar(self, usuario: str, contrasena: str) -> bool:
        """Autentica al cliente en el sistema"""
        pass
    
    @abstractmethod
    def crear_solicitud(self, descripcion: str, prioridad: int = 3) -> Solicitud:
        """Crea una nueva solicitud de servicio"""
        pass
    
    @abstractmethod
    def listar_solicitudes(self) -> List[Solicitud]:
        """Lista todas las solicitudes del cliente"""
        pass
    
    @abstractmethod
    def obtener_solicitud(self, solicitud_id: str) -> Optional[Solicitud]:
        """Obtiene los detalles de una solicitud específica"""
        pass
    
    @abstractmethod
    def cancelar_solicitud(self, solicitud_id: str) -> bool:
        """Cancela una solicitud pendiente"""
        pass
    
    @abstractmethod
    def calificar_prestador(self, prestador_id: str, calificacion: int, comentario: str = "") -> bool:
        """Califica al prestador después de completar el servicio"""
        pass
    
    @abstractmethod
    def obtener_historial(self) -> List[Solicitud]:
        """Obtiene el historial de todas las solicitudes completadas"""
        pass


class Cliente(ClienteInterfaz):
    """Implementación concreta de Cliente para ARLINOST"""
    
    def __init__(self, cliente_id: str, nombre: str, email: str):
        self.cliente_id = cliente_id
        self.nombre = nombre
        self.email = email
        self.autenticado = False
        self.solicitudes: Dict[str, Solicitud] = {}
    
    def autenticar(self, usuario: str, contrasena: str) -> bool:
        """Autentica al cliente"""
        # TODO: Implementar autenticación real con base de datos
        self.autenticado = True
        return True
    
    def crear_solicitud(self, descripcion: str, prioridad: int = 3) -> Solicitud:
        """Crea una nueva solicitud"""
        if not self.autenticado:
            raise Exception("Cliente no autenticado")
        
        solicitud_id = f"SOL-{len(self.solicitudes) + 1}"
        solicitud = Solicitud(
            id=solicitud_id,
            cliente_id=self.cliente_id,
            descripcion=descripcion,
            fecha_creacion=datetime.now(),
            estado="pendiente",
            prioridad=prioridad
        )
        self.solicitudes[solicitud_id] = solicitud
        return solicitud
    
    def listar_solicitudes(self) -> List[Solicitud]:
        """Lista todas las solicitudes"""
        return list(self.solicitudes.values())
    
    def obtener_solicitud(self, solicitud_id: str) -> Optional[Solicitud]:
        """Obtiene una solicitud específica"""
        return self.solicitudes.get(solicitud_id)
    
    def cancelar_solicitud(self, solicitud_id: str) -> bool:
        """Cancela una solicitud"""
        solicitud = self.solicitudes.get(solicitud_id)
        if solicitud and solicitud.estado == "pendiente":
            solicitud.estado = "cancelada"
            return True
        return False
    
    def calificar_prestador(self, prestador_id: str, calificacion: int, comentario: str = "") -> bool:
        """Califica al prestador"""
        # TODO: Implementar sistema de calificación
        return True
    
    def obtener_historial(self) -> List[Solicitud]:
        """Obtiene el historial de solicitudes completadas"""
        return [s for s in self.solicitudes.values() if s.estado == "completada"]
