"""
Tests unitarios para ARLINOST
Pruebas para cliente, prestador y sistema
"""

import unittest
from datetime import datetime
from cliente import Cliente, Solicitud, ClienteInterfaz
from prestador import Prestador, Servicio, PrestadorInterfaz
from app_main import SistemaARLINOST
from database import DatabaseARLINOST
from auth import AuthARLINOST


class TestCliente(unittest.TestCase):
    """Tests para la clase Cliente"""
    
    def setUp(self):
        self.cliente = Cliente("CLI001", "Juan Pérez", "juan@email.com")
    
    def test_autenticacion(self):
        """Prueba autenticación del cliente"""
        resultado = self.cliente.autenticar("usuario", "contraseña")
        self.assertTrue(resultado)
        self.assertTrue(self.cliente.autenticado)
    
    def test_crear_solicitud(self):
        """Prueba creación de solicitud"""
        self.cliente.autenticar("usuario", "contraseña")
        solicitud = self.cliente.crear_solicitud("Necesito reparación", prioridad=4)
        
        self.assertIsNotNone(solicitud)
        self.assertEqual(solicitud.cliente_id, "CLI001")
        self.assertEqual(solicitud.estado, "pendiente")
        self.assertEqual(solicitud.prioridad, 4)
    
    def test_listar_solicitudes(self):
        """Prueba listado de solicitudes"""
        self.cliente.autenticar("usuario", "contraseña")
        self.cliente.crear_solicitud("Solicitud 1")
        self.cliente.crear_solicitud("Solicitud 2")
        
        solicitudes = self.cliente.listar_solicitudes()
        self.assertEqual(len(solicitudes), 2)
    
    def test_cancelar_solicitud(self):
        """Prueba cancelación de solicitud"""
        self.cliente.autenticar("usuario", "contraseña")
        solicitud = self.cliente.crear_solicitud("Solicitud")
        resultado = self.cliente.cancelar_solicitud(solicitud.id)
        
        self.assertTrue(resultado)
        self.assertEqual(solicitud.estado, "cancelada")


class TestPrestador(unittest.TestCase):
    """Tests para la clase Prestador"""
    
    def setUp(self):
        self.prestador = Prestador("PRES001", "Carlos López", "carlos@email.com")
    
    def test_autenticacion(self):
        """Prueba autenticación del prestador"""
        resultado = self.prestador.autenticar("usuario", "contraseña")
        self.assertTrue(resultado)
        self.assertTrue(self.prestador.autenticado)
    
    def test_registrar_servicios(self):
        """Prueba registro de servicios"""
        self.prestador.autenticar("usuario", "contraseña")
        servicios = [
            Servicio("SRV001", "Plomería", "Reparación", 50.0, True),
            Servicio("SRV002", "Fontanería", "Mantenimiento", 40.0, True)
        ]
        resultado = self.prestador.registrar_servicios(servicios)
        
        self.assertTrue(resultado)
        self.assertEqual(len(self.prestador.servicios), 2)
    
    def test_aceptar_solicitud(self):
        """Prueba aceptación de solicitud"""
        self.prestador.autenticar("usuario", "contraseña")
        resultado = self.prestador.aceptar_solicitud("SOL001")
        
        self.assertTrue(resultado)
        self.assertIn("SOL001", self.prestador.asignaciones)
    
    def test_completar_solicitud(self):
        """Prueba completación de solicitud"""
        self.prestador.autenticar("usuario", "contraseña")
        self.prestador.aceptar_solicitud("SOL001")
        resultado = self.prestador.completar_solicitud("SOL001", "Trabajo completado")
        
        self.assertTrue(resultado)
        self.assertEqual(self.prestador.asignaciones["SOL001"].estado, "completada")
    
    def test_obtener_estadisticas(self):
        """Prueba obtención de estadísticas"""
        self.prestador.autenticar("usuario", "contraseña")
        self.prestador.aceptar_solicitud("SOL001")
        self.prestador.completar_solicitud("SOL001", "Completada")
        
        stats = self.prestador.obtener_estadisticas()
        self.assertEqual(stats['solicitudes_completadas'], 1)


class TestSistemaARLINOST(unittest.TestCase):
    """Tests para el sistema principal"""
    
    def setUp(self):
        self.sistema = SistemaARLINOST()
    
    def test_registrar_cliente(self):
        """Prueba registro de cliente"""
        cliente = self.sistema.registrar_cliente("CLI001", "Juan", "juan@email.com")
        self.assertIsNotNone(cliente)
        self.assertEqual(self.sistema.obtener_cliente("CLI001").nombre, "Juan")
    
    def test_registrar_prestador(self):
        """Prueba registro de prestador"""
        prestador = self.sistema.registrar_prestador("PRES001", "Carlos", "carlos@email.com")
        self.assertIsNotNone(prestador)
        self.assertEqual(self.sistema.obtener_prestador("PRES001").nombre, "Carlos")
    
    def test_crear_solicitud(self):
        """Prueba creación de solicitud en el sistema"""
        self.sistema.registrar_cliente("CLI001", "Juan", "juan@email.com")
        solicitud = self.sistema.crear_solicitud("CLI001", "Necesito servicio", prioridad=5)
        
        self.assertIsNotNone(solicitud)
        self.assertEqual(solicitud.estado, "pendiente")
    
    def test_asignar_solicitud(self):
        """Prueba asignación de solicitud"""
        self.sistema.registrar_cliente("CLI001", "Juan", "juan@email.com")
        self.sistema.registrar_prestador("PRES001", "Carlos", "carlos@email.com")
        
        solicitud = self.sistema.crear_solicitud("CLI001", "Servicio")
        resultado = self.sistema.asignar_solicitud(solicitud.id, "PRES001")
        
        self.assertTrue(resultado)
        self.assertEqual(solicitud.estado, "asignada")
    
    def test_completar_flujo(self):
        """Prueba flujo completo: crear, asignar, completar, calificar"""
        # Registrar
        self.sistema.registrar_cliente("CLI001", "Juan", "juan@email.com")
        self.sistema.registrar_prestador("PRES001", "Carlos", "carlos@email.com")
        
        # Crear solicitud
        solicitud = self.sistema.crear_solicitud("CLI001", "Reparación", prioridad=4)
        
        # Asignar
        self.sistema.asignar_solicitud(solicitud.id, "PRES001")
        
        # Actualizar progreso
        self.sistema.actualizar_progreso_solicitud(solicitud.id, 50, "En progreso")
        
        # Completar
        self.sistema.completar_solicitud(solicitud.id, "Completado exitosamente")
        
        # Calificar
        resultado = self.sistema.calificar_prestador("CLI001", "PRES001", 5, "Excelente")
        
        self.assertTrue(resultado)
        self.assertEqual(solicitud.estado, "completada")


class TestDatabase(unittest.TestCase):
    """Tests para la base de datos"""
    
    def setUp(self):
        self.db = DatabaseARLINOST("test_arlinost.db")
    
    def tearDown(self):
        self.db.limpiar_base_datos()
    
    def test_insertar_cliente(self):
        """Prueba inserción de cliente en BD"""
        resultado = self.db.insertar_cliente("CLI001", "Juan", "juan@email.com")
        self.assertTrue(resultado)
    
    def test_obtener_cliente(self):
        """Prueba obtención de cliente de BD"""
        self.db.insertar_cliente("CLI001", "Juan", "juan@email.com")
        cliente = self.db.obtener_cliente("CLI001")
        
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente['nombre'], "Juan")
    
    def test_listar_clientes(self):
        """Prueba listado de clientes"""
        self.db.insertar_cliente("CLI001", "Juan", "juan@email.com")
        self.db.insertar_cliente("CLI002", "María", "maria@email.com")
        
        clientes = self.db.listar_clientes()
        self.assertEqual(len(clientes), 2)
    
    def test_insertar_solicitud(self):
        """Prueba inserción de solicitud"""
        self.db.insertar_cliente("CLI001", "Juan", "juan@email.com")
        resultado = self.db.insertar_solicitud("SOL001", "CLI001", "Descripción", 4)
        self.assertTrue(resultado)
    
    def test_actualizar_estado_solicitud(self):
        """Prueba actualización de estado"""
        self.db.insertar_cliente("CLI001", "Juan", "juan@email.com")
        self.db.insertar_solicitud("SOL001", "CLI001", "Descripción")
        self.db.actualizar_estado_solicitud("SOL001", "asignada")
        
        solicitud = self.db.obtener_solicitud("SOL001")
        self.assertEqual(solicitud['estado'], "asignada")


class TestAuth(unittest.TestCase):
    """Tests para autenticación"""
    
    def setUp(self):
        self.auth = AuthARLINOST()
    
    def test_registrar_usuario(self):
        """Prueba registro de usuario"""
        resultado = self.auth.registrar_usuario(
            "USR001", "usuario", "usuario@email.com", "password123"
        )
        self.assertTrue(resultado)
    
    def test_autenticar_usuario(self):
        """Prueba autenticación de usuario"""
        self.auth.registrar_usuario(
            "USR001", "usuario", "usuario@email.com", "password123"
        )
        token = self.auth.autenticar("USR001", "password123")
        self.assertIsNotNone(token)
    
    def test_autenticar_con_credenciales_invalidas(self):
        """Prueba autenticación con credenciales inválidas"""
        self.auth.registrar_usuario(
            "USR001", "usuario", "usuario@email.com", "password123"
        )
        token = self.auth.autenticar("USR001", "wrongpassword")
        self.assertIsNone(token)
    
    def test_validar_token(self):
        """Prueba validación de token"""
        self.auth.registrar_usuario(
            "USR001", "usuario", "usuario@email.com", "password123"
        )
        token = self.auth.autenticar("USR001", "password123")
        
        valido, usuario_id = self.auth.validar_token(token)
        self.assertTrue(valido)
        self.assertEqual(usuario_id, "USR001")
    
    def test_obtener_usuario(self):
        """Prueba obtención de datos de usuario (sin contraseña)"""
        self.auth.registrar_usuario(
            "USR001", "usuario", "usuario@email.com", "password123", "admin"
        )
        usuario = self.auth.obtener_usuario("USR001")
        
        self.assertIsNotNone(usuario)
        self.assertNotIn('password', usuario)
        self.assertEqual(usuario['rol'], "admin")


if __name__ == '__main__':
    unittest.main()
