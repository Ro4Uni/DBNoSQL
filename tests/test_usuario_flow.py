import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


class UsuarioFlowTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def test_registro_crea_usuario_y_guarda_sesion(self):
        with patch("pymongo.collection.Collection.replace_one", return_value=None) as mock_replace:
            response = self.client.post(
                "/usuario/registro",
                data={
                    "rut": "12345678",
                    "nombre": "Ana",
                    "apellido": "Perez",
                },
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/usuario/eleccion")
        self.assertEqual(mock_replace.call_count, 1)

        with self.client.session_transaction() as session:
            self.assertEqual(session["user_rut"], "12345678")
            self.assertEqual(session["user_nombre"], "Ana")

    def test_perfil_dueno_guarda_datos(self):
        with self.client.session_transaction() as session:
            session["user_id"] = "USU12345678"
            session["rol"] = "dueno"

        with patch("pymongo.collection.Collection.insert_one", return_value=None) as mock_insert:
            response = self.client.post(
                "/usuario/perfil/dueno",
                data={
                    "correo": "dueno@example.com",
                    "telefono": "987654321",
                    "fecha_nacimiento": "1990-01-01",
                    "edad": "35",
                    "calle": "Av. Siempre Viva",
                    "comuna": "Santiago",
                    "region": "RM",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/mascota/formulario")
        self.assertEqual(mock_insert.call_count, 1)

    def test_perfil_veterinaria_guarda_lista_de_usuarios(self):
        with self.client.session_transaction() as session:
            session["user_id"] = "USU12345678"
            session["user_rut"] = "12345678"
            session["rol"] = "veterinaria"

        with patch("pymongo.collection.Collection.insert_one", return_value=None) as mock_insert:
            response = self.client.post(
                "/usuario/perfil/veterinaria",
                data={
                    "rut_recinto": "76543210",
                    "nombre_recinto": "Clínica Test",
                    "especialidad": "General",
                    "calle": "Calle 1",
                    "comuna": "Santiago",
                    "region": "RM",
                    "correo": "vet@example.com",
                    "tiempo_actividad": "3",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/usuario/resena")
        self.assertEqual(mock_insert.call_count, 1)


if __name__ == "__main__":
    unittest.main()
