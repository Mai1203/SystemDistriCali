from app.configuracion import PERMISOS_VISTAS
from app.database.manager import db_manager
from app.models.usuarios import Rol
from sqlalchemy.orm import Session


class PermisosPolicy:
    def obtener(self, usuario):
        # 1. Tupla de obtener_usuario_por_id (tiene 'rol' como string en el tuple)
        if isinstance(usuario, tuple):
            # La consulta selecciona Rol.Nombre.label("rol") en posición 6
            if len(usuario) > 6 and usuario[6] == "ADMINISTRADOR":
                return set(PERMISOS_VISTAS)
        # 2. Objeto ORM - leer ID_Rol directamente (columna, no relación)
        id_rol = getattr(usuario, 'ID_Rol', None)
        if id_rol is not None:
            try:
                engine = db_manager.get_engine()
                with Session(bind=engine) as db:
                    rol = db.query(Rol).filter(Rol.ID_Rol == id_rol).first()
                    if rol and rol.Nombre == "ADMINISTRADOR":
                        return set(PERMISOS_VISTAS)
            except Exception:
                pass

        # Usuario normal: usar campo Permisos
        permisos_str = getattr(usuario, 'Permisos', '') or ""
        return {
            permiso.strip()
            for permiso in permisos_str.split(",")
            if permiso.strip() in PERMISOS_VISTAS
        }

    def puede_acceder(self, usuario, vista):
        return vista in self.obtener(usuario)


def obtener_permisos_usuario(usuario):
    return PermisosPolicy().obtener(usuario)
